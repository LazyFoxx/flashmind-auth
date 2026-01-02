from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 10
    max_overflow: int = 10

    user: str
    password: str
    db: str
    host: str
    port: int

    @property
    def url(self) -> PostgresDsn:
        """Собранный URL с валидацией"""
        url_str = f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"
        return PostgresDsn(url_str)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
    )

    db: DatabaseConfig


settings = Settings()
