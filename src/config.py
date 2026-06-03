"""Application configuration."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    app_name: str = Field(default="Code Repository Q&A Agent", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    embedding_model: str = Field(
        default="text-embedding-3-large", alias="EMBEDDING_MODEL"
    )
    chat_model: str = Field(default="gpt-4.1", alias="CHAT_MODEL")
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    postgres_dsn: str = Field(
        default="postgresql://repoqa:repoqa@localhost:5432/repoqa",
        alias="POSTGRES_DSN",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
