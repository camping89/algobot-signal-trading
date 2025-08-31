import uuid
import time
import logging
from typing import Dict, Any, Optional, Callable, List
from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from shared.services.exceptions import TradingError, ServiceError
from shared.utils.exceptions import ValidationError

logger = logging.getLogger(__name__)

class BaseRouter:
    """
    Base router class with common middleware, error handling, and response formatting.
    
    Features:
    - Request correlation ID generation
    - Request/response logging with timing
    - Standardized error responses
    - Request validation
    - Common middleware pipeline
    """
    
    def __init__(
        self,
        prefix: str,
        tags: List[str],
        dependencies: Optional[List[Callable]] = None,
        include_in_schema: bool = True,
        enable_cors: bool = True,
        enable_timing: bool = True,
        enable_request_logging: bool = True
    ):
        """
        Initialize base router with configuration options.
        
        Args:
            prefix: URL prefix for all routes in this router
            tags: OpenAPI tags for documentation
            dependencies: Global dependencies for all routes
            include_in_schema: Whether to include routes in OpenAPI schema
            enable_cors: Enable CORS headers
            enable_timing: Add timing headers to responses
            enable_request_logging: Log all requests and responses
        """
        self.prefix = prefix
        self.tags = tags
        self.dependencies = dependencies or []
        self.include_in_schema = include_in_schema
        self.enable_cors = enable_cors
        self.enable_timing = enable_timing
        self.enable_request_logging = enable_request_logging
        
        # Create the FastAPI router
        self.router = APIRouter(
            prefix=prefix,
            tags=tags,
            dependencies=self.dependencies,
            include_in_schema=include_in_schema
        )
        
        # Add middleware
        self._setup_middleware()
    
    def _setup_middleware(self) -> None:
        """Set up common middleware for the router."""
        
        @self.router.middleware("http")
        async def add_correlation_id(request: Request, call_next):
            """Add correlation ID to request for tracking."""
            correlation_id = str(uuid.uuid4())
            request.state.correlation_id = correlation_id
            
            # Add to response headers
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
        
        @self.router.middleware("http") 
        async def timing_middleware(request: Request, call_next):
            """Add request timing information."""
            if not self.enable_timing:
                return await call_next(request)
                
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
        
        @self.router.middleware("http")
        async def cors_middleware(request: Request, call_next):
            """Add CORS headers if enabled."""
            response = await call_next(request)
            
            if self.enable_cors:
                response.headers["Access-Control-Allow-Origin"] = "*"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Correlation-ID"
                response.headers["Access-Control-Expose-Headers"] = "X-Correlation-ID, X-Process-Time"
            
            return response
        
        @self.router.middleware("http")
        async def request_logging_middleware(request: Request, call_next):
            """Log requests and responses with correlation ID."""
            if not self.enable_request_logging:
                return await call_next(request)
            
            correlation_id = getattr(request.state, 'correlation_id', 'unknown')
            start_time = time.time()
            
            # Log request
            logger.info(
                f"Request started - {request.method} {request.url.path} "
                f"[{correlation_id}]"
            )
            
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Request completed - {request.method} {request.url.path} "
                f"Status: {response.status_code} Time: {process_time:.3f}s "
                f"[{correlation_id}]"
            )
            
            return response
    
    def create_standard_response(
        self,
        data: Any = None,
        message: str = "Success",
        status: str = "success",
        status_code: int = 200,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create standardized API response format.
        
        Args:
            data: Response data payload
            message: Human-readable message
            status: Status indicator (success/error)
            status_code: HTTP status code
            correlation_id: Request correlation ID
            
        Returns:
            Standardized response dictionary
        """
        response = {
            "status": status,
            "message": message,
            "data": data,
            "timestamp": time.time()
        }
        
        if correlation_id:
            response["correlation_id"] = correlation_id
            
        return response
    
    def create_error_response(
        self,
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
    
    def add_exception_handler(self, exception_type: type, handler: Callable):
        """Add custom exception handler to the router."""
        self.router.add_exception_handler(exception_type, handler)
    
    def setup_default_exception_handlers(self):
        """Set up default exception handlers for common error types."""
        
        @self.router.exception_handler(ValidationError)
        async def validation_error_handler(request: Request, exc: ValidationError):
            correlation_id = getattr(request.state, 'correlation_id', None)
            logger.warning(f"Validation error: {str(exc)} [{correlation_id}]")
            
            return JSONResponse(
                status_code=400,
                content=self.create_error_response(
                    message="Validation failed",
                    error_code="VALIDATION_ERROR",
                    details={"validation_error": str(exc)},
                    status_code=400,
                    correlation_id=correlation_id
                )
            )
        
        @self.router.exception_handler(TradingError)
        async def trading_error_handler(request: Request, exc: TradingError):
            correlation_id = getattr(request.state, 'correlation_id', None)
            logger.error(f"Trading error: {str(exc)} [{correlation_id}]")
            
            return JSONResponse(
                status_code=400,
                content=self.create_error_response(
                    message="Trading operation failed",
                    error_code="TRADING_ERROR",
                    details={"trading_error": str(exc)},
                    status_code=400,
                    correlation_id=correlation_id
                )
            )
        
        @self.router.exception_handler(ServiceError)
        async def service_error_handler(request: Request, exc: ServiceError):
            correlation_id = getattr(request.state, 'correlation_id', None)
            logger.error(f"Service error: {str(exc)} [{correlation_id}]")
            
            return JSONResponse(
                status_code=500,
                content=self.create_error_response(
                    message="Service unavailable",
                    error_code="SERVICE_ERROR",
                    details={"service_error": str(exc)},
                    status_code=500,
                    correlation_id=correlation_id
                )
            )
        
        @self.router.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            correlation_id = getattr(request.state, 'correlation_id', None)
            logger.warning(f"HTTP error: {exc.status_code} - {exc.detail} [{correlation_id}]")
            
            return JSONResponse(
                status_code=exc.status_code,
                content=self.create_error_response(
                    message=exc.detail,
                    error_code="HTTP_ERROR",
                    status_code=exc.status_code,
                    correlation_id=correlation_id
                )
            )
        
        @self.router.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            correlation_id = getattr(request.state, 'correlation_id', None)
            logger.error(f"Unhandled error: {str(exc)} [{correlation_id}]", exc_info=True)
            
            return JSONResponse(
                status_code=500,
                content=self.create_error_response(
                    message="Internal server error",
                    error_code="INTERNAL_ERROR",
                    details={"error": str(exc)} if logger.isEnabledFor(logging.DEBUG) else None,
                    status_code=500,
                    correlation_id=correlation_id
                )
            )
    
    def add_route(self, path: str, methods: List[str], endpoint: Callable, **kwargs):
        """Add a route to the router with standard error handling wrapper."""
        
        async def wrapped_endpoint(*args, **kwargs):
            try:
                result = await endpoint(*args, **kwargs)
                
                # If result is already a Response, return it directly
                if isinstance(result, Response):
                    return result
                
                # If result is a dict with 'status' key, assume it's already formatted
                if isinstance(result, dict) and 'status' in result:
                    return result
                
                # Otherwise, wrap in standard response format
                request = kwargs.get('request')
                correlation_id = getattr(request.state, 'correlation_id', None) if request else None
                
                return self.create_standard_response(
                    data=result,
                    correlation_id=correlation_id
                )
                
            except Exception as exc:
                # Let the exception handlers deal with it
                raise exc
        
        # Add the route with the wrapped endpoint
        for method in methods:
            self.router.add_api_route(
                path=path,
                endpoint=wrapped_endpoint,
                methods=[method.upper()],
                **kwargs
            )
    
    def get_router(self) -> APIRouter:
        """Get the configured FastAPI router instance."""
        return self.router
    
    @asynccontextmanager
    async def request_context(self, request: Request):
        """Context manager for request-specific operations."""
        correlation_id = getattr(request.state, 'correlation_id', 'unknown')
        start_time = time.time()
        
        try:
            yield {
                'correlation_id': correlation_id,
                'start_time': start_time,
                'request': request
            }
        finally:
            process_time = time.time() - start_time
            logger.debug(f"Request context closed - Time: {process_time:.3f}s [{correlation_id}]")

def create_base_router(
    prefix: str,
    tags: List[str],
    **kwargs
) -> BaseRouter:
    """
    Factory function to create a BaseRouter instance with default settings.
    
    Args:
        prefix: URL prefix for the router
        tags: OpenAPI tags
        **kwargs: Additional configuration options
        
    Returns:
        Configured BaseRouter instance
    """
    base_router = BaseRouter(prefix=prefix, tags=tags, **kwargs)
    base_router.setup_default_exception_handlers()
    return base_router