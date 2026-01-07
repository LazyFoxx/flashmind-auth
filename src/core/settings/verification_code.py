from pydantic_settings import BaseSettings, SettingsConfigDict


class VerificationCodeConfig(BaseSettings):
    max_attempts: int
    ttl_seconds: int

    model_config = SettingsConfigDict(
        env_prefix="EMAIL_CODE__", case_sensitive=False, extra="ignore"
    )
