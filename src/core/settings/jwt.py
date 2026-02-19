from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class JwtSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="JWT_", case_sensitive=False, extra="ignore"
    )

    # Универсальный путь — работает в обоих режимах Docker (с file: и с external:)
    private_key_path: Path = Path("/run/secrets/jwt_private_key")
    public_key_path: Path = Path("/run/secrets/jwt_public_key")

    key_id: str
    issuer: str
    access_expire_minutes: int
    refresh_expire_days: int


settings = JwtSettings()
