"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict, Any

from src.repositories.coin_repository import CoinRepository
from src.services.coin_service import CoinService
from src.services.analysis_service import AnalysisService
from src.analyzers.fundamental_analyzer import FundamentalAnalyzer
from src.analyzers.price_analyzer import PriceAnalyzer
from src.analyzers.sentiment_analyzer import SentimentAnalyzer
from src.analyzers.technical_analyzer import TechnicalAnalyzer


@pytest.fixture
def mock_coin_repository():
    """Create a mock coin repository with sample data."""
    repo = Mock(spec=CoinRepository)
    
    # Mock market data
    repo.get_market_data.return_value = {
        "current_price": 50000.0,
        "market_cap": 1000000000000,
        "market_cap_rank": 1,
        "total_volume": 50000000000,
        "circulating_supply": 20000000,
        "total_supply": 21000000,
        "max_supply": 21000000,
        "price_change_percentage_24h": 2.5,
        "price_change_percentage_7d": 5.0,
        "price_change_percentage_30d": 10.0,
        "high_24h": 51000.0,
        "low_24h": 49000.0,
        "ath": 69000.0,
        "atl": 0.01,
    }
    
    # Mock historical prices
    repo.get_historical_prices.return_value = [
        {"price": 48000.0 + i * 100} for i in range(30)
    ]
    
    # Mock coin data
    repo.get_coin_data.return_value = {
        "name": "Bitcoin",
        "symbol": "btc",
        "description": {"en": "Bitcoin is a decentralized digital currency."}
    }
    
    # Mock community data
    repo.get_community_data.return_value = {
        "twitter_followers": 5000000,
        "reddit_subscribers": 2000000,
        "reddit_average_posts_48h": 50,
        "reddit_average_comments_48h": 500,
        "telegram_channel_user_count": 1000000,
    }
    
    # Mock fear & greed index
    repo.get_fear_greed_index.return_value = {
        "value": 65,
        "value_classification": "Greed"
    }
    
    # Mock news articles
    repo.get_news_articles.return_value = [
        {
            "title": "Bitcoin reaches new milestone",
            "description": "Bitcoin price surges...",
            "source": {"name": "CryptoNews"},
            "publishedAt": "2024-01-15T10:00:00Z",
            "url": "https://example.com/news1"
        }
    ]
    
    # Mock coin ID resolution
    repo.get_coin_id.return_value = "bitcoin"
    
    return repo


@pytest.fixture
def coin_repository(mock_coin_repository):
    """Return the mock repository."""
    return mock_coin_repository


@pytest.fixture
def coin_service(coin_repository):
    """Create a coin service with mocked repository."""
    return CoinService(coin_repository)


@pytest.fixture
def analysis_service(coin_repository):
    """Create an analysis service with mocked repository."""
    return AnalysisService(coin_repository)


@pytest.fixture
def fundamental_analyzer(coin_repository):
    """Create a fundamental analyzer with mocked repository."""
    return FundamentalAnalyzer(coin_repository)


@pytest.fixture
def price_analyzer(coin_repository):
    """Create a price analyzer with mocked repository."""
    return PriceAnalyzer(coin_repository)


@pytest.fixture
def sentiment_analyzer(coin_repository):
    """Create a sentiment analyzer with mocked repository."""
    return SentimentAnalyzer(coin_repository)


@pytest.fixture
def technical_analyzer(coin_repository):
    """Create a technical analyzer with mocked repository."""
    return TechnicalAnalyzer(coin_repository)


@pytest.fixture
def sample_coin_id():
    """Sample coin ID for testing."""
    return "bitcoin"


@pytest.fixture
def sample_coin_name():
    """Sample coin name for testing."""
    return "Bitcoin"

