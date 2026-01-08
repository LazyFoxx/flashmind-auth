from abc import ABC, abstractmethod


class AbstractUnitOfWork(ABC):
    """Минималистичный современный UoW для async"""

    async def __aenter__(self) -> "AbstractUnitOfWork":
        return self

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
