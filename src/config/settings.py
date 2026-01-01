from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 10
    max_overflow: int = 10


class Settings(BaseSettings):
    db: DatabaseConfig


settings = Settings()
