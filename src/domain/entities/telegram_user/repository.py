from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID


from src.domain.entities import TelegramUser


class AbstractTelegramUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[TelegramUser]:
        """Получить связь Telegram пользователя по UUID пользователя."""
        ...

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: str) -> Optional[TelegramUser]:
        """Получить связь Telegram пользователя по ID Telegram."""
        ...

    @abstractmethod
    async def add(self, user: TelegramUser) -> None:
        """Создать новую связь Telegram пользователя."""
        ...
