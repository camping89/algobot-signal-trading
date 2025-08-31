import uuid
import time
import logging
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from shared.utils.exceptions import TradingError, ValidationError
from shared.services.exceptions import ServiceError

logger = logging.getLogger(__name__)

def create_error_response(
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 500,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create standardized error response format.
    
    Args:
        message: Error message
        error_code: Specific error code
        details: Additional error details
        status_code: HTTP status code
        correlation_id: Request correlation ID
        
    Returns:
        Standardized error response dictionary
    """
    response = {
        "status": "error",
        "message": message,
        "error_code": error_code,
        "details": details,
        "timestamp": time.time()
    }
    
    if correlation_id:
        response["correlation_id"] = correlation_id
        
    return response

def get_correlation_id(request: Request) -> str:
    """Get or create correlation ID for request tracking."""
    if hasattr(request.state, 'correlation_id'):
        return request.state.correlation_id
    
    # Generate new correlation ID if not present
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    return correlation_id

# Exception Handlers

async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle custom validation errors."""
    correlation_id = get_correlation_id(request)
    logger.warning(f"Validation error: {str(exc)} [{correlation_id}]")
    
    return JSONResponse(
        status_code=400,
        content=create_error_response(
            message="Validation failed",
            error_code="VALIDATION_ERROR",
            details={"validation_error": str(exc)},
            status_code=400,
            correlation_id=correlation_id
        )
    )

async def trading_error_handler(request: Request, exc: TradingError):
    """Handle trading-specific errors."""
    correlation_id = get_correlation_id(request)
    logger.error(f"Trading error: {str(exc)} [{correlation_id}]")
    
    return JSONResponse(
        status_code=400,
        content=create_error_response(
            message="Trading operation failed",
            error_code="TRADING_ERROR",
            details={"trading_error": str(exc)},
            status_code=400,
            correlation_id=correlation_id
        )
    )

async def service_error_handler(request: Request, exc: ServiceError):
    """Handle service-level errors."""
    correlation_id = get_correlation_id(request)
    logger.error(f"Service error: {str(exc)} [{correlation_id}]")
    
    return JSONResponse(
        status_code=500,
        content=create_error_response(
            message="Service unavailable",
            error_code="SERVICE_ERROR",
            details={"service_error": str(exc)},
            status_code=500,
            correlation_id=correlation_id
        )
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions."""
    correlation_id = get_correlation_id(request)
    logger.warning(f"HTTP error: {exc.status_code} - {exc.detail} [{correlation_id}]")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            message=exc.detail,
            error_code="HTTP_ERROR",
            status_code=exc.status_code,
            correlation_id=correlation_id
        )
    )

async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle Starlette HTTP exceptions."""
    correlation_id = get_correlation_id(request)
    logger.warning(f"Starlette HTTP error: {exc.status_code} - {exc.detail} [{correlation_id}]")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            message=str(exc.detail),
            error_code="HTTP_ERROR",
            status_code=exc.status_code,
            correlation_id=correlation_id
        )
    )

async def request_validation_error_handler(request: Request, exc: RequestValidationError):
    """Handle FastAPI request validation errors."""
    correlation_id = get_correlation_id(request)
    logger.warning(f"Request validation error: {str(exc)} [{correlation_id}]")
    
    # Extract detailed validation errors
    validation_errors = []
    for error in exc.errors():
        validation_errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content=create_error_response(
            message="Request validation failed",
            error_code="REQUEST_VALIDATION_ERROR",
            details={"validation_errors": validation_errors},
            status_code=422,
            correlation_id=correlation_id
        )
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    correlation_id = get_correlation_id(request)
    logger.error(f"Unhandled error: {str(exc)} [{correlation_id}]", exc_info=True)
    
    # Only include error details in debug mode
    details = None
    if logger.isEnabledFor(logging.DEBUG):
        details = {
            "error": str(exc),
            "type": type(exc).__name__
        }
    
    return JSONResponse(
        status_code=500,
        content=create_error_response(
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details=details,
            status_code=500,
            correlation_id=correlation_id
        )
    )

def setup_exception_handlers(app):
    """
    Set up all global exception handlers for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    
    # Custom exception handlers
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(TradingError, trading_error_handler)
    app.add_exception_handler(ServiceError, service_error_handler)
    
    # FastAPI/Starlette exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    
    # Catch-all exception handler (should be last)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Global exception handlers registered successfully")