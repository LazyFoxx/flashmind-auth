from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.application.interfaces import AbstractUserRepository
from src.infrastructure.persistence.models import UserModel


class SQlAlchemyUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return user_model.to_domain() if user_model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return user_model.to_domain() if user_model else None

    async def add(self, user: User) -> None:
        user_model = UserModel.from_domain(user)
        self.session.add(user_model)

    async def update(self, user: User) -> None:
        # Обычно делаем через merge или update-выражение
        stmt = (
            update(UserModel)
            .where(UserModel.id == user.id)
            .values(
                email=user.email,
                hashed_password=user.hashed_password,
                is_active=user.is_active,
                email_verified=user.email_verified,
            )
        )
        await self.session.execute(stmt)

    async def set_password(self, user_id: UUID, hashed_password: str) -> None:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(hashed_password=hashed_password)
        )
        await self.session.execute(stmt)
