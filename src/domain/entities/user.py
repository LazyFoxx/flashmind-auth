from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


from src.domain.value_objects.email import Email
from src.domain.value_objects.hashed_password import HashedPassword


@dataclass(slots=True, frozen=True)
class User:
    """
    Доменная сущность пользователя.
    """

    id: UUID
    email: Email
    hashed_password: HashedPassword

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    is_active: bool = True
    email_verified: bool = False
