from redis.asyncio import Redis
from uuid import UUID
from datetime import timedelta

from src.application.interfaces import (
    AbstractRefreshTokenRepository,
)
from src.core.settings.jwt import JwtSettings


class RedisRefreshTokenRepository(AbstractRefreshTokenRepository):
    """
    Whitelist-хранилище refresh-токенов.
    Политика: один пользователь — один активный refresh-токен (автоматическая ротация).
    Использует два индекса для O(1) операций и полной атомарности.
    """

    def __init__(
        self,
        redis_client: Redis,
        settings: JwtSettings,
    ):
        self.redis = redis_client
        self.settings = settings
        self.prefix_user = "active_refresh:user:"  # user_id → jti
        self.prefix_jti = "active_refresh:jti:"  # jti → user_id

        # Вычисляем TTL один раз
        self.refresh_ttl_seconds = int(
            timedelta(days=settings.refresh_expire_days).total_seconds()
        )

    async def save(
        self,
        user_id: UUID,
        token_jti: str,
    ) -> None:
        """
        Сохраняет новый активный refresh-токен.
        Перезаписывает старый автоматически (ротация).
        """
        user_key = f"{self.prefix_user}{user_id}"
        jti_key = f"{self.prefix_jti}{token_jti}"

        # Используем pipeline для уменьшения round-trip'ов
        pipe = self.redis.pipeline()
        pipe.set(user_key, token_jti, ex=self.refresh_ttl_seconds)
        pipe.set(jti_key, str(user_id), ex=self.refresh_ttl_seconds)
        await pipe.execute()

    async def get_user_id_by_jti(self, token_jti: str) -> UUID | None:
        """
        Атомарно:
        - Проверяет существование токена
        - Возвращает user_id
        - Удаляет оба ключа (consume для rotation)

        Если токен уже использован → возвращает None (защита от reuse).
        """
        jti_key = f"{self.prefix_jti}{token_jti}"

        # Получаем user_id и сразу удаляем ключ jti → user_id
        pipe = self.redis.pipeline()
        pipe.getdel(jti_key)  # Redis 6.2+
        await pipe.execute()

        raw_user_id = pipe.getdel(jti_key)

        if raw_user_id is None:
            return None

        user_id = UUID(
            raw_user_id.decode() if isinstance(raw_user_id, bytes) else raw_user_id
        )

        # Удаляем основной ключ user_id → jti
        user_key = f"{self.prefix_user}{user_id}"
        await self.redis.delete(user_key)

        return user_id

    async def revoke_by_user_id(self, user_id: UUID) -> None:
        """
        Отзыв текущей сессии пользователя (logout или смена пароля).
        """
        user_key = f"{self.prefix_user}{user_id}"

        # Получаем текущий jti
        current_jti_bytes = await self.redis.get(user_key)
        if current_jti_bytes is None:
            return  # уже отозван

        current_jti = (
            current_jti_bytes.decode()
            if isinstance(current_jti_bytes, bytes)
            else current_jti_bytes
        )

        # Удаляем оба ключа атомарно
        pipe = self.redis.pipeline()
        pipe.delete(user_key)
        pipe.delete(f"{self.prefix_jti}{current_jti}")
        await pipe.execute()
