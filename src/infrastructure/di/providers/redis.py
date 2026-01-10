from typing import AsyncGenerator
from dishka import Provider, Scope, provide
from redis.asyncio import Redis, from_url

from src.core.settings import RedisSettings


class RedisProvider(Provider):
    # Основной клиент — просто Redis (без AsyncGenerator)
    @provide(scope=Scope.APP)
    async def redis_client(self, redis_settings: RedisSettings) -> Redis:
        client = from_url(
            redis_settings.get_url(),
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
        )
        try:
            await client.ping()
        except Exception as e:
            await client.aclose()
            raise RuntimeError("Cannot connect to Redis") from e

        return client

    # Отдельный провайдер для закрытия при shutdown приложения
    @provide(scope=Scope.APP, provides=AsyncGenerator[None, None])
    async def redis_shutdown(self, redis_client: Redis) -> AsyncGenerator[None, None]:
        try:
            yield
        finally:
            await redis_client.aclose()
