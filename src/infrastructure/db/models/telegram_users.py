from __future__ import annotations
from uuid import UUID
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Boolean, BigInteger
from sqlalchemy import Uuid

from src.infrastructure.db.base import Base
from src.domain.entities.telegram_user.telegram_user import TelegramUser


class TelegramUserModel(Base):
    __tablename__ = "telegram_users"

    # Связь с основной таблицей users
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    
    telegram_id: Mapped[str] = mapped_column(
        BigInteger,
        nullable=False,
        unique=True,
        index=True,
    )
    
    phone_number: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    
    name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    
    username: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    def to_domain(self) -> TelegramUser:
        return TelegramUser(
            user_id=self.user_id,
            telegram_id=self.telegram_id,
            phone_number=self.phone_number,
            name=self.name,
            username=self.username,
            avatar_url=self.avatar_url,
            is_active=self.is_active,
        )

    @classmethod
    def from_domain(cls, user: TelegramUser) -> "TelegramUserModel":
        return cls(
            user_id=user.user_id,
            telegram_id=user.telegram_id,
            phone_number=user.phone_number,
            username=user.username,
            name=user.name,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
        )