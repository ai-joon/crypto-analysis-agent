"""Price analysis module for cryptocurrency tokens."""

import statistics
from src.repositories.coin_repository import CoinRepository
from src.core.interfaces import BaseAnalyzer


class PriceAnalyzer(BaseAnalyzer):
    """Performs price and trend analysis on cryptocurrency tokens."""

    def __init__(self, repository: CoinRepository):
        """
        Initialize price analyzer.

        Args:
            repository: Coin repository instance
        """
        self.repository = repository

    def analyze(self, coin_id: str, coin_name: str) -> str:
        """
        Perform price analysis on a cryptocurrency.

        Args:
            coin_id: CoinGecko coin ID
            coin_name: Human-readable coin name

        Returns:
            Formatted analysis report
        """
        try:
            market_data = self.repository.get_market_data(coin_id)
            historical_7d = self.repository.get_historical_prices(coin_id, days=7)
            historical_30d = self.repository.get_historical_prices(coin_id, days=30)

            current_price = market_data["current_price"]
            price_change_24h = market_data["price_change_percentage_24h"]
            price_change_7d = market_data["price_change_percentage_7d"]
            price_change_30d = market_data["price_change_percentage_30d"]
            high_24h = market_data["high_24h"]
            low_24h = market_data["low_24h"]
            ath = market_data["ath"]
            atl = market_data["atl"]

            # Calculate volatility
            if len(historical_7d) > 1:
                prices_7d = [p["price"] for p in historical_7d]
                volatility_7d = (
                    statistics.stdev(prices_7d) / statistics.mean(prices_7d) * 100
                )
            else:
                volatility_7d = 0

            # Identify support and resistance levels
            if len(historical_30d) >= 30:
                prices_30d = [p["price"] for p in historical_30d]
                sorted_prices = sorted(prices_30d)
                support_level = sorted_prices[
                    len(sorted_prices) // 4
                ]  # 25th percentile
                resistance_level = sorted_prices[
                    3 * len(sorted_prices) // 4
                ]  # 75th percentile
            else:
                support_level = low_24h
                resistance_level = high_24h

            # Build analysis report
            report = f"""**Price Analysis for {coin_name}:**

                        **Current Price Action:**
                        - Current Price: ${current_price:,.2f}
                        - 24h Change: {price_change_24h:+.2f}%
                        - 7d Change: {price_change_7d:+.2f}%
                        - 30d Change: {price_change_30d:+.2f}%

                        **24h Price Range:**
                        - High: ${high_24h:,.2f}
                        - Low: ${low_24h:,.2f}
                        - Range: ${high_24h - low_24h:,.2f} ({(high_24h - low_24h) / low_24h * 100:.2f}%)

                        **Historical Context:**
                        - All-Time High: ${ath:,.2f} ({(current_price - ath) / ath * 100:.2f}% from ATH)
                        - All-Time Low: ${atl:,.2f} ({(current_price - atl) / atl * 100:.2f}% from ATL)

                        **Volatility Assessment:**
                        - 7-Day Volatility: {volatility_7d:.2f}%
                        - Classification: """

            if volatility_7d < 5:
                report += "Low volatility - relatively stable price movement"
            elif volatility_7d < 10:
                report += "Moderate volatility - normal market fluctuations"
            elif volatility_7d < 20:
                report += "High volatility - significant price swings"
            else:
                report += "Extreme volatility - very large price movements"

            report += f"""

**Support and Resistance Levels:**
- Support Level: ${support_level:,.2f} (potential buying opportunity)
- Current Price: ${current_price:,.2f}
- Resistance Level: ${resistance_level:,.2f} (potential selling pressure)

**Price Trend Analysis:**"""

            if price_change_7d > 5:
                report += f"\n{coin_name} is in a strong uptrend over the past week (+{price_change_7d:.2f}%). "
                report += "Bullish momentum is evident with buyers in control. "
            elif price_change_7d > 0:
                report += f"\n{coin_name} shows slight upward momentum (+{price_change_7d:.2f}%) over the past week. "
                report += "The trend is mildly bullish with cautious buying. "
            elif price_change_7d > -5:
                report += f"\n{coin_name} shows slight downward pressure ({price_change_7d:.2f}%) over the past week. "
                report += "The trend is mildly bearish with some selling activity. "
            else:
                report += f"\n{coin_name} is experiencing a significant downtrend ({price_change_7d:.2f}%) over the past week. "
                report += "Bearish momentum is strong with sellers in control. "

            # Price position analysis
            distance_to_resistance = (
                (resistance_level - current_price) / current_price * 100
            )
            distance_to_support = (current_price - support_level) / current_price * 100

            if distance_to_resistance < 5:
                report += f"Price is near resistance (${resistance_level:.2f}), which may act as a ceiling. "
            elif distance_to_support < 5:
                report += f"Price is near support (${support_level:.2f}), which may provide a floor. "
            else:
                report += f"Price is trading in the middle range between support and resistance levels. "

            return report

        except Exception as e:
            return f"Error performing price analysis: {str(e)}"
