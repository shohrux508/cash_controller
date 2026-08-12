from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "backend-template"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./dev.db"
    log_level: str = "INFO"
    log_format: str = "text"  # "json" | "text"
    cors_origins: list[str] = ["*"]


settings = Settings()
