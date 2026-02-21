from fastapi import APIRouter, HTTPException, Request, status, Response, Body
from dishka.integrations.fastapi import FromDishka, inject
from src.application.use_cases.refresh.refresh import RefreshTokensUseCase

from src.presentation.api.dto.auth import (
    TokenAccessResponse,
)
from src.presentation.api.dto.error import (
    UnauthorizedResponse,
)
import structlog
from src.core.settings.jwt import settings as jwt_settings

router = APIRouter(tags=["refresh token"])
logger = structlog.get_logger()


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
    request: Request,
    refresh_token_body: str | None = Body(default=None, embed=True),
) -> TokenAccessResponse:
    refresh_token_cookie = request.cookies.get("refresh_token")
    if refresh_token_cookie:
        logger.debug(
            "Получен рефреш токен через cookies", token=refresh_token_cookie[-15:]
        )
    if refresh_token_body:
        logger.debug("Получен рефреш токен через body", token=refresh_token_body[-15:])

    refresh_token = refresh_token_cookie or refresh_token_body

    if not refresh_token:
        logger.debug("рефреш токен отсутствует!")
        raise HTTPException(status_code=401, detail="Рефреш токен отсутствует")

    tokens = await use_case.execute(refresh_token)

    if refresh_token_cookie:
        response.set_cookie(
            key="refresh_token",
            value=(
                tokens.refresh_token.decode("utf-8")
                if isinstance(tokens.refresh_token, bytes)
                else str(tokens.refresh_token)
            ),
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

    logger.debug("Выданы новые токены")
    return TokenAccessResponse(
        access_token=tokens.access_token,
        expires_in=jwt_settings.access_expire_minutes * 60,
        refresh_token=refresh_token_response,
    )
