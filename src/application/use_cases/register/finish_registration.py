import asyncio
from uuid import uuid4
from src.core.settings import VerificationCodeConfig
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
        verification_code_cfg: VerificationCodeConfig,
    ):
        self.hasher = hasher
        self.verification_code_repo = verification_code_repo
        self.authentication = authentication
        self.uow = uow
        self.max_attempts = verification_code_cfg.max_attempts

    async def execute(self, input_dto: VerifyCodeDTO) -> AuthResponseDTO:
        email_vo = Email.create(input_dto.email)
        user_otp = input_dto.code

        # получаем хеш отпрвленного кода для сравнения
        user_data = await self.verification_code_repo.get_pending(email=email_vo.value)

        # Проверяем наличие pending registration в редис
        if user_data is None:
            raise RequestExpiredError("Запрос истек. Начните регистрацию заново")

        # уменьшаем количество попыток
        (
            is_allowed,
            _,
            remaining_attempts,
        ) = await self.verification_code_repo.increment_and_check(
            email_vo.value, limit_attempts=self.max_attempts
        )

        if not is_allowed:
            # если попытки исчерпаны возвращаем ошибку (запрет на попытки)
            raise LimitCodeAttemptsError(
                "Все попытки исчерпаны, начните регистрацию заново или запросите новый код"
            )

        # Проверяем соответствие кода верификации
        check_code = await asyncio.to_thread(
            self.hasher.verify, user_otp, user_data.otp_hash
        )

        if not check_code:
            # возвращаем ошибку что код не верный и указываем оставшиеся попытки
            raise CodeAttemptError(remaining_attempts=remaining_attempts)

        # Если коды совпадают то добавляем пользователя в бд и возвращаем токены
        user = User(
            id=uuid4(),
            email=email_vo,
            hashed_password=HashedPassword(user_data.hashed_password),
            is_active=True,
            email_verified=True,
        )
        async with self.uow:
            await self.uow.users.add(user)

            # генерируем токены доступа и сохраняем refresh в редис
            (
                access_token,
                refresh_token,
            ) = await self.authentication.authenticate_and_generate_tokens(user.id)

            # очищаем редис
            await self.verification_code_repo.delete_pending(email=email_vo.value)

            await self.uow.commit()

        return AuthResponseDTO(access_token, refresh_token)
