"""Application constants."""

# API Configuration
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
FEAR_GREED_API_URL = "https://api.alternative.me/fng/"

# Cache Configuration
DEFAULT_CACHE_TTL = 300  # 5 minutes in seconds

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
