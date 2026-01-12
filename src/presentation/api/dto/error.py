from pydantic import BaseModel


class EmailAlreadyExistsResponse(BaseModel):
    error: str = "EmailAlreadyExists"
    message: str
    email: str


class CooldownEmailResponse(BaseModel):
    error: str = "CooldownEmail"
    message: str


class RateLimitExceededResponse(BaseModel):
    error: str = "RateLimitExceeded"
    message: str
