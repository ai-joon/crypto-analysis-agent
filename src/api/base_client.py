"""Base API client with common functionality."""

import time
import requests
from typing import Dict, Any, Optional
from abc import ABC

from src.core.exceptions import APIError
from src.core.logging_config import get_logger
from src.config.constants import DEFAULT_TIMEOUT

logger = get_logger(__name__)


class BaseAPIClient(ABC):
    """Base class for API clients with common request handling."""

    def __init__(self, base_url: str, timeout: int = DEFAULT_TIMEOUT, max_retries: int = 2):
        """
        Initialize API client.

        Args:
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for rate-limited requests (default: 2)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

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
        
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                
                # Handle rate limiting (429) with retry
                if response.status_code == 429:
                    if attempt < self.max_retries:
                        # Calculate backoff: exponential with cap (1s, 2s, 4s, max 10s)
                        backoff_time = min(2 ** attempt, 10)
                        retry_after = response.headers.get("Retry-After")
                        if retry_after:
                            try:
                                # Cap Retry-After to reasonable limit (max 10 seconds)
                                retry_after_seconds = int(retry_after)
                                backoff_time = min(retry_after_seconds, 10)
                            except (ValueError, TypeError):
                                pass
                        
                        logger.warning(
                            f"Rate limit hit (429) for {url}. "
                            f"Retrying in {backoff_time}s (attempt {attempt + 1}/{self.max_retries})"
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
                return response.json()
                
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    # Short backoff for timeouts (1-2 seconds)
                    backoff = min(attempt + 1, 2)
                    logger.warning(
                        f"Request timeout for {url}. Retrying in {backoff}s..."
                    )
                    time.sleep(backoff)
                    continue
                raise APIError(
                    f"Request to {url} timed out after {self.timeout}s",
                    endpoint=endpoint,
                )
            except requests.exceptions.HTTPError as e:
                # Don't retry for non-429 errors
                status_code = response.status_code if hasattr(response, 'status_code') else None
                raise APIError(
                    f"HTTP error {status_code} from {url}: {str(e)}",
                    status_code=status_code,
                    endpoint=endpoint,
                )
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries:
                    logger.warning(f"Request failed for {url}. Retrying...")
                    time.sleep(1)
                    continue
                raise APIError(
                    f"Request to {url} failed: {str(e)}",
                    endpoint=endpoint,
                )
        
        # Should never reach here, but just in case
        raise APIError(f"Request to {url} failed after {self.max_retries} retries")
