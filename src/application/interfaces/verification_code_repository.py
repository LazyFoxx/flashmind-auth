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
    async def get_pending(self, email: Email) -> Optional[dict]:
        """
        Возвращает данные pending-регистрации или None, если
        время ключа истекло или ключ удалили

        Args:
            email: email пользователя

        Returns:
            data_pending: dict or None
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

    @abstractmethod
    async def increment_and_check(
        self,
        email: str,
        limit_attempts: int,
    ) -> Tuple[bool, int, int]:
        """
        Атомарно увеличивает счётчик и проверяет лимит.
        Если лимит исчерпан то удаляет ключ. is_allowed = False

        Args:
            email: уникальный идентификатор (email)
            limit_attempts: лимит попыток на window_seconds
        Returns:
            (is_allowed: bool, current_attempts: int, remaining_attempts: int)
        """
        pass

    @abstractmethod
    async def delete(
        self,
        email: str,
    ) -> None:
        """
        Удаляет ключ и все значения связанные с ним.

        Args:
            email: уникальный идентификатор (email)
        """
        pass
