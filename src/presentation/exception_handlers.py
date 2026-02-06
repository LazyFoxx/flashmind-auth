import structlog

from src.application.exceptions import (
    EmailAlreadyExistsError,
    CooldownEmailError,
    RateLimitExceededError,
    CodeAttemptError,
    LimitCodeAttemptsError,
    RequestExpiredError,
    InvalidCredentialsError,
    UserNotFoundError,
    InvalidTokenError,
)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = structlog.get_logger()


async def request_expired_handler(request: Request, exc: RequestExpiredError):
    logger.warning("Запрос истек", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=410,
        content={
            "error": "RequestExpired",
            "message": str(exc),
        },
    )


async def limit_code_attempts_handler(request: Request, exc: LimitCodeAttemptsError):
    logger.warning("Лимит попыток ввести код", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=429,
        content={
            "error": "LimitCodeAttempt",
            "message": str(exc),
        },
    )


async def code_attempts_handler(request: Request, exc: CodeAttemptError):
    logger.warning("Неверная попытка ввести код", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=400,
        content={
            "error": "CodeAttempt",
            "message": str(exc),
            "attempts": exc.remaining_attempts,
        },
    )


async def email_exists_handler(request: Request, exc: EmailAlreadyExistsError):
    logger.warning("Имейл уже существует", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=409,
        content={
            "error": "EmailAlreadyExists",
            "message": str(exc),
            "email": exc.email,
        },
    )


async def cooldown_email_handler(request: Request, exc: CooldownEmailError):
    logger.warning(
        "Попытка отправить имейл до истечения кулдауна",
        error=str(exc),
        path=request.url.path,
    )
    return JSONResponse(
        status_code=429,
        content={
            "error": "CooldownEmail",
            "message": str(exc),
            "remaining_seconds": exc.remaining_seconds,
        },
    )


async def rate_limit_exceed_handler(request: Request, exc: RateLimitExceededError):
    logger.warning("Лимит попыток регистрации", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=429,
        content={
            "error": "RateLimitExceeded",
            "message": str(exc),
        },
    )


async def invalide_credentional_handler(request: Request, exc: InvalidCredentialsError):
    logger.warning("Неверные данные", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=401,
        content={
            "error": "InvalideCredential",
            "message": str(exc),
        },
    )


async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    logger.warning("Неверный имейл", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=200,
        content={
            "message": "Успех!",
        },
    )


async def invalid_token(request: Request, exc: InvalidTokenError):
    logger.info("Неверный токен", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=401,
        headers={"WWW-Authenticate": "Bearer"},
        content={
            "message": f"Неверный токен: {exc}",
        },
    )


def setup_exception_handlers(app: FastAPI):
    """Единая регистрация всех обработчиков ошибок."""
    app.add_exception_handler(EmailAlreadyExistsError, email_exists_handler)  # type: ignore[arg-type]
    app.add_exception_handler(CooldownEmailError, cooldown_email_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RateLimitExceededError, rate_limit_exceed_handler)  # type: ignore[arg-type]
    app.add_exception_handler(CodeAttemptError, code_attempts_handler)  # type: ignore[arg-type]
    app.add_exception_handler(LimitCodeAttemptsError, limit_code_attempts_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestExpiredError, request_expired_handler)  # type: ignore[arg-type]
    app.add_exception_handler(InvalidCredentialsError, invalide_credentional_handler)  # type: ignore[arg-type]
    app.add_exception_handler(UserNotFoundError, user_not_found_handler)  # type: ignore[arg-type]
    app.add_exception_handler(InvalidTokenError, invalid_token)  # type: ignore[arg-type]
