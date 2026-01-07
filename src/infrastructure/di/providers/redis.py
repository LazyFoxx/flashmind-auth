from dishka import Provider, Scope, provide
from redis.asyncio import ConnectionPool
from core.settings.redis import RedisSettings


class RedisProvider(Provider):
    scope = Scope.APP

    settings = provide(RedisSettings)

    @provide
    def get_pool(self, settings: RedisSettings) -> ConnectionPool:
        return ConnectionPool.from_url(
            settings.get_url(),
            max_connections=settings.max_connections,  # ← подбери под нагрузку
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
        )

    # @provide(is_async=True)
    # async def get_redis(self, pool: ConnectionPool) -> Redis:
    #     client = Redis(connection_pool=pool)
    #     try:
    #         yield client
    #     finally:
    #         await client.aclose()
