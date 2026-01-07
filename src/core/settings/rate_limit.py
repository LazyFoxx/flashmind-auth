from pydantic_settings import BaseSettings, SettingsConfigDict


class RateLimitConfig(BaseSettings):
    # Регистрация по email
    register_email_limit: int
    register_email_window_seconds: int

    # Логин
    login_email_limit: int
    login_email_window_seconds: int

    # Resend verification code
    resend_code_cooldown_seconds: int

    model_config = SettingsConfigDict(
        env_prefix="RATE_LIMIT__", case_sensitive=False, extra="ignore"
    )
