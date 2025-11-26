"""Configuration constants for evaluation framework."""

from pathlib import Path

# Paths
EVALUATION_DIR = Path(__file__).parent
PROJECT_ROOT = EVALUATION_DIR.parent
TEST_QUESTIONS_FILE = EVALUATION_DIR / "test_questions.json"
DEFAULT_REPORT_FILE = "evaluation_report.json"

# Test Configuration
DEFAULT_TEST_COINS = ["bitcoin", "ethereum", "solana"]
DEFAULT_CACHE_TTL = 300
ANSWER_TRUNCATE_LENGTH = 500

# LLM Judge Configuration
DEFAULT_JUDGE_MODEL = "gpt-4o-mini"
JUDGE_TEMPERATURE = 0.3
SCORE_MIN = 0
SCORE_MAX = 100

# Performance Weights
ANALYZER_WEIGHT = 0.6
AGENT_WEIGHT = 0.4

# Analyzer Types
ANALYZER_TYPES = {
    "fundamental": "perform_fundamental_analysis",
    "price": "perform_price_analysis",
    "sentiment": "perform_sentiment_analysis",
    "technical": "perform_technical_analysis",
}

# Quality Metrics Thresholds
MIN_PARAGRAPHS = 2
MIN_SECTIONS = 3

# Clarification Keywords
CLARIFICATION_KEYWORDS = ["would you like", "what", "which", "please"]
ANALYSIS_KEYWORDS = ["analysis", "price", "market", "sentiment", "technical"]
