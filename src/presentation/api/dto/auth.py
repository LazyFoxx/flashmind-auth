from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class EmailVerificationSentResponse(BaseModel):
    message: str = "Код подтверждения отправлен на email"
    expires_in: int  # в секундах

    # Можно добавить пример для документации
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Код подтверждения отправлен на email",
                "expires_in": 1800,
            }
        }
    }


class EmailVerificationRequest(BaseModel):
    email: EmailStr
    code: str


class ResendEmailVerificationRequest(BaseModel):
    email: EmailStr


class RegistrationCompletedResponse(BaseModel):
    message: str = "Регистрация прошла успешно!"
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # время жизни access-токена в секундах

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Регистрация прошла успешно!",
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
            }
        }
    }
