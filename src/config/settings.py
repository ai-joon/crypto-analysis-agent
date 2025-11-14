"""Application settings management."""

import os
from typing import Optional
from dataclasses import dataclass

from src.core.exceptions import ConfigurationError
from src.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class Settings:
    """Application settings with validation."""

    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    cache_ttl: int = 300
    request_timeout: int = 10
    verbose: bool = True
    newsapi_key: Optional[str] = None

    def __post_init__(self):
        """Validate settings after initialization."""
        self._validate()

    def _validate(self) -> None:
        """Validate all settings values."""
        if not self.openai_api_key or not self.openai_api_key.strip():
            raise ConfigurationError(
                "OPENAI_API_KEY is required and cannot be empty",
                config_key="OPENAI_API_KEY",
            )

        if not self.openai_api_key.startswith("sk-"):
            logger.warning(
                "OpenAI API key doesn't start with 'sk-'. Please verify it's correct."
            )

        valid_models = [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-3.5-turbo",
        ]
        if self.openai_model not in valid_models:
            logger.warning(
                f"Model '{self.openai_model}' may not be valid. "
                f"Valid models: {', '.join(valid_models)}"
            )

        if self.cache_ttl < 0:
            raise ConfigurationError(
                f"CACHE_TTL must be non-negative, got {self.cache_ttl}",
                config_key="CACHE_TTL",
            )

        if self.request_timeout <= 0:
            raise ConfigurationError(
                f"REQUEST_TIMEOUT must be positive, got {self.request_timeout}",
                config_key="REQUEST_TIMEOUT",
            )

    @classmethod
    def from_env(cls) -> "Settings":
        """
        Create settings from environment variables.

        Returns:
            Settings instance

        Raises:
            ConfigurationError: If required environment variables are missing or invalid
        """
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ConfigurationError(
                "OPENAI_API_KEY environment variable is required",
                config_key="OPENAI_API_KEY",
            )

        try:
            cache_ttl = int(os.getenv("CACHE_TTL", "300"))
        except ValueError as e:
            raise ConfigurationError(
                f"Invalid CACHE_TTL value: {os.getenv('CACHE_TTL')}",
                config_key="CACHE_TTL",
            ) from e

        try:
            request_timeout = int(os.getenv("REQUEST_TIMEOUT", "10"))
        except ValueError as e:
            raise ConfigurationError(
                f"Invalid REQUEST_TIMEOUT value: {os.getenv('REQUEST_TIMEOUT')}",
                config_key="REQUEST_TIMEOUT",
            ) from e

        verbose_str = os.getenv("VERBOSE", "true").lower()
        verbose = verbose_str in ("true", "1", "yes", "on")

        newsapi_key = os.getenv("NEWSAPI_KEY", "").strip()
        newsapi_key = newsapi_key if newsapi_key else None

        settings = cls(
            openai_api_key=openai_api_key.strip(),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip(),
            cache_ttl=cache_ttl,
            request_timeout=request_timeout,
            verbose=verbose,
            newsapi_key=newsapi_key,
        )

        logger.info(
            f"Settings loaded: model={settings.openai_model}, cache_ttl={settings.cache_ttl}s"
        )
        if newsapi_key:
            logger.info("NewsAPI key configured - news features enabled")
        else:
            logger.info("NewsAPI key not configured - news features disabled")
        return settings


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get application settings (singleton pattern).

    Returns:
        Settings instance

    Raises:
        ConfigurationError: If settings cannot be loaded
    """
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings
