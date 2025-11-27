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
- **Ambiguity Handling**: Asks clarifying questions when queries are unclear or ambiguous
- **General Topic Support**: Handles both specific cryptocurrency queries and general blockchain/crypto technology topics

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

1. **CLI Interface** (`src/ui/cli.py`): Rich console interface with markdown support
2. **Agent** (`src/agents/agent.py`): LangChain-based conversational agent with OpenAI Functions
3. **Repository** (`src/repositories/coin_repository.py`): API integration and data retrieval with caching
4. **Analyzers** (`src/analyzers/`): Specialized analysis modules for each dimension:
   - `fundamental_analyzer.py`: Fundamental analysis
   - `price_analyzer.py`: Price and trend analysis
   - `sentiment_analyzer.py`: Sentiment and social metrics analysis
   - `technical_analyzer.py`: Technical indicators analysis
5. **Memory System**: Conversation history and analysis history for context retention

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (GPT-4 or GPT-3.5-turbo)
- Internet connection for API access

## Setup Instructions



### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

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
- `NEWSAPI_KEY`: NewsAPI key for cryptocurrency and blockchain news features (get it from https://newsapi.org/)
- CoinGecko API is free and doesn't require a key for basic usage

### 4. Run the Application

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

### Ambiguity Handling

```
You: Tell me about ETH

Agent: I'd be happy to help! When you say 'Tell me about ETH', would you like:
- A comprehensive analysis (fundamental, price, sentiment, technical)?
- Just the current price and market data?
- Recent news articles?
- A specific type of analysis?
Please let me know what you're most interested in!

You: Comprehensive analysis

Agent: [Performs comprehensive analysis]
```

### General Blockchain Topics

```
You: Provide me some news about blockchain

Agent: [Fetches general blockchain technology news articles]

You: What's happening with DeFi?

Agent: [Searches for DeFi-related news and information]
```

## Data Sources

- **CoinGecko API**: Primary data source for cryptocurrency information
  - No API key required for basic usage
  - Rate limits: ~50 calls/minute for free tier
  - Provides: price data, market data, historical data, community metrics

- **Alternative.me API**: Fear & Greed Index
  - Free public API
  - No authentication required

- **NewsAPI**: News articles for cryptocurrencies and blockchain topics
  - Optional API key (set `NEWSAPI_KEY` in `.env`)
  - Provides: Recent news articles, media coverage, blockchain technology news
  - Supports both specific cryptocurrency queries and general blockchain topics

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
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── env.template              # Environment variable template
├── .gitignore               # Git ignore rules
├── README.md                # This file
├── ARCHITECTURE.md          # Detailed architecture documentation
└── src/
    ├── __init__.py          # Package initialization
    ├── agents/              # Agent implementation
    │   ├── agent.py         # LangChain agent class
    │   ├── tools.py         # Agent tools and functions
    │   └── prompts.py       # System prompts
    ├── analyzers/            # Analysis modules
    │   ├── fundamental_analyzer.py
    │   ├── price_analyzer.py
    │   ├── sentiment_analyzer.py
    │   └── technical_analyzer.py
    ├── api/                  # API clients
    │   ├── coingecko_client.py
    │   ├── fear_greed_client.py
    │   └── newsapi_client.py
    ├── repositories/         # Data access layer
    │   └── coin_repository.py
    ├── services/             # Business logic
    │   ├── coin_service.py
    │   └── analysis_service.py
    ├── ui/                   # User interface
    │   └── cli.py
    └── core/                 # Core utilities
        ├── cache.py
        ├── exceptions.py
        └── interfaces.py
```

## 🚧 Limitations

1. **API Rate Limits**: CoinGecko free tier has rate limits (~50 calls/minute)
2. **Data Accuracy**: Real-time data depends on external API availability
3. **Historical Data**: Limited to data available from CoinGecko
4. **Sentiment Analysis**: Based on available social metrics (may not include all platforms)
5. **Not Financial Advice**: This tool is for educational purposes only

