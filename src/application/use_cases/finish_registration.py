from uuid import uuid4
from src.application.dtos import VerifyCodeDTO, AuthResponseDTO
from src.application.interfaces import (
    AbstractHasher,
    AbstractVerificationCodeRepository,
    AbstractAuthenticationService,
    AbstractUnitOfWork,
)
from src.domain.entities.user import User
from src.domain.value_objects import Email, HashedPassword

from src.application.exceptions import (
    LimitCodeAttemptsError,
    CodeAttemptError,
    RequestExpiredError,
)


class FinishRegistrationUseCase:
    def __init__(
        self,
        hasher: AbstractHasher,
        verification_code_repo: AbstractVerificationCodeRepository,
        authentication: AbstractAuthenticationService,
        uow: AbstractUnitOfWork,
        max_attempts,
    ):
        self.hasher = hasher
        self.verification_code_repo = verification_code_repo
        self.authentication = authentication
        self.uow = uow
        self.max_attempts = max_attempts

    async def execute(self, input_dto: VerifyCodeDTO) -> AuthResponseDTO:
        email = str(Email(input_dto.email))
        user_otp = input_dto.code

        # получаем хеш отпрвленного кода для сравнения
        user_data = await self.verification_code_repo.get_pending(email=email)

        # Проверяем наличие pending registration в редис
        if user_data is None:
            raise RequestExpiredError(str("Запрос истек. Начните регистрацию заново"))

        # Проверяем соответствие кода верификации
        check_code = self.hasher.verify(user_otp, user_data.otp_hash)

        if not check_code:
            # если коды не совпадают - уменьшаем количество попыток
            (
                is_allowed,
                current_attempts,
                remaining_attempts,
            ) = await self.verification_code_repo.increment_and_check(
                email, limit_attempts=self.max_attempts
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
            email=Email(email),
            hashed_password=HashedPassword(user_data.hashed_password),
        )
        async with self.uow:
            await self.uow.users.add(user)
            await self.uow.commit()

        # генерируем токены доступа и сохраняем refresh в редис
        (
            access_token,
            refresh_token,
        ) = await self.authentication.authenticate_and_generate_tokens(user.id)

        return AuthResponseDTO(access_token, refresh_token)
