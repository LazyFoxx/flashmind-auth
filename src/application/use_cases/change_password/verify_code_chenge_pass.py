import asyncio

from src.application.dtos import VerifyCodeDTO
from src.core.settings import VerificationCodeConfig
from src.application.exceptions import (
    LimitCodeAttemptsError,
    CodeAttemptError,
    RequestExpiredError,
    UserNotFoundError,
)

from src.application.interfaces import (
    AbstractAuthenticationService,
    AbstractVerificationCodeRepository,
    AbstractUnitOfWork,
    AbstractHasher,
    AbstractJWTService,
)
from src.domain.value_objects import Email


class VerifyCodeChangePasswordUseCase:
    def __init__(
        self,
        hasher: AbstractHasher,
        verification_code_repo: AbstractVerificationCodeRepository,
        authentication: AbstractAuthenticationService,
        uow: AbstractUnitOfWork,
        verification_code_cfg: VerificationCodeConfig,
        jwt: AbstractJWTService,
    ):
        self.hasher = hasher
        self.verification_code_repo = verification_code_repo
        self.authentication = authentication
        self.uow = uow
        self.max_attempts = verification_code_cfg.max_attempts
        self.jwt = jwt

    async def execute(self, input_dto: VerifyCodeDTO) -> str:
        email_vo = Email.create(input_dto.email)
        user_otp = input_dto.code

        # получаем хеш отпрвленного кода для сравнения
        user_data = await self.verification_code_repo.get_pending(email=email_vo.value)

        # Проверяем наличие pending в редис
        if user_data is None:
            raise RequestExpiredError("Запрос истек. Начните сброс пароля заново")

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
                "Все попытки исчерпаны, начните сброс пароля заново или запросите новый код"
            )

        # Проверяем соответствие кода верификации
        check_code = await asyncio.to_thread(
            self.hasher.verify, user_otp, user_data.otp_hash
        )

        if not check_code:
            # возвращаем ошибку что код не верный и указываем оставшиеся попытки
            raise CodeAttemptError(remaining_attempts=remaining_attempts)

        # Если коды совпадают то выдаем временный токен доступа для сброса пароля
        # очищаем редис
        await self.verification_code_repo.delete_pending(email=email_vo.value)

        async with self.uow:
            user = await self.uow.users.get_by_email(email=email_vo.value)
            await self.uow.commit()

        if not user:
            raise UserNotFoundError(email=email_vo.value)

        access_token = self.jwt.create_access_token(user_id=user.id)

        return access_token
