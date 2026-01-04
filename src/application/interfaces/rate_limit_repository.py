# src/application/interfaces/rate_limit_repository.py
from abc import ABC, abstractmethod
from typing import Tuple


class AbstractRateLimitRepository(ABC):
    """
    Абстрактный репозиторий для rate limiting.
    """

    @abstractmethod
    async def increment_and_check(
        self,
        email: str,
        prefix: str,
        limit_attempts: int,
        window_seconds: int,
    ) -> Tuple[bool, int, int]:
        """
        Атомарно увеличивает счётчик и проверяет лимит.

        Args:
            email: уникальный идентификатор (email)
            prefix: register - для регистрации, login - для логина
            limit_attempts: лимит попыток на window_seconds
            window_seconds: время окна для регистрации
        Returns:
            (is_allowed: bool, current_attempts: int, remaining_attempts: int)
        """
        pass

    @abstractmethod
    async def check_and_set_cooldown(
        self,
        email: str,
        prefix: str = "cooldown",
    ) -> Tuple[bool, int]:
        """
        Проверяет, прошёл ли cooldown, и если да — устанавливает новый.

        Args:
            email: уникальный идентификатор (email)
            prefix: префикс ключа

        Returns:
            (is_allowed: bool, retry_after_seconds: int)
            Если is_allowed = False → retry_after_seconds = сколько секунд осталось ждать
        """
        pass
