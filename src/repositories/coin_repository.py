"""Repository for cryptocurrency data access."""

from typing import Dict, Any, List
from datetime import datetime

from src.api.coingecko_client import CoinGeckoClient
from src.api.fear_greed_client import FearGreedClient
from src.core.cache import Cache
from src.config.constants import DEFAULT_CACHE_TTL


class CoinRepository:
    """Repository for accessing cryptocurrency data with caching."""

    def __init__(self, cache_ttl: int = DEFAULT_CACHE_TTL):
        """
        Initialize coin repository.

        Args:
            cache_ttl: Cache time-to-live in seconds
        """
        self.coingecko_client = CoinGeckoClient()
        self.fear_greed_client = FearGreedClient()
        self.cache = Cache(default_ttl=cache_ttl)

    def get_coin_id(self, query: str) -> str:
        """
        Get CoinGecko ID for a cryptocurrency.

        Args:
            query: Coin name or symbol

        Returns:
            CoinGecko coin ID

        Raises:
            CoinNotFoundError: If coin cannot be found
        """
        cache_key = f"coin_id_{query.lower()}"
        return self.cache.get_or_fetch(
            cache_key, lambda: self.coingecko_client.get_coin_id(query)
        )

    def get_coin_data(self, coin_id: str) -> Dict[str, Any]:
        """
        Get detailed coin data.

        Args:
            coin_id: CoinGecko coin ID

        Returns:
            Coin data dictionary
        """
        cache_key = f"coin_data_{coin_id}"
        return self.cache.get_or_fetch(
            cache_key, lambda: self.coingecko_client.get_coin_data(coin_id)
        )

    def get_market_data(self, coin_id: str) -> Dict[str, Any]:
        """
        Get market data for a coin.

        Args:
            coin_id: CoinGecko coin ID

        Returns:
            Market data dictionary
        """
        data = self.get_coin_data(coin_id)
        market_data = data.get("market_data", {})

        return {
            "current_price": market_data.get("current_price", {}).get("usd"),
            "market_cap": market_data.get("market_cap", {}).get("usd"),
            "market_cap_rank": market_data.get("market_cap_rank"),
            "total_volume": market_data.get("total_volume", {}).get("usd"),
            "high_24h": market_data.get("high_24h", {}).get("usd"),
            "low_24h": market_data.get("low_24h", {}).get("usd"),
            "price_change_24h": market_data.get("price_change_24h"),
            "price_change_percentage_24h": market_data.get("price_change_percentage_24h"),
            "price_change_percentage_7d": market_data.get("price_change_percentage_7d"),
            "price_change_percentage_30d": market_data.get("price_change_percentage_30d"),
            "circulating_supply": market_data.get("circulating_supply"),
            "total_supply": market_data.get("total_supply"),
            "max_supply": market_data.get("max_supply"),
            "ath": market_data.get("ath", {}).get("usd"),
            "atl": market_data.get("atl", {}).get("usd"),
            "ath_date": market_data.get("ath_date", {}).get("usd"),
            "atl_date": market_data.get("atl_date", {}).get("usd"),
        }

    def get_historical_prices(self, coin_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get historical price data.

        Args:
            coin_id: CoinGecko coin ID
            days: Number of days of historical data

        Returns:
            List of price data points
        """
        cache_key = f"historical_{coin_id}_{days}"

        def fetch():
            data = self.coingecko_client.get_market_chart(coin_id, days)
            prices = []
            for timestamp, price in data.get("prices", []):
                prices.append(
                    {
                        "timestamp": timestamp,
                        "date": datetime.fromtimestamp(timestamp / 1000),
                        "price": price,
                    }
                )
            return prices

        return self.cache.get_or_fetch(cache_key, fetch)

    def get_community_data(self, coin_id: str) -> Dict[str, Any]:
        """
        Get community and social media data.

        Args:
            coin_id: CoinGecko coin ID

        Returns:
            Community data dictionary
        """
        data = self.get_coin_data(coin_id)
        community_data = data.get("community_data", {})

        return {
            "twitter_followers": community_data.get("twitter_followers"),
            "reddit_subscribers": community_data.get("reddit_subscribers"),
            "reddit_average_posts_48h": community_data.get("reddit_average_posts_48h"),
            "reddit_average_comments_48h": community_data.get("reddit_average_comments_48h"),
            "telegram_channel_user_count": community_data.get("telegram_channel_user_count"),
        }

    def get_coin_description(self, coin_id: str) -> str:
        """
        Get coin description.

        Args:
            coin_id: CoinGecko coin ID

        Returns:
            Coin description text
        """
        data = self.get_coin_data(coin_id)
        description = data.get("description", {}).get("en", "")

        # Remove HTML tags
        import re

        description = re.sub("<[^<]+?>", "", description)
        return description

    def get_fear_greed_index(self) -> Dict[str, Any]:
        """
        Get Fear & Greed Index.

        Returns:
            Fear & Greed Index data
        """
        cache_key = "fear_greed_index"
        return self.cache.get_or_fetch(
            cache_key, self.fear_greed_client.get_fear_greed_index, ttl=3600
        )  # 1 hour cache for F&G index

