"""Application constants."""

# API Configuration
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
FEAR_GREED_API_URL = "https://api.alternative.me/fng/"
NEWSAPI_BASE_URL = "https://newsapi.org/v2"

# Cache Configuration
DEFAULT_CACHE_TTL = 300  # 5 minutes in seconds
# Increase cache TTL to reduce API calls and avoid rate limits
RATE_LIMIT_CACHE_TTL = 600  # 10 minutes when rate limited

# Request Configuration
DEFAULT_TIMEOUT = 10  # seconds

# Common Coin Symbol Mappings
COIN_SYMBOL_MAPPINGS = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "usdt": "tether",
    "bnb": "binancecoin",
    "sol": "solana",
    "xrp": "ripple",
    "usdc": "usd-coin",
    "ada": "cardano",
    "doge": "dogecoin",
    "avax": "avalanche-2",
    "dot": "polkadot",
    "matic": "matic-network",
    "link": "chainlink",
    "uni": "uniswap",
    "atom": "cosmos",
}

# Analysis Types
ANALYSIS_TYPES = ["fundamental", "price", "sentiment", "technical"]
