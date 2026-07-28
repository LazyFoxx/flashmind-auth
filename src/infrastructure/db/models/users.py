from __future__ import annotations
from uuid import uuid4, UUID
from src.infrastructure.db.base import Base

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, func, Uuid

from sqlalchemy import Column, Integer, DateTime
from datetime import datetime, timezone
from src.infrastructure.db.base import Base
from src.domain.entities import User

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_domain(self) -> User:
        return User(
            id=self.id,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, user: User) -> "UserModel":
        return cls(
            id=user.id,
        )
