from dishka import Provider, Scope, provide
from src.application.interfaces import AbstractRateLimitRepository
from src.infrastructure.caching.repositories.rate_limit_repository_impl import (
    RateLimitRepository,
)


class RateLimitProvider(Provider):
    rate_limit_repo = provide(
        RateLimitRepository,
        provides=AbstractRateLimitRepository,
        scope=Scope.APP,
    )
