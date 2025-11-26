"""Unit tests for service components."""

import pytest
from src.services.coin_service import CoinService
from src.services.analysis_service import AnalysisService
from src.core.exceptions import CoinNotFoundError


class TestCoinService:
    """Test coin service."""
    
    def test_get_coin_info_returns_dict(self, coin_service):
        """Test that get_coin_info returns a dictionary."""
        result = coin_service.get_coin_info("bitcoin")
        assert isinstance(result, dict)
        assert "coin_id" in result
        assert "name" in result
        assert "symbol" in result
    
    def test_get_coin_price_returns_dict(self, coin_service):
        """Test that get_coin_price returns a dictionary."""
        result = coin_service.get_coin_price("bitcoin")
        assert isinstance(result, dict)
        assert "current_price" in result or "name" in result
    
    def test_get_coin_news_returns_dict(self, coin_service):
        """Test that get_coin_news returns a dictionary."""
        result = coin_service.get_coin_news("bitcoin")
        assert isinstance(result, dict)
        assert "news_articles" in result
        assert "news_count" in result


class TestAnalysisService:
    """Test analysis service."""
    
    def test_perform_fundamental_analysis_returns_string(self, analysis_service):
        """Test that fundamental analysis returns a string."""
        result = analysis_service.perform_fundamental_analysis("bitcoin")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_perform_price_analysis_returns_string(self, analysis_service):
        """Test that price analysis returns a string."""
        result = analysis_service.perform_price_analysis("bitcoin")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_perform_sentiment_analysis_returns_string(self, analysis_service):
        """Test that sentiment analysis returns a string."""
        result = analysis_service.perform_sentiment_analysis("bitcoin")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_perform_technical_analysis_returns_string(self, analysis_service):
        """Test that technical analysis returns a string."""
        result = analysis_service.perform_technical_analysis("bitcoin")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_all_analysis_types_produce_substantive_output(self, analysis_service):
        """Test that all analysis types produce substantive multi-paragraph output."""
        analyses = [
            analysis_service.perform_fundamental_analysis("bitcoin"),
            analysis_service.perform_price_analysis("bitcoin"),
            analysis_service.perform_sentiment_analysis("bitcoin"),
            analysis_service.perform_technical_analysis("bitcoin"),
        ]
        
        for analysis in analyses:
            # Check for multiple paragraphs (indicated by multiple newlines or sections)
            assert analysis.count("\n\n") >= 2 or analysis.count("**") >= 4
            # Check for specific data points (numbers)
            assert any(char.isdigit() for char in analysis)

