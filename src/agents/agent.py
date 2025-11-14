"""Main agent class for cryptocurrency analysis."""

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from src.config.settings import Settings
from src.repositories.coin_repository import CoinRepository
from src.services.coin_service import CoinService
from src.services.analysis_service import AnalysisService
from src.agents.tools import create_agent_tools
from src.agents.prompts import get_system_prompt


class CryptoAnalysisAgent:
    """Conversational AI agent for cryptocurrency analysis."""

    def __init__(self, settings: Settings):
        """
        Initialize the crypto analysis agent.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.analysis_history: dict = {}

        # Initialize dependencies
        self.coin_repository = CoinRepository(cache_ttl=settings.cache_ttl)
        self.coin_service = CoinService(self.coin_repository)
        self.analysis_service = AnalysisService(self.coin_repository)

        # Initialize LLM
        self.llm = ChatOpenAI(
            temperature=0.7,
            model=settings.openai_model,
            openai_api_key=settings.openai_api_key,
        )

        # Create tools
        self.tools = create_agent_tools(
            self.coin_service, self.analysis_service, self.analysis_history
        )

        # Create agent using new langchain 1.0.x API
        system_prompt = get_system_prompt()
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_prompt,
            debug=self.settings.verbose,
        )

    def chat(self, user_input: str) -> str:
        """
        Send a message to the agent and get a response.

        Args:
            user_input: User's message

        Returns:
            Agent's response
        """
        try:
            # Use the new agent API
            result = self.agent.invoke({"messages": [HumanMessage(content=user_input)]})
            
            # Extract the response from the result
            if isinstance(result, dict):
                messages = result.get("messages", [])
                if messages:
                    last_message = messages[-1]
                    if hasattr(last_message, "content"):
                        return str(last_message.content)
                    return str(last_message)
                return str(result)
            return str(result)
        except Exception as e:
            return f"I encountered an error: {str(e)}\n\nPlease try rephrasing your question or ask something else."

    def reset_conversation(self) -> None:
        """Reset the conversation memory and analysis history."""
        self.analysis_history.clear()
