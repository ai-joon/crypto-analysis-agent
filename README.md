# Crypto Token Analysis Chat Agent

An AI-powered conversational agent that provides comprehensive cryptocurrency analysis using real-time data, multiple analysis dimensions, and intelligent conversation management.

## Features

### Core Capabilities
- **Multi-dimensional Analysis**: Fundamental, Price, Sentiment, and Technical analysis
- **Real-time Data**: Integration with CoinGecko API for live cryptocurrency data
- **Conversational AI**: Natural language interface with context memory using LangChain
- **Autonomous Analysis Selection**: Intelligently chooses relevant analysis types based on user queries
- **Multi-turn Conversations**: Maintains context across the conversation for follow-up questions
- **Analysis Memory**: Remembers previous analyses for comparisons and references
- **Guardrails**: Stays focused on cryptocurrency domain with polite redirection

### Analysis Types Implemented

#### 1. **Fundamental Analysis**
- Market capitalization and ranking
- Trading volume and liquidity metrics
- Circulating supply, total supply, and max supply
- Volume/Market Cap ratio analysis
- Fully Diluted Valuation (FDV)
- Tokenomics and supply inflation metrics
- Project description and overview

#### 2. **Price Analysis**
- Current price and 24h/7d/30d price changes
- Historical price trends and patterns
- Volatility assessment and classification
- Support and resistance levels
- All-Time High (ATH) and All-Time Low (ATL) analysis
- Price position analysis

#### 3. **Sentiment Analysis**
- Social media metrics (Twitter, Reddit, Telegram)
- Community engagement indicators
- Fear & Greed Index integration
- Sentiment score calculation
- Market sentiment classification
- Social media activity analysis

#### 4. **Technical Analysis**
- Simple Moving Averages (SMA 7, 20, 50)
- Relative Strength Index (RSI)
- MACD (Moving Average Convergence Divergence)
- Moving average crossover signals
- Overbought/oversold conditions
- Technical indicator summary

## Architecture

The system is built with a modular architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                     User (CLI Interface)                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                   LangChain Agent                            │
│  - Conversation Memory                                       │
│  - Tool Selection & Orchestration                            │
│  - Context Management                                        │
└─────────┬────────────────────────────────────────────────────┘
          │
          │  Uses Tools
          ▼
┌─────────────────────────────────────────────────────────────┐
│                     Analysis Tools                           │
│  ┌───────────────┐  ┌───────────────┐  ┌─────────────────┐ │
│  │  Fundamental  │  │     Price     │  │    Sentiment    │ │
│  │   Analyzer    │  │   Analyzer    │  │    Analyzer     │ │
│  └───────┬───────┘  └───────┬───────┘  └────────┬────────┘ │
│          │                   │                    │          │
│  ┌───────▼───────┐  ┌───────▼────────────────────▼────────┐ │
│  │   Technical   │  │        Data Fetcher                  │ │
│  │   Analyzer    │  │  - CoinGecko API Integration         │ │
│  └───────┬───────┘  │  - Data Caching                      │ │
│          │          │  - Coin ID Resolution                │ │
│          └──────────┴──────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                  ┌─────────────────────┐
                  │  External APIs      │
                  │  - CoinGecko        │
                  │  - Fear & Greed     │
                  └─────────────────────┘
```

### Component Details

1. **CLI Interface** (`main.py`): Rich console interface with markdown support
2. **Agent** (`src/agent.py`): LangChain-based conversational agent with OpenAI Functions
3. **Data Fetcher** (`src/data_fetcher.py`): API integration and data retrieval with caching
4. **Analyzers** (`src/analyzers.py`): Specialized analysis modules for each dimension
5. **Memory System**: ConversationBufferMemory for context retention

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key (GPT-4 or GPT-3.5-turbo)
- Internet connection for API access

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd crypto-analysis-agent
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.env` file in the project root:

```bash
# Copy the template
cp env.template .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Required:**
- `OPENAI_API_KEY`: Your OpenAI API key (get it from https://platform.openai.com/api-keys)

**Optional:**
- CoinGecko API is free and doesn't require a key for basic usage
- Additional API keys can be added for enhanced features (CoinMarketCap, NewsAPI)

### 5. Run the Application

```bash
python main.py
```

## 💡 Usage Examples

### Basic Usage

```
You: Tell me about Bitcoin

Agent: [Performs comprehensive analysis across all dimensions]
- Fundamental metrics
- Price trends and volatility
- Sentiment indicators
- Technical analysis
```

### Specific Analysis

```
You: What's the price trend of Ethereum?

Agent: [Focuses on price and technical analysis]
- Price changes and volatility
- Support/resistance levels
- Technical indicators
```

### Follow-up Questions

```
You: Tell me about Bitcoin

Agent: [Provides Bitcoin analysis]

You: Now analyze Ethereum

Agent: [Provides Ethereum analysis]

You: How does Ethereum's sentiment compare to Bitcoin?

Agent: [Retrieves previous analyses and compares sentiment metrics]
```

### Conversational Context

```
You: What's the RSI for Bitcoin?

Agent: [Performs technical analysis and provides RSI value]

You: What about Ethereum?

Agent: [Understands context and provides Ethereum's RSI]
```

## 🎯 Supported Commands

While in the chat interface:

- **Natural questions**: Ask anything about cryptocurrencies
- **`help`**: Display help information
- **`clear`**: Reset conversation memory
- **`exit`** or **`quit`**: Exit the application

## 🔧 Configuration

### Model Selection

The agent automatically tries to use GPT-4 and falls back to GPT-3.5-turbo if GPT-4 is not available.

To force a specific model, edit `main.py`:

```python
agent = CryptoAnalysisAgent(openai_api_key, model="gpt-3.5-turbo")
```

### Cache Duration

API responses are cached for 5 minutes by default. To change this, edit `src/data_fetcher.py`:

```python
self.cache_duration = 300  # Change to desired seconds
```

## Data Sources

- **CoinGecko API**: Primary data source for cryptocurrency information
  - No API key required for basic usage
  - Rate limits: ~50 calls/minute for free tier
  - Provides: price data, market data, historical data, community metrics

- **Alternative.me API**: Fear & Greed Index
  - Free public API
  - No authentication required

## 🧪 Example Conversations

### Example 1: Comprehensive Analysis

```
You: Tell me about Ethereum

Agent: I'll perform a comprehensive analysis of Ethereum (ETH) for you...

**Fundamental Analysis:**
- Market Cap: $221B (Rank #2)
- Trading Volume: $15.2B
- Circulating Supply: 120M ETH
- Volume/Market Cap: 6.8% (healthy liquidity)

**Price Analysis:**
- Current Price: $1,847
- 24h Change: -2.1%
- 7d Change: +3.2%
- Volatility: Moderate
- Support: $1,780 | Resistance: $1,920

**Sentiment Analysis:**
- Sentiment Score: 64/100 (Positive)
- Twitter Followers: 3.2M
- Reddit Subscribers: 1.5M
- Fear & Greed Index: 58 (Greed)

**Technical Analysis:**
- RSI (14): 62 (Neutral to slightly overbought)
- 7-day SMA: Above current price (Bullish)
- MACD: Positive (Bullish momentum)
```

### Example 2: Comparative Analysis

```
You: Compare Bitcoin and Ethereum sentiment

Agent: Let me retrieve the sentiment data for both...

Bitcoin Sentiment:
- Score: 71/100 (Very Positive)
- Social mentions up 18%
- Fear & Greed: 62

Ethereum Sentiment:
- Score: 64/100 (Positive)
- Social mentions up 23%
- Fear & Greed: 58

Comparison:
Bitcoin shows slightly stronger positive sentiment, but Ethereum has
faster-growing social engagement...
```

## 🎨 Project Structure

```
crypto-analysis-agent/
├── main.py                 # CLI interface entry point
├── requirements.txt        # Python dependencies
├── env.template           # Environment variable template
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── ARCHITECTURE.md       # Detailed architecture documentation
└── src/
    ├── __init__.py       # Package initialization
    ├── agent.py          # LangChain agent implementation
    ├── data_fetcher.py   # API integration and data fetching
    └── analyzers.py      # Analysis modules (4 types)
```

## 🚧 Limitations

1. **API Rate Limits**: CoinGecko free tier has rate limits (~50 calls/minute)
2. **Data Accuracy**: Real-time data depends on external API availability
3. **Historical Data**: Limited to data available from CoinGecko
4. **Sentiment Analysis**: Based on available social metrics (may not include all platforms)
5. **Not Financial Advice**: This tool is for educational purposes only

## 🔮 Future Enhancements

Potential improvements and additional features:

- [ ] Persistent conversation history across sessions
- [ ] Comparative analysis tool for side-by-side token comparison
- [ ] Integration with additional data sources (CoinMarketCap, Messari)
- [ ] Advanced charting and visualization
- [ ] Custom alerts and notifications
- [ ] Portfolio tracking and analysis
- [ ] Historical analysis playback
- [ ] Evaluation metrics for analysis quality
- [ ] Web interface (Streamlit or FastAPI)
- [ ] Multi-language support

## 🐛 Troubleshooting

### "OPENAI_API_KEY not found"
- Make sure you've created a `.env` file
- Verify your API key is correctly set
- Check that `python-dotenv` is installed

### "Could not find cryptocurrency"
- Check the spelling of the token name/symbol
- Try alternative names (e.g., "BTC" vs "Bitcoin")
- Ensure the token is listed on CoinGecko

### "Rate limit exceeded"
- Wait a minute and try again
- CoinGecko free tier has rate limits
- Consider implementing longer cache durations

### "Model not found" or GPT-4 errors
- The agent will automatically fall back to GPT-3.5-turbo
- Verify your OpenAI account has access to the model
- Check your API key has sufficient credits

## 📝 Development

### Running Tests

```bash
# Install development dependencies
pip install pytest pytest-cov

# Run tests (when implemented)
pytest tests/
```

### Code Style

The project follows PEP 8 style guidelines. Use tools like `black` and `flake8`:

```bash
pip install black flake8
black src/ main.py
flake8 src/ main.py
```

## 📄 License

This project is created as a take-home challenge submission. See the challenge document for specific terms.

## 🙏 Acknowledgments

- **CoinGecko** for providing comprehensive cryptocurrency data API
- **OpenAI** for GPT models powering the conversational interface
- **LangChain** for agent orchestration framework
- **Alternative.me** for Fear & Greed Index data

## 📧 Support

For issues, questions, or suggestions related to this project, please refer to the challenge submission guidelines.

---

**Disclaimer**: This tool provides educational information only and should not be considered financial advice. Cryptocurrency investments carry significant risk. Always conduct your own research (DYOR) before making investment decisions.

