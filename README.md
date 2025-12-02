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
- **Multi-level Caching**: Combines TTL caching, semantic caching, and in-memory analysis history to reduce latency and API cost
- **LangSmith Integration**: Optional workflow tracing and observability for debugging and monitoring

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
│  │   Technical   │  │      Coin Repository & API Clients   │ │
│  │   Analyzer    │  │  - CoinGecko client                  │ │
│  └───────┬───────┘  │  - Fear & Greed client               │ │
│          │          │  - NewsAPI client                    │ │
│          └──────────┴──────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                  ┌─────────────────────┐
                  │  External APIs      │
                  │  - CoinGecko        │
                  │  - Fear & Greed     │
                  │  - NewsAPI          │
                  │  - LangSmith*       │
                  └─────────────────────┘
* LangSmith is used for tracing/observability rather than user-facing analysis
```

### Component Details

1. **CLI Interface** (`src/ui/cli.py`): Rich console interface with markdown support
2. **Agent** (`src/agents/agent.py`): LangChain-based conversational agent with OpenAI Functions and LangSmith tracing support
3. **Repository** (`src/repositories/coin_repository.py`): API integration and data retrieval with caching
4. **Analyzers** (`src/analyzers/`): Specialized analysis modules for each dimension:
   - `fundamental_analyzer.py`: Fundamental analysis
   - `price_analyzer.py`: Price and trend analysis
   - `sentiment_analyzer.py`: Sentiment and social metrics analysis
   - `technical_analyzer.py`: Technical indicators analysis
5. **Memory System**: Conversation history and analysis history for context retention
6. **LangSmith Tracing**: Optional observability layer for monitoring agent workflows, tool calls, and performance

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
- `OPENAI_MODEL`: Model to use (default: gpt-4o-mini)
- `CACHE_TTL`: Cache duration in seconds (default: 300)
- `SEMANTIC_CACHE_ENABLED`: Enable semantic caching (default: true)
- `SEMANTIC_CACHE_THRESHOLD`: Similarity threshold for cache matching (default: 0.85)
- `SEMANTIC_CACHE_SIZE`: Maximum cache entries (default: 1000)
- `SEMANTIC_CACHE_TTL`: Cache time-to-live in seconds (default: 3600)
- `LANGSMITH_ENABLED`: Enable LangSmith tracing (default: false)
- `LANGSMITH_API_KEY`: LangSmith API key for workflow tracing (get it from https://smith.langchain.com/)
- `LANGSMITH_PROJECT`: Project name for organizing traces (optional)
- CoinGecko API is free and doesn't require a key for basic usage

### 4. Run the Application

```bash
python main.py
```

## Usage Examples

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

- **LangSmith**: Observability and tracing platform (optional)
  - Optional API key (set `LANGSMITH_API_KEY` in `.env`)
  - Provides: Workflow tracing, performance monitoring, debugging tools
  - Enables comprehensive observability for agent operations and tool calls

## Evaluation Framework

The project includes a comprehensive evaluation framework to assess agent performance and accuracy.

### Performance Evaluation

Evaluates agent performance across multiple dimensions:

- **Component Testing**: Individual analyzer components (fundamental, price, sentiment, technical)
- **Integration Testing**: Agent conversational responses and tool selection
- **Memory Testing**: Conversation context and analysis history retention
- **Performance Metrics**: Response times, success rates, and overall scores

**Run Performance Evaluation:**
```bash
python run_evaluation.py --type performance
```

Generates `evaluation_report.json` with detailed metrics including:
- Analyzer success rates and response times
- Agent query handling performance
- Memory persistence verification
- Overall performance score

### Accuracy Evaluation (LLM-as-a-Judge)

Uses an LLM-as-a-Judge architecture to evaluate response quality:

- **Test Questions**: Common questions and edge cases from `evaluation/test_questions.json`
- **Evaluation Criteria**: Accuracy, completeness, relevance, tool selection, clarity
- **Scoring**: 0.0-1.0 scale (Poor to Excellent)
- **Multi-turn Scenarios**: Tests conversation context maintenance

**Run Accuracy Evaluation:**
```bash
python run_evaluation.py --type accuracy

# Or run both evaluations
python run_evaluation.py --type both

# Use different judge model
python run_evaluation.py --type accuracy --judge-model gpt-4
```

Generates `accuracy_evaluation_report.json` with:
- Individual question scores and feedback
- Category breakdown (comprehensive_analysis, price_query, etc.)
- Performance tier distribution
- Overall accuracy statistics

### Evaluation Reports

Both evaluations generate detailed JSON reports:
- `evaluation_report.json`: Performance metrics and component tests
- `accuracy_evaluation_report.json`: Accuracy scores and LLM judge feedback

See `evaluation/README.md` and `evaluation/README_ACCURACY.md` for detailed documentation.

## Semantic Caching

The agent includes semantic caching to reduce API costs and improve response times by reusing similar responses.

### How It Works

1. **Query Embedding**: Converts queries to embedding vectors using OpenAI's embedding model
2. **Similarity Search**: Finds similar cached queries using cosine similarity
3. **Threshold Matching**: Returns cached response if similarity exceeds threshold (default: 0.85)
4. **Expiration Validation**: Each cache entry has a 1-hour expiration deadline (configurable via `SEMANTIC_CACHE_TTL`)
5. **Response Validation**: Invalid responses (errors, API failures) are automatically filtered and not cached
6. **Persistence**: Cache is saved to `semantic_cache.json` and persists across restarts

### Benefits

- **Cost Savings**: Reduces OpenAI API calls for similar queries
- **Faster Responses**: Cached responses return instantly
- **Data Quality**: Only valid responses are cached (errors and API failures are filtered)
- **Automatic Expiration**: Entries expire after 1 hour to ensure data freshness
- **Persistence**: Cache survives restarts - automatically loaded on startup
- **Automatic**: Works transparently without code changes

### Configuration

Add to your `.env` file:

```bash
# Enable/disable semantic cache
SEMANTIC_CACHE_ENABLED=true

# Similarity threshold (0.0-1.0)
# Higher = more strict matching, Lower = more lenient matching
SEMANTIC_CACHE_THRESHOLD=0.85

# Maximum number of cached entries
SEMANTIC_CACHE_SIZE=1000

# Time-to-live in seconds (default: 1 hour)
SEMANTIC_CACHE_TTL=3600

# Optional: Custom cache file path
# SEMANTIC_CACHE_FILE=./cache/semantic_cache.json
```

### Usage

Semantic cache is automatically enabled when `SEMANTIC_CACHE_ENABLED=true`. It works transparently:

1. **First Query**: "Tell me about Bitcoin"
   - Cache miss → LLM call → Response cached

2. **Similar Query**: "What can you tell me about Bitcoin?"
   - Cache hit → Instant response (no LLM call)

3. **Different Query**: "What's the price of Ethereum?"
   - Cache miss → LLM call → New entry cached

### Cache Statistics

View cache statistics in the CLI:

```
> cache
```

Shows cache size, total hits, average hits per entry, and configuration settings.

**Cache Behavior**:
- Cache retrieval is only used for standalone queries (first query in a conversation) to maintain context accuracy
- All queries are cached (not just the first one) for future use
- Each cache entry includes an expiration timestamp (1 hour by default)
- Invalid responses (errors, API failures) are automatically filtered and not cached
- Expired entries are automatically removed when accessed

**Cache File**: The cache file `semantic_cache.json` is automatically created in the project root when the semantic cache is initialized. It stores query-response pairs with embeddings, timestamps, expiration deadlines, and hit counts.

## Example Conversations

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

## Project Structure

```
crypto-analysis-agent/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── env.template              # Environment variable template
├── .gitignore               # Git ignore rules
├── README.md                # This file
├── ARCHITECTURE.md          # Detailed architecture documentation
├── run_evaluation.py        # Evaluation runner script
├── semantic_cache.json      # Semantic cache persistence file (auto-generated)
├── evaluation/               # Evaluation framework
│   ├── evaluate_agent.py    # Performance evaluation
│   ├── evaluate_accuracy.py # Accuracy evaluation (LLM-as-a-Judge)
│   ├── llm_judge.py         # LLM judge implementation
│   ├── test_questions.json  # Test questions for accuracy evaluation
│   ├── evaluation_scenarios.json # Test scenarios
│   ├── README.md            # Evaluation documentation
│   └── README_ACCURACY.md   # Accuracy evaluation documentation
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
        ├── cache.py          # TTL-based cache
        ├── semantic_cache.py # Semantic caching with embeddings
        ├── exceptions.py
        ├── interfaces.py
        ├── logging_config.py
        └── progress.py
```

## LangSmith Tracing

The agent supports LangSmith integration for workflow tracing and observability. LangSmith provides comprehensive monitoring and debugging capabilities for LangChain applications.

### Features

- **Workflow Visualization**: See the complete execution flow of agent interactions with detailed step-by-step breakdown
- **Performance Monitoring**: Track latency, token usage, and costs for each operation
- **Debugging**: Inspect tool calls, LLM requests, responses, and intermediate states
- **Analytics**: Analyze patterns in agent behavior, tool usage frequency, and success rates
- **Error Tracking**: Monitor errors and exceptions across all operations

### Setup

1. **Get LangSmith API Key**:
   - Sign up at https://smith.langchain.com/
   - Navigate to Settings → API Keys
   - Create a new API key

2. **Configure in `.env`**:
```bash
# Enable LangSmith tracing
LANGSMITH_ENABLED=true

# Your LangSmith API key (required when enabled)
LANGSMITH_API_KEY=lsv2_pt_xxxxxxxxxxxxxxxxxxxxx

# Optional: Project name for organizing traces
# If not set, traces will go to your default project
LANGSMITH_PROJECT=crypto-analysis-agent
```

3. **View Traces**: 
   - Once enabled, all agent interactions are automatically traced
   - Visit https://smith.langchain.com/ to view your traces
   - Filter by project, date, or search for specific queries

### What Gets Traced

- **Agent Invocations**: Complete agent execution flow
- **Tool Calls**: All tool invocations including:
  - `get_coin_info` - Coin identification
  - `get_coin_price` - Price data retrieval
  - `get_coin_news` - News article fetching
  - `fundamental_analysis` - Fundamental analysis
  - `price_analysis` - Price trend analysis
  - `sentiment_analysis` - Sentiment metrics
  - `technical_analysis` - Technical indicators
  - `get_previous_analysis` - Historical analysis retrieval
- **LLM Requests**: All OpenAI API calls with prompts and responses
- **Token Usage**: Input/output token counts and costs
- **Latency Metrics**: Response times for each operation
- **Error Handling**: Exceptions and error messages

### Benefits

- **Debug Issues**: Quickly identify where problems occur in the agent workflow
- **Optimize Performance**: Find bottlenecks and optimize slow operations
- **Monitor Costs**: Track token usage and API costs over time
- **Improve Quality**: Analyze which tool combinations work best for different queries

## Limitations

1. **API Rate Limits**: CoinGecko free tier has rate limits (~50 calls/minute)
2. **Data Accuracy**: Real-time data depends on external API availability
3. **Historical Data**: Limited to data available from CoinGecko
4. **Sentiment Analysis**: Based on available social metrics (may not include all platforms)
5. **Semantic Cache**: Requires OpenAI API key for embedding generation (small cost per query)
6. **Cache Expiration**: Cached responses expire after 1 hour (configurable) to ensure data freshness
7. **Not Financial Advice**: This tool is for educational purposes only

