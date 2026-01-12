from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class RedisSettings(BaseSettings):
    host: str
    port: int
    db: str
    password: SecretStr
    max_connections: int

    model_config = SettingsConfigDict(
        env_prefix="REDIS_", case_sensitive=False, extra="ignore"
    )

    def get_url(self) -> str:
        # password = f"{self.password.get_secret_value()}"
        # return f"redis://:{password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"
