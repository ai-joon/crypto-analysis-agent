"""Technical analysis module for cryptocurrency tokens."""

from typing import List
from src.data_fetcher import CryptoDataFetcher


class TechnicalAnalyzer:
    """Performs technical analysis on cryptocurrency tokens."""

    def __init__(self, data_fetcher: CryptoDataFetcher):
        self.data_fetcher = data_fetcher

    def calculate_sma(self, prices: List[float], period: int) -> float:
        """Calculate Simple Moving Average."""
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period

    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return None

        gains = []
        losses = []

        for i in range(1, len(prices)):
            change = prices[i] - prices[i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def analyze(self, coin_id: str, coin_name: str) -> str:
        """
        Perform technical analysis on a cryptocurrency.

        Args:
            coin_id: CoinGecko coin ID
            coin_name: Human-readable coin name

        Returns:
            Formatted analysis report
        """
        try:
            historical_30d = self.data_fetcher.get_historical_prices(coin_id, days=30)
            historical_90d = self.data_fetcher.get_historical_prices(coin_id, days=90)
            market_data = self.data_fetcher.get_market_data(coin_id)

            if not historical_30d or not historical_90d:
                return "Insufficient historical data for technical analysis."

            current_price = market_data["current_price"]
            prices_30d = [p["price"] for p in historical_30d]
            prices_90d = [p["price"] for p in historical_90d]

            # Calculate moving averages
            sma_7 = self.calculate_sma(prices_30d, 7)
            sma_20 = self.calculate_sma(prices_30d, 20)
            sma_50 = (
                self.calculate_sma(prices_90d, 50) if len(prices_90d) >= 50 else None
            )

            # Calculate RSI
            rsi = self.calculate_rsi(prices_30d, 14)

            # Calculate MACD (simplified)
            ema_12 = self.calculate_sma(prices_30d, 12)  # Using SMA as approximation
            ema_26 = self.calculate_sma(prices_30d, 26)
            macd_line = ema_12 - ema_26 if ema_12 and ema_26 else None

            # Build analysis report
            report = f"""**Technical Analysis for {coin_name}:**

**Moving Averages:**
- Current Price: ${current_price:,.2f}"""

            if sma_7:
                report += f"\n- 7-Day SMA: ${sma_7:,.2f}"
                if current_price > sma_7:
                    report += " (Price above - bullish)"
                else:
                    report += " (Price below - bearish)"

            if sma_20:
                report += f"\n- 20-Day SMA: ${sma_20:,.2f}"
                if current_price > sma_20:
                    report += " (Price above - bullish)"
                else:
                    report += " (Price below - bearish)"

            if sma_50:
                report += f"\n- 50-Day SMA: ${sma_50:,.2f}"
                if current_price > sma_50:
                    report += " (Price above - bullish)"
                else:
                    report += " (Price below - bearish)"

            # Moving Average Crossover
            report += f"\n\n**Moving Average Analysis:**\n"
            if sma_7 and sma_20:
                if sma_7 > sma_20:
                    report += "Golden Cross pattern detected (7-day SMA above 20-day SMA) - Bullish signal. "
                    report += "Short-term momentum is stronger than medium-term, suggesting upward trend."
                else:
                    report += "Death Cross pattern detected (7-day SMA below 20-day SMA) - Bearish signal. "
                    report += "Short-term momentum is weaker than medium-term, suggesting downward trend."

            # RSI Analysis
            if rsi:
                report += f"""

**Momentum Indicators:**
- RSI (14): {rsi:.1f}"""

                if rsi >= 70:
                    report += " - **Overbought**"
                    report += "\n  The token is in overbought territory, which may indicate a potential price correction or consolidation ahead."
                elif rsi >= 60:
                    report += " - **Bullish**"
                    report += "\n  Positive momentum with room for continued growth before reaching overbought levels."
                elif rsi >= 40:
                    report += " - **Neutral**"
                    report += "\n  Balanced momentum with no clear directional bias. Waiting for stronger signals."
                elif rsi >= 30:
                    report += " - **Bearish**"
                    report += "\n  Negative momentum with potential for further decline, but approaching oversold levels."
                else:
                    report += " - **Oversold**"
                    report += "\n  The token is in oversold territory, which may indicate a potential buying opportunity or bounce."

            # MACD Analysis
            if macd_line:
                report += f"""

**MACD Indicator:**
- MACD Line: {macd_line:+.4f}"""

                if macd_line > 0:
                    report += " - **Bullish** (above zero line)"
                    report += "\n  Short-term trend is stronger than long-term, indicating bullish momentum."
                else:
                    report += " - **Bearish** (below zero line)"
                    report += "\n  Long-term trend is stronger than short-term, indicating bearish momentum."

            # Overall Technical Summary
            report += f"""

**Technical Summary:**"""

            bullish_signals = 0
            bearish_signals = 0

            if sma_7 and current_price > sma_7:
                bullish_signals += 1
            elif sma_7:
                bearish_signals += 1

            if sma_20 and current_price > sma_20:
                bullish_signals += 1
            elif sma_20:
                bearish_signals += 1

            if rsi and 40 <= rsi <= 60:
                pass  # Neutral
            elif rsi and rsi > 60:
                bullish_signals += 1
            elif rsi:
                bearish_signals += 1

            if macd_line and macd_line > 0:
                bullish_signals += 1
            elif macd_line:
                bearish_signals += 1

            if bullish_signals > bearish_signals:
                report += f"\nTechnical indicators are predominantly bullish ({bullish_signals} bullish vs {bearish_signals} bearish signals). "
                report += f"{coin_name} shows positive technical momentum with multiple indicators supporting upward price movement. "
                report += "Traders may consider long positions, but should wait for confirmation and use appropriate risk management."
            elif bearish_signals > bullish_signals:
                report += f"\nTechnical indicators are predominantly bearish ({bearish_signals} bearish vs {bullish_signals} bullish signals). "
                report += f"{coin_name} shows negative technical momentum with multiple indicators suggesting downward pressure. "
                report += "Caution is advised for long positions. Short-term traders may look for shorting opportunities or wait for reversal signals."
            else:
                report += f"\nTechnical indicators are mixed ({bullish_signals} bullish vs {bearish_signals} bearish signals). "
                report += f"{coin_name} is in a consolidation phase with conflicting signals. "
                report += "The market is indecisive. Traders should wait for clearer technical signals before taking significant positions."

            return report

        except Exception as e:
            return f"Error performing technical analysis: {str(e)}"
