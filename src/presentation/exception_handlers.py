from src.application.exceptions import EmailAlreadyExistsError

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


async def email_exists_handler(request: Request, exc: EmailAlreadyExistsError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "EmailAlreadyExists",
            "message": str(exc),
            "email": exc.email,
        },
    )


def setup_exception_handlers(app: FastAPI):
    """Единая регистрация всех обработчиков ошибок."""
    app.add_exception_handler(EmailAlreadyExistsError, email_exists_handler)  # type: ignore[arg-type]
