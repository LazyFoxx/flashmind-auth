from pydantic import BaseModel, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisConfig(BaseModel):
    url: RedisDsn
    max_connections: int


class VerificationCodeConfig(BaseModel):
    max_attempts: int
    ttl_seconds: int


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 10
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "pk": "pk_%(table_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
    }


class RateLimitConfig(BaseModel):
    # Регистрация по email
    register_email_limit: int
    register_email_window_seconds: int

    # Логин
    login_email_limit: int
    login_email_window_seconds: int

    # Resend verification code
    resend_code_cooldown_seconds: int


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.dev",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        extra="ignore",
    )

    db: DatabaseConfig
    rl: RateLimitConfig
    redis: RedisConfig
    email_code: VerificationCodeConfig


settings = Settings()
