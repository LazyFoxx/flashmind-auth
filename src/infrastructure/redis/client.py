from typing import Optional
from redis.asyncio import Redis, ConnectionPool
from src.config.settings import settings


class RedisClient:
    def __init__(self) -> None:
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[Redis] = None

    async def init(self) -> Redis:
        """
        Вызывается на startup FastAPI.
        """
        if self._pool is None:
            # Настраиваем пул
            self._pool = ConnectionPool.from_url(
                url=settings.redis.url,
                decode_responses=True,
                max_connections=settings.redis.max_connections,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                health_check_interval=30,  # автоматическая проверка
            )
            self._client = Redis(connection_pool=self._pool)

            try:
                await self._client.ping()
            except Exception:
                raise

        return self._client

    async def close(self):
        """
        Вызывается на shutdown FastAPI.
        """
        if self._client:
            await self._client.close()
            self._client = None
            self._pool = None

    def get_client(self) -> Redis:
        """
        Используется в зависимостях.
        """
        if self._client is None:
            raise RuntimeError("Redis client not initialized. Call init() first.")
        return self._client


# Создаём глобальный экземпляр
redis_client = RedisClient()
