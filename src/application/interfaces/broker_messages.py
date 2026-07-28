from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel



class UserPayload(BaseModel):
    user_id: str
    name: Optional[str]
    avatar_url: Optional[str]


class AbstractEventPublisher(ABC):

    @abstractmethod
    async def publish(self, user: UserPayload) -> None:
        """
        Опубликовать событие регистрации.
        
        Args:
            user: UserPayload
        """
        ...