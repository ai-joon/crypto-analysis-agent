"""Service for coin-related operations."""

from typing import Dict, Any

from src.repositories.coin_repository import CoinRepository


class CoinService:
    """Service for cryptocurrency operations."""

    def __init__(self, coin_repository: CoinRepository):
        """
        Initialize coin service.

        Args:
            coin_repository: Coin repository instance
        """
        self.repository = coin_repository

    def get_coin_info(self, query: str) -> Dict[str, Any]:
        """
        Get basic information about a cryptocurrency.

        Args:
            query: Cryptocurrency name or symbol

        Returns:
            Dictionary with coin information

        Raises:
            CoinNotFoundError: If coin cannot be found
        """
        coin_id = self.repository.get_coin_id(query)
        data = self.repository.get_coin_data(coin_id)

        return {
            "coin_id": coin_id,
            "name": data.get("name", query),
            "symbol": data.get("symbol", "").upper(),
        }

    def get_coin_price(self, query: str) -> Dict[str, Any]:
        """
        Get current price and basic market data for a cryptocurrency.

        Args:
            query: Cryptocurrency name or symbol

        Returns:
            Dictionary with price and market data

        Raises:
            CoinNotFoundError: If coin cannot be found
        """
        coin_id = self.repository.get_coin_id(query)
        market_data = self.repository.get_market_data(coin_id)
        coin_info = self.get_coin_info(query)

        return {
            **coin_info,
            **market_data,
        }
