import uuid
import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class CorrelationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding correlation IDs to requests and responses.
    
    Features:
    - Generates unique correlation ID for each request
    - Adds correlation ID to request state
    - Includes correlation ID in response headers
    - Logs request/response with correlation ID
    - Tracks request timing
    """
    
    def __init__(self, app, enable_logging: bool = True, enable_timing: bool = True):
        """
        Initialize correlation middleware.
        
        Args:
            app: FastAPI application
            enable_logging: Enable request/response logging
            enable_timing: Add timing headers to responses
        """
        super().__init__(app)
        self.enable_logging = enable_logging
        self.enable_timing = enable_timing
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with correlation ID tracking.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response with correlation headers
        """
        correlation_id = self._get_or_create_correlation_id(request)
        request.state.correlation_id = correlation_id
        
        start_time = time.time()
        if self.enable_logging:
            logger.info(
                f"Request started - {request.method} {request.url.path} "
                f"[{correlation_id}]"
            )
        try:
            response = await call_next(request)
            
            response.headers["X-Correlation-ID"] = correlation_id
            if self.enable_timing:
                process_time = time.time() - start_time
                response.headers["X-Process-Time"] = f"{process_time:.3f}"
            if self.enable_logging:
                process_time = time.time() - start_time
                logger.info(
                    f"Request completed - {request.method} {request.url.path} "
                    f"Status: {response.status_code} Time: {process_time:.3f}s "
                    f"[{correlation_id}]"
                )
            
            return response
            
        except Exception as exc:
            process_time = time.time() - start_time
            if self.enable_logging:
                logger.error(
                    f"Request failed - {request.method} {request.url.path} "
                    f"Error: {str(exc)} Time: {process_time:.3f}s "
                    f"[{correlation_id}]"
                )
            
            raise exc
    
    def _get_or_create_correlation_id(self, request: Request) -> str:
        """
        Get correlation ID from headers or create a new one.
        
        Args:
            request: HTTP request
            
        Returns:
            Correlation ID string
        """
        correlation_id = request.headers.get("X-Correlation-ID")
        
        if not correlation_id:
            correlation_id = (
                request.headers.get("X-Request-ID") or
                request.headers.get("X-Trace-ID") or
                request.headers.get("Correlation-ID")
            )
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        return correlation_id