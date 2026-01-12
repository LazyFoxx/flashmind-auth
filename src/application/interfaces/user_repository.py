from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID


from src.domain.entities.user import User


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
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email (уникальному).

        Args:
            email: Email пользователя (будет нормализован)

        Returns:
            User или None, если пользователь с таким email не существует
        """
        ...

    @abstractmethod
    async def add(self, user: User) -> None:
        """Добавить нового пользователя в хранилище.

        Пользователь должен быть новым (без ID или с временным).
        После добавления у пользователя должен появиться валидный ID из БД.

        Args:
            user: Объект User с валидными данными (email, hashed_password и т.д.)

        Raises:
            IntegrityError: если email уже занят
        """
        ...

    @abstractmethod
    async def set_password(self, user_id: UUID, hashed_password: str) -> None:
        """Изменить пароль пользователя на новый."""
        ...
