from fastapi import APIRouter, Cookie, HTTPException, status, Response, Body
from dishka.integrations.fastapi import FromDishka, inject
from src.application.use_cases.refresh.refresh import RefreshTokensUseCase

from src.presentation.api.dto.auth import (
    TokenAccessResponse,
)
from src.presentation.api.dto.error import (
    UnauthorizedResponse,
)

router = APIRouter(tags=["refresh token"])


@router.post(
    "/refresh",
    response_model=TokenAccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Выдача нового access токена и ротация refresh токена",
    description=("Принимает "),
    responses={
        401: {
            "model": UnauthorizedResponse,
            "description": "Неверный токен или его отсутствие",
        },
    },
)
@inject
async def refresh(
    response: Response,
    use_case: FromDishka[RefreshTokensUseCase],
    refresh_token_cookie: str | None = Cookie(default=None),
    refresh_token_body: str | None = Body(default=None, embed=True),
) -> TokenAccessResponse:
    refresh_token = refresh_token_cookie or refresh_token_body

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Рефреш токен отсутствует")

    tokens = await use_case.execute(refresh_token)

    if refresh_token_cookie:
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
        refresh_token_response = None
    else:
        refresh_token_response = tokens.refresh_token

    return TokenAccessResponse(
        access_token=tokens.access_token,
        expires_in=1800,
        refresh_token=refresh_token_response,
    )
