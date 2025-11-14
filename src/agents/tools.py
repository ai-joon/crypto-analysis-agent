"""Agent tools for cryptocurrency analysis."""

from typing import List
from langchain.tools import Tool

from src.services.coin_service import CoinService
from src.services.analysis_service import AnalysisService
from src.core.exceptions import CoinNotFoundError, AnalysisError


def create_agent_tools(
    coin_service: CoinService,
    analysis_service: AnalysisService,
    analysis_history: dict,
) -> List[Tool]:
    """
    Create LangChain tools for the agent.

    Args:
        coin_service: Coin service instance
        analysis_service: Analysis service instance
        analysis_history: Dictionary to store analysis history

    Returns:
        List of LangChain tools
    """

    def get_coin_info(query: str) -> str:
        """
        Get basic information about a cryptocurrency.
        Use this when the user asks about a token for the first time.

        Args:
            query: The cryptocurrency name or symbol
        """
        try:
            info = coin_service.get_coin_info(query)
            return f"Found: {info['name']} ({info['symbol']}). CoinGecko ID: {info['coin_id']}"
        except CoinNotFoundError:
            return f"Could not find cryptocurrency '{query}'. Please check the name or symbol and try again."
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
            info = coin_service.get_coin_info(coin_query)
            coin_id = info["coin_id"]
            coin_name = info["name"]

            result = analysis_service.perform_fundamental_analysis(coin_query)

            # Store in history
            if coin_id not in analysis_history:
                analysis_history[coin_id] = {}
            analysis_history[coin_id]["fundamental"] = result
            analysis_history[coin_id]["name"] = coin_name

            return result
        except CoinNotFoundError:
            return f"Could not find cryptocurrency '{coin_query}'."
        except AnalysisError as e:
            return f"Error in fundamental analysis: {str(e)}"
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
            info = coin_service.get_coin_info(coin_query)
            coin_id = info["coin_id"]
            coin_name = info["name"]

            result = analysis_service.perform_price_analysis(coin_query)

            # Store in history
            if coin_id not in analysis_history:
                analysis_history[coin_id] = {}
            analysis_history[coin_id]["price"] = result
            analysis_history[coin_id]["name"] = coin_name

            return result
        except CoinNotFoundError:
            return f"Could not find cryptocurrency '{coin_query}'."
        except AnalysisError as e:
            return f"Error in price analysis: {str(e)}"
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
            info = coin_service.get_coin_info(coin_query)
            coin_id = info["coin_id"]
            coin_name = info["name"]

            result = analysis_service.perform_sentiment_analysis(coin_query)

            # Store in history
            if coin_id not in analysis_history:
                analysis_history[coin_id] = {}
            analysis_history[coin_id]["sentiment"] = result
            analysis_history[coin_id]["name"] = coin_name

            return result
        except CoinNotFoundError:
            return f"Could not find cryptocurrency '{coin_query}'."
        except AnalysisError as e:
            return f"Error in sentiment analysis: {str(e)}"
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
            info = coin_service.get_coin_info(coin_query)
            coin_id = info["coin_id"]
            coin_name = info["name"]

            result = analysis_service.perform_technical_analysis(coin_query)

            # Store in history
            if coin_id not in analysis_history:
                analysis_history[coin_id] = {}
            analysis_history[coin_id]["technical"] = result
            analysis_history[coin_id]["name"] = coin_name

            return result
        except CoinNotFoundError:
            return f"Could not find cryptocurrency '{coin_query}'."
        except AnalysisError as e:
            return f"Error in technical analysis: {str(e)}"
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
            info = coin_service.get_coin_info(coin_query)
            coin_id = info["coin_id"]

            if coin_id not in analysis_history:
                return f"No previous analysis found for {coin_query}. Please run an analysis first."

            history = analysis_history[coin_id]
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
        except CoinNotFoundError:
            return f"Could not find cryptocurrency '{coin_query}'."
        except Exception as e:
            return f"Error retrieving previous analysis: {str(e)}"

    return [
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

