from dishka import Provider, Scope, provide
from src.application.interfaces import AbstractVerificationCodeRepository
from src.infrastructure.caching.repositories.verification_code_repository_impl import (
    VerificationCodeRepository,
)


class VerificationCodeProvider(Provider):
    verification_code_repo = provide(
        VerificationCodeRepository,
        provides=AbstractVerificationCodeRepository,
        scope=Scope.APP,
    )
