"""Shared services module with base classes and utilities."""

from .base_service import BaseService, BaseTradingService, BaseConnectionService, SingletonMeta
from .exceptions import (
    TradingError,
    ConnectionError,
    OKXConnectionError,
    ValidationError,
    TradeExecutionError,
    InsufficientFundsError,
    SymbolNotFoundError,
    OrderNotFoundError,
    PositionNotFoundError,
    RiskLimitExceededError,
    APIError,
    OKXAPIError,
    RateLimitError,
    AuthenticationError,
    ConfigurationError,
    ServiceNotInitializedError
)

__all__ = [
    # Base classes
    'BaseService',
    'BaseTradingService',
    'BaseConnectionService',
    'SingletonMeta',
    
    # Exceptions
    'TradingError',
    'ConnectionError',
    'OKXConnectionError',
    'ValidationError',
    'TradeExecutionError',
    'InsufficientFundsError',
    'SymbolNotFoundError',
    'OrderNotFoundError',
    'PositionNotFoundError',
    'RiskLimitExceededError',
    'APIError',
    'OKXAPIError',
    'RateLimitError',
    'AuthenticationError',
    'ConfigurationError',
    'ServiceNotInitializedError'
]