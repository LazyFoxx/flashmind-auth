from abc import ABC, abstractmethod
from uuid import UUID
from typing import Tuple

from typing import Optional


class AbstractAuthenticationService(ABC):
    """
    Доменный сервис, отвечающий за успешную аутентификацию пользователя,
    выдачу токенов (access + refresh) и ротацию refresh token.
    Вызывается как при логине, так и при регистрации так и при ротации рефреш.
    """

    @abstractmethod
    async def authenticate_and_generate_tokens(
        self, user_id: UUID, refresh_token: Optional[str] = NotImplemented
    ) -> Tuple[str, str]:
        """
        Генерирует access и refresh токены, сохраняет refresh (jti) в хранилище (удаляет предыдущий если он передан для ротации)
        и возвращает пару токенов.

        Returns:
            (access_token: str, refresh_token: str)
        """
        ...
