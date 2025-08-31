"""
Comprehensive health check system for the trading application.
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentHealth(BaseModel):
    name: str
    status: HealthStatus
    message: Optional[str] = None
    last_check: Optional[datetime] = None
    response_time_ms: Optional[float] = None
    metadata: Dict[str, Any] = {}
    
    
class HealthCheckResult(BaseModel):
    status: HealthStatus
    timestamp: datetime
    checks: List[ComponentHealth]
    total_checks: int
    healthy_checks: int
    degraded_checks: int
    unhealthy_checks: int
    response_time_ms: float
    version: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "checks": [
                {
                    "name": check.name,
                    "status": check.status,
                    "message": check.message,
                    "last_check": check.last_check.isoformat() if check.last_check else None,
                    "response_time_ms": check.response_time_ms,
                    "metadata": check.metadata
                }
                for check in self.checks
            ],
            "summary": {
                "total": self.total_checks,
                "healthy": self.healthy_checks,
                "degraded": self.degraded_checks,
                "unhealthy": self.unhealthy_checks
            },
            "response_time_ms": self.response_time_ms,
            "version": self.version
        }


class HealthChecker:
    """
    Main health checker for application components.
    
    Features:
    - Component health checks
    - Dependency health checks
    - Performance monitoring
    - Readiness and liveness probes
    - Caching for performance
    """
    
    def __init__(
        self,
        cache_duration_seconds: int = 10,
        timeout_seconds: int = 5,
        version: str = "1.0.0"
    ):
        """
        Initialize health checker.
        
        Args:
            cache_duration_seconds: How long to cache health check results
            timeout_seconds: Timeout for individual health checks
            version: Application version
        """
        self.cache_duration = timedelta(seconds=cache_duration_seconds)
        self.timeout = timeout_seconds
        self.version = version
        self._checks: Dict[str, Callable] = {}
        self._cached_result: Optional[HealthCheckResult] = None
        self._cache_timestamp: Optional[datetime] = None
        self._check_lock = asyncio.Lock()
    
    def register_check(self, name: str, check_func: Callable) -> None:
        """
        Register a health check function.
        
        Args:
            name: Name of the component
            check_func: Async function that returns ComponentHealth
        """
        self._checks[name] = check_func
        logger.debug(f"Registered health check: {name}")
    
    def unregister_check(self, name: str) -> None:
        """
        Unregister a health check.
        
        Args:
            name: Name of the component
        """
        if name in self._checks:
            del self._checks[name]
            logger.debug(f"Unregistered health check: {name}")
    
    async def check_health(
        self,
        use_cache: bool = True,
        include_details: bool = True
    ) -> HealthCheckResult:
        """
        Perform health checks on all registered components.
        
        Args:
            use_cache: Whether to use cached results if available
            include_details: Whether to include detailed check results
            
        Returns:
            HealthCheckResult with overall status
        """
        if use_cache and self._is_cache_valid():
            logger.debug("Returning cached health check result")
            return self._cached_result
        
        async with self._check_lock:
            if use_cache and self._is_cache_valid():
                return self._cached_result
            
            start_time = time.time()
            checks = []
            tasks = []
            for name, check_func in self._checks.items():
                task = self._run_check_with_timeout(name, check_func)
                tasks.append(task)
            
            if tasks:
                check_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in check_results:
                    if isinstance(result, Exception):
                        logger.error(f"Health check failed with exception: {result}")
                        checks.append(ComponentHealth(
                            name="unknown",
                            status=HealthStatus.UNHEALTHY,
                            message=str(result)
                        ))
                    else:
                        checks.append(result)
            healthy_count = sum(1 for c in checks if c.status == HealthStatus.HEALTHY)
            degraded_count = sum(1 for c in checks if c.status == HealthStatus.DEGRADED)
            unhealthy_count = sum(1 for c in checks if c.status == HealthStatus.UNHEALTHY)
            
            if unhealthy_count > 0:
                overall_status = HealthStatus.UNHEALTHY
            elif degraded_count > 0:
                overall_status = HealthStatus.DEGRADED
            elif healthy_count == len(checks) and len(checks) > 0:
                overall_status = HealthStatus.HEALTHY
            else:
                overall_status = HealthStatus.UNKNOWN
            
            response_time = (time.time() - start_time) * 1000
            
            result = HealthCheckResult(
                status=overall_status,
                timestamp=datetime.utcnow(),
                checks=checks if include_details else [],
                total_checks=len(checks),
                healthy_checks=healthy_count,
                degraded_checks=degraded_count,
                unhealthy_checks=unhealthy_count,
                response_time_ms=response_time,
                version=self.version
            )
            self._cached_result = result
            self._cache_timestamp = datetime.utcnow()
            
            return result
    
    async def _run_check_with_timeout(
        self,
        name: str,
        check_func: Callable
    ) -> ComponentHealth:
        """
        Run a health check with timeout.
        
        Args:
            name: Component name
            check_func: Check function
            
        Returns:
            ComponentHealth result
        """
        try:
            start_time = time.time()
            result = await asyncio.wait_for(
                check_func(),
                timeout=self.timeout
            )
            if not isinstance(result, ComponentHealth):
                result = ComponentHealth(
                    name=name,
                    status=HealthStatus.UNKNOWN,
                    message="Invalid health check response"
                )
            if result.response_time_ms is None:
                result.response_time_ms = (time.time() - start_time) * 1000
            
            return result
            
        except asyncio.TimeoutError:
            logger.warning(f"Health check timeout for {name}")
            return ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check timeout ({self.timeout}s)",
                response_time_ms=self.timeout * 1000
            )
        except Exception as e:
            logger.error(f"Health check error for {name}: {e}")
            return ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=str(e)
            )
    
    def _is_cache_valid(self) -> bool:
        """Check if cached result is still valid."""
        if not self._cached_result or not self._cache_timestamp:
            return False
        
        age = datetime.utcnow() - self._cache_timestamp
        return age < self.cache_duration
    
    async def liveness_probe(self) -> Dict[str, Any]:
        """
        Liveness probe - checks if application is running.
        
        Returns:
            Simple liveness status
        """
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat(),
            "version": self.version
        }
    
    async def readiness_probe(self) -> Dict[str, Any]:
        """
        Readiness probe - checks if application is ready to serve requests.
        
        Returns:
            Readiness status with critical component checks
        """
        # Run health checks (use cache for performance)
        result = await self.check_health(use_cache=True, include_details=False)
        
        # Application is ready if not unhealthy
        is_ready = result.status != HealthStatus.UNHEALTHY
        
        return {
            "ready": is_ready,
            "status": result.status,
            "timestamp": result.timestamp.isoformat(),
            "checks_summary": {
                "total": result.total_checks,
                "healthy": result.healthy_checks,
                "degraded": result.degraded_checks,
                "unhealthy": result.unhealthy_checks
            },
            "version": self.version
        }
    
    async def startup_probe(self) -> Dict[str, Any]:
        """
        Startup probe - checks if application has started successfully.
        
        Returns:
            Startup status
        """
        # Run fresh health checks (no cache)
        result = await self.check_health(use_cache=False, include_details=True)
        
        # Check if critical components are healthy
        critical_healthy = all(
            check.status == HealthStatus.HEALTHY
            for check in result.checks
            if check.name in ["database", "okx"]  # Define critical components
        )
        
        return {
            "started": critical_healthy,
            "status": result.status,
            "timestamp": result.timestamp.isoformat(),
            "critical_components": critical_healthy,
            "all_checks": result.to_dict(),
            "version": self.version
        }


# Standard health check functions

async def check_database_health(mongodb_manager) -> ComponentHealth:
    """Check MongoDB database health."""
    try:
        start_time = time.time()
        
        if not mongodb_manager:
            return ComponentHealth(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message="MongoDB manager not initialized"
            )
        
        is_connected = await mongodb_manager.ensure_connected()
        
        if not is_connected:
            return ComponentHealth(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message="Unable to connect to MongoDB"
            )
        
        conn_info = mongodb_manager.get_connection_info()
        health_info = conn_info.get("health", {})
        if health_info.get("is_healthy", False):
            status = HealthStatus.HEALTHY
            message = "MongoDB connection healthy"
        else:
            status = HealthStatus.DEGRADED
            message = f"MongoDB degraded: {health_info.get('consecutive_failures', 0)} failures"
        
        response_time = (time.time() - start_time) * 1000
        
        return ComponentHealth(
            name="database",
            status=status,
            message=message,
            last_check=datetime.utcnow(),
            response_time_ms=response_time,
            metadata={
                "database": conn_info.get("database"),
                "pool_size": conn_info.get("config", {}).get("max_pool_size"),
                "health": health_info
            }
        )
        
    except Exception as e:
        logger.error(f"Database health check error: {e}")
        return ComponentHealth(
            name="database",
            status=HealthStatus.UNHEALTHY,
            message=str(e)
        )




async def check_okx_health(okx_service) -> ComponentHealth:
    """Check OKX service health."""
    try:
        start_time = time.time()
        
        if not okx_service:
            return ComponentHealth(
                name="okx",
                status=HealthStatus.UNHEALTHY,
                message="OKX service not initialized"
            )
        
        if not okx_service.initialized:
            return ComponentHealth(
                name="okx",
                status=HealthStatus.DEGRADED,
                message="OKX service not connected"
            )
        
        is_connected = await okx_service.ensure_connected()
        
        response_time = (time.time() - start_time) * 1000
        
        if is_connected:
            return ComponentHealth(
                name="okx",
                status=HealthStatus.HEALTHY,
                message="OKX API connection active",
                last_check=datetime.utcnow(),
                response_time_ms=response_time,
                metadata={"connected": True}
            )
        else:
            return ComponentHealth(
                name="okx",
                status=HealthStatus.UNHEALTHY,
                message="OKX API connection lost",
                last_check=datetime.utcnow(),
                response_time_ms=response_time,
                metadata={"connected": False}
            )
            
    except Exception as e:
        logger.error(f"OKX health check error: {e}")
        return ComponentHealth(
            name="okx",
            status=HealthStatus.UNHEALTHY,
            message=str(e)
        )


# Global health checker instance
health_checker = HealthChecker()