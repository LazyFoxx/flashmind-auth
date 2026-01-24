from pydantic_settings import BaseSettings, SettingsConfigDict


class RateLimitConfig(BaseSettings):
    # Регистрация по email
    register_limit: int
    register_window_seconds: int

    # Логин
    login_limit: int
    login_window_seconds: int

    # Сброс пароля
    reset_pass_limit: int
    reset_pass_window_seconds: int

    # Resend verification code
    resend_code_cooldown_seconds: int

    model_config = SettingsConfigDict(
        env_prefix="RATE_LIMIT__", case_sensitive=False, extra="ignore"
    )
