# src/infrastructure/di/providers/auth_use_cases.py
from dishka import Provider, Scope, provide
from src.application.use_cases import (
    InitiateRegistrationUseCase,
    FinishRegistrationUseCase,
    ResendRegistrationCodeUseCase,
    LoginCodeUseCase,
    StartChangePasswordUseCase,
    VerifyCodeChangePasswordUseCase,
    FinishChangePasswordUseCase,
    ResendCodeChangePasswordUseCase,
)


class AuthUseCaseProvider(Provider):
    initiate_registration = provide(InitiateRegistrationUseCase, scope=Scope.REQUEST)
    finish_registration = provide(FinishRegistrationUseCase, scope=Scope.REQUEST)
    resend_registration = provide(ResendRegistrationCodeUseCase, scope=Scope.REQUEST)
    login = provide(LoginCodeUseCase, scope=Scope.REQUEST)
    start_change_password = provide(StartChangePasswordUseCase, scope=Scope.REQUEST)
    verify_code_change_password = provide(
        VerifyCodeChangePasswordUseCase, scope=Scope.REQUEST
    )
    finish_change_password = provide(FinishChangePasswordUseCase, scope=Scope.REQUEST)
    resend_code_change_password = provide(
        ResendCodeChangePasswordUseCase, scope=Scope.REQUEST
    )
