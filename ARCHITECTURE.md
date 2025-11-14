# Architecture Documentation
## Crypto Token Analysis Chat Agent

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Design Decisions](#design-decisions)
6. [Technology Stack](#technology-stack)
7. [Scalability Considerations](#scalability-considerations)

---

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
│  │  LangChain Agent (src/agent.py)                            │ │
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
│  │  Analysis Modules (src/analyzers.py)                    │   │
│  │                                                          │   │
│  │  ┌────────────────┐  ┌────────────────┐                │   │
│  │  │  Fundamental   │  │  Price         │                │   │
│  │  │  Analyzer      │  │  Analyzer      │                │   │
│  │  │  - Market cap  │  │  - Trends      │                │   │
│  │  │  - Volume      │  │  - Volatility  │                │   │
│  │  │  - Supply      │  │  - Support/    │                │   │
│  │  │  - Liquidity   │  │    Resistance  │                │   │
│  │  └────────────────┘  └────────────────┘                │   │
│  │                                                          │   │
│  │  ┌────────────────┐  ┌────────────────┐                │   │
│  │  │  Sentiment     │  │  Technical     │                │   │
│  │  │  Analyzer      │  │  Analyzer      │                │   │
│  │  │  - Social      │  │  - SMA         │                │   │
│  │  │    metrics     │  │  - RSI         │                │   │
│  │  │  - Community   │  │  - MACD        │                │   │
│  │  │  - F&G Index   │  │  - Indicators  │                │   │
│  │  └────────────────┘  └────────────────┘                │   │
│  └─────────────────────┬───────────────────────────────────┘   │
└────────────────────────┼─────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Data Access Layer                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Data Fetcher (src/data_fetcher.py)                        │ │
│  │                                                             │ │
│  │  ┌──────────────────┐  ┌──────────────────────────────┐   │ │
│  │  │ Coin ID          │  │ Cache Manager                 │   │ │
│  │  │ Resolution       │  │ - 5-minute TTL               │   │ │
│  │  │ - Symbol mapping │  │ - In-memory storage          │   │ │
│  │  │ - API search     │  │ - Key-based retrieval        │   │ │
│  │  └──────────────────┘  └──────────────────────────────┘   │ │
│  │                                                             │ │
│  │  ┌────────────────────────────────────────────────────────┐│ │
│  │  │ API Methods                                            ││ │
│  │  │ - get_current_price_data()                            ││ │
│  │  │ - get_market_data()                                   ││ │
│  │  │ - get_historical_prices()                             ││ │
│  │  │ - get_community_data()                                ││ │
│  │  │ - get_coin_description()                              ││ │
│  │  │ - get_fear_greed_index()                              ││ │
│  │  └────────────────────────────────────────────────────────┘│ │
│  └────────────────────────┬───────────────────────────────────┘ │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       External APIs Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │  CoinGecko API  │  │ Alternative.me  │  │   Future APIs  │  │
│  │  - Price data   │  │ - Fear & Greed  │  │  - NewsAPI     │  │
│  │  - Market data  │  │   Index         │  │  - CoinMktCap  │  │
│  │  - Historical   │  │                 │  │                │  │
│  │  - Community    │  │                 │  │                │  │
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

#### LangChain Agent (`src/agent.py`)
- **Responsibility**: Conversation orchestration and tool selection
- **Key Features**:
  - OpenAI Functions Agent for intelligent tool selection
  - ConversationBufferMemory for context retention
  - Tool registry and management
  - Analysis history storage
  - Guardrails via system prompts
- **Design Pattern**: Agent pattern with tool composition

**Tool Functions**:
1. `get_coin_info`: Resolve coin identifiers
2. `fundamental_analysis`: Market and supply analysis
3. `price_analysis`: Price trends and volatility
4. `sentiment_analysis`: Social and market sentiment
5. `technical_analysis`: Technical indicators
6. `get_previous_analysis`: Retrieve cached analyses

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

#### Data Fetcher (`src/data_fetcher.py`)
- **Responsibility**: API integration and data retrieval
- **Key Features**:
  - Coin ID resolution (symbol → CoinGecko ID)
  - Response caching (5-minute TTL)
  - Error handling and graceful degradation
  - Rate limit awareness

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

---

## Design Decisions

### 1. Why LangChain?

**Rationale**:
- Built-in agent orchestration
- OpenAI Functions support for reliable tool selection
- Memory management abstractions
- Extensible tool framework

**Alternative Considered**: Custom agent loop
**Decision**: LangChain provides production-ready abstractions

### 2. Why OpenAI Functions Agent?

**Rationale**:
- More reliable than ReAct-style agents
- Structured tool selection via function calling
- Better at complex tool orchestration
- Fewer parsing errors

### 3. Why In-Memory Storage?

**Rationale**:
- Simpler implementation for MVP
- Session-based use case
- No persistence requirement in core specs
- Fast access times

**Future**: Could add Redis/database for persistence

### 4. Why CoinGecko API?

**Rationale**:
- Free tier with generous limits
- No API key required initially
- Comprehensive data coverage
- Good documentation

**Alternatives**: CoinMarketCap (requires key), Messari

### 5. Caching Strategy

**Rationale**:
- 5-minute TTL balances freshness and API usage
- In-memory cache is fast and simple
- Keyed by (operation, coin_id, parameters)

**Limitation**: Cache not shared across sessions

### 6. Analysis Separation

**Rationale**:
- Each analysis type has distinct logic
- Easier to test and maintain
- Can be extended independently
- Clear separation of concerns

**Pattern**: Strategy pattern for analysis types

### 7. Autonomous Analysis Selection

**Implementation**: System prompt guides LLM to:
- Interpret user intent
- Select relevant analysis types
- Avoid unnecessary tool calls

**Benefit**: Natural conversation, efficient API usage

---

## Technology Stack

### Core Framework
- **Python 3.8+**: Modern Python features, type hints
- **LangChain 0.1.0**: Agent orchestration
- **OpenAI API**: GPT-4/GPT-3.5-turbo for NLU

### Libraries
- **langchain-openai**: OpenAI integration
- **requests**: HTTP client for APIs
- **pycoingecko**: CoinGecko API wrapper
- **pandas/numpy**: Data processing
- **rich**: CLI UI enhancement
- **python-dotenv**: Environment configuration

### External Services
- **CoinGecko API**: Cryptocurrency data
- **Alternative.me API**: Fear & Greed Index
- **OpenAI API**: Language model

---

## Scalability Considerations

### Current Limitations

1. **In-Memory Storage**
   - Limited to single process
   - No cross-session persistence
   - Memory usage grows with conversation length

2. **API Rate Limits**
   - CoinGecko free tier: ~50 calls/minute
   - No rate limiting implementation
   - Cache helps but doesn't guarantee compliance

3. **Single User**
   - CLI interface supports one user
   - No concurrent session handling

### Scalability Solutions

#### For Production Deployment

1. **Database Integration**
   ```
   - PostgreSQL/MongoDB for conversation history
   - Redis for caching layer
   - Enables multi-user, cross-session memory
   ```

2. **API Management**
   ```
   - Rate limiting middleware
   - API key rotation
   - Request queuing for burst handling
   - Premium API tiers for higher limits
   ```

3. **Web Interface**
   ```
   - FastAPI/Flask backend
   - React/Next.js frontend
   - WebSocket for real-time updates
   - Session management
   ```

4. **Microservices Architecture**
   ```
   - Separate services for:
     * Agent orchestration
     * Data fetching
     * Analysis processing
     * User management
   - Message queue (RabbitMQ/Kafka) for async processing
   ```

5. **Caching Strategy Enhancement**
   ```
   - Redis cluster for distributed caching
   - CDN for static data
   - Intelligent cache invalidation
   - Warm cache for popular coins
   ```

6. **Monitoring & Observability**
   ```
   - Application metrics (Prometheus)
   - Logging aggregation (ELK stack)
   - Tracing (Jaeger)
   - Error tracking (Sentry)
   ```

---

## Security Considerations

1. **API Key Management**
   - Environment variables for secrets
   - No hardcoded credentials
   - .gitignore for sensitive files

2. **Input Validation**
   - Sanitize user inputs
   - Guardrails prevent prompt injection
   - Rate limiting for abuse prevention

3. **Data Privacy**
   - No PII collection
   - Conversation data not persisted
   - API calls don't expose user identity

---

## Testing Strategy

### Unit Tests (Recommended)
```python
# test_data_fetcher.py
- Test coin ID resolution
- Test API error handling
- Test cache behavior

# test_analyzers.py
- Test each analyzer with mock data
- Test edge cases (missing data, errors)
- Test calculation correctness

# test_agent.py
- Test tool selection
- Test conversation flow
- Test memory retention
```

### Integration Tests
```python
# test_integration.py
- Test end-to-end analysis flow
- Test with real APIs (rate-limited)
- Test error recovery
```

### Manual Testing
- Conversation flow testing
- Edge case exploration
- User experience validation

---

## Future Enhancements

### High Priority
1. Comparative analysis tool (side-by-side token comparison)
2. Persistent conversation history
3. Web UI with better visualization
4. Enhanced sentiment analysis (Twitter API, Reddit API)

### Medium Priority
5. Portfolio tracking
6. Price alerts
7. Historical analysis playback
8. Custom analysis reports

### Low Priority
9. Multi-language support
10. Voice interface
11. Mobile app
12. Social features (share analyses)

---

## Conclusion

This architecture provides a solid foundation for a cryptocurrency analysis chat agent. The modular design allows for easy extension, the caching strategy optimizes API usage, and the LangChain framework enables sophisticated conversational capabilities.

The system successfully demonstrates:
- Multi-turn conversations with context
- Autonomous analysis selection
- Four types of comprehensive analysis
- Real-time data integration
- Guardrails and error handling
- Natural language interface

The architecture is production-ready for small-scale deployment and has clear paths for scaling to support more users, more data sources, and more sophisticated analyses.

