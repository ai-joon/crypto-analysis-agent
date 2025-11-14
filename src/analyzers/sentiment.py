"""Sentiment analysis module for cryptocurrency tokens."""

from src.data_fetcher import CryptoDataFetcher


class SentimentAnalyzer:
    """Performs sentiment analysis on cryptocurrency tokens."""

    def __init__(self, data_fetcher: CryptoDataFetcher):
        self.data_fetcher = data_fetcher

    def analyze(self, coin_id: str, coin_name: str) -> str:
        """
        Perform sentiment analysis on a cryptocurrency.

        Args:
            coin_id: CoinGecko coin ID
            coin_name: Human-readable coin name

        Returns:
            Formatted analysis report
        """
        try:
            community_data = self.data_fetcher.get_community_data(coin_id)
            market_data = self.data_fetcher.get_market_data(coin_id)
            fng_data = self.data_fetcher.get_fear_greed_index()

            twitter_followers = community_data.get("twitter_followers", 0)
            reddit_subscribers = community_data.get("reddit_subscribers", 0)
            reddit_posts = community_data.get("reddit_average_posts_48h", 0)
            reddit_comments = community_data.get("reddit_average_comments_48h", 0)
            telegram_users = community_data.get("telegram_channel_user_count", 0)

            price_change_7d = market_data.get("price_change_percentage_7d", 0)

            # Calculate sentiment score based on available data
            sentiment_score = 50  # Neutral baseline

            # Adjust based on price action
            if price_change_7d > 10:
                sentiment_score += 15
            elif price_change_7d > 5:
                sentiment_score += 10
            elif price_change_7d > 0:
                sentiment_score += 5
            elif price_change_7d > -5:
                sentiment_score -= 5
            elif price_change_7d > -10:
                sentiment_score -= 10
            else:
                sentiment_score -= 15

            # Adjust based on social engagement
            if reddit_posts and reddit_posts > 20:
                sentiment_score += 5
            if reddit_comments and reddit_comments > 100:
                sentiment_score += 5

            # Cap sentiment score
            sentiment_score = max(0, min(100, sentiment_score))

            # Determine sentiment classification
            if sentiment_score >= 70:
                sentiment_class = "Very Positive"
            elif sentiment_score >= 60:
                sentiment_class = "Positive"
            elif sentiment_score >= 40:
                sentiment_class = "Neutral"
            elif sentiment_score >= 30:
                sentiment_class = "Negative"
            else:
                sentiment_class = "Very Negative"

            # Build analysis report
            report = f"""**Sentiment Analysis for {coin_name}:**

**Overall Sentiment Score: {sentiment_score}/100 - {sentiment_class}**

**Community Engagement:**"""

            if twitter_followers:
                report += f"\n- Twitter Followers: {twitter_followers:,}"
            if reddit_subscribers:
                report += f"\n- Reddit Subscribers: {reddit_subscribers:,}"
            if reddit_posts:
                report += f"\n- Reddit Posts (48h): {reddit_posts:.0f}"
            if reddit_comments:
                report += f"\n- Reddit Comments (48h): {reddit_comments:.0f}"
            if telegram_users:
                report += f"\n- Telegram Members: {telegram_users:,}"

            if not any([twitter_followers, reddit_subscribers, telegram_users]):
                report += "\n- Limited community data available for this token"

            report += f"""

**Market Sentiment Indicators:**
- Crypto Fear & Greed Index: {fng_data['value']}/100 ({fng_data['value_classification']})
- Recent Price Action: {price_change_7d:+.2f}% over 7 days"""

            if price_change_7d > 5:
                report += " - indicating positive market sentiment"
            elif price_change_7d < -5:
                report += " - indicating negative market sentiment"
            else:
                report += " - indicating neutral market sentiment"

            report += f"""

**Sentiment Analysis:**"""

            if sentiment_score >= 70:
                report += f"\n{coin_name} is experiencing very positive sentiment across multiple indicators. "
                report += "The community is highly engaged, and price action reflects strong bullish sentiment. "
                report += (
                    "This could indicate FOMO (Fear of Missing Out) among investors. "
                )
                report += "Exercise caution as extreme positive sentiment can sometimes precede corrections."
            elif sentiment_score >= 60:
                report += f"\n{coin_name} shows positive sentiment overall. "
                report += "Community engagement is healthy, and market participants are generally optimistic. "
                report += "This suggests confidence in the project's direction and potential for continued growth."
            elif sentiment_score >= 40:
                report += f"\n{coin_name} exhibits neutral sentiment. "
                report += "The market is neither particularly bullish nor bearish on this asset. "
                report += "This could indicate a period of consolidation or uncertainty about future direction. "
                report += "Traders are likely waiting for clearer signals before taking strong positions."
            elif sentiment_score >= 30:
                report += f"\n{coin_name} is facing negative sentiment. "
                report += "Community engagement may be declining, and price action reflects bearish sentiment. "
                report += "Market participants are cautious or pessimistic about near-term prospects. "
                report += "This could present a buying opportunity for contrarians, but risk remains elevated."
            else:
                report += f"\n{coin_name} is experiencing very negative sentiment. "
                report += "The community may be discouraged, and price action reflects strong selling pressure. "
                report += "This represents high risk but could also be a capitulation point for long-term investors. "
                report += "Fundamental analysis is critical before considering entry at these levels."

            # Social media insights
            if reddit_posts and reddit_comments:
                engagement_ratio = (
                    reddit_comments / reddit_posts if reddit_posts > 0 else 0
                )
                report += "\n\n**Social Media Activity:**\n"
                report += f"Reddit engagement ratio is {engagement_ratio:.1f} comments per post"
                if engagement_ratio > 10:
                    report += (
                        ", indicating high community interest and active discussions."
                    )
                elif engagement_ratio > 5:
                    report += ", suggesting moderate community engagement."
                else:
                    report += ", showing relatively low discussion activity."

            return report

        except Exception as e:
            return f"Error performing sentiment analysis: {str(e)}"
