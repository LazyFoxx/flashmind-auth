from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import EmailUser, AbstractEmailUserRepository
from src.infrastructure.db.models import EmailUserModel


class SQlAlchemyEmailUserRepository(AbstractEmailUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Optional[EmailUser]:
        stmt = select(EmailUserModel).where(EmailUserModel.user_id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return user_model.to_domain() if user_model else None

    async def get_by_email(self, email: str) -> Optional[EmailUser]:
        stmt = select(EmailUserModel).where(EmailUserModel.email == email)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return user_model.to_domain() if user_model else None

    async def add(self, user: EmailUser) -> None:
        user_model = EmailUserModel.from_domain(user)
        self.session.add(user_model)

    async def update(self, user: EmailUser) -> None:
        stmt = (
            update(EmailUserModel)
            .where(EmailUserModel.user_id == user.user_id)
            .values(
                email=user.email,
                hashed_password=user.hashed_password,
                email_verified=user.email_verified,
            )
        )
        await self.session.execute(stmt)

    async def set_password(self, user_id: UUID, hashed_password: str) -> None:
        stmt = (
            update(EmailUserModel)
            .where(EmailUserModel.user_id == user_id)
            .values(hashed_password=hashed_password)
        )
        await self.session.execute(stmt)
