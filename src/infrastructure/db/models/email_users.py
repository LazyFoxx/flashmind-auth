from __future__ import annotations
from uuid import uuid4, UUID

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import ForeignKey, String, Boolean, DateTime, func, Uuid
from sqlalchemy.ext.asyncio import AsyncAttrs

from src.domain.entities import EmailUser
from src.domain.value_objects import Email, HashedPassword
from src.infrastructure.db.base import Base

class EmailUserModel(Base):
    __tablename__ = "email_users"

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    def to_domain(self) -> EmailUser:
        return EmailUser(
            user_id=self.user_id,
            email=Email(self.email),
            hashed_password=HashedPassword(self.hashed_password),
            email_verified=self.email_verified,
        )

    @classmethod
    def from_domain(cls, user: EmailUser) -> "EmailUserModel":
        return cls(
            user_id=user.user_id,
            email=user.email.value,
            hashed_password=user.hashed_password.value,
            email_verified=user.email_verified,
        )
