from abc import ABC, abstractmethod
from typing import Optional
from fastapi import BackgroundTasks


class AbstractEmailSender(ABC):
    """
    Используется для верификации email, сброса пароля посредством отправки кода.
    """

    @abstractmethod
    async def send_register_verification_code(
        self, email: str, code: str, background_tasks: Optional[BackgroundTasks] = None
    ) -> None:
        """
        Отправляет email с кодом верификации email при регистрации фоново через BackgroundTasks

        """
        ...

    @abstractmethod
    async def send_fogot_password_verification_code(
        self, email: str, code: str, background_tasks: Optional[BackgroundTasks] = None
    ) -> None:
        """
        Отправляет email с кодом верификации для смены пароля фоново через BackgroundTasks

        """
        ...
