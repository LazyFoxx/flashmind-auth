from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, UTC
from uuid import UUID, uuid4

from pydantic import (
    EmailStr,
)

from domain.value_objects.email import Email
from domain.value_objects.hashed_password import HashedPassword


@dataclass(slots=True, frozen=True)
class User:
    """
    Доменная сущность пользователя.
    """

    id: UUID
    email: Email
    hashed_password: HashedPassword

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    is_active: bool = True
    is_email_verified: bool = False

    @classmethod
    def create_new(
        cls,
        email: EmailStr,
        hashed_password: str,
        now: datetime | None = None,
    ) -> User:
        """
        Создаёт нового пользователя.
        Используется в use case регистрации.
        """
        now = now or datetime.utcnow()
        normalized_email = email.strip().lower()

        return cls(
            id=uuid4(),
            email=normalized_email,
            hashed_password=hashed_password,
            is_active=True,
            is_email_verified=True,
            created_at=now,
            updated_at=now,
        )
