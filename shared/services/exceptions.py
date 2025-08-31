"""Custom exceptions for trading services."""


class TradingError(Exception):
    """Base exception for all trading-related errors."""
    pass


class ConnectionError(TradingError):
    """Base exception for connection-related errors."""
    pass



class OKXConnectionError(ConnectionError):
    """OKX API connection specific errors."""
    pass


class ValidationError(TradingError):
    """Data validation errors."""
    pass


class TradeExecutionError(TradingError):
    """Errors during trade execution."""
    pass


class InsufficientFundsError(TradeExecutionError):
    """Insufficient funds for trade execution."""
    pass


class SymbolNotFoundError(TradeExecutionError):
    """Trading symbol not found or not available."""
    pass


class OrderNotFoundError(TradingError):
    """Order not found in the system."""
    pass


class PositionNotFoundError(TradingError):
    """Position not found in the system."""
    pass


class RiskLimitExceededError(TradingError):
    """Risk management limits exceeded."""
    pass


class APIError(TradingError):
    """External API errors."""
    
    def __init__(self, message: str, code: str = None, response: dict = None):
        super().__init__(message)
        self.code = code
        self.response = response



class OKXAPIError(APIError):
    """OKX API specific errors."""
    pass


class RateLimitError(APIError):
    """API rate limit exceeded."""
    
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after


class AuthenticationError(TradingError):
    """Authentication/authorization errors."""
    pass


class ConfigurationError(TradingError):
    """Configuration-related errors."""
    pass


class ServiceNotInitializedError(TradingError):
    """Service not properly initialized."""
    pass