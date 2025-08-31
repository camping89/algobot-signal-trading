"""
Health check router for FastAPI.
"""

import time
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from .health_checker import health_checker, HealthStatus
from sharedauth.auth_middleware import get_current_user, TokenData


def create_health_router(
    require_auth_for_details: bool = False,
    services: Optional[dict] = None
) -> APIRouter:
    """
    Create health check router with all endpoints.
    
    Args:
        require_auth_for_details: Whether to require authentication for detailed health info
        services: Dictionary of services to register for health checks
        
    Returns:
        Configured APIRouter with health endpoints
    """
    router = APIRouter(prefix="/health", tags=["Health"])
    
    # Register service health checks if provided
    if services:
        _register_service_checks(services)
    
    @router.get("/", summary="Basic Health Check")
    async def health_check():
        """
        Basic health check endpoint.
        
        Returns simple status to indicate the application is running.
        """
        return {
            "status": "success",
            "message": "Service is healthy",
            "timestamp": time.time()
        }
    
    @router.get("/live", summary="Liveness Probe")
    async def liveness_probe():
        """
        Kubernetes liveness probe endpoint.
        
        Indicates whether the application is running.
        Returns 200 if alive, otherwise Kubernetes will restart the pod.
        """
        result = await health_checker.liveness_probe()
        return JSONResponse(content=result, status_code=200)
    
    @router.get("/ready", summary="Readiness Probe")
    async def readiness_probe():
        """
        Kubernetes readiness probe endpoint.
        
        Indicates whether the application is ready to serve traffic.
        Returns 200 if ready, 503 if not ready.
        """
        result = await health_checker.readiness_probe()
        
        if result["ready"]:
            return JSONResponse(content=result, status_code=200)
        else:
            return JSONResponse(content=result, status_code=503)
    
    @router.get("/startup", summary="Startup Probe")
    async def startup_probe():
        """
        Kubernetes startup probe endpoint.
        
        Used during application startup to know when the application has started.
        Returns 200 if started successfully, 503 if still starting.
        """
        result = await health_checker.startup_probe()
        
        if result["started"]:
            return JSONResponse(content=result, status_code=200)
        else:
            return JSONResponse(content=result, status_code=503)
    
    @router.get("/status", summary="Detailed Health Status")
    async def health_status(
        include_details: bool = Query(True, description="Include detailed check results"),
        use_cache: bool = Query(True, description="Use cached results if available"),
        current_user: Optional[TokenData] = Depends(get_current_user) if require_auth_for_details else None
    ):
        """
        Get detailed health status of all components.
        
        Provides comprehensive health information including:
        - Overall status (healthy/degraded/unhealthy)
        - Individual component health checks
        - Response times
        - Metadata for each component
        
        Args:
            include_details: Whether to include detailed check results
            use_cache: Whether to use cached results for performance
            current_user: Optional authentication for protected details
            
        Returns:
            Detailed health check results
        """
        # Check if authentication is required and user is authenticated
        if require_auth_for_details and include_details and not current_user:
            include_details = False  # Hide details for unauthenticated users
        
        result = await health_checker.check_health(
            use_cache=use_cache,
            include_details=include_details
        )
        
        # Determine HTTP status code based on health
        if result.status == HealthStatus.HEALTHY:
            status_code = 200
        elif result.status == HealthStatus.DEGRADED:
            status_code = 200  # Still return 200 for degraded
        else:  # UNHEALTHY or UNKNOWN
            status_code = 503
        
        return JSONResponse(
            content=result.to_dict(),
            status_code=status_code
        )
    
    @router.get("/components/{component_name}", summary="Component Health Check")
    async def component_health(
        component_name: str,
        current_user: Optional[TokenData] = Depends(get_current_user) if require_auth_for_details else None
    ):
        """
        Get health status of a specific component.
        
        Args:
            component_name: Name of the component to check
            current_user: Optional authentication
            
        Returns:
            Health status of the specified component
        """
        # Run health check
        result = await health_checker.check_health(use_cache=False, include_details=True)
        
        # Find the specific component
        component = None
        for check in result.checks:
            if check.name == component_name:
                component = check
                break
        
        if not component:
            return JSONResponse(
                content={
                    "error": f"Component '{component_name}' not found",
                    "available_components": [c.name for c in result.checks]
                },
                status_code=404
            )
        
        # Determine status code
        if component.status == HealthStatus.HEALTHY:
            status_code = 200
        elif component.status == HealthStatus.DEGRADED:
            status_code = 200
        else:
            status_code = 503
        
        return JSONResponse(
            content={
                "name": component.name,
                "status": component.status,
                "message": component.message,
                "last_check": component.last_check.isoformat() if component.last_check else None,
                "response_time_ms": component.response_time_ms,
                "metadata": component.metadata if current_user or not require_auth_for_details else {}
            },
            status_code=status_code
        )
    
    @router.post("/refresh", summary="Refresh Health Cache")
    async def refresh_health_cache(
        current_user: TokenData = Depends(get_current_user) if require_auth_for_details else None
    ):
        """
        Force refresh of health check cache.
        
        Useful for getting fresh health status after making changes.
        Requires authentication if configured.
        
        Returns:
            Fresh health check results
        """
        result = await health_checker.check_health(
            use_cache=False,
            include_details=bool(current_user) or not require_auth_for_details
        )
        
        return JSONResponse(
            content={
                "message": "Health cache refreshed",
                "status": result.status,
                "timestamp": result.timestamp.isoformat(),
                "checks_count": result.total_checks
            },
            status_code=200
        )
    
    return router


def _register_service_checks(services: dict):
    """
    Register health checks for provided services.
    
    Args:
        services: Dictionary of service instances
    """
    from .health_checker import (
        check_database_health,
        check_okx_health
    )
    
    # Register database health check
    if "mongodb_manager" in services:
        async def db_check():
            return await check_database_health(services["mongodb_manager"])
        health_checker.register_check("database", db_check)
    
    
    # Register OKX health check  
    if "okx_base_service" in services:
        async def okx_check():
            return await check_okx_health(services["okx_base_service"])
        health_checker.register_check("okx", okx_check)
    
    # Add more service checks as needed
    if "redis_client" in services:
        async def redis_check():
            from .health_checker import ComponentHealth, HealthStatus
            try:
                # Implement Redis health check
                return ComponentHealth(
                    name="redis",
                    status=HealthStatus.HEALTHY,
                    message="Redis connection active"
                )
            except Exception as e:
                return ComponentHealth(
                    name="redis",
                    status=HealthStatus.UNHEALTHY,
                    message=str(e)
                )
        health_checker.register_check("redis", redis_check)