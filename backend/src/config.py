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

    # CORS Configuration (comma-separated string in .env, converted to list)
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Optional: Anthropic API (alternative to OpenAI)
    ANTHROPIC_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    def __init__(self, **kwargs):
        """Initialize settings and parse CORS_ORIGINS from string."""
        super().__init__(**kwargs)
        # Convert CORS_ORIGINS string to list
        if isinstance(self.CORS_ORIGINS, str):
            # Handle empty string
            if not self.CORS_ORIGINS.strip():
                self.CORS_ORIGINS = "http://localhost:5173,http://localhost:3000"
            # Split comma-separated string into list
            self._cors_origins_list = [
                origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()
            ]
        else:
            self._cors_origins_list = list(self.CORS_ORIGINS) if self.CORS_ORIGINS else []
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return self._cors_origins_list


# Global settings instance
settings = Settings()
