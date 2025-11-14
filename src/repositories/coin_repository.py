"""Repository for cryptocurrency data access."""

from typing import Dict, Any, List, Optional
from datetime import datetime

from src.api.coingecko_client import CoinGeckoClient
from src.api.fear_greed_client import FearGreedClient
from src.api.newsapi_client import NewsAPIClient
from src.core.cache import Cache
from src.core.exceptions import APIError
from src.core.logging_config import get_logger
from src.config.constants import DEFAULT_CACHE_TTL

logger = get_logger(__name__)


class CoinRepository:
    """Repository for accessing cryptocurrency data with caching."""

    def __init__(
        self, cache_ttl: int = DEFAULT_CACHE_TTL, newsapi_key: Optional[str] = None
    ):
        """
        Initialize coin repository.

        Args:
            cache_ttl: Cache time-to-live in seconds
            newsapi_key: Optional NewsAPI key for news features
        """
        self.coingecko_client = CoinGeckoClient()
        self.fear_greed_client = FearGreedClient()
        self.newsapi_client = NewsAPIClient(api_key=newsapi_key)
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

        Raises:
            APIError: If API request fails (including rate limits)
        """
        cache_key = f"coin_data_{coin_id}"
        
        # Check cache first (even if expired) to avoid unnecessary API calls
        cached = self.cache.get(cache_key, allow_stale=True)
        if cached:
            return cached
        
        def fetch_with_error_handling():
            try:
                return self.coingecko_client.get_coin_data(coin_id)
            except APIError as e:
                # If rate limited, try to return stale cache data
                if e.status_code == 429:
                    cached = self.cache.get(cache_key, allow_stale=True)
                    if cached:
                        logger.warning("Using cached data due to rate limit")
                        return cached
                raise
        
        return self.cache.get_or_fetch(cache_key, fetch_with_error_handling)

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

        # Helper function to safely extract USD value
        def get_usd_value(key: str):
            value = market_data.get(key)
            if isinstance(value, dict):
                return value.get("usd")
            return value

        return {
            "current_price": get_usd_value("current_price"),
            "market_cap": get_usd_value("market_cap"),
            "market_cap_rank": market_data.get("market_cap_rank"),
            "total_volume": get_usd_value("total_volume"),
            "high_24h": get_usd_value("high_24h"),
            "low_24h": get_usd_value("low_24h"),
            "price_change_24h": market_data.get("price_change_24h"),
            "price_change_percentage_24h": market_data.get(
                "price_change_percentage_24h"
            ),
            "price_change_percentage_7d": market_data.get("price_change_percentage_7d"),
            "price_change_percentage_30d": market_data.get(
                "price_change_percentage_30d"
            ),
            "circulating_supply": market_data.get("circulating_supply"),
            "total_supply": market_data.get("total_supply"),
            "max_supply": market_data.get("max_supply"),
            "ath": get_usd_value("ath"),
            "atl": get_usd_value("atl"),
            "ath_date": get_usd_value("ath_date"),
            "atl_date": get_usd_value("atl_date"),
        }

    def get_historical_prices(
        self, coin_id: str, days: int = 30
    ) -> List[Dict[str, Any]]:
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
            "reddit_average_comments_48h": community_data.get(
                "reddit_average_comments_48h"
            ),
            "telegram_channel_user_count": community_data.get(
                "telegram_channel_user_count"
            ),
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

    def get_news_articles(
        self, coin_name: str, coin_symbol: str = "", page_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get latest news articles for a cryptocurrency.

        Args:
            coin_name: Full name of the cryptocurrency (e.g., "Bitcoin")
            coin_symbol: Symbol of the cryptocurrency (e.g., "BTC")
            page_size: Number of articles to return (default: 10)

        Returns:
            List of news articles with title, description, url, publishedAt, source
        """
        if not self.newsapi_client.api_key:
            return []

        cache_key = f"news_{coin_name.lower()}_{coin_symbol.lower()}"
        # Cache news for 1 hour (news doesn't change that frequently)
        return self.cache.get_or_fetch(
            cache_key,
            lambda: self.newsapi_client.get_crypto_news(
                coin_name, coin_symbol, page_size
            ),
            ttl=3600,
        )
