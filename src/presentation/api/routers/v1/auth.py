from fastapi import APIRouter


router = APIRouter(prefix="/auth", tags=["auth"])


# @router.post(
#     "/register",
#     response_model=EmailVerificationSentResponse,
#     status_code=status.HTTP_200_OK,
# )
# @inject
# async def register(
#     data: RegisterRequest,
#     use_case: FromDishka[InitiateRegistrationUseCase],
# ) -> EmailVerificationSentResponse:
#     pass


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
