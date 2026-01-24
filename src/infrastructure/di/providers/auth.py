from dishka import Provider, Scope, provide
from src.application.interfaces import AbstractAuthenticationService
from src.secure.authentication_service import AuthenticationService


class AuthProvider(Provider):
    authentitication = provide(
        AuthenticationService,
        provides=AbstractAuthenticationService,
        scope=Scope.APP,
    )
