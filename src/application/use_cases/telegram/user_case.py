# src/application/use_cases/telegram/user_case.py
import asyncio
from uuid import uuid4
from src.application.interfaces import (
    AbstractHasher,
    AbstractUnitOfWork,
    AbstractAuthenticationService,
    AbstractRateLimitRepository,
    AbstractEventPublisher,
    UserPayload,
)
from src.domain.entities import TelegramUser, User
from src.application.dtos import AuthResponseDTO
from .dto import TelegramLoginInput

from src.application.exceptions import (
    InvalidCredentialsError,
)


class TelegramLoginUseCase:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        authentication: AbstractAuthenticationService,
        publisher: AbstractEventPublisher,
    ):
        self.uow = uow
        self.authentication = authentication
        self.publisher = publisher

    async def execute(self, input_dto: TelegramLoginInput) -> AuthResponseDTO:
        """
        Выполняет логин/регистрацию пользователя через Telegram.
        
        Args:
            input_dto: Данные из Telegram OIDC токена
            
        Returns:
            AuthResponseDTO с токенами доступа
        """
        
         # Проверяем, существует ли пользователь в БД
        async with self.uow:
            telegram_user = await self.uow.telegram_users.get_by_telegram_id(
                telegram_id=input_dto.tg_user_id
            )
            
        if telegram_user is None:
        # Если пользователь не найден проводим регистрацию
            user = User(id=uuid4(),)
            telegram_user = TelegramUser(user_id=user.id,
                                      telegram_id=input_dto.tg_user_id,
                                      name=input_dto.name,
                                      username=input_dto.username,
                                      phone_number=input_dto.phone,
                                      avatar_url=input_dto.avatar_url)
        
            async with self.uow:
                await self.uow.users.add(user)
                await self.uow.telegram_users.add(telegram_user)

            
            # оповещаем сервисы о регистрации пользователя
            await self.publisher.publish(UserPayload(user_id=str(user.id),
                                                     name=telegram_user.name,
                                                     avatar_url=telegram_user.avatar_url,))
            


        # генерируем токены доступа и сохраняем refresh в редис
        (
            access_token,
            refresh_token,
        ) = await self.authentication.authenticate_and_generate_tokens(user_id=telegram_user.user_id)

        return AuthResponseDTO(access_token, refresh_token)
