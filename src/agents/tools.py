"""Agent tools for cryptocurrency analysis."""

from typing import List, Callable, Dict, Any
from functools import wraps
from datetime import datetime
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
# General blockchain/crypto technology terms that should be searched directly
GENERAL_CRYPTO_TERMS = [
    "blockchain",
    "cryptocurrency",
    "crypto",
    "defi",
    "decentralized finance",
    "nft",
    "non-fungible token",
    "web3",
    "smart contract",
    "dapp",
    "decentralized application",
    "crypto market",
    "digital asset",
    "cryptocurrency market",
]


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
        NOTE: This does NOT return price data. Use get_coin_price for price information.

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
    def get_coin_price(query: str) -> str:
        """
        Get current price and basic market data for a cryptocurrency.
        Use this when the user asks about price, current value, market cap, volume, or 24h changes.
        Examples: "What's the price of Bitcoin?", "How much is Sol worth?", "What's Ethereum's market cap?"

        Args:
            query: The cryptocurrency name or symbol

        Returns:
            Formatted market data string
        """
        progress.info(f"Getting price data for: {query}")
        data = coin_service.get_coin_price(query)
        progress.success(f"Retrieved price data for {data.get('name', query)}")
        coin_name = data.get("name", query)
        symbol = data.get("symbol", "")

        # Format price data
        parts = [f"**{coin_name} ({symbol}) - Current Market Data:**\n"]

        if (current_price := data.get("current_price")) is not None:
            parts.append(f"**Current Price:** ${current_price:,.2f}")

        if (market_cap := data.get("market_cap")) is not None:
            rank = data.get("market_cap_rank", "N/A")
            parts.append(f"**Market Cap:** ${market_cap:,.0f} (Rank: #{rank})")

        if (volume_24h := data.get("total_volume")) is not None:
            parts.append(f"**24h Volume:** ${volume_24h:,.0f}")

        if (change_24h := data.get("price_change_percentage_24h")) is not None:
            change_symbol = "+" if change_24h >= 0 else ""
            parts.append(f"**24h Change:** {change_symbol}{change_24h:+.2f}%")

        high_24h = data.get("high_24h")
        low_24h = data.get("low_24h")
        if high_24h is not None and low_24h is not None:
            parts.append(f"🔺 **24h High:** ${high_24h:,.2f}")
            parts.append(f"🔻 **24h Low:** ${low_24h:,.2f}")

        return "\n".join(parts) if len(parts) > 1 else "No market data available."

    @handle_tool_errors
    def get_coin_news(query: str, page_size: int = 10) -> str:
        """
        Get latest news articles for a cryptocurrency or blockchain technology topic.
        Use this when the user asks about news, recent articles, media coverage, or what's happening with a cryptocurrency.
        Examples: "What's the news about Bitcoin?", "Show me recent articles about Ethereum",
        "What's happening with Solana?", "Provide me some news about blockchain"

        Args:
            query: The cryptocurrency name, symbol, or blockchain technology topic
            page_size: Number of articles to return (default: 10, max: 20)

        Returns:
            Formatted news articles string
        """
        progress.info(f"Fetching news articles for: {query}")

        # Check if NewsAPI is configured
        if not coin_service.repository.newsapi_client.api_key:
            progress.warning("NewsAPI key not configured - news features unavailable")
            return (
                f"**News for {query}:**\n\n"
                "News features are not available because NewsAPI key is not configured. "
                "Please set the NEWSAPI_KEY environment variable to enable news features."
            )

        query_lower = query.lower().strip()

        # Check if query is about general blockchain/crypto technology
        is_general_topic = any(term in query_lower for term in GENERAL_CRYPTO_TERMS)

        news_articles = []
        topic_name = query

        if is_general_topic:
            # For general blockchain/crypto topics, search directly using NewsAPI
            progress.info(
                f"Searching for general blockchain/crypto news about: {query}"
            )
            try:
                news_articles = coin_service.repository.newsapi_client.search_news(
                    query=query, page_size=min(page_size, 20), days_back=7
                )
                topic_name = query
            except Exception as e:
                progress.error(f"Error searching news: {str(e)}")
                return f"Error fetching news about {query}: {str(e)}"
        else:
            # Try to get news for a specific cryptocurrency
            try:
                data = coin_service.get_coin_news(query, page_size=min(page_size, 20))
                topic_name = data.get("name", query)
                news_articles = data.get("news_articles", [])
            except CoinNotFoundError:
                # If not found as a coin, try searching as a general topic anyway
                progress.info(
                    f"'{query}' not found as cryptocurrency, searching as general topic"
                )
                try:
                    news_articles = coin_service.repository.newsapi_client.search_news(
                        query=query, page_size=min(page_size, 20), days_back=7
                    )
                    topic_name = query
                except Exception as e:
                    progress.error(f"Error searching news: {str(e)}")
                    return (
                        f"Could not find cryptocurrency '{query}' and encountered an error "
                        f"searching for general news: {str(e)}. Please check the name or try a different query."
                    )

        news_count = len(news_articles)

        if news_count == 0:
            progress.info("No recent news articles found")
            return (
                f"**News for {topic_name}:**\n\n"
                "No recent news articles found in the past 7 days. "
                "This could indicate low media attention or a quiet period for this topic."
            )

        progress.success(f"Found {news_count} news articles for {topic_name}")

        # Format news articles
        parts = [f"**Latest News for {topic_name} ({news_count} articles found):**\n"]

        for i, article in enumerate(news_articles, 1):
            title = article.get("title", "No title")
            description = article.get("description", "")
            source = article.get("source", {}).get("name", "Unknown source")
            published = article.get("publishedAt", "")
            url = article.get("url", "")

            # Format date if available
            if published:
                try:
                    pub_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
                    date_str = pub_date.strftime("%Y-%m-%d %H:%M")
                except (ValueError, AttributeError):
                    date_str = published[:16] if len(published) >= 16 else published
            else:
                date_str = "Unknown date"

            parts.append(f"\n{i}. **{title}**")
            parts.append(f"   Source: {source} | Published: {date_str}")
            if description:
                # Truncate long descriptions
                desc = (
                    description[:200] + "..." if len(description) > 200 else description
                )
                parts.append(f"   {desc}")
            if url:
                parts.append(f"   Link: {url}")

        return "\n".join(parts)

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
                "Use this first when encountering a new token to verify it exists. "
                "For price queries, use get_coin_price instead."
            ),
        ),
        Tool(
            name="get_coin_price",
            func=get_coin_price,
            description=(
                "Get current price and basic market data (price, market cap, volume, 24h changes). "
                "Use this when user asks about price, current value, 'how much is X worth', "
                "market cap, or 24h price changes. This is a quick lookup tool for current market data."
            ),
        ),
        Tool(
            name="get_coin_news",
            func=get_coin_news,
            description=(
                "Get latest news articles for a cryptocurrency or blockchain technology topic. "
                "Use this when user asks about news, recent articles, media coverage, "
                "'what's happening with X', 'show me news about X', 'what are the latest developments', "
                "or asks for news about blockchain technology, cryptocurrency, DeFi, NFTs, Web3, etc. "
                "Works for both specific cryptocurrencies (e.g., Bitcoin, Ethereum) and general topics (e.g., blockchain, crypto, DeFi). "
                "Returns recent news articles with titles, sources, dates, and links."
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
    ]
