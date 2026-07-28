from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID


from src.domain.entities import User


class AbstractUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Получить пользователя по его уникальному идентификатору.

        Args:
            user_id: UUID пользователя

        Returns:
            Объект User, если найден, иначе None
        """
        ...

    @abstractmethod
    async def add(self, user: User) -> None:
        """Добавить нового пользователя в хранилище.

        Args:
            user: User

        Raises:
            IntegrityError: если email уже занят
        """
        ...
