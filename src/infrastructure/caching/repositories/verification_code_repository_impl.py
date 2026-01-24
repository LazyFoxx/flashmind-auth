import asyncio
import json
from src.application.interfaces import (
    AbstractVerificationCodeRepository,
    PendingRegistrationData,
)
from redis.asyncio import Redis
from typing import Optional, Tuple


class VerificationCodeRepository(AbstractVerificationCodeRepository):
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    def _get_key_pending_reg(self, email: str) -> str:
        return f"pending_data:{str(email).lower()}"

    def _get_key_increment_a_check(self, email: str) -> str:
        return f"verifi_code_attempts:{str(email).lower()}"

    async def create_pending(
        self,
        email: str,
        otp_hash: str,
        ttl_seconds: int,
        max_attempts: int,
        hashed_password: Optional[str] = None,
    ) -> None:
        pending_key = self._get_key_pending_reg(email)
        attempts_key = self._get_key_increment_a_check(email)

        data = {
            "email": str(email),
            "hashed_password": hashed_password,
            "otp_hash": otp_hash,
            "max_attempts": max_attempts,
        }

        # Делаем обе операции параллельно
        await asyncio.gather(
            self.redis.set(pending_key, json.dumps(data), ex=ttl_seconds),
            self.redis.delete(attempts_key),
        )

        return None

    async def get_pending(self, email: str) -> Optional[PendingRegistrationData]:
        key = self._get_key_pending_reg(email)
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
        email: str,
        limit_attempts: int,
    ) -> Tuple[bool, int, int]:
        key = self._get_key_increment_a_check(email)
        # Если ключа нет — создаёт его со значением 1 и возвращает 1.
        # Если ключ есть — увеличивает его значение на 1 и возвращает новое значение.
        current_attempts = await self.redis.incr(key)

        if current_attempts == 1:
            await self.redis.expire(key, 1800)

        # Сколько осталось попыток
        remaining_attempts = max(0, limit_attempts - current_attempts)

        is_allowed = current_attempts < limit_attempts

        return is_allowed, current_attempts, remaining_attempts

    async def delete_pending(
        self,
        email: str,
    ) -> None:
        # если регистрация прошла успешно то удалям временные данные
        await self.redis.delete(self._get_key_pending_reg(email))
        await self.redis.delete(self._get_key_increment_a_check(email))
