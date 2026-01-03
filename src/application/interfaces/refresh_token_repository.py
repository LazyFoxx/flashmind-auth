from abc import ABC, abstractmethod
from datetime import timedelta
from uuid import UUID


class AbstractRefreshTokenRepository(ABC):
    """Хранилище действующих refresh-токенов (whitelist подход).

    Один пользователь — один действующий refresh-токен (ротация).
    """

    @abstractmethod
    async def save(
        self,
        user_id: UUID,
        token_jti: str,
        expires_in: timedelta,
    ) -> None:
        """Сохранить новый действующий refresh-токен для пользователя.

        Перезаписывает предыдущий токен того же пользователя (ротация).

        Args:
            user_id: ID пользователя
            token_jti: Уникальный идентификатор токена (jti claim)
            expires_in: Время жизни токена
        """
        ...

    @abstractmethod
    async def get_user_id_by_jti(self, token_jti: str) -> UUID | None:
        """Получить ID пользователя по jti refresh-токена.

        Если токен не найден или истёк — возвращает None.
        """
        ...

    @abstractmethod
    async def revoke_by_user_id(self, user_id: UUID) -> None:
        """Отозвать текущий refresh-токен пользователя (например, при logout)."""
        ...
