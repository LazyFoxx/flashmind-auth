from src.application.interfaces import AbstractVerificationCodeRepository
from typing import Tuple, Optional
from redis.asyncio import Redis
from src.domain.value_objects import Email


class VerificationCodeRepository(AbstractVerificationCodeRepository):
    # def __init__(self, redis: Redis = Depends(redis_client.get_client)):
    #     self.redis = redis

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def create_pending(
        self,
        email: Email,
        hashed_password: str,
        otp_hash: str,
        ttl_seconds: int,
        max_attempts: int,
    ) -> None:
        pass

    async def get_pending(self, email: Email) -> Optional[Tuple[str, str, str]]:
        pass

    # async def verify_code(
    #     self,
    #     email: Email,
    #     submitted_otp_hash: str,
    # ) -> Tuple[int, bool]:
    #     pass
