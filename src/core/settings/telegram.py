from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False, extra="ignore", env_prefix="TELEGRAM_"
    )
    
    client_id: str
    client_server: str
    jwks_url: str