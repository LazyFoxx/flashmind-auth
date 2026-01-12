# src/infrastructure/di/providers/auth_use_cases.py
from dishka import Provider, Scope, provide
from src.application.use_cases import (
    InitiateRegistrationUseCase,
    FinishRegistrationUseCase,
    ResendRegistrationCodeUseCase,
)


class AuthUseCaseProvider(Provider):
    initiate_registration = provide(InitiateRegistrationUseCase, scope=Scope.REQUEST)
    finish_registration = provide(FinishRegistrationUseCase, scope=Scope.REQUEST)
    resend_registration = provide(ResendRegistrationCodeUseCase, scope=Scope.REQUEST)
