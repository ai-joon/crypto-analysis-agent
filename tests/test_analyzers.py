"""Unit tests for analyzer components."""

import pytest
from src.analyzers.fundamental_analyzer import FundamentalAnalyzer
from src.analyzers.price_analyzer import PriceAnalyzer
from src.analyzers.sentiment_analyzer import SentimentAnalyzer
from src.analyzers.technical_analyzer import TechnicalAnalyzer


class TestFundamentalAnalyzer:
    """Test fundamental analyzer."""

    def test_analyze_returns_string(
        self, fundamental_analyzer, sample_coin_id, sample_coin_name
    ):
        """Test that analyze returns a string."""
        result = fundamental_analyzer.analyze(sample_coin_id, sample_coin_name)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_analyze_includes_market_metrics(
        self, fundamental_analyzer, sample_coin_id, sample_coin_name
    ):
        """Test that analysis includes market metrics."""
        result = fundamental_analyzer.analyze(sample_coin_id, sample_coin_name)
        assert "Market Cap" in result or "market cap" in result.lower()
        assert "Current Price" in result or "price" in result.lower()

    def test_analyze_includes_supply_metrics(
        self, fundamental_analyzer, sample_coin_id, sample_coin_name
    ):
        """Test that analysis includes supply metrics."""
        result = fundamental_analyzer.analyze(sample_coin_id, sample_coin_name)
        assert "Supply" in result or "supply" in result.lower()

    def test_analyze_handles_errors_gracefully(
        self, coin_repository, sample_coin_id, sample_coin_name
    ):
        """Test that errors are handled gracefully."""
        coin_repository.get_market_data.side_effect = Exception("API Error")
        analyzer = FundamentalAnalyzer(coin_repository)
        result = analyzer.analyze(sample_coin_id, sample_coin_name)
        assert isinstance(result, str)
        assert "Error" in result


class TestPriceAnalyzer:
    """Test price analyzer."""

    def test_analyze_returns_string(
        self, price_analyzer, sample_coin_id, sample_coin_name
    ):
        """Test that analyze returns a string."""
        result = price_analyzer.analyze(sample_coin_id, sample_coin_name)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_analyze_includes_price_data(
        self, price_analyzer, sample_coin_id, sample_coin_name
    ):
        """Test that analysis includes price data."""
        result = price_analyzer.analyze(sample_coin_id, sample_coin_name)
        assert "Price" in result or "price" in result.lower()
        assert "Change" in result or "change" in result.lower()

    def test_analyze_includes_volatility(
        self, price_analyzer, sample_coin_id, sample_coin_name
    ):
        """Test that analysis includes volatility assessment."""
        result = price_analyzer.analyze(sample_coin_id, sample_coin_name)
        assert "Volatility" in result or "volatility" in result.lower()

    def test_analyze_includes_support_resistance(
        self, price_analyzer, sample_coin_id, sample_coin_name
    ):
        """Test that analysis includes support and resistance levels."""
        result = price_analyzer.analyze(sample_coin_id, sample_coin_name)
        assert "Support" in result or "support" in result.lower()
        assert "Resistance" in result or "resistance" in result.lower()

    def test_analyze_includes_trend_analysis(
        self, price_analyzer, sample_coin_id, sample_coin_name
    ):
        """Test that analysis includes trend analysis."""
        result = price_analyzer.analyze(sample_coin_id, sample_coin_name)
        assert any(
            term in result.lower()
            for term in ["trend", "uptrend", "downtrend", "momentum"]
        )


class TestSentimentAnalyzer:
    """Test sentiment analyzer."""

    def test_analyze_returns_string(
        self, sentiment_analyzer, sample_coin_id, sample_coin_name
    ):
        """Test that analyze returns a string."""
        result = sentiment_analyzer.analyze(sample_coin_id, sample_coin_name)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_analyze_includes_sentiment_score(
        self, sentiment_analyzer, sample_coin_id, sample_coin_name
    ):
        """Test that analysis includes sentiment score."""
        result = sentiment_analyzer.analyze(sample_coin_id, sample_coin_name)
        assert "Sentiment" in result or "sentiment" in result.lower()
        assert "/100" in result or "score" in result.lower()

    def test_analyze_includes_community_metrics(
        self, sentiment_analyzer, sample_coin_id, sample_coin_name
    ):
        """Test that analysis includes community metrics."""
        result = sentiment_analyzer.analyze(sample_coin_id, sample_coin_name)
        # Check for social media mentions
        assert any(
            term in result.lower()
            for term in ["twitter", "reddit", "telegram", "community"]
        )

    def test_analyze_includes_fear_greed_index(
        self, sentiment_analyzer, sample_coin_id, sample_coin_name
    ):
        """Test that analysis includes Fear & Greed Index."""
        result = sentiment_analyzer.analyze(sample_coin_id, sample_coin_name)
        assert (
            "Fear" in result
            or "Greed" in result
            or "fear" in result.lower()
            or "greed" in result.lower()
        )


class TestTechnicalAnalyzer:
    """Test technical analyzer."""

    def test_analyze_returns_string(
        self, technical_analyzer, sample_coin_id, sample_coin_name
    ):
        """Test that analyze returns a string."""
        result = technical_analyzer.analyze(sample_coin_id, sample_coin_name)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_analyze_includes_technical_indicators(
        self, technical_analyzer, sample_coin_id, sample_coin_name
    ):
        """Test that analysis includes technical indicators."""
        result = technical_analyzer.analyze(sample_coin_id, sample_coin_name)
        assert any(term in result for term in ["SMA", "RSI", "MACD", "Moving Average"])

    def test_calculate_sma(self, technical_analyzer):
        """Test SMA calculation."""
        prices = [100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0]
        sma = technical_analyzer.calculate_sma(prices, 7)
        assert sma == 130.0

    def test_calculate_rsi(self, technical_analyzer):
        """Test RSI calculation."""
        prices = [100.0] * 20
        rsi = technical_analyzer.calculate_rsi(prices, 14)
        assert rsi is not None
        assert 0 <= rsi <= 100

    def test_analyze_handles_insufficient_data(
        self, coin_repository, sample_coin_id, sample_coin_name
    ):
        """Test handling of insufficient historical data."""
        coin_repository.get_historical_prices.return_value = []
        analyzer = TechnicalAnalyzer(coin_repository)
        result = analyzer.analyze(sample_coin_id, sample_coin_name)
        assert isinstance(result, str)
        assert "Insufficient" in result or "data" in result.lower()
