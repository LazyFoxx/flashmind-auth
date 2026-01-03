# src/application/interfaces/authentication_service.py
from abc import ABC, abstractmethod
from uuid import UUID
from typing import Tuple


class AbstractAuthenticationService(ABC):
    """
    Доменный сервис, отвечающий за успешную аутентификацию пользователя
    и выдачу токенов (access + refresh).
    Вызывается после проверки пароля — как при логине, так и при регистрации.
    """

    @abstractmethod
    async def authenticate_and_generate_tokens(
        self,
        user_id: UUID,
    ) -> Tuple[str, str]:
        """
        Генерирует access и refresh токены, сохраняет refresh (jti) в хранилище
        и возвращает пару токенов.

        Returns:
            (access_token: str, refresh_token: str)
        """
        ...
