from abc import ABC, abstractmethod

from src.domain.entities import AbstractEmailUserRepository, AbstractUserRepository, AbstractTelegramUserRepository

class AbstractUnitOfWork(ABC):
    """Минималистичный современный UoW для async"""

    email_users: AbstractEmailUserRepository
    users: AbstractUserRepository
    telegram_users: AbstractTelegramUserRepository

    async def __aenter__(self) -> "AbstractUnitOfWork":
        return self

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
