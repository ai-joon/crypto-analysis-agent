# Architecture Documentation
## Crypto Token Analysis Chat Agent


## System Overview

The Crypto Token Analysis Chat Agent is a conversational AI system designed to provide comprehensive cryptocurrency analysis through natural language interaction. The system leverages LangChain for agent orchestration, OpenAI's GPT models for natural language understanding, and real-time cryptocurrency data from public APIs.

### Key Architectural Goals

1. **Modularity**: Separate concerns across data fetching, analysis, and agent logic
2. **Extensibility**: Easy to add new analysis types or data sources
3. **Reliability**: Graceful error handling and fallback mechanisms
4. **Performance**: Caching strategies to minimize API calls
5. **User Experience**: Natural conversation flow with context awareness

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  CLI Interface (main.py)                                   │ │
│  │  - Rich Console UI                                         │ │
│  │  - Command Processing                                      │ │
│  │  - User Input Handling                                     │ │
│  └──────────────────────┬─────────────────────────────────────┘ │
└─────────────────────────┼───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Agent Orchestration Layer                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  LangChain Agent (`src/agents/agent.py`)                   │ │
│  │  ┌──────────────────┐  ┌──────────────────────────────┐   │ │
│  │  │ OpenAI Functions │  │ Conversation Memory          │   │ │
│  │  │ Agent            │  │ - BufferMemory               │   │ │
│  │  │ - Tool Selection │  │ - Context Retention          │   │ │
│  │  │ - Intent Analysis│  │ - Message History            │   │ │
│  │  └──────────────────┘  └──────────────────────────────┘   │ │
│  │                                                             │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Tool Registry                                         │ │ │
│  │  │ - get_coin_info()                                    │ │ │
│  │  │ - get_coin_price()                                   │ │ │
│  │  │ - get_coin_news()                                    │ │ │
│  │  │ - fundamental_analysis()                             │ │ │
│  │  │ - price_analysis()                                   │ │ │
│  │  │ - sentiment_analysis()                               │ │ │
│  │  │ - technical_analysis()                               │ │ │
│  │  │ - get_previous_analysis()                            │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Analysis History Store                                │ │ │
│  │  │ - In-memory cache of previous analyses               │ │ │
│  │  │ - Keyed by coin_id                                   │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────┬───────────────────────────────────┘ │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Analysis Layer                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Analysis Modules (src/analyzers/)                     │   │
│  │                                                          │   │
│  │  ┌────────────────────┐  ┌────────────────────┐      │   │
│  │  │  Fundamental       │  │  Price             │      │   │
│  │  │  Analyzer          │  │  Analyzer          │      │   │
│  │  │  (fundamental_     │  │  (price_analyzer.py)│      │   │
│  │  │   analyzer.py)     │  │  - Trends          │      │   │
│  │  │  - Market cap      │  │  - Volatility      │      │   │
│  │  │  - Volume          │  │  - Support/        │      │   │
│  │  │  - Supply          │  │    Resistance      │      │   │
│  │  │  - Liquidity       │  │                    │      │   │
│  │  └────────────────────┘  └────────────────────┘      │   │
│  │                                                          │   │
│  │  ┌────────────────────┐  ┌────────────────────┐      │   │
│  │  │  Sentiment         │  │  Technical         │      │   │
│  │  │  Analyzer          │  │  Analyzer          │      │   │
│  │  │  (sentiment_       │  │  (technical_       │      │   │
│  │  │   analyzer.py)     │  │   analyzer.py)     │      │   │
│  │  │  - Social          │  │  - SMA             │      │   │
│  │  │    metrics         │  │  - RSI             │      │   │
│  │  │  - Community       │  │  - MACD            │      │   │
│  │  │  - F&G Index       │  │  - Indicators      │      │   │
│  │  └────────────────────┘  └────────────────────┘      │   │
│  └─────────────────────┬───────────────────────────────────┘   │
└────────────────────────┼─────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Data Access Layer                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Coin Repository (`src/repositories/coin_repository.py`)   │ │
│  │  ┌──────────────────┐  ┌──────────────────────────────┐   │ │
│  │  │ Coin ID          │  │ Cache Manager                 │   │ │
│  │  │ Resolution       │  │ - 5-minute TTL (configurable) │   │ │
│  │  │ - Symbol mapping │  │ - In-memory storage          │   │ │
│  │  │ - API search     │  │ - Key-based retrieval        │   │ │
│  │  └──────────────────┘  └──────────────────────────────┘   │ │
│  │                                                             │ │
│  │  ┌────────────────────────────────────────────────────────┐│ │
│  │  │ API Clients (`src/api/`)                               ││ │
│  │  │ - CoinGeckoClient (price/market/history)              ││ │
│  │  │ - FearGreedClient (Fear & Greed Index)                ││ │
│  │  │ - NewsAPIClient (crypto & blockchain news)            ││ │
│  │  └────────────────────────────────────────────────────────┘│ │
│  └────────────────────────┬───────────────────────────────────┘ │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       External APIs Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │  CoinGecko API  │  │ Alternative.me  │  │  NewsAPI       │  │
│  │  - Price data   │  │ - Fear & Greed  │  │ - Crypto news  │  │
│  │  - Market data  │  │   Index         │  │ - Blockchain   │  │
│  │  - Historical   │  │                 │  │   news         │  │
│  │  - Community    │  │                 │  │ - General      │  │
│  │                 │  │                 │  │   topics       │  │
│  └─────────────────┘  └─────────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. User Interface Layer

#### CLI Interface (`main.py`)
- **Responsibility**: User interaction and command handling
- **Key Features**:
  - Rich console output with markdown rendering
  - Command parsing (help, clear, exit)
  - Session management
  - Error display and user feedback
- **Dependencies**: Rich library for enhanced console UI

### 2. Agent Orchestration Layer

#### LangChain Agent (`src/agents/agent.py`)
- **Responsibility**: Conversation orchestration and tool selection
- **Key Features**:
  - OpenAI Functions Agent for intelligent tool selection
  - Conversation history management (full message history)
  - Tool registry and management
  - Analysis history storage
  - Guardrails via system prompts
  - Ambiguity handling and clarification requests
- **Design Pattern**: Agent pattern with tool composition

**Tool Functions**:
1. `get_coin_info`: Resolve coin identifiers
2. `get_coin_price`: Get current price and market data (quick lookup)
3. `get_coin_news`: Get news articles (supports both specific coins and general blockchain topics)
4. `fundamental_analysis`: Market and supply analysis
5. `price_analysis`: Price trends and volatility
6. `sentiment_analysis`: Social and market sentiment
7. `technical_analysis`: Technical indicators
8. `get_previous_analysis`: Retrieve cached analyses

**Conversation Memory**:
- Type: Buffer memory (stores all messages)
- Retention: Session-based (cleared on reset)
- Purpose: Enable follow-up questions and context awareness

**Analysis History**:
```python
{
    "bitcoin": {
        "name": "Bitcoin",
        "fundamental": "...",
        "price": "...",
        "sentiment": "...",
        "technical": "..."
    }
}
```

### 3. Analysis Layer

#### Fundamental Analyzer
- **Inputs**: Coin ID, coin name
- **Data Sources**: Market data, description
- **Outputs**: 
  - Market cap, rank, price
  - Volume and liquidity metrics
  - Supply statistics
  - Tokenomics assessment
  
#### Price Analyzer
- **Inputs**: Coin ID, coin name
- **Data Sources**: Current market data, historical prices (7d, 30d)
- **Calculations**:
  - Volatility: Standard deviation of prices
  - Support/Resistance: 25th and 75th percentiles
  - Trend classification
- **Outputs**: Price action, volatility assessment, trend analysis

#### Sentiment Analyzer
- **Inputs**: Coin ID, coin name
- **Data Sources**: Community data, market data, Fear & Greed Index
- **Sentiment Score Calculation**:
  ```
  Base score: 50 (neutral)
  + Price action adjustment (-15 to +15)
  + Social engagement adjustment (0 to +10)
  = Final score (0-100)
  ```
- **Outputs**: Sentiment score, social metrics, market indicators

#### Technical Analyzer
- **Inputs**: Coin ID, coin name
- **Data Sources**: Historical prices (30d, 90d)
- **Indicators**:
  - SMA (7, 20, 50 periods)
  - RSI (14 periods)
  - MACD (12/26 EMAs)
- **Outputs**: Technical indicators, trend signals, recommendations

### 4. Data Access Layer

#### Coin Repository (`src/repositories/coin_repository.py`)
- **Responsibility**: API integration and data retrieval
- **Key Features**:
  - Coin ID resolution (symbol → CoinGecko ID)
  - Response caching (5-minute TTL, configurable)
  - Error handling and graceful degradation
  - Rate limit awareness
  - Multiple API client integration (CoinGecko, Fear & Greed, NewsAPI)

**Caching Strategy**:
```python
cache = {
    "price_bitcoin": (data, timestamp),
    "history_bitcoin_7": (data, timestamp),
    ...
}
```

**API Endpoints Used**:
- `/coins/{id}`: Detailed coin data
- `/coins/{id}/market_chart`: Historical prices
- `/coins/list`: All available coins
- `/search/trending`: Trending coins

---

## Data Flow

### Example: User asks "Tell me about Bitcoin"

```
1. User Input
   ↓
2. CLI Interface (main.py)
   - Captures input
   - Sends to agent
   ↓
3. LangChain Agent (src/agent.py)
   - Analyzes intent
   - Determines relevant analyses: all types (comprehensive query)
   - Plans tool execution sequence
   ↓
4. Tool Execution
   a. get_coin_info("bitcoin")
      ↓ Data Fetcher resolves "bitcoin" → "bitcoin"
      ↓ Returns: "Found: Bitcoin (BTC)"
   
   b. fundamental_analysis("bitcoin")
      ↓ Fundamental Analyzer
      ↓ Data Fetcher: get_market_data()
      ↓ CoinGecko API: /coins/bitcoin
      ↓ Cache stores result
      ↓ Returns formatted report
      ↓ Agent stores in analysis_history
   
   c. price_analysis("bitcoin")
      ↓ Price Analyzer
      ↓ Data Fetcher: get_historical_prices(7d, 30d)
      ↓ CoinGecko API: /coins/bitcoin/market_chart
      ↓ Calculations: volatility, support/resistance
      ↓ Returns formatted report
      ↓ Agent stores in analysis_history
   
   d. sentiment_analysis("bitcoin")
      ↓ Sentiment Analyzer
      ↓ Data Fetcher: get_community_data(), get_fear_greed_index()
      ↓ APIs: CoinGecko + Alternative.me
      ↓ Calculation: sentiment score
      ↓ Returns formatted report
      ↓ Agent stores in analysis_history
   
   e. technical_analysis("bitcoin")
      ↓ Technical Analyzer
      ↓ Data Fetcher: get_historical_prices(30d, 90d)
      ↓ Calculations: SMA, RSI, MACD
      ↓ Returns formatted report
      ↓ Agent stores in analysis_history
   ↓
5. LLM Synthesis
   - Agent provides all tool outputs to LLM
   - LLM synthesizes comprehensive response
   - Natural language formatting
   ↓
6. CLI Display
   - Rich markdown rendering
   - Formatted panels and styling
   ↓
7. Memory Update
   - Conversation history updated
   - Ready for follow-up questions
```

### Follow-up Question: "What was Bitcoin's RSI?"

```
1. User Input → CLI → Agent
   ↓
2. Agent analyzes:
   - "Bitcoin" references previous context
   - "RSI" is technical indicator
   - Tool needed: get_previous_analysis
   ↓
3. get_previous_analysis("bitcoin", "technical")
   - Retrieves from analysis_history
   - Returns cached technical analysis
   ↓
4. LLM extracts RSI value from cached report
   ↓
5. Response: "Looking back at my technical analysis for Bitcoin, 
               the RSI (14) was at 62..."
```