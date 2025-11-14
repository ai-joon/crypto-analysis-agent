"""Base API client with common functionality."""

import requests
from typing import Dict, Any, Optional
from abc import ABC

from src.core.exceptions import APIError
from src.config.constants import DEFAULT_TIMEOUT


class BaseAPIClient(ABC):
    """Base class for API clients with common request handling."""

    def __init__(self, base_url: str, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize API client.

        Args:
            base_url: Base URL for the API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a GET request to the API.

        Args:
            endpoint: API endpoint (relative to base_url)
            params: Query parameters

        Returns:
            Response data as dictionary

        Raises:
            APIError: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise APIError(f"Request to {url} timed out after {self.timeout}s")
        except requests.exceptions.HTTPError as e:
            raise APIError(
                f"HTTP error {response.status_code} from {url}: {str(e)}",
                status_code=response.status_code,
            )
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request to {url} failed: {str(e)}")

