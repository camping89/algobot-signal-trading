"""Enhanced error handling utilities for trading services."""

import logging
import asyncio
import functools
from typing import Any, Callable, Optional, Union, Type, Dict
from contextlib import contextmanager
import traceback
import time
from dataclasses import dataclass

from .services.exceptions import (
    TradingError,
    OKXConnectionError,
    OKXAPIError,
    RateLimitError,
    AuthenticationError,
    ValidationError,
    TradeExecutionError,
    InsufficientFundsError,
    SymbolNotFoundError,
    OrderNotFoundError,
    PositionNotFoundError,
    ServiceNotInitializedError
)

logger = logging.getLogger(__name__)


@dataclass
class ErrorContext:
    service_name: str
    operation: str
    user_id: Optional[str] = None
    symbol: Optional[str] = None
    order_id: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None


class RetryConfig:

    def __init__(
        self,
        max_attempts: int = 3,
        delay: float = 1.0,
        exponential_backoff: bool = True,
        max_delay: float = 60.0,
        retryable_exceptions: tuple = None
    ):
        self.max_attempts = max_attempts
        self.delay = delay
        self.exponential_backoff = exponential_backoff
        self.max_delay = max_delay
        self.retryable_exceptions = retryable_exceptions or (
            OKXConnectionError,
            RateLimitError,
        )


class ErrorHandler:

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(f"{service_name}.ErrorHandler")
    
    
    def map_okx_error(self, error: Exception, context: ErrorContext) -> TradingError:
        """Map OKX specific errors to appropriate exceptions."""
        error_str = str(error).lower()
        
        if "connection" in error_str or "network" in error_str:
            return OKXConnectionError(f"OKX connection error in {context.operation}: {error}")
        elif "rate limit" in error_str or "too many requests" in error_str:
            return RateLimitError(f"OKX rate limit exceeded in {context.operation}: {error}")
        elif "authentication" in error_str or "unauthorized" in error_str or "invalid api" in error_str:
            return AuthenticationError(f"OKX authentication error in {context.operation}: {error}")
        elif "insufficient" in error_str or "balance" in error_str:
            return InsufficientFundsError(f"Insufficient funds for {context.operation}: {error}")
        elif "symbol" in error_str or "instrument" in error_str:
            return SymbolNotFoundError(f"Symbol/instrument error in {context.operation}: {error}")
        elif "order" in error_str and "not found" in error_str:
            return OrderNotFoundError(f"Order not found in {context.operation}: {error}")
        elif "position" in error_str and "not found" in error_str:
            return PositionNotFoundError(f"Position not found in {context.operation}: {error}")
        else:
            return OKXAPIError(f"OKX API error in {context.operation}: {error}")
    
    def map_validation_error(self, error: Exception, context: ErrorContext) -> ValidationError:
        return ValidationError(f"Validation error in {context.operation}: {error}")
    
    def map_generic_error(self, error: Exception, context: ErrorContext) -> TradingError:
        if "okx" in self.service_name.lower():
            return self.map_okx_error(error, context)
        else:
            return TradingError(f"Error in {context.operation}: {error}")
    
    def handle_error(
        self,
        error: Exception,
        context: ErrorContext,
        fallback_return: Any = None,
        reraise: bool = True
    ) -> Any:
        """
        Handle an error with proper mapping and logging.
        
        Args:
            error: The exception that occurred
            context: Error context information
            fallback_return: Value to return if not re-raising
            reraise: Whether to re-raise the mapped exception
            
        Returns:
            fallback_return if not re-raising, otherwise raises
        """
        # Map to specific exception if it's a generic Exception
        if type(error) == Exception:
            mapped_error = self.map_generic_error(error, context)
        elif isinstance(error, (ValueError, TypeError)):
            mapped_error = self.map_validation_error(error, context)
        else:
            # Already a specific exception, use as-is
            mapped_error = error
        
        # Log with full context
        self.logger.error(
            f"Error in {context.service_name}.{context.operation}: {mapped_error}",
            extra={
                'service_name': context.service_name,
                'operation': context.operation,
                'user_id': context.user_id,
                'symbol': context.symbol,
                'order_id': context.order_id,
                'error_type': type(mapped_error).__name__,
                'additional_info': context.additional_info,
                'stack_trace': traceback.format_exc()
            }
        )
        
        if reraise:
            raise mapped_error
        else:
            return fallback_return


def with_error_handling(
    operation: str,
    fallback_return: Any = None,
    reraise: bool = True,
    retry_config: Optional[RetryConfig] = None
):
    """
    Decorator for handling errors in service methods.
    
    Args:
        operation: Name of the operation being performed
        fallback_return: Value to return on error if not re-raising
        reraise: Whether to re-raise mapped exceptions
        retry_config: Retry configuration for transient errors
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            service_name = getattr(self, '__class__').__name__
            error_handler = ErrorHandler(service_name)
            
            context = ErrorContext(
                service_name=service_name,
                operation=operation,
                symbol=kwargs.get('symbol') or (args[0].symbol if args and hasattr(args[0], 'symbol') else None),
                order_id=kwargs.get('order_id') or (args[0].order_id if args and hasattr(args[0], 'order_id') else None)
            )
            
            attempts = 1
            if retry_config:
                attempts = retry_config.max_attempts
            
            last_error = None
            for attempt in range(attempts):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(self, *args, **kwargs)
                    else:
                        return func(self, *args, **kwargs)
                        
                except Exception as e:
                    last_error = e
                    
                    # Check if we should retry
                    if (retry_config and 
                        attempt < attempts - 1 and 
                        isinstance(e, retry_config.retryable_exceptions)):
                        
                        delay = retry_config.delay
                        if retry_config.exponential_backoff:
                            delay *= (2 ** attempt)
                        delay = min(delay, retry_config.max_delay)
                        
                        error_handler.logger.warning(
                            f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}"
                        )
                        await asyncio.sleep(delay)
                        continue
                    
                    break
            
            return error_handler.handle_error(
                last_error,
                context,
                fallback_return,
                reraise
            )
        
        @functools.wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            service_name = getattr(self, '__class__').__name__
            error_handler = ErrorHandler(service_name)
            
            context = ErrorContext(
                service_name=service_name,
                operation=operation,
                symbol=kwargs.get('symbol') or (args[0].symbol if args and hasattr(args[0], 'symbol') else None),
                order_id=kwargs.get('order_id') or (args[0].order_id if args and hasattr(args[0], 'order_id') else None)
            )
            
            attempts = 1
            if retry_config:
                attempts = retry_config.max_attempts
            
            last_error = None
            for attempt in range(attempts):
                try:
                    return func(self, *args, **kwargs)
                        
                except Exception as e:
                    last_error = e
                    
                    # Check if we should retry
                    if (retry_config and 
                        attempt < attempts - 1 and 
                        isinstance(e, retry_config.retryable_exceptions)):
                        
                        delay = retry_config.delay
                        if retry_config.exponential_backoff:
                            delay *= (2 ** attempt)
                        delay = min(delay, retry_config.max_delay)
                        
                        error_handler.logger.warning(
                            f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}"
                        )
                        time.sleep(delay)
                        continue
                    
                    break
            
            return error_handler.handle_error(
                last_error,
                context,
                fallback_return,
                reraise
            )
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


@contextmanager
def error_context(service_name: str, operation: str, **context_kwargs):
    """
    Context manager for handling errors with proper context.
    
    Usage:
        with error_context('OKXTradingService', 'place_order', symbol='BTC-USDT'):
            # code that might raise exceptions
            pass
    """
    error_handler = ErrorHandler(service_name)
    context = ErrorContext(
        service_name=service_name,
        operation=operation,
        **context_kwargs
    )
    
    try:
        yield error_handler
    except Exception as e:
        error_handler.handle_error(e, context, reraise=True)


STANDARD_RETRY = RetryConfig(max_attempts=3, delay=1.0, exponential_backoff=True)
FAST_RETRY = RetryConfig(max_attempts=2, delay=0.5, exponential_backoff=False)
CONNECTION_RETRY = RetryConfig(
    max_attempts=5, 
    delay=2.0, 
    exponential_backoff=True,
    max_delay=30.0,
    retryable_exceptions=(OKXConnectionError, RateLimitError)
)