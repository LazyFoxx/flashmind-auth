from dishka import Provider, Scope, provide
from src.application.interfaces import AbstractJWTService
from src.infrastructure.services.authlib_service import AuthlibJWTService


class JwtProvider(Provider):
    # Основной JWT-сервис (singleton на всё приложение)
    jwt_service = provide(
        AuthlibJWTService,
        provides=AbstractJWTService,
        scope=Scope.APP,
    )
