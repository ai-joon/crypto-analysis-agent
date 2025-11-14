"""Custom exceptions for the crypto analysis application."""


class CryptoAnalysisError(Exception):
    """Base exception for all crypto analysis errors."""

    def __init__(self, message: str, details: dict = None):
        """
        Initialize crypto analysis error.

        Args:
            message: Error message
            details: Optional dictionary with additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class CoinNotFoundError(CryptoAnalysisError):
    """Raised when a cryptocurrency cannot be found."""

    def __init__(self, coin_query: str, suggestions: list = None):
        """
        Initialize coin not found error.

        Args:
            coin_query: The query that failed
            suggestions: Optional list of suggested coin names
        """
        self.coin_query = coin_query
        self.suggestions = suggestions or []
        message = f"Could not find cryptocurrency: {coin_query}"
        if suggestions:
            message += f". Did you mean: {', '.join(suggestions[:3])}?"
        super().__init__(
            message, {"coin_query": coin_query, "suggestions": suggestions}
        )


class APIError(CryptoAnalysisError):
    """Raised when an API request fails."""

    def __init__(self, message: str, status_code: int = None, endpoint: str = None):
        """
        Initialize API error.

        Args:
            message: Error message
            status_code: HTTP status code if applicable
            endpoint: API endpoint that failed
        """
        self.status_code = status_code
        self.endpoint = endpoint
        details = {}
        if status_code:
            details["status_code"] = status_code
        if endpoint:
            details["endpoint"] = endpoint
        
        # Add user-friendly message for rate limits
        if status_code == 429:
            message = (
                "API rate limit exceeded. The service is temporarily unavailable due to too many requests. "
                "Please wait a few minutes and try again. "
                "Tip: The application uses caching to reduce API calls."
            )
        
        super().__init__(message, details)


class AnalysisError(CryptoAnalysisError):
    """Raised when an analysis operation fails."""

    def __init__(self, analysis_type: str, message: str, coin_id: str = None):
        """
        Initialize analysis error.

        Args:
            analysis_type: Type of analysis that failed
            message: Error message
            coin_id: Coin ID if applicable
        """
        self.analysis_type = analysis_type
        self.coin_id = coin_id
        error_message = f"{analysis_type} analysis failed: {message}"
        super().__init__(
            error_message,
            {"analysis_type": analysis_type, "coin_id": coin_id},
        )


class ValidationError(CryptoAnalysisError):
    """Raised when input validation fails."""

    def __init__(self, field: str, message: str):
        """
        Initialize validation error.

        Args:
            field: Field name that failed validation
            message: Validation error message
        """
        self.field = field
        super().__init__(f"Validation error for {field}: {message}", {"field": field})


class ConfigurationError(CryptoAnalysisError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str, config_key: str = None):
        """
        Initialize configuration error.

        Args:
            message: Error message
            config_key: Configuration key if applicable
        """
        self.config_key = config_key
        super().__init__(message, {"config_key": config_key})
