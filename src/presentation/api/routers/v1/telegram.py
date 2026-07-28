from fastapi import APIRouter, status, Response
from dishka.integrations.fastapi import FromDishka, inject

from src.application.use_cases import (
    TelegramLoginUseCase, TelegramLoginInput,
)

from src.application.dtos import AuthCredentialsDTO
from src.presentation.api.dto.v1.auth import (
    LoginResponse,
)
from src.presentation.api.dto.v1.telegram import TelegramAuthRequest
from src.infrastructure.telegram.token_service import TelegramTokenService
from src.core.settings.jwt import settings as jwt_settings

router = APIRouter()


@router.post(
    "/telegram",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Авторизация через телеграм",
    description=("В случае валидных данных выдает токены доступа."),
)
@inject
async def login(
    payload: TelegramAuthRequest,
    response: Response,
    use_case: FromDishka[TelegramLoginUseCase],
    token_decode: FromDishka[TelegramTokenService],
) -> None:
    dto = AuthCredentialsDTO(email=payload.email, password=payload.password)
    tokens = await use_case.execute(input_dto=dto)

    
    telegram_user = token_decode.execute(token=payload.id_token)
    use_case.execute(telegram_user)
    
    
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

    return LoginResponse(
        access_token=tokens.access_token,
        expires_in=jwt_settings.access_expire_minutes * 60,
        refresh_token=tokens.refresh_token,
    )
