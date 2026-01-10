from fastapi import APIRouter, status
from dishka import FromDishka
from src.application.use_cases import InitiateRegistrationUseCase
from src.presentation.api.dto.auth import RegisterRequest, MessageResponse
from src.application.dtos import AuthCredentialsDTO

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Начало регистрации пользователя",
    description=("Отправляет код подтверждения на указанный email. "),
    response_model=MessageResponse,
)
async def initiate_registration(
    payload: RegisterRequest,
    use_case: FromDishka[InitiateRegistrationUseCase],
):
    """
    Инициирует процесс регистрации:
    - Проверяет, существует ли email
    - Проверяет лимит запросов
    - Отправляет email с OTP
    - Сохраняет временные данные в Redis
    """

    dto = AuthCredentialsDTO(email=payload.email, password=payload.password)
    await use_case.execute(dto)
    return MessageResponse(message="Код верификации успешно отправлен!")


# @router.post(
#     "/verify-registration",
#     response_model=RegistrationCompletedResponse,
#     status_code=status.HTTP_201_CREATED,
# )
# @inject
# async def verify_registration(
#     data: EmailVerificationRequest,
#     use_case: FromDishka[FinishRegistrationUseCase],
# ) -> RegistrationCompletedResponse:
#     pass


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
