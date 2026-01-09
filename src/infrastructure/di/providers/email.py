from dishka import Provider, Scope, provide
from application.interfaces import AbstractEmailSender
from infrastructure.services.email_sender import ResendEmailSender


class EmailProvider(Provider):
    email_sender = provide(
        ResendEmailSender,
        provides=AbstractEmailSender,
        scope=Scope.APP,
    )
