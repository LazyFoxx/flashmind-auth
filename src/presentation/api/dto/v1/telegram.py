from pydantic import BaseModel


class TelegramAuthRequest(BaseModel):
    id_token: str