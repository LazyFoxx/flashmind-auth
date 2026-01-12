from pydantic_settings import BaseSettings, SettingsConfigDict


class EmailSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False, extra="ignore", env_prefix="EMAIL_"
    )

    from_email: str
    from_name: str
    resend_api_key: str
    dev: bool
