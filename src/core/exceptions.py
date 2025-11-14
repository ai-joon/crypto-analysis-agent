"""Custom exceptions for the crypto analysis application."""


class CryptoAnalysisError(Exception):
    """Base exception for all crypto analysis errors."""


class CoinNotFoundError(CryptoAnalysisError):
    """Raised when a cryptocurrency cannot be found."""

    def __init__(self, coin_query: str):
        self.coin_query = coin_query
        super().__init__(f"Could not find cryptocurrency: {coin_query}")


class APIError(CryptoAnalysisError):
    """Raised when an API request fails."""

    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(message)


class AnalysisError(CryptoAnalysisError):
    """Raised when an analysis operation fails."""

    def __init__(self, analysis_type: str, message: str):
        self.analysis_type = analysis_type
        super().__init__(f"{analysis_type} analysis failed: {message}")

