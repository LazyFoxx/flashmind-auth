from src.application.interfaces import AbstractRateLimitRepository
from typing import Tuple
from redis.asyncio import Redis


class RateLimitRepository(AbstractRateLimitRepository):
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def increment_and_check(
        self,
        email: str,
        prefix: str,
        limit_attempts: int,
        window_seconds: int,
    ) -> Tuple[bool, int, int]:
        key = f"{prefix}:{email.lower()}"

        # Если ключа нет — создаёт его со значением 1 и возвращает 1.
        # Если ключ есть — увеличивает его значение на 1 и возвращает новое значение.
        current_attempts = await self.redis.incr(key)
        if current_attempts == 1:
            await self.redis.expire(key, window_seconds)

        # Сколько осталось попыток до истечения window
        remaining_attempts = max(0, limit_attempts - current_attempts)

        is_allowed = current_attempts <= limit_attempts

        return is_allowed, current_attempts, remaining_attempts

    async def check_and_set_cooldown(self, email: str, cooldown: int) -> bool:
        key = f"cooldown:{email.lower()}"
        created = await self.redis.set(key, "1", ex=cooldown, nx=True)
        return created is True
