from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class LoginRequest(RegisterRequest):
    email: EmailStr
    password: str = Field(..., min_length=8)


class MessageResponse(BaseModel):
    message: str = Field(..., description="Информационное сообщение для клиента")

    model_config = {
        "json_schema_extra": {
            "example": {"message": "Код верификации успешно отправлен!"}
        }
    }


class EmailVerificationRequest(BaseModel):
    email: EmailStr
    code: str


class ResendEmailVerificationRequest(BaseModel):
    email: EmailStr


class LoginResponse(BaseModel):
    message: str = "Успешная авторизация!"
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # время жизни access-токена в секундах
    refresh_token: str | None = Field(
        default=None,
        description="Возвращается только для non-cookie клиентов (mobile / native)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJ...",
                    "token_type": "bearer",
                    "expires_in": 1800,
                    "refresh_token": None,
                },
                {
                    "access_token": "eyJ...",
                    "token_type": "bearer",
                    "expires_in": 1800,
                    "refresh_token": "def50200...",
                },
            ]
        }
    }


class TokenAccessResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # время жизни access-токена в секундах
    refresh_token: str | None = Field(
        default=None,
        description="Возвращается только для non-cookie клиентов (mobile / native)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJ...",
                    "token_type": "bearer",
                    "expires_in": 1800,
                    "refresh_token": None,
                },
                {
                    "access_token": "eyJ...",
                    "token_type": "bearer",
                    "expires_in": 1800,
                    "refresh_token": "def50200...",
                },
            ]
        }
    }


class NewPasswordRequest(BaseModel):
    password: str = Field(..., min_length=8)
