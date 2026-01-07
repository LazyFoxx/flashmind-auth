from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


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

    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    is_active: bool = True
    is_email_verified: bool = False
