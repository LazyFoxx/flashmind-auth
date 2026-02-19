from fastapi import APIRouter, status, Response
from dishka.integrations.fastapi import FromDishka, inject

from src.application.use_cases import (
    LoginCodeUseCase,
)

from src.application.dtos import AuthCredentialsDTO
from src.presentation.api.dto.auth import (
    LoginRequest,
    LoginResponse,
)
from src.presentation.api.dto.error import (
    InvalideCredentialResponse,
    RateLimitExceededResponse,
)

from src.core.settings.jwt import settings as jwt_settings

router = APIRouter(tags=["login"])


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Авторизация по email и password",
    description=("В случае валидных данных выдает токены доступа."),
    responses={
        401: {
            "model": InvalideCredentialResponse,
            "description": "Неверный логин или пароль",
        },
        429: {
            "model": RateLimitExceededResponse,
            "description": "Попытки ввести правильный пароль исчерпаны, повторите позже",
        },
        200: {
            "model": LoginResponse,
            "description": "Успешная авторизация",
        },
    },
)
@inject
async def login(
    payload: LoginRequest,
    response: Response,
    use_case: FromDishka[LoginCodeUseCase],
) -> LoginResponse:
    dto = AuthCredentialsDTO(email=payload.email, password=payload.password)
    tokens = await use_case.execute(input_dto=dto)

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,  # Защита от XSS — JS не увидит токен
        secure=False,  # Только HTTPS (в dev можно временно False)
        samesite="lax",  # "strict" тоже можно, но "lax" удобнее для UX
        max_age=60 * 60 * 24 * 30,  # 30 дней
        path="/",  # Доступен для всего сайта
        # domain="api.example.com"   # если нужен кросс-домен
    )

    return LoginResponse(
        access_token=tokens.access_token,
        expires_in=jwt_settings.access_expire_minutes * 60,
        refresh_token=tokens.refresh_token,
    )
