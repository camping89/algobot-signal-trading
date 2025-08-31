"""Service registry for dependency injection setup."""

import logging
from shared.container import ServiceContainer

# Import all services
from app.trading.services.okx.okx_base_service import OKXBaseService
from app.trading.services.okx.okx_trading_service import OKXTradingService
from app.trading.services.okx.okx_market_service import OKXMarketService
from app.trading.services.okx.okx_account_service import OKXAccountService
from app.trading.services.okx.okx_algo_service import OKXAlgoService

logger = logging.getLogger(__name__)


def create_service_container() -> ServiceContainer:
    """
    Create and configure the service container with all dependencies.
    
    Returns:
        Configured ServiceContainer instance
    """
    container = ServiceContainer()
    
    # Register base services (these are singletons)
    container.register_type('okx_base_service', OKXBaseService)
    
    # Register OKX services with their dependencies
    container.register_type('okx_trading_service', OKXTradingService, ['okx_base_service'])
    container.register_type('okx_market_service', OKXMarketService, ['okx_base_service'])
    container.register_type('okx_account_service', OKXAccountService, ['okx_base_service'])
    container.register_type('okx_algo_service', OKXAlgoService, ['okx_base_service'])
    
    logger.info("Service container configured with all dependencies")
    return container


def get_service_names() -> dict:
    """
    Get all registered service names organized by category.
    
    Returns:
        Dictionary with service categories and names
    """
    return {
        'base_services': [
            'okx_base_service'
        ],
        'okx_services': [
            'okx_trading_service',
            'okx_market_service',
            'okx_account_service',
            'okx_algo_service'
        ]
    }


class ServiceProvider:
    """
    Service provider wrapper for easy access to container services.
    Provides a clean interface for getting services throughout the application.
    """
    
    def __init__(self, container: ServiceContainer):
        self._container = container
    
    @property
    def container(self) -> ServiceContainer:
        """Get the underlying container."""
        return self._container
    
    
    # OKX Services
    @property
    def okx_base_service(self) -> OKXBaseService:
        return self._container.get('okx_base_service')
    
    @property
    def okx_trading_service(self) -> OKXTradingService:
        return self._container.get('okx_trading_service')
    
    @property
    def okx_market_service(self) -> OKXMarketService:
        return self._container.get('okx_market_service')
    
    @property
    def okx_account_service(self) -> OKXAccountService:
        return self._container.get('okx_account_service')
    
    @property
    def okx_algo_service(self) -> OKXAlgoService:
        return self._container.get('okx_algo_service')


# Global service provider instance
_service_provider: ServiceProvider = None


def init_services() -> ServiceProvider:
    """
    Initialize global service provider.
    Should be called once at application startup.
    
    Returns:
        ServiceProvider instance
    """
    global _service_provider
    
    if _service_provider is None:
        container = create_service_container()
        _service_provider = ServiceProvider(container)
        logger.info("Global service provider initialized")
    
    return _service_provider


def get_services() -> ServiceProvider:
    """
    Get the global service provider.
    
    Returns:
        ServiceProvider instance
        
    Raises:
        RuntimeError: If services not initialized
    """
    global _service_provider
    
    if _service_provider is None:
        raise RuntimeError("Services not initialized. Call init_services() first.")
    
    return _service_provider


async def shutdown_services():
    """Shutdown all services and cleanup resources."""
    global _service_provider
    
    if _service_provider is not None:
        await _service_provider.container.shutdown_all_services()
        _service_provider = None
        logger.info("All services shutdown and cleanup completed")