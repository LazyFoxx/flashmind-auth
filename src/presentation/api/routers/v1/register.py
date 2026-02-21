from fastapi import APIRouter, status, BackgroundTasks, Response
from dishka.integrations.fastapi import FromDishka, inject
from src.infrastructure.rabbit.models import MessagePayload
from src.infrastructure.rabbit.publisher import RabbitPublisher
from src.application.dtos import VerifyCodeDTO

from src.application.use_cases import (
    FinishRegistrationUseCase,
    ResendRegistrationCodeUseCase,
    InitiateRegistrationUseCase,
)

from src.application.dtos import AuthCredentialsDTO
from src.presentation.api.dto.auth import (
    EmailVerificationRequest,
    LoginResponse,
    RegisterRequest,
    MessageResponse,
    ResendEmailVerificationRequest,
)
from src.presentation.api.dto.error import (
    CodeAttemptResponse,
    CooldownEmailResponse,
    EmailAlreadyExistsResponse,
    LimitCodeAttemptsResponse,
    RateLimitExceededResponse,
    RequestExpiredResponse,
)

from src.core.settings.jwt import settings as jwt_settings

router = APIRouter(tags=["register"])


@router.post(
    "/register",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Начало регистрации пользователя",
    description=("Отправляет код подтверждения на указанный email. "),
    response_model=MessageResponse,
    responses={
        409: {
            "model": EmailAlreadyExistsResponse,
            "description": "Такой имейл уже используется",
        },
        429: {
            "model": RateLimitExceededResponse,
            "description": "Исчерпаны попытки регистрации",
        },
        202: {
            "model": MessageResponse,
            "description": "Успешная инициализация регистрации",
        },
    },
)
@inject
async def initiate_registration(
    payload: RegisterRequest,
    background_tasks: BackgroundTasks,
    use_case: FromDishka[InitiateRegistrationUseCase],
) -> MessageResponse:
    """
    Инициирует процесс регистрации:
    - Проверяет, существует ли email
    - Проверяет лимит запросов
    - Отправляет email с OTP
    - Сохраняет временные данные в Redis
    """

    dto = AuthCredentialsDTO(email=payload.email, password=payload.password)
    await use_case.execute(input_dto=dto, background_tasks=background_tasks)
    return MessageResponse(message="Код верификации успешно отправлен!")


@router.post(
    "/register/verify-code",
    response_model=LoginResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Завершение регистрации и получение токенов",
    description=(
        "Проверяет код → создаёт пользователя → выдаёт access token в теле и "
        "refresh token в httpOnly cookie"
    ),
    responses={
        400: {
            "model": CodeAttemptResponse,
            "description": "Неверный код подтверждения",
        },
        429: {
            "model": LimitCodeAttemptsResponse,
            "description": "Исчерпаны попытки ввести код правильно",
        },
        410: {
            "model": RequestExpiredResponse,
            "description": "Истёк срок действия запроса на регистрацию",
        },
        201: {
            "model": LoginResponse,
            "description": "Успешная регистрация",
        },
    },
)
@inject
async def verify_registration(
    payload: EmailVerificationRequest,
    response: Response,
    use_case: FromDishka[FinishRegistrationUseCase],
    publisher: FromDishka[RabbitPublisher],
) -> LoginResponse:
    """
    Завершает процесс регистрации:
    - Проверяет код подтверждения
    - Проверяет лимит запросов
    - Сохраняет пользователя в БД
    - В случае успеха производит автологин с выдачей токенов
    """
    dto = VerifyCodeDTO(email=payload.email, code=payload.code)
    tokens, user_id = await use_case.execute(input_dto=dto)

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

    await publisher.publish(
        exchange="events",  # Название обменника
        routing_key="user.registered",  # Роутинг-ключ
        payload=MessagePayload(user_id=user_id),  # Модель с данными
    )

    return LoginResponse(
        access_token=tokens.access_token,
        expires_in=jwt_settings.access_expire_minutes * 60,
        refresh_token=tokens.refresh_token,
    )


@router.post(
    "/register/resend-code",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Повторная отправка кода подтверждения",
    description=("Отправляет код подтверждения на указанный email."),
    responses={
        410: {
            "model": RequestExpiredResponse,
            "description": "Истёк срок действия запроса на регистрацию",
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
async def resend_verify_code(
    payload: ResendEmailVerificationRequest,
    background_tasks: BackgroundTasks,
    use_case: FromDishka[ResendRegistrationCodeUseCase],
) -> MessageResponse:
    """
    Отправляет код подтверждения повторно:
    - Проверяет что сессия регистрации еще действует
    - Генерирует новый код и отправляет на email
    - Удаляет старый код и попытки ввода!
    """
    email = payload.email
    await use_case.execute(email=email, background_tasks=background_tasks)
    return MessageResponse(message="Код верификации успешно отправлен!")
