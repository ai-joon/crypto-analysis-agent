"""Application settings management."""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings."""

    openai_api_key: str
    openai_model: str = "gpt-4"
    cache_ttl: int = 300
    request_timeout: int = 10
    verbose: bool = True

    @classmethod
    def from_env(cls) -> "Settings":
        """
        Create settings from environment variables.

        Returns:
            Settings instance

        Raises:
            ValueError: If required environment variables are missing
        """
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        return cls(
            openai_api_key=openai_api_key,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4"),
            cache_ttl=int(os.getenv("CACHE_TTL", "300")),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "10")),
            verbose=os.getenv("VERBOSE", "true").lower() == "true",
        )


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get application settings (singleton pattern).

    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings

