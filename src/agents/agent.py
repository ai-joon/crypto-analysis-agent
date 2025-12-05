"""Main agent class for cryptocurrency analysis."""

import os
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from src.config.settings import Settings
from src.repositories.coin_repository import CoinRepository
from src.services.coin_service import CoinService
from src.services.analysis_service import AnalysisService
from src.agents.tools import create_agent_tools
from src.agents.prompts import get_system_prompt
from src.core.logging_config import get_logger
from src.core.progress import get_progress_logger
from src.core.semantic_cache import SemanticCache

logger = get_logger(__name__)
progress = get_progress_logger()


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
        self.conversation_messages: List[BaseMessage] = []

        self.semantic_cache = None
        if settings.semantic_cache_enabled:
            try:
                self.semantic_cache = SemanticCache(
                    api_key=settings.openai_api_key,
                    similarity_threshold=settings.semantic_cache_threshold,
                    max_cache_size=settings.semantic_cache_size,
                    ttl=settings.semantic_cache_ttl,
                    cache_file=settings.semantic_cache_file,
                )
                cache_size = len(self.semantic_cache._cache)
                if cache_size > 0:
                    progress.info(
                        f"Semantic cache initialized with {cache_size} entries from file"
                    )
                else:
                    progress.info("Semantic cache initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize semantic cache: {e}")
                self.semantic_cache = None

        progress.info("Initializing crypto analysis agent...")

        if settings.langsmith_enabled:
            self._setup_langsmith(settings)

        self.coin_repository = CoinRepository(
            cache_ttl=settings.cache_ttl, newsapi_key=settings.newsapi_key
        )
        self.coin_service = CoinService(self.coin_repository)
        self.analysis_service = AnalysisService(self.coin_repository)

        self.llm = ChatOpenAI(
            temperature=0.7,
            model=settings.openai_model,
            openai_api_key=settings.openai_api_key,
        )

        self.tools = create_agent_tools(
            self.coin_service, self.analysis_service, self.analysis_history
        )

        system_prompt = get_system_prompt()
        try:
            # Lazy import to avoid torch/transformers import issues at module level
            # Use create_openai_tools_agent which is the modern API and may avoid torch dependency
            try:
                from langchain.agents import create_openai_tools_agent
                from langchain.agents import AgentExecutor
                from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
                
                prompt = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    MessagesPlaceholder(variable_name="messages"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ])
                
                agent_runnable = create_openai_tools_agent(self.llm, self.tools, prompt)
                self.agent = AgentExecutor(agent=agent_runnable, tools=self.tools, verbose=False)
                progress.success(f"Agent initialized with {len(self.tools)} tools")
            except (ImportError, OSError) as import_err:
                # Fallback to create_agent if the modern API fails or doesn't exist
                error_msg = str(import_err).lower()
                if "create_openai_tools_agent" in error_msg or "cannot import name" in error_msg:
                    # create_openai_tools_agent doesn't exist in this LangChain version, use create_agent
                    progress.info("Using create_agent (create_openai_tools_agent not available in this LangChain version)")
                    from langchain.agents import create_agent
                    self.agent = create_agent(
                        model=self.llm,
                        tools=self.tools,
                        system_prompt=system_prompt,
                        debug=False,
                    )
                    progress.success(f"Agent initialized with {len(self.tools)} tools")
                elif "torch" in error_msg or "dll" in error_msg or "1114" in error_msg:
                    progress.warning("Encountered PyTorch import issue, trying fallback method...")
                    try:
                        from langchain.agents import create_agent
                        self.agent = create_agent(
                            model=self.llm,
                            tools=self.tools,
                            system_prompt=system_prompt,
                            debug=False,
                        )
                        progress.success(f"Agent initialized with {len(self.tools)} tools (fallback method)")
                    except (ImportError, OSError):
                        progress.error(
                            "Failed to import required dependencies due to PyTorch DLL issue.\n"
                            "Try one of these solutions:\n"
                            "1. Reinstall PyTorch: pip uninstall torch && pip install torch\n"
                            "2. Install CPU-only PyTorch: pip install torch --index-url https://download.pytorch.org/whl/cpu\n"
                            "3. Install Visual C++ Redistributables from Microsoft\n"
                            "4. Update LangChain: pip install --upgrade langchain langchain-openai"
                        )
                        raise
                else:
                    raise
        except Exception as e:
            progress.error(f"Failed to initialize agent: {str(e)}")
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

        is_standalone = len(self.conversation_messages) == 0

        if self.semantic_cache and is_standalone:
            cached_response = self.semantic_cache.get(user_input)
            if cached_response:
                progress.cache("Using cached response from semantic cache")
                self.conversation_messages.append(HumanMessage(content=user_input))
                self.conversation_messages.append(AIMessage(content=cached_response))
                return cached_response

        try:
            user_message = HumanMessage(content=user_input)
            self.conversation_messages.append(user_message)

            result = self.agent.invoke({"messages": self.conversation_messages})

            response_text = ""
            if isinstance(result, dict):
                messages = result.get("messages", [])
                if messages:
                    existing_count = len(self.conversation_messages)
                    new_messages = (
                        messages[existing_count:]
                        if len(messages) > existing_count
                        else []
                    )

                    for msg in reversed(new_messages):
                        if isinstance(msg, AIMessage) or (
                            hasattr(msg, "content")
                            and not isinstance(msg, HumanMessage)
                        ):
                            if hasattr(msg, "content"):
                                response_text = str(msg.content)
                                break

                    if not response_text and messages:
                        last_msg = messages[-1]
                        if isinstance(last_msg, AIMessage) or (
                            hasattr(last_msg, "content")
                            and not isinstance(last_msg, HumanMessage)
                        ):
                            if hasattr(last_msg, "content"):
                                response_text = str(last_msg.content)

                    if new_messages:
                        self.conversation_messages.extend(new_messages)
                    elif not response_text and messages:
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
                if response_text:
                    self.conversation_messages.append(AIMessage(content=response_text))

            if response_text and self.semantic_cache:
                try:
                    self.semantic_cache.set(user_input, response_text)
                except Exception as e:
                    logger.warning(f"Failed to save to semantic cache: {e}")

            return (
                response_text
                if response_text
                else "I apologize, but I couldn't generate a response. Please try rephrasing your question."
            )
        except Exception as e:
            return f"I encountered an error: {str(e)}\n\nPlease try rephrasing your question or ask something else."

    def reset_conversation(self) -> None:
        """
        Reset the conversation memory and analysis history.

        Clears all stored messages and analysis results.
        """
        progress.info("Resetting conversation history")
        self.conversation_messages.clear()
        self.analysis_history.clear()

    def _setup_langsmith(self, settings: Settings) -> None:
        """Setup LangSmith tracing for LangChain operations."""
        if not settings.langsmith_api_key:
            logger.warning(
                "LangSmith enabled but API key not provided. Tracing will be disabled."
            )
            return

        try:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key

            if settings.langsmith_project:
                os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
            else:
                os.environ.pop("LANGCHAIN_PROJECT", None)

            project_name = settings.langsmith_project or "default"
            progress.info(f"LangSmith tracing enabled (project: {project_name})")
            logger.info(f"LangSmith tracing configured for project: {project_name}")
        except Exception as e:
            logger.error(f"Failed to setup LangSmith tracing: {e}")
            progress.warning(
                "LangSmith tracing setup failed, continuing without tracing"
            )

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get semantic cache statistics."""
        if self.semantic_cache:
            return self.semantic_cache.get_stats()
        return {"enabled": False}
