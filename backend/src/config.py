"""
Environment configuration management using Pydantic Settings.

This module loads configuration from environment variables with validation.
"""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM provider: "groq" (cloud, TPM limits) or "ollama" (local, no truncation)
    LLM_PROVIDER: str = "groq"
    # Ollama (local; no API key, no TPM limit; full PRD context)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    # Groq (cloud; API key required; on_demand TPM 6000)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"  # Faster; use llama-3.3-70b-versatile for quality

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # CORS Configuration (comma-separated string in .env, converted to list)
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # LLM output cap (suggestions 1 & 4: lower = faster)
    LLM_MAX_TOKENS: int = 2000

    # LLM timeout: per-call max seconds for Groq API (keep under MAX_ANALYSIS_TIMEOUT_SEC)
    LLM_TIMEOUT_SEC: int = 45

    # Max wall-clock for entire analysis (executor + stream); used by task_processor and stream endpoint
    MAX_ANALYSIS_TIMEOUT_SEC: int = 120

    # Stage 1 structure extraction: max chars per section before sub-chunking
    MAX_SECTION_CHARS: int = 4000

    # Scoring: "rules" (default), "llm", or "hybrid" (blend rule-based + LLM)
    SCORING_MODE: str = "rules"

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
