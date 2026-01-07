from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import RedisDsn, SecretStr


class RedisSettings(BaseSettings):
    host: str
    port: int
    db: str
    password: SecretStr
    max_connections: int

    model_config = SettingsConfigDict(
        env_prefix="REDIS_", case_sensitive=False, extra="ignore"
    )

    def build_dsn(self) -> RedisDsn:
        password = f"{self.password.get_secret_value()}"
        return RedisDsn(f"redis://:{password}@{self.host}:{self.port}/{self.db}")
