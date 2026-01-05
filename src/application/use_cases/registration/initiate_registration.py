import secrets
from application.dtos import AuthCredentialsDTO
from application.exceptions import EmailAlreadyExistsError, RateLimitExceededError
from application.interfaces import (
    AbstractEmailSender,
    AbstractHasher,
    AbstractRateLimitRepository,
    AbstractUserRepository,
    AbstractVerificationCodeRepository,
)
from domain.value_objects import Email, HashedPassword

from src.config.settings import settings


class InitiateRegistrationUseCase:
    def __init__(
        self,
        hasher: AbstractHasher,
        rate_limit_repo: AbstractRateLimitRepository,
        verification_code_repo: AbstractVerificationCodeRepository,
        email_sender: AbstractEmailSender,
        user_repo: AbstractUserRepository,
    ):
        self.hasher = hasher
        self.rate_limit_repo = rate_limit_repo
        self.verification_code_repo = verification_code_repo
        self.email_sender = email_sender
        self.user_repo = user_repo
        self.rate_limit_cfg = settings.rl
        self.email_code_cfg = settings.email_code

    async def execute(self, input_dto: AuthCredentialsDTO) -> None:
        email_vo = Email(input_dto.email)
        password_hash = HashedPassword(self.hasher.hash(input_dto.password))

        # Проверка уникальности email
        if await self.user_repo.get_by_email(email_vo):
            raise EmailAlreadyExistsError(str(email_vo))

        # Rate limiting
        is_allowed, _, remaining = await self.rate_limit_repo.increment_and_check(
            email=email_vo,
            prefix="register",
            limit_attempts=self.rate_limit_cfg.register_email_limit,
            window_seconds=self.rate_limit_cfg.register_email_window_seconds,
        )
        if not is_allowed:
            raise RateLimitExceededError(remaining)

        # Генерируем код верификации
        otp = str(secrets.randbelow(899000) + 100000)
        # Отправляем код верификации на email пользователя
        self.email_sender.send_register_verification_code(email_vo, otp)
        # Хешируем код для безопасности
        otp_hash = self.hasher.hash(otp)

        # Сохраняет временные данные о регистрации  в Redis (email, password_hash, otp_hash)
        self.verification_code_repo.create_pending(
            email=email_vo,
            hashed_password=password_hash,
            otp_hash=otp_hash,
            ttl_seconds=self.email_code_cfg.ttl_seconds,
            max_attempts=self.email_code_cfg.max_attempts,
        )

        return None
