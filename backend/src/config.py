"""
Environment configuration management using Pydantic Settings.

This module loads configuration from environment variables with validation.
"""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI API Configuration
    OPENAI_API_KEY: str = ""

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # Optional: Anthropic API (alternative to OpenAI)
    ANTHROPIC_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    def __init__(self, **kwargs):
        """Initialize settings and parse CORS_ORIGINS from string if needed."""
        super().__init__(**kwargs)
        # If CORS_ORIGINS is a string (from env), split it
        if isinstance(self.CORS_ORIGINS, str):
            self.CORS_ORIGINS = [
                origin.strip() for origin in self.CORS_ORIGINS.split(",")
            ]


# Global settings instance
settings = Settings()
