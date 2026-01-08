# infrastructure/persistence/models/user_model.py
from __future__ import annotations

from datetime import datetime
from uuid import uuid4, UUID

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import MetaData, String, Boolean, DateTime, func, Uuid
from sqlalchemy.ext.asyncio import AsyncAttrs  # Важно для async

from domain.entities.user import User
from domain.value_objects.email import Email  # предполагаю, что Email — value object
from src.config.settings import settings


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс для всех моделей (с поддержкой async)."""

    metadata = MetaData(
        naming_convention=settings.db.naming_convention,
    )


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,  # uuid4(), а не uuid.uuid4 — чуть быстрее и idiomatic
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
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

    def to_domain(self) -> User:
        """Конвертирует загруженную ORM-модель в чистую доменную сущность."""
        return User(
            id=self.id,
            email=Email(self.email),  # value object
            hashed_password=self.hashed_password,
            created_at=self.created_at,
            updated_at=self.updated_at,
            is_active=self.is_active,
            is_email_verified=self.email_verified,
        )

    @classmethod
    def from_domain(cls, user: User) -> "UserModel":
        """Альтернативный конструктор: создаёт модель из доменной сущности."""
        return cls(
            id=user.id,
            email=str(user.email),
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            is_email_verified=user.is_email_verified,
        )
