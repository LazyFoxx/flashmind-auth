# src/infrastructure/di/providers/config.py
from dishka import Provider, Scope, provide
from src.core.settings import (
    VerificationCodeConfig,
    RateLimitConfig,
)


class ConfigProvider(Provider):
    scope = Scope.APP

    # Целые объекты настроек
    verification_code = provide(VerificationCodeConfig)
    rate_limit = provide(RateLimitConfig)

    # Отдельные примитивы
    # rate limit
    register_email_limit = provide(
        lambda s: s.rate_limit.register_email_limit, provides=str
    )
    register_email_window_seconds = provide(
        lambda s: s.rate_limit.register_email_window_seconds, provides=str
    )
    login_email_limit = provide(lambda s: s.rate_limit.login_email_limit, provides=str)
    login_email_window_seconds = provide(
        lambda s: s.rate_limit.login_email_window_seconds, provides=str
    )
    resend_code_cooldown_seconds = provide(
        lambda s: s.rate_limit.resend_code_cooldown_seconds, provides=str
    )

    # verification code
    max_attempts = provide(lambda s: s.verification_code.max_attempts, provides=str)
    ttl_seconds = provide(lambda s: s.verification_code.ttl_seconds, provides=str)
