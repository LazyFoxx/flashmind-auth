from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


from src.domain.value_objects.email import Email
from src.domain.value_objects.hashed_password import HashedPassword


@dataclass(slots=True, frozen=True)
class EmailUser:
    """
    Доменная сущность email пользователя.
    """

    user_id: UUID
    email: Email
    hashed_password: HashedPassword
    email_verified: bool = False
