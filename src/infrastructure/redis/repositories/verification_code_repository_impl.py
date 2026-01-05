import json
from src.application.interfaces import (
    AbstractVerificationCodeRepository,
    PendingRegistrationData,
)
from redis.asyncio import Redis
from src.domain.value_objects import Email
from typing import Optional, Tuple


class VerificationCodeRepository(AbstractVerificationCodeRepository):
    # def __init__(self, redis: Redis = Depends(redis_client.get_client)):
    #     self.redis = redis

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    def _get_key(self, email: Email) -> str:
        return f"pending_registration:{str(email).lower()}"

    async def create_pending(
        self,
        email: Email,
        hashed_password: str,
        otp_hash: str,
        ttl_seconds: int,
        max_attempts: int,
    ) -> None:
        key = self._get_key(email)

        data = {
            "email": str(email),
            "hashed_password": hashed_password,
            "verification_code": otp_hash,
            "attempts_left": max_attempts,
        }

        await self.redis.set(
            key,
            json.dumps(data),
            ex=ttl_seconds,
        )

        return None

    async def get_pending(self, email: Email) -> Optional[dict]:
        key = self._get_key(email)
        raw = await self.redis.get(key)

        if not raw:
            return None

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            await self.redis.delete(key)
            return None

        return PendingRegistrationData(
            email=data["email"],
            hashed_password=data["hashed_password"],
            otp_hash=data["otp_hash"],
            max_attempts=data["max_attempts"],
        )

    async def increment_and_check(
        self,
        email: Email,
        limit_attempts: int,
    ) -> Tuple[bool, int, int]:
        key = self._get_key(email)
        # Если ключа нет — создаёт его со значением 1 и возвращает 1.
        # Если ключ есть — увеличивает его значение на 1 и возвращает новое значение.
        current_attempts = await self.redis.incr(key)

        # Сколько осталось попыток до истечения window
        remaining_attempts = max(0, limit_attempts - current_attempts)

        is_allowed = current_attempts <= limit_attempts

        return is_allowed, current_attempts, remaining_attempts

    async def delete_pending(
        self,
        email: Email,
    ) -> None:
        self.redis.delete(self._get_key(email))
