from dishka import Provider, Scope, provide
from application.interfaces import AbstractJWTService
from infrastructure.services.jwt.authlib_service import AuthlibJWTService


class JwtProvider(Provider):
    # Основной JWT-сервис (singleton на всё приложение)
    jwt_service = provide(
        AuthlibJWTService,
        provides=AbstractJWTService,
        scope=Scope.APP,
    )
