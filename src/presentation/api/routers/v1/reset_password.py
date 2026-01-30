from fastapi import APIRouter, Depends, status, BackgroundTasks, Response
from dishka.integrations.fastapi import FromDishka, inject
from src.secure.dependencies import get_current_user
from src.domain.entities.user import User
from src.application.dtos import VerifyCodeDTO

from src.application.use_cases import (
    StartChangePasswordUseCase,
    VerifyCodeChangePasswordUseCase,
    ResendCodeChangePasswordUseCase,
    FinishChangePasswordUseCase,
)

from src.presentation.api.dto.auth import (
    EmailVerificationRequest,
    LoginResponse,
    MessageResponse,
    ResendEmailVerificationRequest,
    TokenAccessResponse,
    NewPasswordRequest,
)
from src.presentation.api.dto.error import (
    CodeAttemptResponse,
    CooldownEmailResponse,
    LimitCodeAttemptsResponse,
    RateLimitExceededResponse,
    RequestExpiredResponse,
)

router = APIRouter(tags=["reset_password"])


@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Начало сброса пароля",
    description=("Отправляет код подтверждения на указанный email."),
    response_model=MessageResponse,
    responses={
        200: {
            "model": MessageResponse,
            "description": "Успешная инициализация сброса пароля",
        },
        429: {
            "model": RateLimitExceededResponse,
            "description": "Исчерпаны попытки сброса пароля",
        },
    },
)
@inject
async def initiate_change_pass(
    payload: ResendEmailVerificationRequest,
    background_tasks: BackgroundTasks,
    use_case: FromDishka[StartChangePasswordUseCase],
) -> MessageResponse:
    """
    Инициирует процесс сброса пароля:
    - Проверяет лимит запросов
    - Отправляет email с OTP
    - Сохраняет временные данные в Redis
    """

    await use_case.execute(payload.email, background_tasks=background_tasks)
    return MessageResponse(message="Код подтверждения успешно отправлен!")


@router.post(
    "/forgot-password/verify-code",
    status_code=status.HTTP_200_OK,
    summary="Подтверждение кода",
    description=("Проверяет код и выдает access токен для смены пароля"),
    response_model=TokenAccessResponse,
    responses={
        200: {
            "model": TokenAccessResponse,
            "description": "Код для сброса пароля подтвержден ( если выдается имейл не существующий в базе данных то все равно код 200 без токенов доступа!)",
        },
        410: {
            "model": RequestExpiredResponse,
            "description": "Истёк срок действия запроса на сброс пароля (начать заново)",
        },
        400: {
            "model": CodeAttemptResponse,
            "description": "Неверный код подтверждения",
        },
        429: {
            "model": LimitCodeAttemptsResponse,
            "description": "Исчерпаны попытки ввести код правильно",
        },
    },
)
@inject
async def verify_code_change_pass(
    payload: EmailVerificationRequest,
    use_case: FromDishka[VerifyCodeChangePasswordUseCase],
) -> TokenAccessResponse:
    """
    Проверяет код верификации и в случае успеха возвращает временный токен для смены пароля
    """
    dto = VerifyCodeDTO(email=payload.email, code=payload.code)
    access_token = await use_case.execute(input_dto=dto)
    return TokenAccessResponse(access_token=access_token, expires_in=1800)


@router.post(
    "/forgot-password/resend-code",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Повторная отправка кода подтверждения",
    description=("Отправляет код подтверждения на указанный email."),
    responses={
        410: {
            "model": RequestExpiredResponse,
            "description": "Истёк срок действия запроса на сброс пароля (начать заново)",
        },
        429: {
            "model": CooldownEmailResponse,
            "description": "Слишком частый запрос на отправку кода",
        },
        202: {
            "model": MessageResponse,
            "description": "Код отправлен на email",
        },
    },
)
@inject
async def password_resend_verify_code(
    payload: ResendEmailVerificationRequest,
    background_tasks: BackgroundTasks,
    use_case: FromDishka[ResendCodeChangePasswordUseCase],
) -> MessageResponse:
    """
    Отправляет код подтверждения повторно:
    - Проверяет что сессия сброса пароля еще действует
    - Генерирует новый код и отправляет на email
    - Удаляет старый код и попытки ввода!
    """
    email = payload.email
    await use_case.execute(email=email, background_tasks=background_tasks)
    return MessageResponse(message="Код верификации успешно отправлен!")


@router.post(
    "/forgot-password/change-password",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Смена пароля пользователем",
    description=("Меняет пароль пользователя в БД на новый и производит автологин."),
    responses={
        200: {
            "model": LoginResponse,
            "description": "Успешная авторизация",
        },
    },
)
@inject
async def change_password(
    payload: NewPasswordRequest,
    response: Response,
    use_case: FromDishka[FinishChangePasswordUseCase],
    user: User = Depends(get_current_user),
) -> LoginResponse:
    tokens = await use_case.execute(user, payload.password)

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
        expires_in=1800,
        refresh_token=tokens.refresh_token,
    )
