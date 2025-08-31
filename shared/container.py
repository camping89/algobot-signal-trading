"""Dependency injection container for managing service instances."""

import logging
from typing import Any, Dict, Callable, TypeVar, Generic, Type, Optional
from threading import Lock
import asyncio

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServiceFactory(Generic[T]):
    """Factory wrapper for service creation."""
    
    def __init__(self, factory_func: Callable[..., T], dependencies: list = None):
        self.factory_func = factory_func
        self.dependencies = dependencies or []
    
    def create(self, container: 'ServiceContainer') -> T:
        """Create service instance with resolved dependencies."""
        resolved_deps = []
        for dep_name in self.dependencies:
            resolved_deps.append(container.get(dep_name))
        
        return self.factory_func(*resolved_deps)


class ServiceContainer:
    """
    Dependency injection container with singleton support and lifecycle management.
    
    Provides service registration, resolution, and cleanup functionality.
    Ensures services are instantiated only once (singleton pattern).
    """
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, ServiceFactory] = {}
        self._lock = Lock()
        self._initialized_services: set = set()
        self._logger = logging.getLogger(self.__class__.__name__)
    
    def register_singleton(self, name: str, instance: Any):
        """
        Register a singleton service instance.
        
        Args:
            name: Service name for lookup
            instance: Service instance
        """
        with self._lock:
            self._services[name] = instance
            self._logger.debug(f"Registered singleton service: {name}")
    
    def register_factory(self, name: str, factory_func: Callable, dependencies: list = None):
        """
        Register a service factory with dependencies.
        
        Args:
            name: Service name for lookup
            factory_func: Function to create service instance
            dependencies: List of dependency service names
        """
        with self._lock:
            self._factories[name] = ServiceFactory(factory_func, dependencies)
            self._logger.debug(f"Registered factory service: {name} with dependencies: {dependencies}")
    
    def register_type(self, name: str, service_type: Type[T], dependencies: list = None):
        """
        Register a service type (class) with dependencies.
        
        Args:
            name: Service name for lookup
            service_type: Service class type
            dependencies: List of dependency service names
        """
        self.register_factory(name, service_type, dependencies)
    
    def get(self, name: str) -> Any:
        """
        Get service instance by name.
        Creates instance if not exists using registered factory.
        
        Args:
            name: Service name
            
        Returns:
            Service instance
            
        Raises:
            ValueError: If service not registered
        """
        with self._lock:
            # Return existing instance if available
            if name in self._services:
                return self._services[name]
            
            # Create instance using factory
            if name in self._factories:
                factory = self._factories[name]
                instance = factory.create(self)
                self._services[name] = instance
                self._logger.debug(f"Created service instance: {name}")
                return instance
            
            raise ValueError(f"Service '{name}' not registered")
    
    def get_optional(self, name: str) -> Optional[Any]:
        """
        Get service instance by name, return None if not found.
        
        Args:
            name: Service name
            
        Returns:
            Service instance or None
        """
        try:
            return self.get(name)
        except ValueError:
            return None
    
    def has_service(self, name: str) -> bool:
        """
        Check if service is registered.
        
        Args:
            name: Service name
            
        Returns:
            True if service is registered
        """
        with self._lock:
            return name in self._services or name in self._factories
    
    async def initialize_service(self, name: str) -> bool:
        """
        Initialize a service if it supports initialization.
        
        Args:
            name: Service name
            
        Returns:
            True if initialization successful or not needed
        """
        if name in self._initialized_services:
            return True
        
        service = self.get(name)
        
        # Check if service has initialization method
        if hasattr(service, 'ensure_initialized'):
            try:
                result = await service.ensure_initialized()
                if result:
                    self._initialized_services.add(name)
                    self._logger.info(f"Initialized service: {name}")
                else:
                    self._logger.error(f"Failed to initialize service: {name}")
                return result
            except Exception as e:
                self._logger.exception(f"Error initializing service {name}: {e}")
                return False
        elif hasattr(service, 'initialize'):
            try:
                result = await service.initialize()
                if result:
                    self._initialized_services.add(name)
                    self._logger.info(f"Initialized service: {name}")
                else:
                    self._logger.error(f"Failed to initialize service: {name}")
                return result
            except Exception as e:
                self._logger.exception(f"Error initializing service {name}: {e}")
                return False
        else:
            # Service doesn't need initialization
            self._initialized_services.add(name)
            return True
    
    async def initialize_all_services(self) -> Dict[str, bool]:
        """
        Initialize all registered services that support initialization.
        
        Returns:
            Dictionary with service names and initialization results
        """
        results = {}
        
        # Get all service names
        all_services = set(self._services.keys()) | set(self._factories.keys())
        
        for service_name in all_services:
            results[service_name] = await self.initialize_service(service_name)
        
        return results
    
    async def shutdown_service(self, name: str):
        """
        Shutdown a service if it supports shutdown.
        
        Args:
            name: Service name
        """
        if name not in self._services:
            return
        
        service = self._services[name]
        
        if hasattr(service, 'shutdown'):
            try:
                await service.shutdown()
                self._logger.info(f"Shutdown service: {name}")
            except Exception as e:
                self._logger.exception(f"Error shutting down service {name}: {e}")
        
        # Remove from initialized services
        self._initialized_services.discard(name)
    
    async def shutdown_all_services(self):
        """Shutdown all services that support shutdown."""
        # Shutdown in reverse order to handle dependencies
        service_names = list(self._services.keys())
        service_names.reverse()
        
        for service_name in service_names:
            await self.shutdown_service(service_name)
        
        self._logger.info("All services shutdown")
    
    def clear(self):
        """Clear all registered services and factories."""
        with self._lock:
            self._services.clear()
            self._factories.clear()
            self._initialized_services.clear()
            self._logger.debug("Cleared all services")
    
    def list_services(self) -> Dict[str, str]:
        """
        List all registered services with their status.
        
        Returns:
            Dictionary with service names and status
        """
        services = {}
        
        for name in self._services.keys():
            services[name] = "instantiated"
        
        for name in self._factories.keys():
            if name not in services:
                services[name] = "registered"
        
        return services