from abc import ABC, abstractmethod
from src.domain.value_objects import Email
from typing import Optional, Tuple


class AbstractVerificationCodeRepository(ABC):
    """
    Репозиторий для хранения и управления данными незавершённой регистрации.
    """

    @abstractmethod
    async def create_pending(
        self,
        email: Email,
        hashed_password: str,
        otp_hash: str,
        ttl_seconds: int,
        max_attempts: int,
    ) -> None:
        """
        Сохраняет данные pending-регистрации и устанавливает TTL.
        Перезаписывает существующую запись (если пользователь начал регистрацию заново или отправил код повторно).

        Args:
            email: email пользователя
            hashed_password: хеш пароля
            otp_hash: хеш кода верификации
            ttl_seconds: время жизни записи
            max_attempts: количество попыток подтвердить код

        Returns:
            None
        """
        pass

    @abstractmethod
    async def get_pending(self, email: Email) -> Optional[Tuple[str, str, str]]:
        """
        Возвращает данные pending-регистрации или None, если:

        Args:
            email: email пользователя

        Returns:
            (email: str, hashed_password: str, otp_hash: str)
        """
        pass

    @abstractmethod
    async def verify_code(
        self,
        email: Email,
        submitted_otp_hash: str,
    ) -> Tuple[int, bool]:
        """
        Проверяет код.

        Args:
            email: email пользователя
            submitted_otp_hash: хеш кода верификации

        Returns:
            (attempts: int, success: bool)

        - Если запись не существует или истекла → (0, False)
        - Если код верный → (любое_число, True) и запись удаляется
        - Если код неверный и остались попытки → (оставшиеся_попытки, False)
        - Если код неверный и попытки кончились → (0, False) и запись удаляется
        """
        pass
