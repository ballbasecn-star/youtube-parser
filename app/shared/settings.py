"""Application settings using Pydantic Settings.

Configuration can be set via environment variables.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="YOUTUBE_PARSER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # App info
    app_name: str = "youtube-parser"
    app_version: str = "0.1.0"

    # HTTP client settings
    http_timeout: float = 30.0
    http_connect_timeout: float = 10.0

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "console"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings instance
    """
    return Settings()