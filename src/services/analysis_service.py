"""Service for orchestrating cryptocurrency analyses."""

from src.repositories.coin_repository import CoinRepository
from src.analyzers import (
    FundamentalAnalyzer,
    PriceAnalyzer,
    SentimentAnalyzer,
    TechnicalAnalyzer,
)
from src.core.exceptions import AnalysisError


class AnalysisService:
    """Service for performing cryptocurrency analyses."""

    def __init__(self, coin_repository: CoinRepository):
        """
        Initialize analysis service.

        Args:
            coin_repository: Coin repository instance
        """
        self.repository = coin_repository
        self.fundamental_analyzer = FundamentalAnalyzer(coin_repository)
        self.price_analyzer = PriceAnalyzer(coin_repository)
        self.sentiment_analyzer = SentimentAnalyzer(coin_repository)
        self.technical_analyzer = TechnicalAnalyzer(coin_repository)

    def get_coin_name(self, query: str) -> str:
        """
        Get coin name from query.

        Args:
            query: Cryptocurrency name or symbol

        Returns:
            Coin name

        Raises:
            CoinNotFoundError: If coin cannot be found
        """
        coin_id = self.repository.get_coin_id(query)
        data = self.repository.get_coin_data(coin_id)
        return data.get("name", query)

    def perform_fundamental_analysis(self, query: str) -> str:
        """
        Perform fundamental analysis.

        Args:
            query: Cryptocurrency name or symbol

        Returns:
            Analysis report

        Raises:
            CoinNotFoundError: If coin cannot be found
            AnalysisError: If analysis fails
        """
        coin_id = self.repository.get_coin_id(query)
        coin_name = self.get_coin_name(query)
        try:
            return self.fundamental_analyzer.analyze(coin_id, coin_name)
        except Exception as e:
            raise AnalysisError("fundamental", str(e))

    def perform_price_analysis(self, query: str) -> str:
        """
        Perform price analysis.

        Args:
            query: Cryptocurrency name or symbol

        Returns:
            Analysis report

        Raises:
            CoinNotFoundError: If coin cannot be found
            AnalysisError: If analysis fails
        """
        coin_id = self.repository.get_coin_id(query)
        coin_name = self.get_coin_name(query)
        try:
            return self.price_analyzer.analyze(coin_id, coin_name)
        except Exception as e:
            raise AnalysisError("price", str(e))

    def perform_sentiment_analysis(self, query: str) -> str:
        """
        Perform sentiment analysis.

        Args:
            query: Cryptocurrency name or symbol

        Returns:
            Analysis report

        Raises:
            CoinNotFoundError: If coin cannot be found
            AnalysisError: If analysis fails
        """
        coin_id = self.repository.get_coin_id(query)
        coin_name = self.get_coin_name(query)
        try:
            return self.sentiment_analyzer.analyze(coin_id, coin_name)
        except Exception as e:
            raise AnalysisError("sentiment", str(e))

    def perform_technical_analysis(self, query: str) -> str:
        """
        Perform technical analysis.

        Args:
            query: Cryptocurrency name or symbol

        Returns:
            Analysis report

        Raises:
            CoinNotFoundError: If coin cannot be found
            AnalysisError: If analysis fails
        """
        coin_id = self.repository.get_coin_id(query)
        coin_name = self.get_coin_name(query)
        try:
            return self.technical_analyzer.analyze(coin_id, coin_name)
        except Exception as e:
            raise AnalysisError("technical", str(e))
