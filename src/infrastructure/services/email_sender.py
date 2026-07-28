from typing import List, Optional
import resend
from fastapi import BackgroundTasks
import structlog
import httpx

from src.application.interfaces import AbstractEmailSender
from src.core.settings import EmailSettings

import aiosmtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional

import resend
from fastapi import BackgroundTasks
import structlog

from src.application.interfaces import AbstractEmailSender
from src.core.settings import EmailSettings


class ResendEmailSender:
    """Вспомогательный класс для отправки через Resend API (для иностранных почт)"""

    def __init__(self, settings: EmailSettings):
        resend.api_key = settings.resend_api_key
        self.from_email = settings.from_email
        self.from_name = settings.from_name
        self.logger = structlog.get_logger(__name__)

    async def send(
        self,
        to: str | List[str],
        subject: str,
        plain_text: str,
        html: Optional[str] = None,
    ) -> None:
        """Отправка через Resend API"""
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
            self.logger.info("Email sent via Resend", email_id=resp.get('id', '—'))
        except Exception as e:
            self.logger.error("Resend email send failed", error=str(e))
            raise

class UnisenderGoEmailSender:
    """Вспомогательный класс для отправки через Unisender Go Web API (для RU почт)"""

    def __init__(self, settings: EmailSettings):
        self.api_key = settings.unisender_api_key
        self.from_email = settings.from_email
        self.from_name = settings.from_name
        self.base_url = 'https://goapi.unisender.ru/ru/transactional/api/v1'
        self.logger = structlog.get_logger(__name__)

    async def send(
        self,
        to: str | List[str],
        subject: str,
        plain_text: str,
        html: Optional[str] = None,
    ) -> None:
        """Отправка через Unisender Go Web API"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-KEY": self.api_key
        }

        # Приводим получателей к формату Unisender JSON
        recipients_list = [{"email": email} for email in (to if isinstance(to, list) else [to])]

        request_body = {
            "message": {
                "recipients": recipients_list,
                "body": {
                    "plaintext": plain_text
                },
                "subject": subject,
                "from_email": self.from_email,
                "from_name": self.from_name,
                "track_links": 0,
                "track_read": 0
            }
        }

        if html:
            request_body["message"]["body"]["html"] = html

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.base_url+'/email/send.json', json=request_body, headers=headers)
                response.raise_for_status()
                
                resp_data = response.json()
                self.logger.info("Email sent via Unisender Go", job_id=resp_data.get("job_id", "—"))
        except httpx.HTTPStatusError as exc:
            self.logger.error(
                "Unisender Go API error", 
                status_code=exc.response.status_code, 
                response=exc.response.text
            )
            raise
        except Exception as e:
            self.logger.error("Unisender Go email send failed", error=str(e))
            raise

class SmtpEmailSender:
    """Вспомогательный класс для отправки через SMTP (для RU почт)"""

    def __init__(self, settings: EmailSettings):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_login = settings.smtp_login
        self.smtp_password = settings.smtp_password
        self.from_email = settings.from_email
        self.from_name = settings.from_name
        self.logger = structlog.get_logger(__name__)

    async def send(
        self,
        to: str | List[str],
        subject: str,
        plain_text: str,
        html: Optional[str] = None,
    ) -> None:
        """Асинхронная отправка через SMTP Яндекса (Порт 465)"""
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{self.from_name} <{self.smtp_login}>"
        msg["To"] = to if isinstance(to, list) else to
        msg["Subject"] = subject
        msg.attach(MIMEText(plain_text, "plain"))

        if html:
            msg.attach(MIMEText(html, "html"))

        try:
            # Для порта 465 используем use_tls=True
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_login,
                password=self.smtp_password,
                start_tls=True,  
            )
            self.logger.info("Email sent via SMTP (Yandex)", subject=subject)
        except Exception as e:
            self.logger.error("SMTP email send failed", error=str(e))
            raise



class SmartEmailSender(AbstractEmailSender):
    """
    Умный отправщик email, который автоматически выбирает провайдера:
    - Resend для иностранных почт (gmail, yahoo, outlook и т.д.)
    - SMTP (Яндекс) для RU почт (mail.ru, yandex.ru, rambler и т.д.)
    """

    RU_ZONE_SUFFIXES = (
        ".ru",
        ".рф",
        ".su",
        "yandex.by",
        "yandex.kz",
        "yandex.ua",
    )

    # 2. Специфические зарубежные домены российских сервисов
    SPECIFIC_RU_DOMAINS = {
        "@yandex.com",
        "@vk.com",
    }

    def __init__(self, settings: EmailSettings):
        self.settings = settings
        self.resend_sender = ResendEmailSender(settings)
        self.smtp_sender = SmtpEmailSender(settings)
        self.dev = settings.dev
        self.logger = structlog.get_logger(__name__)

    @classmethod
    def _is_ru_email(cls, email: str) -> bool:
        """Проверяет, является ли email российским.

        Сначала проверяет массовые зоны (.ru, .рф), затем специфические домены.
        """
        email_lower = email.lower()

        # Шаг 1: Быстрая проверка по национальным доменным зонам
        if email_lower.endswith(cls.RU_ZONE_SUFFIXES):
            return True

        # Шаг 2: Проверка специфических доменов (yandex.com, vk.com)
        return any(
            email_lower.endswith(domain) for domain in cls.SPECIFIC_RU_DOMAINS
        )

    async def _send_email(
        self,
        to: str | List[str],
        subject: str,
        plain_text: str,
        html: Optional[str] = None,
    ) -> None:
        """Выбирает провайдера в зависимости от email"""
        target_email = to[0] if isinstance(to, list) else to

        if self._is_ru_email(target_email):
            await self.smtp_sender.send(
                to=to,
                subject=subject,
                plain_text=plain_text,
                html=html,
            )
        else:
            await self.resend_sender.send(
                to=to,
                subject=subject,
                plain_text=plain_text,
                html=html,
            )

    async def send(
        self,
        to: str | List[str],
        subject: str,
        plain_text: str,
        html: Optional[str] = None,
        *,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        """Основной метод отправки"""
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

        self.logger.info("Email sent", email=to)

    async def send_register_verification_code(
        self,
        email: str,
        code: str,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        """Отправка кода верификации при регистрации"""
        if self.dev:
            self.logger.info(f"Код верификации email: {code}")
            return

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

    async def send_fogot_password_verification_code(
        self,
        email: str,
        code: str,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        """Отправка кода подтверждения сброса пароля"""
        if self.dev:
            self.logger.info(f"Код сброса пароля: {code}")
            return

        subject = "FlashMind — сброс пароля"
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
    <h1 style="margin-bottom: 8px;">FlashMind — сброс пароля</h1>
    <p style="font-size: 16px; line-height: 1.5;">
        Ваш код для подтверждения для сброса пароля:
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
        Если вы не запрашивали сброс пароля — просто проигнорируйте это письмо.
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

# class ResendEmailSender(AbstractEmailSender):
#     """
#     Отправка email через Resend.com

#     • Один экземпляр на приложение (Scope.APP)
#     • BackgroundTasks передаётся только при необходимости
#     • Работает и внутри HTTP-запроса, и вне его (тесты, CLI, workers)
#     """

#     def __init__(self, settings: EmailSettings):
#         resend.api_key = settings.resend_api_key
#         self.from_email = settings.from_email
#         self.from_name = settings.from_name
#         self.dev = settings.dev
#         self.logger = structlog.get_logger(__name__)

#     async def _send_email(
#         self,
#         to: str | List[str],
#         subject: str,
#         plain_text: str,
#         html: Optional[str] = None,
#     ) -> None:
#         """Низкоуровневая отправка одного письма"""
#         params = {
#             "from": f"{self.from_name} <{self.from_email}>",
#             "to": to if isinstance(to, list) else [to],
#             "subject": subject,
#             "text": plain_text,
#         }

#         if html:
#             params["html"] = html

#         try:
#             resp = resend.Emails.send(params)
#             # В продакшене здесь logger.info(...)
#             print(f"Email sent → ID: {resp.get('id', '—')}")
#         except Exception as e:
#             # В продакшене: logger.error + Sentry/capture_exception
#             print(f"Email send failed: {e}")
#             raise

#     async def send(
#         self,
#         to: str | List[str],
#         subject: str,
#         plain_text: str,
#         html: Optional[str] = None,
#         *,
#         background_tasks: Optional[BackgroundTasks] = None,
#     ) -> None:
#         """
#         Основной публичный метод отправки.

#         Args:
#             background_tasks: если передан → отправка в фоне
#                               если None → синхронная отправка
#         """

#         async def _task():
#             await self._send_email(
#                 to=to,
#                 subject=subject,
#                 plain_text=plain_text,
#                 html=html,
#             )

#         if background_tasks is not None:
#             background_tasks.add_task(_task)
#         else:
#             await _task()
        
        

#         self.logger.info("Код отправлен на email", email=to)

#     async def send_register_verification_code(
#         self,
#         email: str,
#         code: str,
#         background_tasks: Optional[BackgroundTasks] = None,
#     ) -> None:
#         """Отправка кода верификации при регистрации на email
#         если settings.dev = True то отправляет в консоль"""

#         if self.dev:  # не отправляет на email и выводит код в консоль
#             self.logger.info(f"Код верификации email: {code}")
#             return None
#         self.logger.info(f"Код верификации email: {code}")

#         subject = "FlashMind — подтвердите email"
#         plain_text = (
#             f"Ваш код подтверждения: {code}\n\n"
#             "Код действителен 10 минут.\n"
#             "Если это не вы — просто проигнорируйте письмо."
#         )

#         html = f"""<!DOCTYPE html>
# <html>
# <head>
#     <meta charset="utf-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
# </head>
# <body style="font-family: system-ui, sans-serif; max-width: 560px; margin: 40px auto; color: #111;">
#     <h1 style="margin-bottom: 8px;">Добро пожаловать в FlashMind!</h1>
#     <p style="font-size: 16px; line-height: 1.5;">
#         Ваш код для подтверждения email:
#     </p>
#     <div style="
#         font-size: 32px;
#         font-weight: bold;
#         letter-spacing: 12px;
#         text-align: center;
#         background: #f8f9fa;
#         padding: 24px;
#         border-radius: 12px;
#         margin: 24px 0;
#     ">
#         {code}
#     </div>
#     <p style="color: #555; font-size: 14px;">
#         Код действителен <strong>10 минут</strong>.<br>
#         Если вы не регистрировались — просто проигнорируйте это письмо.
#     </p>
# </body>
# </html>"""

#         await self.send(
#             to=email,
#             subject=subject,
#             plain_text=plain_text,
#             html=html,
#             background_tasks=background_tasks,
#         )

#     async def send_fogot_password_verification_code(
#         self,
#         email: str,
#         code: str,
#         background_tasks: Optional[BackgroundTasks] = None,
#     ) -> None:
#         """Отправка кода подтверждения сброса пароля на email
#         если settings.dev = True то отправляет в консоль"""

#         if self.dev:  # не отправляет на email и выводит код в консоль
#             self.logger.info(f"Код сброса пароля: {code}")
#             return None
        
#         self.logger.info(f"Код сброса пароля: {code}")

#         subject = "FlashMind — сброс пароля"
#         plain_text = (
#             f"Ваш код подтверждения: {code}\n\n"
#             "Код действителен 10 минут.\n"
#             "Если это не вы — просто проигнорируйте письмо."
#         )

#         html = f"""<!DOCTYPE html>
# <html>
# <head>
#     <meta charset="utf-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
# </head>
# <body style="font-family: system-ui, sans-serif; max-width: 560px; margin: 40px auto; color: #111;">
#     <h1 style="margin-bottom: 8px;">Добро пожаловать в FlashMind!</h1>
#     <p style="font-size: 16px; line-height: 1.5;">
#         Ваш код для подтверждения для сброса пароля:
#     </p>
#     <div style="
#         font-size: 32px;
#         font-weight: bold;
#         letter-spacing: 12px;
#         text-align: center;
#         background: #f8f9fa;
#         padding: 24px;
#         border-radius: 12px;
#         margin: 24px 0;
#     ">
#         {code}
#     </div>
#     <p style="color: #555; font-size: 14px;">
#         Код действителен <strong>10 минут</strong>.<br>
#         Если вы не запрашивали сброс пароля — просто проигнорируйте это письмо.
#     </p>
# </body>
# </html>"""

#         await self.send(
#             to=email,
#             subject=subject,
#             plain_text=plain_text,
#             html=html,
#             background_tasks=background_tasks,
#         )
