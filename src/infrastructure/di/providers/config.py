from dishka import FromDishka, Provider, Scope, provide
from src.core.settings import (
    VerificationCodeConfig,
    RateLimitConfig,
    DatabaseSettings,
    RedisSettings,
    JwtSettings,
    EmailSettings,
    RabbitSettings,
)
from authlib.jose import JsonWebKey


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
    def jwt_settings(self) -> JwtSettings:
        return JwtSettings()

    @provide(scope=Scope.APP)
    def email_settings(self) -> EmailSettings:
        return EmailSettings()

    @provide(scope=Scope.APP)
    def provide_public_key(self, settings: FromDishka[JwtSettings]) -> JsonWebKey:
        with open(settings.public_key_path) as f:
            return JsonWebKey.import_key(f.read(), {"kty": "RSA"})

    @provide(scope=Scope.APP)
    def rabbit_settings(self) -> RabbitSettings:
        return RabbitSettings()
