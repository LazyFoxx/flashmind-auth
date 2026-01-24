import asyncio
import secrets

from fastapi import BackgroundTasks
from src.core.settings import VerificationCodeConfig, RateLimitConfig
from src.application.dtos import AuthCredentialsDTO
from src.application.exceptions import (
    EmailAlreadyExistsError,
    RateLimitExceededError,
    CooldownEmailError,
)
from src.application.interfaces import (
    AbstractEmailSender,
    AbstractHasher,
    AbstractRateLimitRepository,
    AbstractVerificationCodeRepository,
    AbstractUnitOfWork,
)
from src.domain.value_objects import Email, HashedPassword


class InitiateRegistrationUseCase:
    def __init__(
        self,
        hasher: AbstractHasher,
        rate_limit_repo: AbstractRateLimitRepository,
        verification_code_repo: AbstractVerificationCodeRepository,
        email_sender: AbstractEmailSender,
        uow: AbstractUnitOfWork,
        verification_code_cfg: VerificationCodeConfig,
        rate_limit_cgf: RateLimitConfig,
    ):
        self.hasher = hasher
        self.rate_limit_repo = rate_limit_repo
        self.verification_code_repo = verification_code_repo
        self.email_sender = email_sender
        self.uow = uow
        self.register_limit = rate_limit_cgf.register_limit
        self.register_window_seconds = rate_limit_cgf.register_window_seconds
        self.ttl_seconds = verification_code_cfg.ttl_seconds
        self.max_attempts = verification_code_cfg.max_attempts
        self.resend_code_cooldown_seconds = rate_limit_cgf.resend_code_cooldown_seconds

    async def execute(
        self, input_dto: AuthCredentialsDTO, background_tasks: BackgroundTasks
    ) -> None:
        email_vo = Email.create(input_dto.email)

        password_hash = HashedPassword(
            await asyncio.to_thread(self.hasher.hash, input_dto.password)
        )

        # Проверка уникальности email
        async with self.uow:
            if await self.uow.users.get_by_email(email_vo.value):
                raise EmailAlreadyExistsError(email=email_vo.value)

            await self.uow.commit()

        # Rate limiting
        is_allowed, _, _ = await self.rate_limit_repo.increment_and_check(
            email=email_vo.value,
            prefix="register",
            limit_attempts=self.register_limit,
            window_seconds=self.register_window_seconds,
        )
        if not is_allowed:
            raise RateLimitExceededError(
                "Слишком много попыток регистрации, повторите через час"
            )

        # проверяем rate limit на отправвку email
        created, seconds_left = await self.rate_limit_repo.check_and_set_cooldown(
            email=email_vo.value, cooldown=self.resend_code_cooldown_seconds
        )
        if not created:
            raise CooldownEmailError(remaining_seconds=seconds_left)

        # Генерируем код верификации
        otp = str(secrets.randbelow(899000) + 100000)
        # Отправляем код верификации на email пользователя
        await self.email_sender.send_register_verification_code(
            email_vo.value, otp, background_tasks=background_tasks
        )
        # Хешируем код для безопасности
        otp_hash = await asyncio.to_thread(self.hasher.hash, otp)
        # Сохраняет временные данные о регистрации  в Redis (email, password_hash, otp_hash)
        await self.verification_code_repo.create_pending(
            email=email_vo.value,
            hashed_password=password_hash.value,
            otp_hash=otp_hash,
            ttl_seconds=self.ttl_seconds,
            max_attempts=self.max_attempts,
        )

        return None
