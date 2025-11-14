"""Main agent class for cryptocurrency analysis."""

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

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

        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True, output_key="output"
        )

        # Create agent executor
        self.agent_executor = self._create_agent_executor()

    def _create_agent_executor(self) -> AgentExecutor:
        """
        Create the agent executor.

        Returns:
            Configured AgentExecutor
        """
        system_prompt = get_system_prompt()

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_openai_functions_agent(
            llm=self.llm, tools=self.tools, prompt=prompt
        )

        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=self.settings.verbose,
            max_iterations=6,
            return_intermediate_steps=False,
            handle_parsing_errors=True,
        )

        return agent_executor

    def chat(self, user_input: str) -> str:
        """
        Send a message to the agent and get a response.

        Args:
            user_input: User's message

        Returns:
            Agent's response
        """
        try:
            response = self.agent_executor.invoke({"input": user_input})
            return response["output"]
        except Exception as e:
            return f"I encountered an error: {str(e)}\n\nPlease try rephrasing your question or ask something else."

    def reset_conversation(self) -> None:
        """Reset the conversation memory and analysis history."""
        self.memory.clear()
        self.analysis_history.clear()

