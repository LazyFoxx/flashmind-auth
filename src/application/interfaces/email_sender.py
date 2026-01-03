# src/application/interfaces/email_sender.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class AbstractEmailSender(ABC):
    """
    Абстрактный сервис отправки email.
    Используется для верификации email, сброса пароля, уведомлений и т.д.
    """

    @abstractmethod
    async def send(
        self,
        to: str | List[str],
        subject: str,
        plain_text: str,
        html: str | None = None,
        template_data: Dict[str, Any] | None = None,
    ) -> None:
        """
        Отправляет email

        Args:
            to: один адрес или список
            subject: тема письма
            plain_text: текстовая версия
            html: HTML-версия (опционально)
            template_data: данные для шаблонизатора (если используешь)
        """
        ...
