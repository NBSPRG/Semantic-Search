from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/mini_ml",
        alias="DATABASE_URL",
    )
    model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        alias="MODEL_NAME",
    )
    embedding_timeout_seconds: float = Field(default=3.0, alias="EMBEDDING_TIMEOUT_SECONDS")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    storage_backend: str = Field(default="postgres", alias="STORAGE_BACKEND")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
