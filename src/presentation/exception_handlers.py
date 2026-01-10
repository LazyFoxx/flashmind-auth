from src.application.exceptions import (
    EmailAlreadyExistsError,
    CooldownEmailError,
    RateLimitExceededError,
)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


async def email_exists_handler(request: Request, exc: EmailAlreadyExistsError):
    return JSONResponse(
        status_code=409,
        content={
            "error": "EmailAlreadyExists",
            "message": str(exc),
            "email": exc.email,
        },
    )


async def cooldown_email_handler(request: Request, exc: CooldownEmailError):
    return JSONResponse(
        status_code=429,
        content={
            "error": "CooldownEmail",
            "message": str(exc),
        },
    )


async def rate_limit_exceed_handler(request: Request, exc: RateLimitExceededError):
    return JSONResponse(
        status_code=429,
        content={
            "error": "RateLimitExceeded",
            "message": str(exc),
        },
    )


def setup_exception_handlers(app: FastAPI):
    """Единая регистрация всех обработчиков ошибок."""
    app.add_exception_handler(EmailAlreadyExistsError, email_exists_handler)  # type: ignore[arg-type]
    app.add_exception_handler(CooldownEmailError, cooldown_email_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RateLimitExceededError, rate_limit_exceed_handler)  # type: ignore[arg-type]
