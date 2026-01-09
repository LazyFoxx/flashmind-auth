from dishka import FromDishka, Provider, Scope, provide
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

    # Отдельные примитивы
    # rate limit
    @provide(scope=Scope.APP)
    def register_email_window_seconds(self, rl: RateLimitConfig = FromDishka()) -> int:
        return rl.register_email_window_seconds

    @provide(scope=Scope.APP)
    def login_email_limit(self, rl: RateLimitConfig = FromDishka()) -> int:
        return rl.login_email_limit

    @provide(scope=Scope.APP)
    def login_email_window_seconds(self, rl: RateLimitConfig = FromDishka()) -> int:
        return rl.login_email_window_seconds

    @provide(scope=Scope.APP)
    def resend_code_cooldown_seconds(self, rl: RateLimitConfig = FromDishka()) -> int:
        return rl.resend_code_cooldown_seconds

    # verification code

    @provide(scope=Scope.APP)
    def verification_code_max_attempts(
        self, vc: VerificationCodeConfig = FromDishka()
    ) -> int:
        return vc.max_attempts

    @provide(scope=Scope.APP)
    def verification_code_ttl_seconds(
        self, vc: VerificationCodeConfig = FromDishka()
    ) -> int:
        return vc.ttl_seconds
