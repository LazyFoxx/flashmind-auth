from dishka import Provider, Scope, provide
from src.core.settings import (
    VerificationCodeConfig,
    RateLimitConfig,
    DatabaseSettings,
    RedisSettings,
    JwtSettings,
    EmailSettings,
)


class ConfigProvider(Provider):
    # Целые объекты настроек
    @provide(scope=Scope.APP)
    def verification_code(self) -> VerificationCodeConfig:
        return VerificationCodeConfig()

    @provide(scope=Scope.APP)
    def rate_limit(self) -> RateLimitConfig:
        return RateLimitConfig()

    @provide(scope=Scope.APP)
    def db_settings(self) -> DatabaseSettings:
        return DatabaseSettings()

    @provide(scope=Scope.APP)
    def redis_settings(self) -> RedisSettings:
        return RedisSettings()

    @provide(scope=Scope.APP)
    def get_jwt_settings(self) -> JwtSettings:
        return JwtSettings()

    @provide(scope=Scope.APP)
    def email_settings(self) -> EmailSettings:
        return EmailSettings()
