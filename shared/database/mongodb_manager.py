"""MongoDB connection manager with connection pooling and health monitoring."""

import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure, OperationFailure
import threading

from shared.services.exceptions import ConnectionError, ConfigurationError, ValidationError

logger = logging.getLogger(__name__)


class MongoDBConfig:
    
    def __init__(
        self,
        url: str,
        database_name: str,
        min_pool_size: int = 10,
        max_pool_size: int = 50,
        max_idle_time_ms: int = 30000,
        wait_queue_timeout_ms: int = 5000,
        server_selection_timeout_ms: int = 5000,
        connect_timeout_ms: int = 10000,
        socket_timeout_ms: int = 0,
        heartbeat_frequency_ms: int = 10000,
        retry_writes: bool = True,
        retry_reads: bool = True
    ):
        self.url = url
        self.database_name = database_name
        self.min_pool_size = min_pool_size
        self.max_pool_size = max_pool_size
        self.max_idle_time_ms = max_idle_time_ms
        self.wait_queue_timeout_ms = wait_queue_timeout_ms
        self.server_selection_timeout_ms = server_selection_timeout_ms
        self.connect_timeout_ms = connect_timeout_ms
        self.socket_timeout_ms = socket_timeout_ms
        self.heartbeat_frequency_ms = heartbeat_frequency_ms
        self.retry_writes = retry_writes
        self.retry_reads = retry_reads
    
    def to_connection_params(self) -> Dict[str, Any]:
        """Convert configuration to Motor connection parameters."""
        return {
            "minPoolSize": self.min_pool_size,
            "maxPoolSize": self.max_pool_size,
            "maxIdleTimeMS": self.max_idle_time_ms,
            "waitQueueTimeoutMS": self.wait_queue_timeout_ms,
            "serverSelectionTimeoutMS": self.server_selection_timeout_ms,
            "connectTimeoutMS": self.connect_timeout_ms,
            "socketTimeoutMS": self.socket_timeout_ms,
            "heartbeatFrequencyMS": self.heartbeat_frequency_ms,
            "retryWrites": self.retry_writes,
            "retryReads": self.retry_reads,
        }


class ConnectionHealthMonitor:
    
    def __init__(self, client: AsyncIOMotorClient, check_interval: int = 30):
        self.client = client
        self.check_interval = check_interval
        self.is_healthy = True
        self.last_check = None
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        self._monitor_task = None
        self._stop_monitoring = False
    
    async def start_monitoring(self):
        """Start the health monitoring task."""
        if self._monitor_task is None or self._monitor_task.done():
            self._stop_monitoring = False
            self._monitor_task = asyncio.create_task(self._monitor_loop())
            logger.info("Started MongoDB health monitoring")
    
    async def stop_monitoring(self):
        """Stop the health monitoring task."""
        self._stop_monitoring = True
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped MongoDB health monitoring")
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        while not self._stop_monitoring:
            try:
                await self.check_health()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def check_health(self) -> bool:
        """Check MongoDB connection health."""
        try:
            # Perform a simple ping operation
            await self.client.admin.command('ping')
            
            if not self.is_healthy:
                logger.info("MongoDB connection recovered")
                
            self.is_healthy = True
            self.consecutive_failures = 0
            self.last_check = datetime.utcnow()
            return True
            
        except Exception as e:
            self.consecutive_failures += 1
            
            if self.is_healthy:
                logger.warning(f"MongoDB health check failed: {e}")
            
            if self.consecutive_failures >= self.max_consecutive_failures:
                if self.is_healthy:
                    logger.error(f"MongoDB connection unhealthy after {self.consecutive_failures} failures")
                self.is_healthy = False
            
            self.last_check = datetime.utcnow()
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current health status."""
        return {
            "is_healthy": self.is_healthy,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "consecutive_failures": self.consecutive_failures
        }


class MongoDBManager:
    """
    MongoDB connection manager with connection pooling, health monitoring, and retry logic.
    Implements singleton pattern to ensure only one connection pool per configuration.
    """
    
    _instances: Dict[str, 'MongoDBManager'] = {}
    _lock = threading.Lock()
    
    def __new__(cls, config: MongoDBConfig):
        # Use database URL as the key for singleton instances
        key = f"{config.url}:{config.database_name}"
        
        with cls._lock:
            if key not in cls._instances:
                instance = super(MongoDBManager, cls).__new__(cls)
                cls._instances[key] = instance
        
        return cls._instances[key]
    
    def __init__(self, config: MongoDBConfig):
        # Prevent re-initialization of singleton
        if hasattr(self, '_initialized'):
            return
        
        self.config = config
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.health_monitor: Optional[ConnectionHealthMonitor] = None
        self._connected = False
        self._connection_lock = asyncio.Lock()
        self.logger = logging.getLogger(f"{self.__class__.__name__}:{config.database_name}")
        self._initialized = True
    
    async def connect(self) -> bool:
        """
        Establish MongoDB connection with connection pooling.
        
        Returns:
            bool: True if connection successful, False otherwise
            
        Raises:
            ConnectionError: If connection fails after retries
            ConfigurationError: If configuration is invalid
        """
        async with self._connection_lock:
            if self._connected and self.client:
                return True
            
            try:
                self.logger.info(f"Connecting to MongoDB: {self.config.database_name}")
                
                if not self.config.url:
                    raise ConfigurationError("MongoDB URL is required")
                if not self.config.database_name:
                    raise ConfigurationError("Database name is required")
                
                connection_params = self.config.to_connection_params()
                self.client = AsyncIOMotorClient(self.config.url, **connection_params)
                
                await self.client.admin.command('ping')
                
                # Get database reference
                self.database = self.client[self.config.database_name]
                
                # Start health monitoring
                self.health_monitor = ConnectionHealthMonitor(self.client)
                await self.health_monitor.start_monitoring()
                
                self._connected = True
                self.logger.info(f"Successfully connected to MongoDB with connection pool")
                return True
                
            except (ServerSelectionTimeoutError, ConnectionFailure) as e:
                error_msg = f"MongoDB connection failed: {e}"
                self.logger.error(error_msg)
                raise ConnectionError(error_msg) from e
            except OperationFailure as e:
                error_msg = f"MongoDB authentication/authorization failed: {e}"
                self.logger.error(error_msg)
                raise ConnectionError(error_msg) from e
            except Exception as e:
                error_msg = f"Unexpected MongoDB connection error: {e}"
                self.logger.exception(error_msg)
                raise ConnectionError(error_msg) from e
    
    async def disconnect(self):
        """Disconnect from MongoDB and cleanup resources."""
        async with self._connection_lock:
            if not self._connected:
                return
            
            try:
                if self.health_monitor:
                    await self.health_monitor.stop_monitoring()
                    self.health_monitor = None
                
                if self.client:
                    self.client.close()
                    self.client = None
                
                self.database = None
                self._connected = False
                self.logger.info("Disconnected from MongoDB")
                
            except Exception as e:
                self.logger.exception(f"Error during MongoDB disconnect: {e}")
    
    async def ensure_connected(self) -> bool:
        """Ensure connection is active, reconnect if necessary."""
        if not self._connected or not self.client:
            return await self.connect()
        
        # Check if connection is still healthy
        if self.health_monitor and not self.health_monitor.is_healthy:
            self.logger.warning("MongoDB connection unhealthy, attempting reconnection")
            await self.disconnect()
            return await self.connect()
        
        return True
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """
        Get database instance.
        
        Returns:
            AsyncIOMotorDatabase: Database instance
            
        Raises:
            ConnectionError: If not connected to database
        """
        if not self._connected or not self.database:
            raise ConnectionError("Not connected to MongoDB. Call connect() first.")
        
        return self.database
    
    def get_collection(self, collection_name: str) -> AsyncIOMotorCollection:
        """
        Get collection instance.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            AsyncIOMotorCollection: Collection instance
            
        Raises:
            ConnectionError: If not connected to database
            ValidationError: If collection name is invalid
        """
        if not collection_name:
            raise ValidationError("Collection name cannot be empty")
        
        database = self.get_database()
        return database[collection_name]
    
    async def create_indexes(self, collection_name: str, indexes: List[Dict[str, Any]]):
        """
        Create indexes on a collection.
        
        Args:
            collection_name: Name of the collection
            indexes: List of index specifications
            
        Raises:
            ConnectionError: If not connected to database
            ValidationError: If parameters are invalid
        """
        if not await self.ensure_connected():
            raise ConnectionError("Unable to establish MongoDB connection")
        
        if not indexes:
            return
        
        try:
            collection = self.get_collection(collection_name)
            
            for index_spec in indexes:
                if 'keys' not in index_spec:
                    raise ValidationError(f"Index specification missing 'keys': {index_spec}")
                
                keys = index_spec['keys']
                options = index_spec.get('options', {})
                
                await collection.create_index(keys, **options)
                self.logger.debug(f"Created index on {collection_name}: {keys}")
            
            self.logger.info(f"Created {len(indexes)} indexes on collection '{collection_name}'")
            
        except Exception as e:
            error_msg = f"Failed to create indexes on {collection_name}: {e}"
            self.logger.exception(error_msg)
            raise ConnectionError(error_msg) from e
    
    @asynccontextmanager
    async def get_session(self):
        """
        Get a MongoDB session for transactions.
        
        Usage:
            async with mongodb_manager.get_session() as session:
                # Use session for operations
                pass
        """
        if not await self.ensure_connected():
            raise ConnectionError("Unable to establish MongoDB connection")
        
        session = None
        try:
            session = await self.client.start_session()
            yield session
        finally:
            if session:
                await session.end_session()
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information and statistics."""
        if not self._connected or not self.client:
            return {
                "connected": False,
                "database": None,
                "health": None
            }
        
        health_status = self.health_monitor.get_status() if self.health_monitor else None
        
        return {
            "connected": self._connected,
            "database": self.config.database_name,
            "health": health_status,
            "config": {
                "min_pool_size": self.config.min_pool_size,
                "max_pool_size": self.config.max_pool_size,
                "max_idle_time_ms": self.config.max_idle_time_ms,
                "server_selection_timeout_ms": self.config.server_selection_timeout_ms
            }
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


# Global registry for MongoDB managers
_mongodb_managers: Dict[str, MongoDBManager] = {}
_managers_lock = threading.Lock()


def get_mongodb_manager(config: MongoDBConfig) -> MongoDBManager:
    """
    Get or create a MongoDB manager instance.
    
    Args:
        config: MongoDB configuration
        
    Returns:
        MongoDBManager: Manager instance
    """
    key = f"{config.url}:{config.database_name}"
    
    with _managers_lock:
        if key not in _mongodb_managers:
            _mongodb_managers[key] = MongoDBManager(config)
        
        return _mongodb_managers[key]


async def shutdown_all_managers():
    """Shutdown all MongoDB managers and cleanup resources."""
    with _managers_lock:
        managers = list(_mongodb_managers.values())
        _mongodb_managers.clear()
    
    for manager in managers:
        try:
            await manager.disconnect()
        except Exception as e:
            logger.exception(f"Error shutting down MongoDB manager: {e}")
    
    logger.info("All MongoDB managers shut down")