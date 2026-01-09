from abc import ABC, abstractmethod

from src.application.interfaces import AbstractUserRepository


class AbstractUnitOfWork(ABC):
    """Минималистичный современный UoW для async"""

    users: AbstractUserRepository

    async def __aenter__(self) -> "AbstractUnitOfWork":
        return self

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
