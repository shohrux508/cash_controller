from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "cash-controller"
    debug: bool = False

    # Database
    database_url: str = "sqlite+aiosqlite:///./dev.db"

    # Logging
    log_level: str = "INFO"
    log_format: str = "text"  # "json" | "text"

    # CORS
    cors_origins: list[str] = ["*"]

    # Telegram Bot
    bot_token: str = ""
    admin_chat_ids: list[int] = []


settings = Settings()
