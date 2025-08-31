"""Global exception handlers for FastAPI application."""

import logging
from datetime import datetime
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from .services.exceptions import (
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

logger = logging.getLogger(__name__)


class ExceptionHandlers:

    @staticmethod
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation error on {request.url}: {exc.errors()}")
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "validation_error",
                "message": "Request validation failed",
                "details": exc.errors(),
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        )

    @staticmethod
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(f"HTTP error {exc.status_code} on {request.url}: {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "http_error",
                "message": exc.detail,
                "status_code": exc.status_code,
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        )

    @staticmethod
    async def authentication_exception_handler(request: Request, exc: AuthenticationError):
        logger.error(f"Authentication error on {request.url}: {exc}")
        
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "authentication_error",
                "message": "Authentication failed",
                "details": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        )

    @staticmethod
    async def validation_error_handler(request: Request, exc: ValidationError):
        logger.warning(f"Validation error on {request.url}: {exc}")
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "validation_error",
                "message": "Invalid request parameters",
                "details": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        )

    @staticmethod
    async def connection_error_handler(request: Request, exc: ConnectionError):
        logger.error(f"Connection error on {request.url}: {exc}")
        
        # Determine specific error type
        if isinstance(exc, OKXConnectionError):
            service = "OKX"
        else:
            service = "Unknown"
        
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "connection_error",
                "message": f"{service} service connection failed",
                "details": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path),
                "service": service.lower()
            }
        )

    @staticmethod
    async def service_not_initialized_handler(request: Request, exc: ServiceNotInitializedError):
        logger.error(f"Service not initialized on {request.url}: {exc}")
        
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "service_unavailable",
                "message": "Required service is not available",
                "details": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        )

    @staticmethod
    async def insufficient_funds_handler(request: Request, exc: InsufficientFundsError):
        logger.warning(f"Insufficient funds on {request.url}: {exc}")
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "insufficient_funds",
                "message": "Insufficient funds for the requested operation",
                "details": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        )

    @staticmethod
    async def symbol_not_found_handler(request: Request, exc: SymbolNotFoundError):
        logger.warning(f"Symbol not found on {request.url}: {exc}")
        
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "symbol_not_found",
                "message": "Trading symbol not found or unavailable",
                "details": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        )

    @staticmethod
    async def order_not_found_handler(request: Request, exc: OrderNotFoundError):
        """Handle order not found errors."""
        logger.warning(f"Order not found on {request.url}: {exc}")
        
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "order_not_found",
                "message": "Order not found",
                "details": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        )

    @staticmethod
    async def position_not_found_handler(request: Request, exc: PositionNotFoundError):
        logger.warning(f"Position not found on {request.url}: {exc}")
        
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "position_not_found",
                "message": "Position not found",
                "details": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        )

    @staticmethod
    async def rate_limit_handler(request: Request, exc: RateLimitError):
        logger.warning(f"Rate limit exceeded on {request.url}: {exc}")
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "rate_limit_exceeded",
                "message": "Rate limit exceeded, please try again later",
                "details": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path),
                "retry_after": getattr(exc, 'retry_after', 60)
            }
        )

    @staticmethod
    async def trade_execution_error_handler(request: Request, exc: TradeExecutionError):
        logger.error(f"Trade execution error on {request.url}: {exc}")
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "trade_execution_error",
                "message": "Trade execution failed",
                "details": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        )

    @staticmethod
    async def api_error_handler(request: Request, exc: APIError):
        """Handle API errors."""
        logger.error(f"API error on {request.url}: {exc}")
        
        # Determine API type
        if isinstance(exc, OKXAPIError):
            api_type = "OKX"
        else:
            api_type = "Unknown"
        
        response_content = {
            "error": "api_error",
            "message": f"{api_type} API error occurred",
            "details": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path),
            "api": api_type.lower()
        }
        
        # Include additional error info if available
        if hasattr(exc, 'code') and exc.code:
            response_content["error_code"] = exc.code
        if hasattr(exc, 'response') and exc.response:
            response_content["api_response"] = exc.response
        
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content=response_content
        )

    @staticmethod
    async def risk_limit_handler(request: Request, exc: RiskLimitExceededError):
        logger.warning(f"Risk limit exceeded on {request.url}: {exc}")
        
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "risk_limit_exceeded",
                "message": "Operation blocked by risk management",
                "details": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        )

    @staticmethod
    async def trading_error_handler(request: Request, exc: TradingError):
        logger.error(f"Trading error on {request.url}: {exc}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "trading_error",
                "message": "A trading error occurred",
                "details": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        )

    @staticmethod
    async def general_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unexpected error on {request.url}: {exc}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred",
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        )


def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI app."""
    handlers = ExceptionHandlers()
    
    # Pydantic validation errors
    app.add_exception_handler(RequestValidationError, handlers.validation_exception_handler)
    
    # HTTP exceptions
    app.add_exception_handler(HTTPException, handlers.http_exception_handler)
    
    # Custom trading exceptions (specific first, then general)
    app.add_exception_handler(AuthenticationError, handlers.authentication_exception_handler)
    app.add_exception_handler(ValidationError, handlers.validation_error_handler)
    app.add_exception_handler(ServiceNotInitializedError, handlers.service_not_initialized_handler)
    app.add_exception_handler(InsufficientFundsError, handlers.insufficient_funds_handler)
    app.add_exception_handler(SymbolNotFoundError, handlers.symbol_not_found_handler)
    app.add_exception_handler(OrderNotFoundError, handlers.order_not_found_handler)
    app.add_exception_handler(PositionNotFoundError, handlers.position_not_found_handler)
    app.add_exception_handler(RateLimitError, handlers.rate_limit_handler)
    app.add_exception_handler(TradeExecutionError, handlers.trade_execution_error_handler)
    app.add_exception_handler(RiskLimitExceededError, handlers.risk_limit_handler)
    app.add_exception_handler(APIError, handlers.api_error_handler)
    app.add_exception_handler(ConnectionError, handlers.connection_error_handler)
    app.add_exception_handler(TradingError, handlers.trading_error_handler)
    
    # Catch-all for unexpected exceptions
    app.add_exception_handler(Exception, handlers.general_exception_handler)
    
    logger.info("All exception handlers registered")