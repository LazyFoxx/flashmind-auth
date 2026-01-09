from dishka import Provider, Scope, provide
from application.interfaces import AbstractHasher
from infrastructure.services.secure.hasher_impl import PasslibHasher


class Hasherrovider(Provider):
    hasher = provide(
        PasslibHasher,
        provides=AbstractHasher,
        scope=Scope.APP,
    )
