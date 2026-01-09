from dishka import Provider, Scope, provide
from src.application.interfaces import AbstractRefreshTokenRepository
from src.infrastructure.caching.repositories.refresh_token import (
    RedisRefreshTokenRepository,
)


class RefreshTokenProvider(Provider):
    refresh_token = provide(
        RedisRefreshTokenRepository,
        provides=AbstractRefreshTokenRepository,
        scope=Scope.APP,
    )
