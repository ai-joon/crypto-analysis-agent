# Architecture Documentation
## Crypto Token Analysis Chat Agent


## System Overview

The Crypto Token Analysis Chat Agent is a conversational AI system designed to provide comprehensive cryptocurrency analysis through natural language interaction. The system leverages LangChain for agent orchestration, OpenAI's GPT models for natural language understanding, and real-time cryptocurrency data from public APIs.

### Key Architectural Goals

1. **Modularity**: Separate concerns across data fetching, analysis, and agent logic
2. **Extensibility**: Easy to add new analysis types or data sources
3. **Reliability**: Graceful error handling and fallback mechanisms
4. **Performance**: Multi-layer caching strategies to minimize API calls
5. **User Experience**: Natural conversation flow with context awareness
6. **Observability**: Optional tracing and monitoring capabilities
7. **Cost Efficiency**: Semantic caching to reduce LLM API costs

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  CLI Interface (`src/ui/cli.py`)                          │ │
│  │  - Rich Console UI                                         │ │
│  │  - Command Processing (help, clear, exit, cache stats)    │ │
│  │  - User Input Handling                                     │ │
│  │  - Agent Initialization                                    │ │
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
│  │  │ Agent            │  │ - Full message history      │   │ │
│  │  │ - create_openai_ │  │ - Context retention         │   │ │
│  │  │   tools_agent    │  │ - Session-based             │   │ │
│  │  │ - Tool Selection │  │                             │   │ │
│  │  │ - Intent Analysis│  └──────────────────────────────┘   │ │
│  │  └──────────────────┘                                      │ │
│  │                                                             │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Semantic Cache (`src/core/semantic_cache.py`)        │ │ │
│  │  │ - Embedding-based similarity matching                │ │ │
│  │  │ - Configurable threshold (default: 0.85)             │ │ │
│  │  │ - TTL-based expiration (default: 1 hour)            │ │ │
│  │  │ - Persistent JSON storage                            │ │ │
│  │  │ - Error response filtering                           │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Tool Registry (`src/agents/tools.py`)              │ │ │
│  │  │ - get_coin_info()                                   │ │ │
│  │  │ - get_previous_analysis()                          │ │ │
│  │  │ - fundamental_analysis()                            │ │ │
│  │  │ - price_analysis()                                 │ │ │
│  │  │ - sentiment_analysis()                             │ │ │
│  │  │ - technical_analysis()                              │ │ │
│  │  │ - Error handling decorator                          │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Analysis History Store                                │ │ │
│  │  │ - In-memory cache of previous analyses               │ │ │
│  │  │ - Keyed by coin_id                                   │ │ │
│  │  │ - Stores all analysis types per coin                 │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ LangSmith Integration (Optional)                      │ │ │
│  │  │ - Workflow tracing and observability                  │ │ │
│  │  │ - Performance monitoring                              │ │ │
│  │  │ - Token usage tracking                               │ │ │
│  │  │ - Error tracking                                     │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────┬───────────────────────────────────┘ │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Service Layer                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Coin Service (`src/services/coin_service.py`)           │ │
│  │  - get_coin_info()                                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Analysis Service (`src/services/analysis_service.py`)     │ │
│  │  - perform_fundamental_analysis()                        │ │
│  │  - perform_price_analysis()                              │ │
│  │  - perform_sentiment_analysis()                           │ │
│  │  - perform_technical_analysis()                          │ │
│  └────────────────────────┬───────────────────────────────────┘ │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Analysis Layer                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Analysis Modules (`src/analyzers/`)                   │   │
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
│  │  │ Coin ID          │  │ TTL Cache Manager            │   │ │
│  │  │ Resolution       │  │ (`src/core/cache.py`)        │   │ │
│  │  │ - Symbol mapping │  │ - 5-minute TTL (configurable) │   │ │
│  │  │ - API search     │  │ - In-memory storage          │   │ │
│  │  │                  │  │ - Key-based retrieval        │   │ │
│  │  │                  │  │ - Stale data fallback        │   │ │
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
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Observability Layer (Optional)                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  LangSmith Platform                                         │ │
│  │  - Workflow tracing                                         │ │
│  │  - Performance metrics                                      │ │
│  │  - Token usage analytics                                    │ │
│  │  - Error tracking                                           │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. User Interface Layer

#### CLI Interface (`src/ui/cli.py`)
- **Responsibility**: User interaction and command handling
- **Key Features**:
  - Rich console output with markdown rendering
  - Command parsing (help, clear, exit, cache/stats)
  - Session management
  - Agent initialization and error handling
  - Semantic cache statistics display
  - Error display and user feedback
- **Dependencies**: Rich library for enhanced console UI
- **Entry Point**: `main.py` initializes settings and starts CLI

### 2. Agent Orchestration Layer

#### LangChain Agent (`src/agents/agent.py`)
- **Responsibility**: Conversation orchestration and tool selection
- **Key Features**:
  - OpenAI Functions Agent using `create_openai_tools_agent` (with fallback to `create_agent`)
  - Conversation history management (full message history)
  - Semantic cache integration for response caching
  - LangSmith tracing support (optional)
  - Tool registry and management
  - Analysis history storage
  - Guardrails via system prompts
  - Ambiguity handling and clarification requests
- **Design Pattern**: Agent pattern with tool composition
- **LLM**: Configurable OpenAI model (default: `gpt-4o-mini`)

**Semantic Cache** (`src/core/semantic_cache.py`):
- **Purpose**: Cache similar queries using embedding similarity
- **Features**:
  - Uses OpenAI embeddings (`text-embedding-3-small`) for query matching
  - Cosine similarity threshold (default: 0.85)
  - TTL-based expiration (default: 1 hour)
  - Persistent JSON storage (`semantic_cache.json`)
  - Automatic error response filtering
  - LRU-style eviction when max size reached
  - Hit count tracking for statistics
- **Benefits**: Reduces API costs by reusing responses for semantically similar queries

**Tool Functions** (`src/agents/tools.py`):
1. `get_coin_info`: Resolve coin identifiers (name, symbol, CoinGecko ID)
2. `get_previous_analysis`: Retrieve cached analyses (handles ambiguous references like "it", "that token")
3. `fundamental_analysis`: Market and supply analysis
4. `price_analysis`: Price trends and volatility
5. `sentiment_analysis`: Social and market sentiment
6. `technical_analysis`: Technical indicators
- **Error Handling**: Unified error handling decorator for consistent error messages

**Conversation Memory**:
- Type: Full message history (List[BaseMessage])
- Retention: Session-based (cleared on reset)
- Purpose: Enable follow-up questions and context awareness
- Implementation: Stores HumanMessage and AIMessage objects

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

**LangSmith Integration** (Optional):
- **Purpose**: Observability and workflow tracing
- **Features**:
  - Automatic tracing of all agent invocations
  - Tool call tracking with parameters and results
  - LLM request/response logging
  - Token usage and cost tracking
  - Performance metrics (latency)
  - Error tracking and debugging
- **Configuration**: Enabled via `LANGSMITH_ENABLED=true` in environment
- **Project Organization**: Optional project name for trace organization

### 3. Service Layer

#### Coin Service (`src/services/coin_service.py`)
- **Responsibility**: Business logic for coin-related operations
- **Key Features**:
  - Coin information retrieval (name, symbol, CoinGecko ID)
  - Abstraction layer between agent tools and repository

#### Analysis Service (`src/services/analysis_service.py`)
- **Responsibility**: Orchestration of analysis operations
- **Key Features**:
  - Coordinates analyzer modules
  - Error handling and exception wrapping
  - Coin name resolution
  - Delegates to appropriate analyzers based on analysis type

### 4. Analysis Layer

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

### 5. Data Access Layer

#### Coin Repository (`src/repositories/coin_repository.py`)
- **Responsibility**: API integration and data retrieval
- **Key Features**:
  - Coin ID resolution (symbol → CoinGecko ID)
  - Response caching via TTL Cache (5-minute TTL, configurable)
  - Error handling and graceful degradation
  - Rate limit awareness with stale data fallback
  - Multiple API client integration (CoinGecko, Fear & Greed, NewsAPI)

#### TTL Cache (`src/core/cache.py`)
- **Purpose**: Time-based caching for API responses
- **Features**:
  - Configurable TTL (default: 5 minutes)
  - In-memory storage with timestamp tracking
  - Stale data fallback option (useful during rate limits)
  - Key-based retrieval
  - Automatic expiration

**Caching Strategy**:
```python
# TTL Cache (for API responses)
cache = {
    "coin_id_bitcoin": (data, timestamp),
    "coin_data_bitcoin": (data, timestamp),
    "historical_bitcoin_30": (data, timestamp),
    "fear_greed_index": (data, timestamp),
    "news_bitcoin_btc": (data, timestamp),
    ...
}

# Semantic Cache (for LLM responses)
semantic_cache = {
    "md5_hash": CachedResponse(
        query="...",
        response="...",
        embedding=[...],
        timestamp=...,
        expires_at=...,
        hit_count=...
    ),
    ...
}
```

**API Endpoints Used**:
- `/coins/{id}`: Detailed coin data
- `/coins/{id}/market_chart`: Historical prices
- `/coins/list`: All available coins
- `/search/trending`: Trending coins

### 6. Configuration Layer

#### Settings Management (`src/config/settings.py`)
- **Responsibility**: Centralized configuration with validation
- **Key Features**:
  - Environment variable loading
  - Settings validation
  - Default values
  - Singleton pattern for global access
- **Configuration Options**:
  - OpenAI API key and model selection
  - Cache TTL settings
  - Semantic cache configuration (enabled, threshold, size, TTL)
  - LangSmith integration (enabled, API key, project name)
  - NewsAPI key (optional)
  - Request timeout
  - Verbose logging

---

## Data Flow

### Example: User asks "Tell me about Bitcoin"

```
1. User Input
   ↓
2. CLI Interface (src/ui/cli.py)
   - Captures input
   - Sends to agent
   ↓
3. LangChain Agent (src/agents/agent.py)
   - Checks semantic cache for similar queries
   - If cache hit: returns cached response (skips steps 4-6)
   - If cache miss: proceeds with analysis
   - Analyzes intent
   - Determines relevant analyses: all types (comprehensive query)
   - Plans tool execution sequence
   ↓
4. Tool Execution (via Service Layer)
   a. get_coin_info("bitcoin")
      ↓ CoinService.get_coin_info()
      ↓ CoinRepository.get_coin_id() → checks TTL cache
      ↓ CoinGecko API: /coins/list (if not cached)
      ↓ Returns: "Found: Bitcoin (BTC)"
   
   b. fundamental_analysis("bitcoin")
      ↓ AnalysisService.perform_fundamental_analysis()
      ↓ FundamentalAnalyzer.analyze()
      ↓ CoinRepository.get_market_data() → checks TTL cache
      ↓ CoinGecko API: /coins/bitcoin (if not cached)
      ↓ TTL Cache stores result
      ↓ Returns formatted report
      ↓ Agent stores in analysis_history
   
   c. price_analysis("bitcoin")
      ↓ AnalysisService.perform_price_analysis()
      ↓ PriceAnalyzer.analyze()
      ↓ CoinRepository.get_historical_prices(7d, 30d) → checks TTL cache
      ↓ CoinGecko API: /coins/bitcoin/market_chart (if not cached)
      ↓ Calculations: volatility, support/resistance
      ↓ Returns formatted report
      ↓ Agent stores in analysis_history
   
   d. sentiment_analysis("bitcoin")
      ↓ AnalysisService.perform_sentiment_analysis()
      ↓ SentimentAnalyzer.analyze()
      ↓ CoinRepository.get_community_data(), get_fear_greed_index()
      ↓ APIs: CoinGecko + Alternative.me (with caching)
      ↓ Calculation: sentiment score
      ↓ Returns formatted report
      ↓ Agent stores in analysis_history
   
   e. technical_analysis("bitcoin")
      ↓ AnalysisService.perform_technical_analysis()
      ↓ TechnicalAnalyzer.analyze()
      ↓ CoinRepository.get_historical_prices(30d, 90d) → checks TTL cache
      ↓ Calculations: SMA, RSI, MACD
      ↓ Returns formatted report
      ↓ Agent stores in analysis_history
   ↓
5. LLM Synthesis
   - Agent provides all tool outputs to LLM
   - LLM synthesizes comprehensive response
   - Natural language formatting
   ↓
6. Semantic Cache Storage
   - Validates response (filters errors)
   - Generates query embedding
   - Stores query-response pair with metadata
   - Saves to persistent JSON file
   ↓
7. CLI Display
   - Rich markdown rendering
   - Formatted panels and styling
   ↓
8. Memory Update
   - Conversation history updated
   - Ready for follow-up questions
   ↓
9. LangSmith Tracing (if enabled)
   - All steps traced with metadata
   - Performance metrics recorded
   - Token usage tracked
```

### Follow-up Question: "What was Bitcoin's RSI?"

```
1. User Input → CLI → Agent
   ↓
2. Semantic Cache Check
   - Checks for similar queries (not a standalone query, skip cache)
   - Proceeds with agent processing
   ↓
3. Agent analyzes:
   - "Bitcoin" references previous context (from conversation memory)
   - "RSI" is technical indicator
   - Tool needed: get_previous_analysis
   ↓
4. get_previous_analysis("bitcoin", "technical")
   - CoinService resolves "bitcoin" → coin_id
   - Retrieves from analysis_history
   - Returns cached technical analysis
   ↓
5. LLM Synthesis
   - Extracts RSI value from cached report
   - Formats natural language response
   ↓
6. Response: "Looking back at my technical analysis for Bitcoin, 
              the RSI (14) was at 62..."
   ↓
7. Memory Update
   - Conversation history updated with new exchange
   - Analysis history unchanged (reused existing analysis)
```

### Example: Semantic Cache Hit

```
1. User Input: "Tell me about Ethereum"
   ↓
2. Semantic Cache Check
   - Generates embedding for query
   - Searches cached queries for similarity
   - Finds similar query: "What can you tell me about Ethereum?"
   - Similarity: 0.92 (above threshold 0.85)
   ↓
3. Cache Hit
   - Returns cached response immediately
   - Skips all API calls and analysis
   - Updates conversation memory
   ↓
4. Response: [Cached response from previous similar query]
   ↓
5. Benefits:
   - Zero API calls
   - Instant response
   - Cost savings
```

---

## Key Architectural Features

### Multi-Layer Caching Strategy

The system employs two complementary caching mechanisms:

1. **TTL Cache** (`src/core/cache.py`):
   - Caches API responses with time-based expiration
   - Default TTL: 5 minutes (configurable)
   - Reduces external API calls
   - Supports stale data fallback during rate limits

2. **Semantic Cache** (`src/core/semantic_cache.py`):
   - Caches LLM responses using embedding similarity
   - Matches semantically similar queries (not just exact matches)
   - Reduces OpenAI API costs significantly
   - Persistent storage across sessions
   - Configurable similarity threshold and TTL

### Service Layer Abstraction

The service layer (`src/services/`) provides:
- **Separation of Concerns**: Business logic separated from data access
- **Reusability**: Services can be used by multiple consumers
- **Testability**: Easier to mock and test individual components
- **Error Handling**: Centralized exception handling and transformation

### Observability with LangSmith

Optional LangSmith integration provides:
- **Workflow Tracing**: Complete visibility into agent execution
- **Performance Monitoring**: Latency tracking for each operation
- **Cost Tracking**: Token usage and API cost monitoring
- **Debugging**: Inspect tool calls, LLM requests, and intermediate states
- **Analytics**: Pattern analysis for agent behavior optimization

### Error Handling Strategy

- **Unified Error Handling**: Decorator pattern for consistent error messages
- **Graceful Degradation**: Stale cache fallback during rate limits
- **User-Friendly Messages**: Clear error messages with suggestions
- **Error Filtering**: Semantic cache filters out error responses

### Configuration Management

- **Centralized Settings**: Single source of truth for configuration (`src/config/settings.py`)
- **Environment-Based**: Configuration via environment variables
- **Validation**: Automatic validation of settings on initialization
- **Defaults**: Sensible defaults for optional settings
- **Singleton Pattern**: Global access to settings throughout application