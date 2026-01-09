import secrets
from src.application.interfaces import (
    AbstractHasher,
    AbstractUserRepository,
    AbstractVerificationCodeRepository,
    AbstractRateLimitRepository,
    AbstractEmailSender,
)
from src.domain.value_objects import Email

from src.application.exceptions import CooldownEmailError, RequestExpiredError


class ResendRegistrationCodeUseCase:
    def __init__(
        self,
        hasher: AbstractHasher,
        verification_code_repo: AbstractVerificationCodeRepository,
        user_repo: AbstractUserRepository,
        rate_limit_repo: AbstractRateLimitRepository,
        email_sender: AbstractEmailSender,
        ttl_seconds,
        max_attempts,
        resend_code_cooldown_seconds,
    ):
        self.hasher = hasher
        self.verification_code_repo = verification_code_repo
        self.user_repo = user_repo
        self.rate_limit_repo = rate_limit_repo
        self.email_sender = email_sender
        self.ttl_seconds = ttl_seconds
        self.max_attempts = max_attempts
        self.resend_code_cooldown_seconds = resend_code_cooldown_seconds

    async def execute(self, email) -> None:
        email_vo = str(Email(email))

        user_data = await self.verification_code_repo.get_pending(email=email)

        # Проверяем наличие pending registration в редис
        if user_data is None:
            raise RequestExpiredError(str("Запрос истек. Начните регистрацию заново"))

        # проверяем rate limit на отправвку email
        check_cooldown = self.rate_limit_repo.check_and_set_cooldown(
            email=email_vo, cooldown=self.resend_code_cooldown_seconds
        )
        if not check_cooldown:
            raise CooldownEmailError(
                "Пожалуйста подождите пока будет допустимо отправить новый код"
            )

        # Генерируем код верификации
        otp = str(secrets.randbelow(899000) + 100000)
        # Отправляем код верификации на email пользователя
        await self.email_sender.send_register_verification_code(email_vo, otp)
        # Хешируем код для безопасности
        otp_hash = self.hasher.hash(otp)

        # Сохраняет временные данные о регистрации  в Redis (email, password_hash, otp_hash)
        await self.verification_code_repo.create_pending(
            email=email_vo,
            hashed_password=user_data.hashed_password,
            otp_hash=otp_hash,
            ttl_seconds=self.ttl_seconds,
            max_attempts=self.max_attempts,
        )

        return None
