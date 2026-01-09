# src/di/container.py
from dishka import make_async_container

from providers import (
    AuthProvider,
    ConfigProvider,
    DbProvider,
    EmailProvider,
    FastAPIProvider,
    Hasherrovider,
    JwtProvider,
    RateLimitProvider,
    RedisProvider,
    VerificationCodeProvider,
)

# Список всех провайдеров
_PROVIDERS = [
    AuthProvider(),
    ConfigProvider(),
    DbProvider(),
    EmailProvider(),
    FastAPIProvider(),
    Hasherrovider(),
    JwtProvider(),
    RateLimitProvider(),
    RedisProvider(),
    VerificationCodeProvider(),
]


def get_container():
    """
    Фабрика для создания Dishka контейнера.
    Вызывается только при старте приложения (в lifespan) или в тестах.
    """
    return make_async_container(*_PROVIDERS)
