"""Base classes and interfaces for the application."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseAnalyzer(ABC):
    """Base class for all analysis modules."""

    @abstractmethod
    def analyze(self, coin_id: str, coin_name: str) -> str:
        """
        Perform analysis on a cryptocurrency.

        Args:
            coin_id: CoinGecko coin ID
            coin_name: Human-readable coin name

        Returns:
            Formatted analysis report
        """
        raise NotImplementedError


class BaseAPIClient(ABC):
    """Base class for API clients."""

    @abstractmethod
    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a GET request to the API.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response data as dictionary

        Raises:
            APIError: If the request fails
        """
        raise NotImplementedError
