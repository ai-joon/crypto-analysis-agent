"""Agent tools for cryptocurrency analysis."""

from typing import List
from langchain_core.tools import Tool

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
        Get basic information about a cryptocurrency (name, symbol, coin ID).
        Use this when the user asks about a token for the first time or needs basic identification.
        NOTE: This does NOT return price data. Use get_coin_price for price information.

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

    def get_coin_price(query: str) -> str:
        """
        Get current price and basic market data for a cryptocurrency.
        Use this when the user asks about price, current value, market cap, volume, or 24h changes.
        Examples: "What's the price of Bitcoin?", "How much is Sol worth?", "What's Ethereum's market cap?"

        Args:
            query: The cryptocurrency name or symbol
        """
        try:
            data = coin_service.get_coin_price(query)
            coin_name = data.get("name", query)
            symbol = data.get("symbol", "")
            current_price = data.get("current_price")
            market_cap = data.get("market_cap")
            volume_24h = data.get("total_volume")
            change_24h = data.get("price_change_percentage_24h")
            high_24h = data.get("high_24h")
            low_24h = data.get("low_24h")
            market_cap_rank = data.get("market_cap_rank")

            result = f"**{coin_name} ({symbol}) - Current Market Data:**\n\n"
            
            if current_price is not None:
                result += f"💰 **Current Price:** ${current_price:,.2f}\n"
            
            if market_cap is not None:
                result += f"📊 **Market Cap:** ${market_cap:,.0f} (Rank: #{market_cap_rank or 'N/A'})\n"
            
            if volume_24h is not None:
                result += f"📈 **24h Volume:** ${volume_24h:,.0f}\n"
            
            if change_24h is not None:
                change_symbol = "📈" if change_24h >= 0 else "📉"
                result += f"{change_symbol} **24h Change:** {change_24h:+.2f}%\n"
            
            if high_24h is not None and low_24h is not None:
                result += f"🔺 **24h High:** ${high_24h:,.2f}\n"
                result += f"🔻 **24h Low:** ${low_24h:,.2f}\n"

            return result
        except CoinNotFoundError:
            return f"Could not find cryptocurrency '{query}'. Please check the name or symbol and try again."
        except Exception as e:
            return f"Error fetching price data: {str(e)}"

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
        Use this when the user asks about something you analyzed earlier, references "earlier", 
        "before", "what you said about", or asks follow-up questions about a previously analyzed token.
        
        If coin_query is ambiguous (like "it", "that token", "this"), try to infer from context
        by checking which tokens have been analyzed. If multiple tokens exist, return info about all of them.

        Args:
            coin_query: The cryptocurrency name or symbol (can be "it", "that", etc. - will try to infer)
            analysis_type: Type of analysis to retrieve (fundamental, price, sentiment, technical, or all)
        """
        try:
            # If query is ambiguous, check if we have any analysis history
            ambiguous_terms = ["it", "that", "this", "the token", "that token", "this token"]
            coin_query_lower = coin_query.lower().strip()
            
            # If ambiguous and we have history, try to infer
            if coin_query_lower in ambiguous_terms and analysis_history:
                # Return info about all analyzed tokens
                if len(analysis_history) == 1:
                    # Only one token analyzed, use it
                    coin_id = list(analysis_history.keys())[0]
                    history = analysis_history[coin_id]
                    coin_name = history.get("name", coin_id)
                else:
                    # Multiple tokens - return summary
                    result = "Multiple tokens have been analyzed. Here are the previous analyses:\n\n"
                    for coin_id, history in analysis_history.items():
                        coin_name = history.get("name", coin_id)
                        result += f"\n{'='*60}\n{coin_name} ({coin_id}):\n"
                        for atype in ["fundamental", "price", "sentiment", "technical"]:
                            if atype in history:
                                result += f"- {atype.capitalize()} analysis available\n"
                    result += "\nPlease specify which token you're asking about, or I can show all analyses."
                    return result
            else:
                # Normal lookup
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
                        result += f"\n{'='*60}\n{atype.capitalize()} Analysis:\n{history[atype]}\n"
                return result
            elif analysis_type in history:
                return f"{analysis_type.capitalize()} Analysis for {coin_name}:\n\n{history[analysis_type]}"
            else:
                return f"No {analysis_type} analysis found for {coin_name}."
        except CoinNotFoundError:
            # If not found and we have history, suggest analyzed tokens
            if analysis_history:
                analyzed = ", ".join([h.get("name", cid) for cid, h in analysis_history.items()])
                return f"Could not find cryptocurrency '{coin_query}'. Previously analyzed tokens: {analyzed}. Please specify one of these or provide the correct token name."
            return f"Could not find cryptocurrency '{coin_query}'."
        except Exception as e:
            return f"Error retrieving previous analysis: {str(e)}"

    return [
        Tool(
            name="get_coin_info",
            func=get_coin_info,
            description="Get basic information about a cryptocurrency (name, symbol, coin ID only - NO PRICE). Use this first when encountering a new token to verify it exists. For price queries, use get_coin_price instead.",
        ),
        Tool(
            name="get_coin_price",
            func=get_coin_price,
            description="Get current price and basic market data (price, market cap, volume, 24h changes). Use this when user asks about price, current value, 'how much is X worth', market cap, or 24h price changes. This is a quick lookup tool for current market data.",
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
            description="Retrieve previous analysis results. Use when user references earlier analyses, asks follow-up questions like 'What about its performance?', 'What are the risks?', 'What did you say about X earlier?', or asks for comparisons. Can handle ambiguous references like 'it', 'that token' by inferring from conversation context.",
        ),
    ]

