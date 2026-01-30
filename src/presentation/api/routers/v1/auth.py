from fastapi import APIRouter, Cookie, Depends, status, BackgroundTasks, Response
from dishka.integrations.fastapi import FromDishka, inject
from src.secure.dependencies import get_current_user
from src.domain.entities.user import User
from src.application.dtos import VerifyCodeDTO

from src.application.use_cases import (
    StartChangePasswordUseCase,
    VerifyCodeChangePasswordUseCase,
    LoginCodeUseCase,
    FinishRegistrationUseCase,
    ResendRegistrationCodeUseCase,
    ResendCodeChangePasswordUseCase,
    FinishChangePasswordUseCase,
    InitiateRegistrationUseCase,
)

from src.application.dtos import AuthCredentialsDTO
from src.presentation.api.dto.auth import (
    EmailVerificationRequest,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    MessageResponse,
    RegistrationCompletedResponse,
    ResendEmailVerificationRequest,
    TokenAccessResponse,
    NewPasswordRequest,
)
from src.presentation.api.dto.error import (
    CodeAttemptResponse,
    CooldownEmailResponse,
    EmailAlreadyExistsResponse,
    InvalideCredentialResponse,
    LimitCodeAttemptsResponse,
    RateLimitExceededResponse,
    RequestExpiredResponse,
    UnauthorizedResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


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
    response_model=RegistrationCompletedResponse,
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
            "model": RegistrationCompletedResponse,
            "description": "Успешная регистрация",
        },
    },
)
@inject
async def verify_registration(
    payload: EmailVerificationRequest,
    response: Response,
    use_case: FromDishka[FinishRegistrationUseCase],
) -> RegistrationCompletedResponse:
    """
    Завершает процесс регистрации:
    - Проверяет код подтверждения
    - Проверяет лимит запросов
    - Сохраняет пользователя в БД
    - В случае успеха производит автологин с выдачей токенов
    """
    dto = VerifyCodeDTO(email=payload.email, code=payload.code)
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

    return RegistrationCompletedResponse(
        access_token=tokens.access_token, expires_in=1800
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

    return LoginResponse(access_token=tokens.access_token, expires_in=1800)


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

    return LoginResponse(access_token=tokens.access_token, expires_in=1800)


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
    use_case: FromDishka[FinishChangePasswordUseCase],
    refresh_token: str | None = Cookie(default=None),
) -> TokenAccessResponse:
    tokens = await use_case.execute(refresh_token)

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

    return TokenAccessResponse(access_token=tokens.access_token, expires_in=1800)
