"""Fundamental analysis module for cryptocurrency tokens."""

from src.data_fetcher import CryptoDataFetcher


class FundamentalAnalyzer:
    """Performs fundamental analysis on cryptocurrency tokens."""

    def __init__(self, data_fetcher: CryptoDataFetcher):
        self.data_fetcher = data_fetcher

    def analyze(self, coin_id: str, coin_name: str) -> str:
        """
        Perform fundamental analysis on a cryptocurrency.

        Args:
            coin_id: CoinGecko coin ID
            coin_name: Human-readable coin name

        Returns:
            Formatted analysis report
        """
        try:
            market_data = self.data_fetcher.get_market_data(coin_id)
            description = self.data_fetcher.get_coin_description(coin_id)

            # Calculate metrics
            current_price = market_data["current_price"]
            market_cap = market_data["market_cap"]
            total_volume = market_data["total_volume"]
            circulating_supply = market_data["circulating_supply"]
            total_supply = market_data["total_supply"]
            max_supply = market_data["max_supply"]
            market_cap_rank = market_data["market_cap_rank"]

            # Volume to Market Cap ratio
            volume_mcap_ratio = (total_volume / market_cap * 100) if market_cap else 0

            # Supply metrics
            supply_inflation = (
                ((total_supply - circulating_supply) / circulating_supply * 100)
                if circulating_supply and total_supply
                else None
            )

            # Build analysis report
            report = f"""**Fundamental Analysis for {coin_name}:**

**Market Metrics:**
- Market Cap: ${market_cap:,.0f} (Rank #{market_cap_rank})
- Current Price: ${current_price:,.2f}
- 24h Trading Volume: ${total_volume:,.0f}
- Volume/Market Cap Ratio: {volume_mcap_ratio:.2f}% {"(healthy liquidity)" if volume_mcap_ratio > 5 else "(low liquidity)"}

**Supply Metrics:**
- Circulating Supply: {circulating_supply:,.0f} {coin_name}
- Total Supply: {total_supply:,.0f} {coin_name if total_supply else "N/A"}
- Max Supply: {max_supply:,.0f} {coin_name if max_supply else "Unlimited (no max cap)"}"""

            if supply_inflation is not None and supply_inflation > 0:
                report += f"\n- Supply Inflation: {supply_inflation:.2f}% (tokens yet to be released)"

            # Fully Diluted Valuation
            if max_supply and current_price:
                fdv = max_supply * current_price
                report += f"\n- Fully Diluted Valuation: ${fdv:,.0f}"
            elif total_supply and current_price:
                fdv = total_supply * current_price
                report += (
                    f"\n- Fully Diluted Valuation: ${fdv:,.0f} (based on total supply)"
                )

            # Brief description
            if description:
                desc_short = (
                    description[:500] + "..." if len(description) > 500 else description
                )
                report += f"\n\n**Project Overview:**\n{desc_short}"

            # Liquidity assessment
            report += f"\n\n**Liquidity Assessment:**\n"
            if volume_mcap_ratio > 10:
                report += "Excellent liquidity with high trading activity. The token can be easily bought or sold without significant price impact."
            elif volume_mcap_ratio > 5:
                report += "Good liquidity with healthy trading volume. Moderate ease of entry and exit."
            elif volume_mcap_ratio > 2:
                report += "Fair liquidity. Some slippage may occur on larger trades."
            else:
                report += "Low liquidity. Large trades may experience significant price impact and slippage."

            return report

        except Exception as e:
            return f"Error performing fundamental analysis: {str(e)}"
