import asyncio
import secrets
from src.core.settings import VerificationCodeConfig, RateLimitConfig
from src.application.interfaces import (
    AbstractHasher,
    AbstractVerificationCodeRepository,
    AbstractRateLimitRepository,
    AbstractEmailSender,
)
from src.domain.value_objects import Email

from src.application.exceptions import CooldownEmailError, RequestExpiredError
from fastapi import BackgroundTasks


class ResendRegistrationCodeUseCase:
    def __init__(
        self,
        hasher: AbstractHasher,
        verification_code_repo: AbstractVerificationCodeRepository,
        rate_limit_repo: AbstractRateLimitRepository,
        email_sender: AbstractEmailSender,
        verification_code_cfg: VerificationCodeConfig,
        rate_limit_cgf: RateLimitConfig,
    ):
        self.hasher = hasher
        self.verification_code_repo = verification_code_repo
        self.rate_limit_repo = rate_limit_repo
        self.email_sender = email_sender
        self.ttl_seconds = verification_code_cfg.ttl_seconds
        self.max_attempts = verification_code_cfg.max_attempts
        self.resend_code_cooldown_seconds = rate_limit_cgf.resend_code_cooldown_seconds

    async def execute(self, email, background_tasks: BackgroundTasks) -> None:
        email_vo = Email.create(email)

        user_data = await self.verification_code_repo.get_pending(email=email)

        # Проверяем наличие pending registration в редис
        if user_data is None:
            raise RequestExpiredError(str("Запрос истек. Начните регистрацию заново"))

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
            hashed_password=user_data.hashed_password,
            otp_hash=otp_hash,
            ttl_seconds=self.ttl_seconds,
            max_attempts=self.max_attempts,
        )

        return None
