from abc import ABC, abstractmethod
from typing import Optional, Tuple
from dataclasses import dataclass


# DTO для хранения pending-регистрации
@dataclass(frozen=True)
class PendingRegistrationData:
    email: str
    hashed_password: str
    otp_hash: str
    max_attempts: int


class AbstractVerificationCodeRepository(ABC):
    """
    Репозиторий для хранения и управления данными незавершённой работы с otp.
    """

    @abstractmethod
    async def create_pending(
        self,
        email: str,
        otp_hash: str,
        ttl_seconds: int,
        max_attempts: int,
        hashed_password: Optional[str] = None,
    ) -> None:
        """
        Сохраняет данные pending по email и устанавливает TTL.
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
    async def get_pending(self, email: str) -> Optional[PendingRegistrationData]:
        """
        Возвращает данные pending по email или None, если
        время ключа истекло или ключ удалили

        Args:
            email: email пользователя

        Returns:
            data_pending: PendingRegistrationData or None
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
    async def delete_pending(
        self,
        email: str,
    ) -> None:
        """
        Удаляет ключи и все значения связанные с ним.
        например при усмешной регистрации

        Args:
            email: уникальный идентификатор (email)
        """
        pass
