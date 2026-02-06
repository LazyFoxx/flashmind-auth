from pydantic import BaseModel, EmailStr, Field, validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        ...,
        max_length=128,
        description="Пароль должен быть не менее 8 символов и содержать хотя бы одну строчную, заглавную буквы и хотя бы одну цифру",
    )

    @validator("password")
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Пароль должен быть не менее 8 символов")

        if not any(c.isupper() for c in value):
            raise ValueError(
                "Пароль должен содержать хотя бы одну заглавную букву (A-Z)"
            )

        if not any(c.islower() for c in value):
            raise ValueError(
                "Пароль должен содержать хотя бы одну строчную букву (a-z)"
            )

        if not any(c.isdigit() for c in value):
            raise ValueError("Пароль должен содержать хотя бы одну цифру (0-9)")

        if len(value) < 8:
            raise ValueError("Пароль должен состоять минимум из 8 символов")

        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        ...,
        max_length=128,
        description="Пароль должен быть не менее 8 символов и содержать хотя бы одну строчную, заглавную буквы и хотя бы одну цифру",
    )


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
    password: str = Field(
        ...,
        max_length=128,
        description="Пароль должен быть не менее 8 символов и содержать хотя бы одну строчную, заглавную буквы и хотя бы одну цифру",
    )

    @validator("password")
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Пароль должен быть не менее 8 символов")

        if not any(c.isupper() for c in value):
            raise ValueError(
                "Пароль должен содержать хотя бы одну заглавную букву (A-Z)"
            )

        if not any(c.islower() for c in value):
            raise ValueError(
                "Пароль должен содержать хотя бы одну строчную букву (a-z)"
            )

        if not any(c.isdigit() for c in value):
            raise ValueError("Пароль должен содержать хотя бы одну цифру (0-9)")

        if len(value) < 8:
            raise ValueError("Пароль должен состоять минимум из 8 символов")

        return value
