from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass(slots=True, frozen=True)
class User:
    """
    Доменная сущность пользователя.
    """

    id: UUID
    created_at: Optional[datetime] = None

