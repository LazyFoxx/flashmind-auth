from dishka import Provider, Scope, provide
from src.application.interfaces import AbstractEmailSender
from src.infrastructure.services.email_sender import SmartEmailSender


class EmailProvider(Provider):
    email_sender = provide(
        SmartEmailSender,
        provides=AbstractEmailSender,
        scope=Scope.APP,
    )
