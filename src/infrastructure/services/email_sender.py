from typing import List, Optional
import resend
from fastapi import BackgroundTasks

from src.application.interfaces import AbstractEmailSender
from src.core.settings import EmailSettings


class ResendEmailSender(AbstractEmailSender):
    """
    Отправка email через Resend.com

    • Один экземпляр на приложение (Scope.APP)
    • BackgroundTasks передаётся только при необходимости
    • Работает и внутри HTTP-запроса, и вне его (тесты, CLI, workers)
    """

    def __init__(self, settings: EmailSettings):
        resend.api_key = settings.resend_api_key
        self.from_email = settings.from_email
        self.from_name = settings.from_name
        self.dev = settings.dev

    async def _send_email(
        self,
        to: str | List[str],
        subject: str,
        plain_text: str,
        html: Optional[str] = None,
    ) -> None:
        """Низкоуровневая отправка одного письма"""
        params = {
            "from": f"{self.from_name} <{self.from_email}>",
            "to": to if isinstance(to, list) else [to],
            "subject": subject,
            "text": plain_text,
        }

        if html:
            params["html"] = html

        try:
            resp = resend.Emails.send(params)
            # В продакшене здесь logger.info(...)
            print(f"Email sent → ID: {resp.get('id', '—')}")
        except Exception as e:
            # В продакшене: logger.error + Sentry/capture_exception
            print(f"Email send failed: {e}")
            raise

    async def send(
        self,
        to: str | List[str],
        subject: str,
        plain_text: str,
        html: Optional[str] = None,
        *,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        """
        Основной публичный метод отправки.

        Args:
            background_tasks: если передан → отправка в фоне
                              если None → синхронная отправка
        """

        async def _task():
            await self._send_email(
                to=to,
                subject=subject,
                plain_text=plain_text,
                html=html,
            )

        if background_tasks is not None:
            background_tasks.add_task(_task)
        else:
            await _task()

    async def send_register_verification_code(
        self,
        email: str,
        code: str,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        """Отправка кода верификации при регистрации на email
        если settings.dev = True то отправляет в консоль"""

        if self.dev:  # не отправляет на email и выводит код в консоль
            print(code)
            return None

        subject = "FlashMind — подтвердите email"
        plain_text = (
            f"Ваш код подтверждения: {code}\n\n"
            "Код действителен 10 минут.\n"
            "Если это не вы — просто проигнорируйте письмо."
        )

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: system-ui, sans-serif; max-width: 560px; margin: 40px auto; color: #111;">
    <h1 style="margin-bottom: 8px;">Добро пожаловать в FlashMind!</h1>
    <p style="font-size: 16px; line-height: 1.5;">
        Ваш код для подтверждения email:
    </p>
    <div style="
        font-size: 32px;
        font-weight: bold;
        letter-spacing: 12px;
        text-align: center;
        background: #f8f9fa;
        padding: 24px;
        border-radius: 12px;
        margin: 24px 0;
    ">
        {code}
    </div>
    <p style="color: #555; font-size: 14px;">
        Код действителен <strong>10 минут</strong>.<br>
        Если вы не регистрировались — просто проигнорируйте это письмо.
    </p>
</body>
</html>"""

        await self.send(
            to=email,
            subject=subject,
            plain_text=plain_text,
            html=html,
            background_tasks=background_tasks,
        )
