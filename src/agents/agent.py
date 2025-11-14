"""Main agent class for cryptocurrency analysis."""

from typing import Dict, Any, List
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from src.config.settings import Settings
from src.repositories.coin_repository import CoinRepository
from src.services.coin_service import CoinService
from src.services.analysis_service import AnalysisService
from src.agents.tools import create_agent_tools
from src.agents.prompts import get_system_prompt
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class CryptoAnalysisAgent:
    """Conversational AI agent for cryptocurrency analysis."""

    def __init__(self, settings: Settings) -> None:
        """
        Initialize the crypto analysis agent.

        Args:
            settings: Application settings

        Raises:
            ConfigurationError: If agent cannot be initialized
        """
        self.settings = settings
        self.analysis_history: Dict[str, Dict[str, Any]] = {}
        self.conversation_messages: List[BaseMessage] = []  # Store conversation history

        logger.info("Initializing crypto analysis agent...")

        # Initialize dependencies
        self.coin_repository = CoinRepository(
            cache_ttl=settings.cache_ttl, newsapi_key=settings.newsapi_key
        )
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
        try:
            self.agent = create_agent(
                model=self.llm,
                tools=self.tools,
                system_prompt=system_prompt,
                debug=self.settings.verbose,
            )
            logger.info(f"Agent initialized successfully with {len(self.tools)} tools")
        except Exception as e:
            logger.error(f"Failed to initialize agent: {str(e)}", exc_info=True)
            raise

    def chat(self, user_input: str) -> str:
        """
        Send a message to the agent and get a response.
        Maintains conversation context across multiple turns.

        Args:
            user_input: User's message

        Returns:
            Agent's response

        Raises:
            ValueError: If user_input is empty or invalid
        """
        if not user_input or not user_input.strip():
            raise ValueError("User input cannot be empty")

        logger.debug(f"Processing user input: {user_input[:50]}...")

        try:
            # Add user message to conversation history
            user_message = HumanMessage(content=user_input)
            self.conversation_messages.append(user_message)

            # Use the new agent API with full conversation history
            result = self.agent.invoke({"messages": self.conversation_messages})

            # Extract the response from the result
            response_text = ""
            if isinstance(result, dict):
                messages = result.get("messages", [])
                if messages:
                    # The agent returns all messages including new ones
                    # Find new messages that aren't in our history yet
                    existing_count = len(self.conversation_messages)
                    new_messages = (
                        messages[existing_count:]
                        if len(messages) > existing_count
                        else []
                    )

                    # Find the last AI message (response)
                    for msg in reversed(new_messages):
                        if isinstance(msg, AIMessage) or (
                            hasattr(msg, "content")
                            and not isinstance(msg, HumanMessage)
                        ):
                            if hasattr(msg, "content"):
                                response_text = str(msg.content)
                                break

                    # If no new messages found, check the last message in the result
                    if not response_text and messages:
                        last_msg = messages[-1]
                        if isinstance(last_msg, AIMessage) or (
                            hasattr(last_msg, "content")
                            and not isinstance(last_msg, HumanMessage)
                        ):
                            if hasattr(last_msg, "content"):
                                response_text = str(last_msg.content)

                    # Update conversation history with new messages
                    if new_messages:
                        self.conversation_messages.extend(new_messages)
                    elif not response_text and messages:
                        # Fallback: add the last message if it's new
                        last_msg = messages[-1]
                        if (
                            len(self.conversation_messages) == 0
                            or self.conversation_messages[-1] != last_msg
                        ):
                            self.conversation_messages.append(
                                AIMessage(content=str(last_msg))
                            )
                            response_text = str(last_msg)
                else:
                    response_text = str(result)
            else:
                response_text = str(result)
                # Add as AI message if we got a string response
                if response_text:
                    self.conversation_messages.append(AIMessage(content=response_text))

            return (
                response_text
                if response_text
                else "I apologize, but I couldn't generate a response. Please try rephrasing your question."
            )
        except Exception as e:
            error_msg = f"I encountered an error: {str(e)}\n\nPlease try rephrasing your question or ask something else."
            # Don't store error messages in conversation history
            return error_msg

    def reset_conversation(self) -> None:
        """
        Reset the conversation memory and analysis history.

        Clears all stored messages and analysis results.
        """
        logger.info("Resetting conversation history")
        self.conversation_messages.clear()
        self.analysis_history.clear()
