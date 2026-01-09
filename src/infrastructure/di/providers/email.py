from dishka import Provider, Scope, provide
from src.application.interfaces import AbstractEmailSender
from src.infrastructure.services.email_sender import ResendEmailSender


class EmailProvider(Provider):
    email_sender = provide(
        ResendEmailSender,
        provides=AbstractEmailSender,
        scope=Scope.APP,
    )
