from typing import AsyncGenerator
from dishka import Provider, Scope, provide
from redis.asyncio import Redis, from_url

from core.settings import RedisSettings


class RedisProvider(Provider):
    @provide(scope=Scope.APP)
    async def redis_client(
        self, redis_settings: RedisSettings
    ) -> AsyncGenerator[Redis, None]:
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

        try:
            yield client
        finally:
            await client.aclose()  # гарантированно закроется
