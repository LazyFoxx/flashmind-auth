from dishka import Provider, Scope, provide
from src.application.interfaces import AbstractHasher
from src.secure.hasher_impl import PasslibHasher


class HasherProvider(Provider):
    hasher = provide(
        PasslibHasher,
        provides=AbstractHasher,
        scope=Scope.APP,
    )
