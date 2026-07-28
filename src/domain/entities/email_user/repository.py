from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID


from src.domain.entities import EmailUser


class AbstractEmailUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[EmailUser]:
        """Получить пользователя по его уникальному идентификатору.

        Args:
            user_id: UUID пользователя

        Returns:
            Объект User, если найден, иначе None
        """
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[EmailUser]:
        """Получить пользователя по email (уникальному).

        Args:
            email: Email пользователя (будет нормализован)

        Returns:
            User или None
        """
        ...

    @abstractmethod
    async def add(self, user: EmailUser) -> None:
        """Добавить нового пользователя в хранилище.

        Args:
            user: EmailUser

        Raises:
            IntegrityError: если email уже занят
        """
        ...

    @abstractmethod
    async def set_password(self, user_id: UUID, hashed_password: str) -> None:
        """Изменить пароль пользователя на новый."""
        ...
