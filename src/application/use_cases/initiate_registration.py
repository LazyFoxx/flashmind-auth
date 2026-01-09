import secrets
from src.application.dtos import AuthCredentialsDTO
from src.application.exceptions import EmailAlreadyExistsError, RateLimitExceededError
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
        register_email_limit,
        register_email_window_seconds,
        ttl_seconds,
        max_attempts,
    ):
        self.hasher = hasher
        self.rate_limit_repo = rate_limit_repo
        self.verification_code_repo = verification_code_repo
        self.email_sender = email_sender
        self.uow = uow
        self.register_email_limit = register_email_limit
        self.register_email_window_seconds = register_email_window_seconds
        self.ttl_seconds = ttl_seconds
        self.max_attempts = max_attempts

    async def execute(self, input_dto: AuthCredentialsDTO) -> None:
        email_vo = str(Email(input_dto.email))
        password_hash = str(HashedPassword(self.hasher.hash(input_dto.password)))

        # Проверка уникальности email
        async with self.uow:
            if await self.uow.users.get_by_email(email_vo):
                raise EmailAlreadyExistsError(email_vo)

        # Rate limiting
        is_allowed, _, remaining = await self.rate_limit_repo.increment_and_check(
            email=email_vo,
            prefix="register",
            limit_attempts=self.register_email_limit,
            window_seconds=self.register_email_window_seconds,
        )
        if not is_allowed:
            raise RateLimitExceededError(remaining)

        # Генерируем код верификации
        otp = str(secrets.randbelow(899000) + 100000)
        # Отправляем код верификации на email пользователя
        await self.email_sender.send_register_verification_code(email_vo, otp)
        # Хешируем код для безопасности
        otp_hash = self.hasher.hash(otp)

        # Сохраняет временные данные о регистрации  в Redis (email, password_hash, otp_hash)
        await self.verification_code_repo.create_pending(
            email=email_vo,
            hashed_password=password_hash,
            otp_hash=otp_hash,
            ttl_seconds=self.ttl_seconds,
            max_attempts=self.max_attempts,
        )

        return None
