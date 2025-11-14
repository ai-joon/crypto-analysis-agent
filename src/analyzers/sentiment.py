"""Sentiment analysis module for cryptocurrency tokens."""

from datetime import datetime

from src.repositories.coin_repository import CoinRepository
from src.core.interfaces import BaseAnalyzer


class SentimentAnalyzer(BaseAnalyzer):
    """Performs sentiment analysis on cryptocurrency tokens."""

    def __init__(self, repository: CoinRepository):
        """
        Initialize sentiment analyzer.

        Args:
            repository: Coin repository instance
        """
        self.repository = repository

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
            community_data = self.repository.get_community_data(coin_id)
            market_data = self.repository.get_market_data(coin_id)
            fng_data = self.repository.get_fear_greed_index()
            
            # Get coin symbol for news search
            coin_data = self.repository.get_coin_data(coin_id)
            coin_symbol = coin_data.get("symbol", "").upper()

            twitter_followers = community_data.get("twitter_followers", 0)
            reddit_subscribers = community_data.get("reddit_subscribers", 0)
            reddit_posts = community_data.get("reddit_average_posts_48h", 0)
            reddit_comments = community_data.get("reddit_average_comments_48h", 0)
            telegram_users = community_data.get("telegram_channel_user_count", 0)

            price_change_7d = market_data.get("price_change_percentage_7d", 0)

            # Fetch latest news articles
            news_articles = self.repository.get_news_articles(
                coin_name, coin_symbol, page_size=10
            )
            news_count = len(news_articles)

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

            # Adjust based on news coverage
            if news_count > 0:
                # More news articles can indicate higher interest/attention
                if news_count >= 8:
                    sentiment_score += 5
                elif news_count >= 5:
                    sentiment_score += 3
                elif news_count >= 3:
                    sentiment_score += 2

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

            report += "\n\n**Sentiment Analysis:**"

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

            # News coverage section
            if news_count > 0:
                report += f"\n\n**Latest News Coverage ({news_count} articles found):**\n"
                # Show top 5 most recent articles
                for i, article in enumerate(news_articles[:5], 1):
                    title = article.get("title", "No title")
                    source = article.get("source", {}).get("name", "Unknown source")
                    published = article.get("publishedAt", "")
                    
                    # Format date if available
                    if published:
                        try:
                            pub_date = datetime.fromisoformat(
                                published.replace("Z", "+00:00")
                            )
                            date_str = pub_date.strftime("%Y-%m-%d")
                        except (ValueError, AttributeError):
                            date_str = published[:10] if len(published) >= 10 else published
                    else:
                        date_str = "Unknown date"
                    
                    report += f"{i}. **{title}**\n"
                    report += f"   Source: {source} | Date: {date_str}\n"
                    
                    # Add URL if available
                    url = article.get("url")
                    if url:
                        report += f"   Link: {url}\n"
                    report += "\n"
                
                if news_count > 5:
                    report += f"*... and {news_count - 5} more articles*\n"
                
                report += "\n**News Impact:**\n"
                if news_count >= 8:
                    report += "High news coverage indicates significant market attention and potential volatility. "
                    report += "Monitor news developments closely as they can drive price movements."
                elif news_count >= 5:
                    report += "Moderate news coverage suggests ongoing interest. "
                    report += "Recent developments may influence market sentiment."
                else:
                    report += "Limited recent news coverage. "
                    report += "The token may be in a consolidation phase or awaiting major developments."
            elif news_count == 0 and self.repository.newsapi_client.api_key:
                report += "\n\n**News Coverage:**\n"
                report += "No recent news articles found for this cryptocurrency in the past 7 days. "
                report += "This could indicate low media attention or a quiet period for the project."

            return report

        except Exception as e:
            return f"Error performing sentiment analysis: {str(e)}"
