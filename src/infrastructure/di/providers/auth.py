from dishka import Provider, Scope, provide
from application.interfaces import AbstractAuthenticationService
from infrastructure.services.authentication_service import AuthenticationService


class AuthProvider(Provider):
    authentitication = provide(
        AuthenticationService,
        provides=AbstractAuthenticationService,
        scope=Scope.APP,
    )
