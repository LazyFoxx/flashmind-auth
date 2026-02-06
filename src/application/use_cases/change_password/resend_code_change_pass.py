import asyncio
import secrets
from fastapi import BackgroundTasks
from src.core.settings import VerificationCodeConfig, RateLimitConfig
from src.application.exceptions import CooldownEmailError, RequestExpiredError
from src.application.interfaces import (
    AbstractEmailSender,
    AbstractRateLimitRepository,
    AbstractVerificationCodeRepository,
    AbstractUnitOfWork,
    AbstractHasher,
)
from src.domain.value_objects import Email


class ResendCodeChangePasswordUseCase:
    def __init__(
        self,
        rate_limit_repo: AbstractRateLimitRepository,
        hasher: AbstractHasher,
        verification_code_repo: AbstractVerificationCodeRepository,
        email_sender: AbstractEmailSender,
        uow: AbstractUnitOfWork,
        verification_code_cfg: VerificationCodeConfig,
        rate_limit_cgf: RateLimitConfig,
    ):
        self.rate_limit_repo = rate_limit_repo
        self.hasher = hasher
        self.verification_code_repo = verification_code_repo
        self.email_sender = email_sender
        self.uow = uow
        self.reset_pass_limit = rate_limit_cgf.reset_pass_limit
        self.reset_pass_window_seconds = rate_limit_cgf.reset_pass_window_seconds
        self.ttl_seconds = verification_code_cfg.ttl_seconds
        self.max_attempts = verification_code_cfg.max_attempts
        self.resend_code_cooldown_seconds = rate_limit_cgf.resend_code_cooldown_seconds

    async def execute(self, email: str, background_tasks: BackgroundTasks) -> None:
        email_vo = Email.create(email)

        user_data = await self.verification_code_repo.get_pending(email=email)

        # Проверяем наличие pending registration в редис
        if user_data is None:
            raise RequestExpiredError(str("Запрос истек. Начните сброс пароля заново"))

        # проверяем rate limit на отправвку email
        created, seconds_left = await self.rate_limit_repo.check_and_set_cooldown(
            email=email_vo.value, cooldown=self.resend_code_cooldown_seconds
        )
        if not created:
            raise CooldownEmailError(remaining_seconds=seconds_left)

        # Генерируем код верификации
        otp = str(secrets.randbelow(899000) + 100000)
        # Отправляем код верификации на email пользователя
        await self.email_sender.send_fogot_password_verification_code(
            email_vo.value, otp, background_tasks=background_tasks
        )
        # Хешируем код для безопасности
        otp_hash = await asyncio.to_thread(self.hasher.hash, otp)
        # Сохраняет временные данные в Redis (email, otp_hash)
        await self.verification_code_repo.create_pending(
            email=email_vo.value,
            otp_hash=otp_hash,
            ttl_seconds=self.ttl_seconds,
            max_attempts=self.max_attempts,
        )

        return None
