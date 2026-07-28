from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from src.application.interfaces import AbstractJWKSCache
from src.infrastructure.telegram.token_service import TelegramTokenService
from src.infrastructure.caching.repositories.jwks_cache_redis import RedisJWKSCache
from src.infrastructure.telegram.jwks_client import TelegramJWKSClient


class TelegramAuthProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_jwks_cache(self, redis: Redis) -> AbstractJWKSCache:
        return RedisJWKSCache(redis)

    telegram_jwks_client = provide(TelegramJWKSClient, scope=Scope.APP)
    telegram_token_service = provide(TelegramTokenService, scope=Scope.REQUEST)
