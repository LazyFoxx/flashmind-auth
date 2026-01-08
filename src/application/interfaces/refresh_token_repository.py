from abc import ABC, abstractmethod
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
    ) -> None:
        """Сохранить новый действующий refresh-токен для пользователя.

        Перезаписывает предыдущий токен того же пользователя (ротация).

        Args:
            user_id: ID пользователя
            token_jti: Уникальный идентификатор токена (jti claim)
        """
        ...

    @abstractmethod
    async def get_user_id_by_jti(self, token_jti: str) -> UUID | None:
        """Атомарная операция:
        1. Возвращает данные токена (user_id, expires_at), если он существует
        2. Немедленно удаляет его из хранилища (поддержка rotation)

        Возвращает None, если токен уже был использован или не существует.
        """
        ...

    @abstractmethod
    async def revoke_by_user_id(self, user_id: UUID) -> None:
        """
        Отзыв текущей сессии пользователя (logout или смена пароля).
        """
        ...
