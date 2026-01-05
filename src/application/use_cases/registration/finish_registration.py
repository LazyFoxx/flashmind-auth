from application.dtos import VerifyCodeDTO, AuthResponseDTO
from application.interfaces import (
    AbstractEmailSender,
    AbstractHasher,
    AbstractRateLimitRepository,
    AbstractUserRepository,
    AbstractVerificationCodeRepository,
)
from domain.value_objects import Email

from src.config.settings import settings


class FinishRegistrationUseCase:
    def __init__(
        self,
        password_hasher: AbstractHasher,
        rate_limit_repo: AbstractRateLimitRepository,
        verification_code_repo: AbstractVerificationCodeRepository,
        email_sender: AbstractEmailSender,
        user_repo: AbstractUserRepository,
    ):
        self.password_hasher = password_hasher
        self.rate_limit_repo = rate_limit_repo
        self.verification_code_repo = verification_code_repo
        self.email_sender = email_sender
        self.user_repo = user_repo
        self.rate_limit_cfg = settings.rl
        self.email_code_cfg = settings.email_code

    async def execute(self, input_dto: VerifyCodeDTO) -> AuthResponseDTO:
        email = Email(input_dto.email)
        # user_code = input_dto.code

        # получаем хеш отпрвленного кода для сравнения
        _, _, otp_hash = self.verification_code_repo.get_pending(email=email)

        # Проверяем соответствие кода верификации
        # result =
