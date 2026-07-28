from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

@dataclass(slots=True, frozen=True)
class TelegramUser:
    """
    Доменная сущность email пользователя.
    """

    user_id: UUID
    telegram_id: str  # ID в Telegram
    name: Optional[str] = None
    username: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
