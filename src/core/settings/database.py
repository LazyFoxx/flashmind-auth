# src/core/settings/database.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, SecretStr


class DatabaseSettings(BaseSettings):
    host: str
    port: int
    user: str
    password: SecretStr
    db: str

    pool_size: int
    max_overflow: int

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_", case_sensitive=False, extra="ignore"
    )

    def build_dsn(self) -> PostgresDsn:
        """
        Собирает и валидирует DSN с помощью Pydantic PostgresDsn.
        Гарантирует корректность URL на этапе старта приложения.
        """
        dsn = PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.user,
            password=self.password.get_secret_value(),  # получаем str из SecretStr
            host=self.host,
            port=self.port,
            path=f"/{self.db}",
        )

        return dsn
