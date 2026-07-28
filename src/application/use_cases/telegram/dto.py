from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class TelegramLoginInput:
    tg_user_id: str
    name: str
    username: str
    avatar_url: Optional[str]
    phone = Optional[str]
