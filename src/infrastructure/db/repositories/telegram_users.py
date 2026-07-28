from typing import Optional
from uuid import UUID
import structlog

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.telegram_user.telegram_user import TelegramUser
from src.domain.entities.telegram_user.repository import AbstractTelegramUserRepository
from src.infrastructure.db.models import TelegramUserModel


logger = structlog.get_logger(__name__)


class SQLAlchemyTelegramUserRepository(AbstractTelegramUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Optional[TelegramUser]:
        stmt = select(TelegramUserModel).where(TelegramUserModel.user_id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return user_model.to_domain() if user_model else None

    async def get_by_telegram_id(self, telegram_id: str) -> Optional[TelegramUser]:
        stmt = select(TelegramUserModel).where(TelegramUserModel.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return user_model.to_domain() if user_model else None

    async def add(self, user: TelegramUser) -> None:
        user_model = TelegramUserModel.from_domain(user)
        self.session.add(user_model)
