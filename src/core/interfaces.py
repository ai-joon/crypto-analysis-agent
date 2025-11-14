"""Base classes and interfaces for the application."""

from abc import ABC, abstractmethod


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
