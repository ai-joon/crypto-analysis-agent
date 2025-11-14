"""NewsAPI client for fetching cryptocurrency news."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import requests

from src.core.exceptions import APIError
from src.core.logging_config import get_logger
from src.config.constants import DEFAULT_TIMEOUT

logger = get_logger(__name__)


class NewsAPIClient:
    """Client for NewsAPI to fetch cryptocurrency news articles."""

    BASE_URL = "https://newsapi.org/v2"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize NewsAPI client.

        Args:
            api_key: NewsAPI API key (optional, can be None if not configured)
        """
        self.api_key = api_key
        self.timeout = DEFAULT_TIMEOUT

    def _get_headers(self) -> Dict[str, str]:
        """
        Get request headers with API key.

        Returns:
            Headers dictionary

        Raises:
            APIError: If API key is not configured
        """
        if not self.api_key:
            raise APIError(
                "NewsAPI key is not configured. Please set NEWSAPI_KEY environment variable.",
                endpoint="newsapi",
            )
        return {"X-Api-Key": self.api_key}

    def search_news(
        self,
        query: str,
        language: str = "en",
        sort_by: str = "publishedAt",
        page_size: int = 10,
        days_back: int = 7,
    ) -> List[Dict[str, Any]]:
        """
        Search for news articles about a cryptocurrency.

        Args:
            query: Search query (e.g., "Bitcoin", "Ethereum")
            language: Language code (default: "en")
            sort_by: Sort order - "relevancy", "popularity", or "publishedAt" (default: "publishedAt")
            page_size: Number of articles to return (default: 10, max: 100)
            days_back: Number of days to look back (default: 7)

        Returns:
            List of news articles with title, description, url, publishedAt, source

        Raises:
            APIError: If the request fails or API key is missing
        """
        if not self.api_key:
            logger.warning("NewsAPI key not configured, returning empty news list")
            return []

        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)

        params = {
            "q": query,
            "language": language,
            "sortBy": sort_by,
            "pageSize": min(page_size, 100),  # NewsAPI max is 100
            "from": from_date.strftime("%Y-%m-%d"),
            "to": to_date.strftime("%Y-%m-%d"),
        }

        try:
            url = f"{self.BASE_URL}/everything"
            response = requests.get(
                url, params=params, headers=self._get_headers(), timeout=self.timeout
            )

            if response.status_code == 401:
                raise APIError(
                    "NewsAPI authentication failed. Please check your API key.",
                    status_code=401,
                    endpoint="everything",
                )
            elif response.status_code == 429:
                logger.warning("NewsAPI rate limit exceeded")
                return []
            elif response.status_code == 426:
                raise APIError(
                    "NewsAPI upgrade required. Free tier may have limitations.",
                    status_code=426,
                    endpoint="everything",
                )

            response.raise_for_status()
            data = response.json()

            if data.get("status") != "ok":
                error_message = data.get("message", "Unknown error from NewsAPI")
                logger.error(f"NewsAPI error: {error_message}")
                return []

            articles = data.get("articles", [])
            # Filter out articles without title or description
            filtered_articles = [
                article
                for article in articles
                if article.get("title") and article.get("title") != "[Removed]"
            ]

            logger.info(f"Found {len(filtered_articles)} news articles for '{query}'")
            return filtered_articles[:page_size]

        except requests.exceptions.Timeout:
            logger.warning("NewsAPI request timed out")
            return []
        except requests.exceptions.HTTPError as e:
            logger.error(f"NewsAPI HTTP error: {str(e)}")
            raise APIError(
                f"HTTP error {response.status_code} from NewsAPI: {str(e)}",
                status_code=response.status_code,
                endpoint="everything",
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"NewsAPI request failed: {str(e)}")
            raise APIError(
                f"Request to NewsAPI failed: {str(e)}", endpoint="everything"
            )
        except Exception as e:
            logger.error(f"Unexpected error in NewsAPI client: {str(e)}", exc_info=True)
            return []

    def get_crypto_news(
        self, coin_name: str, coin_symbol: str = "", page_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get cryptocurrency news for a specific coin.

        Tries multiple search queries to get comprehensive results.

        Args:
            coin_name: Full name of the cryptocurrency (e.g., "Bitcoin")
            coin_symbol: Symbol of the cryptocurrency (e.g., "BTC")
            page_size: Number of articles to return (default: 10)

        Returns:
            List of news articles
        """
        if not self.api_key:
            return []

        # Try multiple search queries
        queries = [coin_name]
        if coin_symbol:
            queries.append(coin_symbol)
            queries.append(f"{coin_name} {coin_symbol}")

        all_articles = []
        seen_urls = set()

        for query in queries:
            try:
                articles = self.search_news(query, page_size=page_size, days_back=7)
                for article in articles:
                    url = article.get("url")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_articles.append(article)
                        if len(all_articles) >= page_size:
                            break
                if len(all_articles) >= page_size:
                    break
            except APIError:
                # Continue with next query if one fails
                continue

        return all_articles[:page_size]
