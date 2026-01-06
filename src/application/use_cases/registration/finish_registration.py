from uuid import uuid4
from application.dtos import VerifyCodeDTO, AuthResponseDTO
from application.interfaces import (
    AbstractHasher,
    AbstractUserRepository,
    AbstractVerificationCodeRepository,
    AbstractAuthenticationService,
)
from domain.entities.user import User
from domain.value_objects import Email

from src.config.settings import settings

from application.exceptions import (
    LimitCodeAttemptsError,
    CodeAttemptError,
    RequestExpiredError,
)


class FinishRegistrationUseCase:
    def __init__(
        self,
        hasher: AbstractHasher,
        verification_code_repo: AbstractVerificationCodeRepository,
        user_repo: AbstractUserRepository,
        authentication: AbstractAuthenticationService,
    ):
        self.hasher = hasher
        self.verification_code_repo = verification_code_repo
        self.user_repo = user_repo
        self.rate_limit_cfg = settings.rl
        self.email_code_cfg = settings.email_code
        self.authentication = authentication

    async def execute(self, input_dto: VerifyCodeDTO) -> AuthResponseDTO:
        email = Email(input_dto.email)
        user_otp = input_dto.code

        # получаем хеш отпрвленного кода для сравнения
        user_data = self.verification_code_repo.get_pending(email=email)

        # Проверяем наличие pending registration в редис
        if user_data is None:
            raise RequestExpiredError(str("Запрос истек. Начните регистрацию заново"))

        # Проверяем соответствие кода верификации
        check_code = self.hasher.verify(user_otp, user_data.otp_hash)

        if not check_code:
            # если коды не совпадают - уменьшаем количество попыток
            is_allowed, current_attempts, remaining_attempts = (
                self.verification_code_repo.increment_and_check(
                    email, limit_attempts=self.email_code_cfg.max_attempts
                )
            )

            if not is_allowed:
                # если попытки исчерпаны возвращаем ошибку (запрет на попытки)
                raise LimitCodeAttemptsError(
                    "Все попытки исчерпаны, начните регистрацию заново или запросите новый код"
                )

            # возвращаем ошибку что код не верный и указываем оставшиеся попытки
            raise CodeAttemptError(
                f"Неверный код, осталось {remaining_attempts} попыток"
            )

        # Если коды совпадают то добавляем пользователя в бд и возвращаем токены
        user = User(
            id=uuid4(),
            email=email,
            hashed_password=user_data.hashed_password,
        )

        self.user_repo.add(user)

        # генерируем токены доступа и сохраняем refresh в редис
        access_token, refresh_token = (
            self.authentication.authenticate_and_generate_tokens()
        )

        return AuthResponseDTO(access_token, refresh_token)
