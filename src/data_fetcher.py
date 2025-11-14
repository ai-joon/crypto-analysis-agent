"""Module for fetching cryptocurrency data from various APIs."""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import time


class CryptoDataFetcher:
    """Fetches cryptocurrency data from CoinGecko and other sources."""

    def __init__(self):
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        self.cache = {}
        self.cache_duration = 300  # 5 minutes cache

    def _get_cached_or_fetch(self, cache_key: str, fetch_func) -> Any:
        """Get data from cache or fetch if expired."""
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                return data

        data = fetch_func()
        self.cache[cache_key] = (data, time.time())
        return data

    def get_coin_id(self, query: str) -> Optional[str]:
        """
        Convert a coin name or symbol to CoinGecko coin ID.

        Args:
            query: Coin name or symbol (e.g., 'bitcoin', 'BTC', 'ethereum', 'ETH')

        Returns:
            CoinGecko coin ID or None if not found
        """
        query = query.lower().strip()

        # Common mappings
        common_mappings = {
            "btc": "bitcoin",
            "eth": "ethereum",
            "usdt": "tether",
            "bnb": "binancecoin",
            "sol": "solana",
            "xrp": "ripple",
            "usdc": "usd-coin",
            "ada": "cardano",
            "doge": "dogecoin",
            "avax": "avalanche-2",
            "dot": "polkadot",
            "matic": "matic-network",
            "link": "chainlink",
            "uni": "uniswap",
            "atom": "cosmos",
        }

        if query in common_mappings:
            return common_mappings[query]

        # Try direct match
        try:
            response = requests.get(f"{self.coingecko_base_url}/coins/list", timeout=10)
            if response.status_code == 200:
                coins = response.json()
                for coin in coins:
                    if (
                        coin["id"] == query
                        or coin["symbol"].lower() == query
                        or coin["name"].lower() == query
                    ):
                        return coin["id"]
        except Exception as e:
            print(f"Error fetching coin list: {e}")

        return None

    def get_current_price_data(self, coin_id: str) -> Dict[str, Any]:
        """
        Get current price and market data for a coin.

        Args:
            coin_id: CoinGecko coin ID

        Returns:
            Dictionary containing price and market data
        """

        def fetch():
            url = f"{self.coingecko_base_url}/coins/{coin_id}"
            params = {
                "localization": "false",
                "tickers": "false",
                "community_data": "true",
                "developer_data": "false",
                "sparkline": "false",
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        return self._get_cached_or_fetch(f"price_{coin_id}", fetch)

    def get_market_data(self, coin_id: str) -> Dict[str, Any]:
        """
        Get detailed market data for a coin.

        Args:
            coin_id: CoinGecko coin ID

        Returns:
            Dictionary containing market data
        """
        data = self.get_current_price_data(coin_id)
        market_data = data.get("market_data", {})

        return {
            "current_price": market_data.get("current_price", {}).get("usd"),
            "market_cap": market_data.get("market_cap", {}).get("usd"),
            "market_cap_rank": market_data.get("market_cap_rank"),
            "total_volume": market_data.get("total_volume", {}).get("usd"),
            "high_24h": market_data.get("high_24h", {}).get("usd"),
            "low_24h": market_data.get("low_24h", {}).get("usd"),
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
            "ath": market_data.get("ath", {}).get("usd"),
            "atl": market_data.get("atl", {}).get("usd"),
            "ath_date": market_data.get("ath_date", {}).get("usd"),
            "atl_date": market_data.get("atl_date", {}).get("usd"),
        }

    def get_historical_prices(
        self, coin_id: str, days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get historical price data for a coin.

        Args:
            coin_id: CoinGecko coin ID
            days: Number of days of historical data

        Returns:
            List of price data points
        """

        def fetch():
            url = f"{self.coingecko_base_url}/coins/{coin_id}/market_chart"
            params = {
                "vs_currency": "usd",
                "days": days,
                "interval": "daily" if days > 1 else "hourly",
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

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

        return self._get_cached_or_fetch(f"history_{coin_id}_{days}", fetch)

    def get_community_data(self, coin_id: str) -> Dict[str, Any]:
        """
        Get community and social media data for a coin.

        Args:
            coin_id: CoinGecko coin ID

        Returns:
            Dictionary containing community data
        """
        data = self.get_current_price_data(coin_id)
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
        Get the description of a cryptocurrency.

        Args:
            coin_id: CoinGecko coin ID

        Returns:
            Description text
        """
        data = self.get_current_price_data(coin_id)
        description = data.get("description", {}).get("en", "")

        # Remove HTML tags
        import re

        description = re.sub("<[^<]+?>", "", description)

        return description

    def search_trending_coins(self) -> List[Dict[str, Any]]:
        """
        Get trending coins.

        Returns:
            List of trending coins
        """

        def fetch():
            url = f"{self.coingecko_base_url}/search/trending"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()

        return self._get_cached_or_fetch("trending", fetch)

    def get_fear_greed_index(self) -> Dict[str, Any]:
        """
        Get the Fear & Greed Index.
        Note: This uses an alternative API as CoinGecko doesn't provide this directly.

        Returns:
            Dictionary containing fear & greed data
        """
        try:
            # Using alternative.me API for Fear & Greed Index
            response = requests.get("https://api.alternative.me/fng/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("data") and len(data["data"]) > 0:
                    fng_data = data["data"][0]
                    return {
                        "value": int(fng_data.get("value", 50)),
                        "value_classification": fng_data.get(
                            "value_classification", "Neutral"
                        ),
                        "timestamp": fng_data.get("timestamp"),
                    }
        except Exception as e:
            print(f"Error fetching Fear & Greed Index: {e}")

        return {
            "value": 50,
            "value_classification": "Neutral",
            "timestamp": None,
        }
