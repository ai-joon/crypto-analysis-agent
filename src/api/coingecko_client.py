"""CoinGecko API client."""

from typing import Dict, Any, List

from src.api.base_client import BaseAPIClient
from src.config.constants import COINGECKO_BASE_URL, COIN_SYMBOL_MAPPINGS
from src.core.exceptions import CoinNotFoundError
from src.core.progress import get_progress_logger

progress = get_progress_logger()


class CoinGeckoClient(BaseAPIClient):
    """Client for CoinGecko API."""

    def __init__(self):
        """Initialize CoinGecko client."""
        super().__init__(COINGECKO_BASE_URL, service_name="CoinGecko")

    def get_coin_id(self, query: str) -> str:
        """
        Convert a coin name or symbol to CoinGecko coin ID.

        Args:
            query: Coin name or symbol

        Returns:
            CoinGecko coin ID

        Raises:
            CoinNotFoundError: If coin cannot be found
        """
        query = query.lower().strip()
        progress.info(f"Looking up coin: {query}")

        # Check common mappings first
        if query in COIN_SYMBOL_MAPPINGS:
            coin_id = COIN_SYMBOL_MAPPINGS[query]
            progress.success(f"Found coin ID: {coin_id}")
            return coin_id

        # Search in coin list
        try:
            coins = self.get_coin_list()
            for coin in coins:
                if (
                    coin["id"] == query
                    or coin["symbol"].lower() == query
                    or coin["name"].lower() == query
                ):
                    progress.success(f"Found coin ID: {coin['id']}")
                    return coin["id"]
        except Exception:
            pass

        raise CoinNotFoundError(query)

    def get_coin_list(self) -> List[Dict[str, Any]]:
        """
        Get list of all available coins.

        Returns:
            List of coin dictionaries
        """
        return self.get("coins/list")

    def get_coin_data(self, coin_id: str) -> Dict[str, Any]:
        """
        Get detailed coin data.

        Args:
            coin_id: CoinGecko coin ID

        Returns:
            Coin data dictionary
        """
        return self.get(
            f"coins/{coin_id}",
            params={
                "localization": "false",
                "tickers": "false",
                "community_data": "true",
                "developer_data": "false",
                "sparkline": "false",
            },
        )

    def get_market_chart(
        self, coin_id: str, days: int = 30, vs_currency: str = "usd"
    ) -> Dict[str, Any]:
        """
        Get historical market data.

        Args:
            coin_id: CoinGecko coin ID
            days: Number of days of historical data
            vs_currency: Target currency (default: usd)

        Returns:
            Market chart data
        """
        return self.get(
            f"coins/{coin_id}/market_chart",
            params={
                "vs_currency": vs_currency,
                "days": days,
                "interval": "daily" if days > 1 else "hourly",
            },
        )
