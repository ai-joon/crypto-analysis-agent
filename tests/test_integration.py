"""Integration tests for the full system."""

import pytest
from src.agents.agent import CryptoAnalysisAgent
from src.config.settings import Settings
from unittest.mock import Mock, patch


class TestAgentIntegration:
    """Integration tests for the agent."""
    
    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        settings = Mock(spec=Settings)
        settings.openai_api_key = "test-key"
        settings.openai_model = "gpt-3.5-turbo"
        settings.cache_ttl = 300
        settings.newsapi_key = None
        return settings
    
    @pytest.fixture
    def agent(self, mock_settings):
        """Create agent with mocked dependencies."""
        with patch('src.agents.agent.ChatOpenAI'):
            with patch('src.agents.agent.create_agent'):
                agent = CryptoAnalysisAgent(mock_settings)
                return agent
    
    def test_agent_initialization(self, agent):
        """Test that agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'chat')
        assert hasattr(agent, 'reset_conversation')
        assert hasattr(agent, 'conversation_messages')
        assert hasattr(agent, 'analysis_history')
    
    def test_conversation_memory(self, agent):
        """Test that conversation memory works."""
        initial_count = len(agent.conversation_messages)
        
        # Mock the agent's invoke method
        agent.agent = Mock()
        agent.agent.invoke.return_value = {
            "messages": [
                Mock(content="Test response", spec=["content"])
            ]
        }
        
        response = agent.chat("Tell me about Bitcoin")
        
        # Check that conversation history was updated
        assert len(agent.conversation_messages) > initial_count
    
    def test_reset_conversation(self, agent):
        """Test that reset_conversation clears memory."""
        agent.conversation_messages.append(Mock())
        agent.analysis_history["bitcoin"] = {"test": "data"}
        
        agent.reset_conversation()
        
        assert len(agent.conversation_messages) == 0
        assert len(agent.analysis_history) == 0


class TestEndToEndFlow:
    """End-to-end flow tests."""
    
    def test_analysis_flow(self, analysis_service):
        """Test the complete analysis flow."""
        # Test that we can perform all analysis types
        coin_query = "bitcoin"
        
        fundamental = analysis_service.perform_fundamental_analysis(coin_query)
        price = analysis_service.perform_price_analysis(coin_query)
        sentiment = analysis_service.perform_sentiment_analysis(coin_query)
        technical = analysis_service.perform_technical_analysis(coin_query)
        
        # All should return non-empty strings
        assert all(isinstance(r, str) and len(r) > 0 
                  for r in [fundamental, price, sentiment, technical])
        
        # All should contain substantive content
        assert all(len(r) > 100 for r in [fundamental, price, sentiment, technical])

