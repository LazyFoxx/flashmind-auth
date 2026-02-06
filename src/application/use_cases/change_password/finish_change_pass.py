import asyncio
import structlog
from src.application.dtos.auth_response_dto import AuthResponseDTO
from src.domain.entities.user import User
from src.domain.value_objects.hashed_password import HashedPassword
from src.application.interfaces import (
    AbstractAuthenticationService,
    AbstractVerificationCodeRepository,
    AbstractUnitOfWork,
    AbstractHasher,
)


class FinishChangePasswordUseCase:
    def __init__(
        self,
        hasher: AbstractHasher,
        verification_code_repo: AbstractVerificationCodeRepository,
        authentication: AbstractAuthenticationService,
        uow: AbstractUnitOfWork,
    ):
        self.hasher = hasher
        self.verification_code_repo = verification_code_repo
        self.authentication = authentication
        self.uow = uow
        self.logger = structlog.get_logger(__name__)

    async def execute(self, user: User, new_password: str) -> AuthResponseDTO:
        # хешируем пароль
        password_hash = HashedPassword(
            await asyncio.to_thread(self.hasher.hash, new_password)
        )

        # Обновляем пароль пользователя
        async with self.uow:
            await self.uow.users.set_password(user.id, password_hash.value)
            await self.uow.commit()
        self.logger.info("Пароль изменен в БД", user_id=user.id)

        # генерируем токены доступа и сохраняем refresh в редис
        (
            access_token,
            refresh_token,
        ) = await self.authentication.authenticate_and_generate_tokens(user.id)
        self.logger.info("Сгенерированны токены", user_id=user.id)

        return AuthResponseDTO(access_token, refresh_token)
