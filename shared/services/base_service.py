"""Base service classes for reducing code duplication across services."""

from abc import ABC, ABCMeta, abstractmethod
from typing import Generic, TypeVar
import logging
import asyncio
from threading import Lock

logger = logging.getLogger(__name__)

T = TypeVar('T')


class SingletonMeta(type):
    """Thread-safe Singleton metaclass implementation."""
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class SingletonABCMeta(SingletonMeta, ABCMeta):
    """Combined metaclass for Singleton pattern with Abstract Base Classes."""
    pass


class BaseService(ABC):
    """
    Abstract base service class with common functionality.
    Provides connection management, initialization patterns, and error handling.
    """
    
    def __init__(self):
        """Initialize base service with common attributes."""
        self._initialized = False
        self._initialization_lock = asyncio.Lock()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @property
    def initialized(self) -> bool:
        """Check if service is initialized."""
        return self._initialized
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the service.
        Must be implemented by subclasses.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def shutdown(self):
        """
        Shutdown the service and cleanup resources.
        Must be implemented by subclasses.
        """
        pass
    
    async def ensure_initialized(self) -> bool:
        """
        Ensure service is initialized, thread-safe initialization.
        
        Returns:
            bool: True if initialized successfully, False otherwise
        """
        if self._initialized:
            return True
        
        async with self._initialization_lock:
            if self._initialized:
                return True
            
            try:
                result = await self.initialize()
                if result:
                    self._initialized = True
                    self.logger.info(f"{self.__class__.__name__} initialized successfully")
                else:
                    self.logger.error(f"Failed to initialize {self.__class__.__name__}")
                return result
            except Exception as e:
                self.logger.exception(f"Error initializing {self.__class__.__name__}: {e}")
                return False
    
    def __del__(self):
        """Cleanup on deletion."""
        if self._initialized:
            # Create event loop if needed for async cleanup
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.shutdown())
                else:
                    loop.run_until_complete(self.shutdown())
            except RuntimeError:
                self.logger.warning(f"Could not properly shutdown {self.__class__.__name__}")


class BaseTradingService(BaseService, Generic[T]):
    """
    Base class for trading services with connection dependency.
    Provides common patterns for services that depend on a connection service.
    """
    
    def __init__(self, connection_service: T):
        """
        Initialize trading service with connection dependency.
        
        Args:
            connection_service: The connection service (MT5 or OKX base service)
        """
        super().__init__()
        self.connection_service = connection_service
    
    @property
    def connected(self) -> bool:
        """Check if underlying connection is active."""
        return self.connection_service.initialized if self.connection_service else False
    
    async def ensure_connected(self) -> bool:
        """
        Ensure connection service is connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        if not self.connection_service:
            self.logger.error("No connection service available")
            return False
        
        if hasattr(self.connection_service, 'ensure_connected'):
            return await self.connection_service.ensure_connected()
        elif hasattr(self.connection_service, 'initialized'):
            return self.connection_service.initialized
        else:
            self.logger.error("Connection service doesn't support connection checking")
            return False
    
    async def initialize(self) -> bool:
        """
        Default initialization that checks connection.
        Can be overridden by subclasses for additional initialization.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        return await self.ensure_connected()


class BaseConnectionService(BaseService, metaclass=SingletonABCMeta):
    """
    Base class for connection services (MT5, OKX).
    Implements singleton pattern with thread-safe initialization.
    """
    
    def __init__(self):
        """Initialize connection service as singleton."""
        if hasattr(self, '_singleton_initialized'):
            return
        
        super().__init__()
        self._singleton_initialized = True
        self._connection = None
    
    @property
    def connection(self):
        """Get the underlying connection object."""
        return self._connection
    
    @abstractmethod
    async def connect(self, *args, **kwargs) -> bool:
        """
        Establish connection with external service.
        Must be implemented by subclasses.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self):
        """
        Disconnect from external service.
        Must be implemented by subclasses.
        """
        pass
    
    async def ensure_connected(self) -> bool:
        """
        Verify connection is active, attempt reconnection if needed.
        
        Returns:
            bool: True if connected, False otherwise
        """
        if not self._initialized:
            return False
        
        return self._initialized
    
    async def shutdown(self):
        """Shutdown connection and cleanup resources."""
        if self._initialized:
            await self.disconnect()
            self._connection = None
            self._initialized = False
            self.logger.info(f"{self.__class__.__name__} connection closed")