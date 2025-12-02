"""Agent tools for cryptocurrency analysis."""

from typing import List, Callable, Dict, Any
from functools import wraps
from langchain_core.tools import Tool

from src.services.coin_service import CoinService
from src.services.analysis_service import AnalysisService
from src.core.exceptions import CoinNotFoundError, AnalysisError, APIError
from src.core.logging_config import get_logger
from src.core.progress import get_progress_logger

logger = get_logger(__name__)
progress = get_progress_logger()

# Constants
AMBIGUOUS_TERMS = ["it", "that", "this", "the token", "that token", "this token"]
ANALYSIS_TYPES = ["fundamental", "price", "sentiment", "technical"]


def handle_tool_errors(func: Callable) -> Callable:
    """
    Decorator to handle common tool errors consistently.

    Args:
        func: Tool function to wrap

    Returns:
        Wrapped function with error handling
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CoinNotFoundError as e:
            query = args[0] if args else "unknown"
            suggestions = getattr(e, "suggestions", [])
            if suggestions:
                return (
                    f"Could not find cryptocurrency '{query}'. "
                    f"Did you mean: {', '.join(suggestions[:3])}?"
                )
            return f"Could not find cryptocurrency '{query}'. Please check the name or symbol and try again."
        except AnalysisError as e:
            progress.error(f"Analysis error in {e.analysis_type} analysis: {str(e)}")
            return f"Error in {e.analysis_type} analysis: {str(e)}"
        except APIError as e:
            if e.status_code == 429:
                progress.warning(
                    "Rate limit exceeded. Please wait 1-2 minutes and try again."
                )
                return (
                    "Rate limit exceeded: The API is temporarily unavailable due to too many requests. "
                    "Please wait 1-2 minutes and try again. "
                    "The application uses caching to minimize API calls."
                )
            progress.error(f"API error: {str(e)}")
            return f"API error: {str(e)}"
        except Exception as e:
            progress.error(f"Unexpected error: {str(e)}")
            return f"An unexpected error occurred: {str(e)}. Please try again."

    return wrapper


def store_analysis_result(
    coin_id: str,
    coin_name: str,
    analysis_type: str,
    result: str,
    analysis_history: Dict[str, Any],
) -> None:
    """
    Store analysis result in history.

    Args:
        coin_id: CoinGecko coin ID
        coin_name: Human-readable coin name
        analysis_type: Type of analysis performed
        result: Analysis result string
        analysis_history: Dictionary to store analysis history
    """
    if coin_id not in analysis_history:
        analysis_history[coin_id] = {}
    analysis_history[coin_id][analysis_type] = result
    analysis_history[coin_id]["name"] = coin_name


def create_analysis_tool(
    analysis_type: str,
    analysis_method: Callable[[str], str],
    coin_service: CoinService,
    analysis_history: Dict[str, Any],
) -> Callable[[str], str]:
    """
    Factory function to create analysis tool functions.

    Args:
        analysis_type: Type of analysis (fundamental, price, sentiment, technical)
        analysis_method: Method from AnalysisService to call
        coin_service: Coin service instance
        analysis_history: Dictionary to store analysis history

    Returns:
        Tool function
    """

    @handle_tool_errors
    def analysis_tool(coin_query: str) -> str:
        """
        Perform {analysis_type} analysis on a cryptocurrency.

        Args:
            coin_query: The cryptocurrency name or symbol

        Returns:
            Analysis report string
        """
        info = coin_service.get_coin_info(coin_query)
        coin_id = info["coin_id"]
        coin_name = info["name"]

        progress.info(f"Performing {analysis_type} analysis for {coin_name}...")
        result = analysis_method(coin_query)
        progress.success(f"Completed {analysis_type} analysis for {coin_name}")

        store_analysis_result(
            coin_id, coin_name, analysis_type, result, analysis_history
        )
        return result

    analysis_tool.__doc__ = analysis_tool.__doc__.format(analysis_type=analysis_type)
    return analysis_tool


def create_agent_tools(
    coin_service: CoinService,
    analysis_service: AnalysisService,
    analysis_history: Dict[str, Any],
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

    @handle_tool_errors
    def get_coin_info(query: str) -> str:
        """
        Get basic information about a cryptocurrency (name, symbol, coin ID).
        Use this when the user asks about a token for the first time or needs basic identification.
        NOTE: This does NOT return price data. For price and market information, use the price_analysis tool.

        Args:
            query: The cryptocurrency name or symbol

        Returns:
            Formatted coin information string
        """
        progress.info(f"Getting coin information for: {query}")
        info = coin_service.get_coin_info(query)
        progress.success(f"Found: {info['name']} ({info['symbol']})")
        return (
            f"Found: {info['name']} ({info['symbol']}). CoinGecko ID: {info['coin_id']}"
        )

    @handle_tool_errors
    def get_previous_analysis(coin_query: str, analysis_type: str = "all") -> str:
        """
        Retrieve previous analysis results for a cryptocurrency.
        Use this when the user asks about something you analyzed earlier, references "earlier",
        "before", "what you said about", or asks follow-up questions about a previously analyzed token.

        If coin_query is ambiguous (like "it", "that token", "this"), try to infer from context
        by checking which tokens have been analyzed. If multiple tokens exist, return info about all of them.

        Args:
            coin_query: The cryptocurrency name or symbol (can be "it", "that", etc. - will try to infer)
            analysis_type: Type of analysis to retrieve (fundamental, price, sentiment, technical, or all)

        Returns:
            Previous analysis results string
        """
        coin_query_lower = coin_query.lower().strip()

        # Handle ambiguous references
        if coin_query_lower in AMBIGUOUS_TERMS and analysis_history:
            if len(analysis_history) == 1:
                # Only one token analyzed, use it
                coin_id = list(analysis_history.keys())[0]
                history = analysis_history[coin_id]
                coin_name = history.get("name", coin_id)
            else:
                # Multiple tokens - return summary
                result_parts = [
                    "Multiple tokens have been analyzed. Here are the previous analyses:\n"
                ]
                for cid, hist in analysis_history.items():
                    cname = hist.get("name", cid)
                    result_parts.append(f"\n{'='*60}\n{cname} ({cid}):")
                    for atype in ANALYSIS_TYPES:
                        if atype in hist:
                            result_parts.append(
                                f"- {atype.capitalize()} analysis available"
                            )
                result_parts.append(
                    "\nPlease specify which token you're asking about, or I can show all analyses."
                )
                return "\n".join(result_parts)
        else:
            # Normal lookup
            info = coin_service.get_coin_info(coin_query)
            coin_id = info["coin_id"]

        if coin_id not in analysis_history:
            return f"No previous analysis found for {coin_query}. Please run an analysis first."

        history = analysis_history[coin_id]
        coin_name = history.get("name", coin_query)

        if analysis_type == "all":
            result_parts = [f"Previous analyses for {coin_name}:\n"]
            for atype in ANALYSIS_TYPES:
                if atype in history:
                    result_parts.append(
                        f"\n{'='*60}\n{atype.capitalize()} Analysis:\n{history[atype]}"
                    )
            return (
                "\n".join(result_parts)
                if len(result_parts) > 1
                else f"No analyses found for {coin_name}."
            )
        elif analysis_type in history:
            return f"{analysis_type.capitalize()} Analysis for {coin_name}:\n\n{history[analysis_type]}"
        else:
            return f"No {analysis_type} analysis found for {coin_name}."

    # Create analysis tools using factory function
    fundamental_tool = create_analysis_tool(
        "fundamental",
        analysis_service.perform_fundamental_analysis,
        coin_service,
        analysis_history,
    )
    price_tool = create_analysis_tool(
        "price",
        analysis_service.perform_price_analysis,
        coin_service,
        analysis_history,
    )
    sentiment_tool = create_analysis_tool(
        "sentiment",
        analysis_service.perform_sentiment_analysis,
        coin_service,
        analysis_history,
    )
    technical_tool = create_analysis_tool(
        "technical",
        analysis_service.perform_technical_analysis,
        coin_service,
        analysis_history,
    )

    return [
        Tool(
            name="get_coin_info",
            func=get_coin_info,
            description=(
                "Get basic information about a cryptocurrency (name, symbol, coin ID only - NO PRICE). "
                "Use this first when encountering a new token to verify it exists or resolve ambiguous names/symbols. "
                "For price and market data queries, use the price_analysis tool instead."
            ),
        ),
        Tool(
            name="get_previous_analysis",
            func=get_previous_analysis,
            description=(
                "Retrieve previous analysis results. Use when user references earlier analyses, "
                "asks follow-up questions like 'What about its performance?', 'What are the risks?', "
                "'What did you say about X earlier?', or asks for comparisons. "
                "Can handle ambiguous references like 'it', 'that token' by inferring from conversation context."
            ),
        ),
        Tool(
            name="fundamental_analysis",
            func=fundamental_tool,
            description=(
                "Perform fundamental analysis including market cap, volume, supply, "
                "liquidity, and tokenomics."
            ),
        ),
        Tool(
            name="price_analysis",
            func=price_tool,
            description=(
                "Perform price analysis including trends, volatility, support/resistance, "
                "and historical performance."
            ),
        ),
        Tool(
            name="sentiment_analysis",
            func=sentiment_tool,
            description=(
                "Perform sentiment analysis including social media metrics, "
                "community engagement, and market sentiment."
            ),
        ),
        Tool(
            name="technical_analysis",
            func=technical_tool,
            description=(
                "Perform technical analysis including moving averages, RSI, MACD, "
                "and technical indicators."
            ),
        ),
    ]
