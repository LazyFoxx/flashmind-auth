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
        в течении window_seconds может быть только limit_attempts попыток

        Args:
            email: уникальный идентификатор (email)
            prefix: register - для регистрации, login - для логина
            limit_attempts: лимит попыток
            window_seconds: время окна для регистрации/логина
        Returns:
            (is_allowed: bool, current_attempts: int, remaining_attempts: int)
        """
        pass

    @abstractmethod
    async def check_and_set_cooldown(
        self,
        email: str,
        cooldown: int,
    ) -> Tuple[bool, int]:
        """
        Проверяет, прошёл ли cooldown, и если да — возвращает True
        и устанавливает новый, иначе False. Так же возвращает в секундах оставшийся cooldown

        Args:
            email: уникальный идентификатор (email)

        Returns:
            is_allowed: bool
            remaining_cooldown: int
        """
        pass
