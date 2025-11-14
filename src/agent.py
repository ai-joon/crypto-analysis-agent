"""LangChain conversational agent for crypto analysis."""

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.data_fetcher import CryptoDataFetcher
from src.analyzers import (
    FundamentalAnalyzer,
    PriceAnalyzer,
    SentimentAnalyzer,
    TechnicalAnalyzer,
)


class CryptoAnalysisAgent:
    """Conversational AI agent for cryptocurrency analysis."""

    def __init__(self, openai_api_key: str, model: str = "gpt-4"):
        """
        Initialize the crypto analysis agent.

        Args:
            openai_api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-4)
        """
        self.data_fetcher = CryptoDataFetcher()
        self.fundamental_analyzer = FundamentalAnalyzer(self.data_fetcher)
        self.price_analyzer = PriceAnalyzer(self.data_fetcher)
        self.sentiment_analyzer = SentimentAnalyzer(self.data_fetcher)
        self.technical_analyzer = TechnicalAnalyzer(self.data_fetcher)

        # Initialize LLM
        self.llm = ChatOpenAI(
            temperature=0.7, model=model, openai_api_key=openai_api_key
        )

        # Create tools
        self.tools = self._create_tools()

        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True, output_key="output"
        )

        # Create agent
        self.agent_executor = self._create_agent()

        # Store analysis results for reference
        self.analysis_history = {}

    def _create_tools(self):
        """Create tools for the agent."""

        def get_coin_info(query: str) -> str:
            """
            Get basic information about a cryptocurrency.
            Use this when the user asks about a token for the first time.

            Args:
                query: The cryptocurrency name or symbol (e.g., 'bitcoin', 'BTC', 'ethereum')
            """
            try:
                coin_id = self.data_fetcher.get_coin_id(query)
                if not coin_id:
                    return f"Could not find cryptocurrency '{query}'. Please check the name or symbol and try again."

                data = self.data_fetcher.get_current_price_data(coin_id)
                name = data.get("name", query)
                symbol = data.get("symbol", "").upper()

                return f"Found: {name} ({symbol}). CoinGecko ID: {coin_id}"
            except Exception as e:
                return f"Error fetching coin info: {str(e)}"

        def fundamental_analysis_tool(coin_query: str) -> str:
            """
            Perform fundamental analysis on a cryptocurrency.
            This includes market cap, volume, supply metrics, liquidity, and tokenomics.

            Args:
                coin_query: The cryptocurrency name or symbol
            """
            try:
                coin_id = self.data_fetcher.get_coin_id(coin_query)
                if not coin_id:
                    return f"Could not find cryptocurrency '{coin_query}'."

                data = self.data_fetcher.get_current_price_data(coin_id)
                coin_name = data.get("name", coin_query)

                result = self.fundamental_analyzer.analyze(coin_id, coin_name)

                # Store in history
                if coin_id not in self.analysis_history:
                    self.analysis_history[coin_id] = {}
                self.analysis_history[coin_id]["fundamental"] = result
                self.analysis_history[coin_id]["name"] = coin_name

                return result
            except Exception as e:
                return f"Error in fundamental analysis: {str(e)}"

        def price_analysis_tool(coin_query: str) -> str:
            """
            Perform price analysis on a cryptocurrency.
            This includes price trends, volatility, support/resistance levels, and historical performance.

            Args:
                coin_query: The cryptocurrency name or symbol
            """
            try:
                coin_id = self.data_fetcher.get_coin_id(coin_query)
                if not coin_id:
                    return f"Could not find cryptocurrency '{coin_query}'."

                data = self.data_fetcher.get_current_price_data(coin_id)
                coin_name = data.get("name", coin_query)

                result = self.price_analyzer.analyze(coin_id, coin_name)

                # Store in history
                if coin_id not in self.analysis_history:
                    self.analysis_history[coin_id] = {}
                self.analysis_history[coin_id]["price"] = result
                self.analysis_history[coin_id]["name"] = coin_name

                return result
            except Exception as e:
                return f"Error in price analysis: {str(e)}"

        def sentiment_analysis_tool(coin_query: str) -> str:
            """
            Perform sentiment analysis on a cryptocurrency.
            This includes social media metrics, community engagement, and market sentiment indicators.

            Args:
                coin_query: The cryptocurrency name or symbol
            """
            try:
                coin_id = self.data_fetcher.get_coin_id(coin_query)
                if not coin_id:
                    return f"Could not find cryptocurrency '{coin_query}'."

                data = self.data_fetcher.get_current_price_data(coin_id)
                coin_name = data.get("name", coin_query)

                result = self.sentiment_analyzer.analyze(coin_id, coin_name)

                # Store in history
                if coin_id not in self.analysis_history:
                    self.analysis_history[coin_id] = {}
                self.analysis_history[coin_id]["sentiment"] = result
                self.analysis_history[coin_id]["name"] = coin_name

                return result
            except Exception as e:
                return f"Error in sentiment analysis: {str(e)}"

        def technical_analysis_tool(coin_query: str) -> str:
            """
            Perform technical analysis on a cryptocurrency.
            This includes moving averages, RSI, MACD, and other technical indicators.

            Args:
                coin_query: The cryptocurrency name or symbol
            """
            try:
                coin_id = self.data_fetcher.get_coin_id(coin_query)
                if not coin_id:
                    return f"Could not find cryptocurrency '{coin_query}'."

                data = self.data_fetcher.get_current_price_data(coin_id)
                coin_name = data.get("name", coin_query)

                result = self.technical_analyzer.analyze(coin_id, coin_name)

                # Store in history
                if coin_id not in self.analysis_history:
                    self.analysis_history[coin_id] = {}
                self.analysis_history[coin_id]["technical"] = result
                self.analysis_history[coin_id]["name"] = coin_name

                return result
            except Exception as e:
                return f"Error in technical analysis: {str(e)}"

        def get_previous_analysis(coin_query: str, analysis_type: str = "all") -> str:
            """
            Retrieve previous analysis results for a cryptocurrency.
            Use this when the user asks about something you analyzed earlier.

            Args:
                coin_query: The cryptocurrency name or symbol
                analysis_type: Type of analysis to retrieve (fundamental, price, sentiment, technical, or all)
            """
            try:
                coin_id = self.data_fetcher.get_coin_id(coin_query)
                if not coin_id:
                    return f"Could not find cryptocurrency '{coin_query}'."

                if coin_id not in self.analysis_history:
                    return f"No previous analysis found for {coin_query}. Please run an analysis first."

                history = self.analysis_history[coin_id]
                coin_name = history.get("name", coin_query)

                if analysis_type == "all":
                    result = f"Previous analyses for {coin_name}:\n\n"
                    for atype in ["fundamental", "price", "sentiment", "technical"]:
                        if atype in history:
                            result += f"\n{'='*60}\n{history[atype]}\n"
                    return result
                elif analysis_type in history:
                    return history[analysis_type]
                else:
                    return f"No {analysis_type} analysis found for {coin_name}."
            except Exception as e:
                return f"Error retrieving previous analysis: {str(e)}"

        tools = [
            Tool(
                name="get_coin_info",
                func=get_coin_info,
                description="Get basic information about a cryptocurrency. Use this first when encountering a new token.",
            ),
            Tool(
                name="fundamental_analysis",
                func=fundamental_analysis_tool,
                description="Perform fundamental analysis including market cap, volume, supply, liquidity, and tokenomics.",
            ),
            Tool(
                name="price_analysis",
                func=price_analysis_tool,
                description="Perform price analysis including trends, volatility, support/resistance, and historical performance.",
            ),
            Tool(
                name="sentiment_analysis",
                func=sentiment_analysis_tool,
                description="Perform sentiment analysis including social media metrics, community engagement, and market sentiment.",
            ),
            Tool(
                name="technical_analysis",
                func=technical_analysis_tool,
                description="Perform technical analysis including moving averages, RSI, MACD, and technical indicators.",
            ),
            Tool(
                name="get_previous_analysis",
                func=get_previous_analysis,
                description="Retrieve previous analysis results. Use when user references earlier analyses or asks for comparisons.",
            ),
        ]

        return tools

    def _create_agent(self):
        """Create the agent executor."""

        system_message = """You are an expert cryptocurrency analyst with deep knowledge of blockchain technology, tokenomics, market analysis, and technical indicators.

                            Your role is to help users understand and analyze cryptocurrency tokens through comprehensive, data-driven analysis.

                            **Guidelines:**

                            1. **Stay On Topic**: Only discuss cryptocurrency, blockchain, Web3, and related financial topics. Politely redirect off-topic questions.

                            2. **Autonomous Analysis Selection**: 
                            - When a user asks about a token, intelligently decide which types of analysis are most relevant to their question
                            - For general queries like "Tell me about Bitcoin", run comprehensive analysis (fundamental, price, sentiment, technical)
                            - For specific queries like "What's the price trend of Ethereum?", focus on price and technical analysis
                            - For questions about "community" or "sentiment", focus on sentiment analysis
                            - For "market cap" or "supply" questions, focus on fundamental analysis

                            3. **Use Tools Effectively**:
                            - Use get_coin_info first when encountering a new token to verify it exists
                            - Use analysis tools based on what's relevant to the user's query
                            - Use get_previous_analysis when users reference earlier discussions or ask for comparisons

                            4. **Conversational Memory**:
                            - Remember context from earlier in the conversation
                            - When users say "it" or "that token", understand what they're referring to
                            - Compare tokens when asked (e.g., "How does Bitcoin's sentiment compare to Ethereum?")

                            5. **Handle Ambiguity**:
                            - If a query is unclear, ask clarifying questions
                            - Suggest common cryptocurrencies if a token isn't found
                            - Explain what types of analysis you can provide

                            6. **Present Information Clearly**:
                            - Use the analysis results from tools as your primary source
                            - Synthesize information from multiple analyses when relevant
                            - Provide actionable insights and interpretations
                            - Be honest about limitations and uncertainties

                            7. **Risk Awareness**:
                            - This is educational information, not financial advice
                            - Remind users that cryptocurrency investments are risky
                            - Encourage users to do their own research (DYOR)

                            Remember: You're here to educate and inform, not to give investment advice. Be thorough, accurate, and helpful."""

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_message),
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
            verbose=True,
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

    def reset_conversation(self):
        """Reset the conversation memory."""
        self.memory.clear()
        self.analysis_history.clear()
