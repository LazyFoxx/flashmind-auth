from fastapi import APIRouter, status, BackgroundTasks, Response
from dishka.integrations.fastapi import FromDishka, inject

from src.application.use_cases import (
    InitiateRegistrationUseCase,
    FinishRegistrationUseCase,
)
from src.application.dtos import AuthCredentialsDTO, VerifyCodeDTO
from src.presentation.api.dto.auth import (
    EmailVerificationRequest,
    RegisterRequest,
    MessageResponse,
    RegistrationCompletedResponse,
)
from src.presentation.api.dto.error import (
    EmailAlreadyExistsResponse,
    RateLimitExceededResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        409: {
            "model": EmailAlreadyExistsResponse,
            "description": "Email уже занят",
            "content": {
                "application/json": {
                    "example": {
                        "error": "EmailAlreadyExists",
                        "message": "User with this email already exists",
                        "email": "user@example.com",
                    }
                }
            },
        },
        429: {
            "model": RateLimitExceededResponse,
            "description": 'Слишком много попыток регистарции: "error": "RateLimitExceeded". \n Кулдаун отправки смс кода - "error": "CooldownEmail"',
            "content": {
                "application/json": {
                    "example": {
                        "error": "RateLimitExceeded",
                        "message": "Too many attempts, please try again later",
                    }
                }
            },
        },
        202: {
            "model": MessageResponse,
            "description": "Успех!",
            "content": {
                "application/json": {
                    "example": {"message": "Код верификации успешно отправлен!"}
                }
            },
        },
    },
    summary="Начало регистрации пользователя",
    description=("Отправляет код подтверждения на указанный email. "),
    response_model=MessageResponse,
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


# @router.post(
#     "/resend-verification",
#     response_model=EmailVerificationSentResponse,
#     status_code=status.HTTP_200_OK,
# )
# @inject
# async def resend_verification(
#     data: ResendEmailVerificationRequest,
#     use_case: FromDishka[ResendRegistrationCodeUseCase],
# ) -> EmailVerificationSentResponse:
#     pass
