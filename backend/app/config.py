"""Application configuration using Pydantic settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application settings
    app_name: str = "tdd-claude-dev-container"
    debug: bool = False

    # Database settings
    database_url: str = "sqlite+aiosqlite:///./data/app.db"

    # Docker settings
    docker_socket: str = "unix:///var/run/docker.sock"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000


# Global settings instance
settings = Settings()
