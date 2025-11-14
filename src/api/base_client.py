"""Base API client with common functionality."""

import time
import requests
from typing import Dict, Any, Optional
from abc import ABC

from src.core.exceptions import APIError
from src.core.logging_config import get_logger
from src.core.progress import get_progress_logger
from src.config.constants import DEFAULT_TIMEOUT

logger = get_logger(__name__)
progress = get_progress_logger()


class BaseAPIClient(ABC):
    """Base class for API clients with common request handling."""

    def __init__(
        self,
        base_url: str,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = 2,
        service_name: Optional[str] = None,
    ):
        """
        Initialize API client.

        Args:
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for rate-limited requests (default: 2)
            service_name: Optional service name for progress messages
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.service_name = service_name or self._extract_service_name(base_url)
        self._last_endpoint = None

    def _extract_service_name(self, url: str) -> str:
        """Extract service name from URL."""
        try:
            # Extract domain name and capitalize
            domain = url.split("//")[-1].split("/")[0]
            # Get the main domain (e.g., api.coingecko.com -> coingecko)
            parts = domain.split(".")
            if len(parts) >= 2:
                return parts[-2].title()
            return parts[0].title()
        except Exception:
            return "API"

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a GET request to the API with retry logic for rate limits.

        Args:
            endpoint: API endpoint (relative to base_url)
            params: Query parameters

        Returns:
            Response data as dictionary

        Raises:
            APIError: If the request fails after all retries
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Show progress only on first attempt for this endpoint
        if self._last_endpoint is None or self._last_endpoint != endpoint:
            progress.api_call(self.service_name)
            self._last_endpoint = endpoint

        for attempt in range(self.max_retries + 1):
            try:
                response = requests.get(url, params=params, timeout=self.timeout)

                # Handle rate limiting (429) with retry
                if response.status_code == 429:
                    if attempt < self.max_retries:
                        # Calculate backoff: exponential with cap (1s, 2s, 4s, max 10s)
                        backoff_time = min(2**attempt, 10)
                        retry_after = response.headers.get("Retry-After")
                        if retry_after:
                            try:
                                # Cap Retry-After to reasonable limit (max 10 seconds)
                                retry_after_seconds = int(retry_after)
                                backoff_time = min(retry_after_seconds, 10)
                            except (ValueError, TypeError):
                                pass

                        progress.warning(
                            f"Rate limit hit. Retrying in {backoff_time}s (attempt {attempt + 1}/{self.max_retries})..."
                        )
                        time.sleep(backoff_time)
                        continue
                    else:
                        # Max retries reached - fail fast instead of waiting
                        raise APIError(
                            f"Rate limit exceeded for {url}. "
                            f"Please wait a few minutes before trying again. "
                            f"CoinGecko free tier allows ~50 calls/minute.",
                            status_code=429,
                            endpoint=endpoint,
                        )

                response.raise_for_status()
                data = response.json()
                # Show success only on first successful attempt
                if attempt == 0:
                    progress.success(
                        f"Successfully received data from {self.service_name}"
                    )
                return data

            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    # Short backoff for timeouts (1-2 seconds)
                    backoff = min(attempt + 1, 2)
                    progress.warning(f"Request timeout. Retrying in {backoff}s...")
                    time.sleep(backoff)
                    continue
                raise APIError(
                    f"Request to {url} timed out after {self.timeout}s",
                    endpoint=endpoint,
                )
            except requests.exceptions.HTTPError as e:
                # Don't retry for non-429 errors
                status_code = (
                    response.status_code if hasattr(response, "status_code") else None
                )
                raise APIError(
                    f"HTTP error {status_code} from {url}: {str(e)}",
                    status_code=status_code,
                    endpoint=endpoint,
                )
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries:
                    progress.warning("Request failed. Retrying...")
                    time.sleep(1)
                    continue
                raise APIError(
                    f"Request to {url} failed: {str(e)}",
                    endpoint=endpoint,
                )

        # Should never reach here, but just in case
        raise APIError(f"Request to {url} failed after {self.max_retries} retries")
