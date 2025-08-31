"""Refactored OKX base service using base service classes."""

from okx.api.account import Account
from okx.api.trade import Trade
from okx.api.algotrade import AlgoTrade
from okx.api.public import Public as PublicData
from okx.api.market import Market as MarketData
import logging
from typing import Optional
import ssl
import certifi
import os
from shared.services.base_service import BaseConnectionService
from shared.services.exceptions import (
    OKXConnectionError,
    OKXAPIError,
    AuthenticationError,
    ServiceNotInitializedError
)

# Properly configure SSL certificate verification
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# Create SSL context with proper certificate verification
ssl_context = ssl.create_default_context(cafile=certifi.where())

logger = logging.getLogger(__name__)


class OKXBaseService(BaseConnectionService):
    """
    Base service for OKX API connection management.
    Handles initialization, authentication, and cleanup of OKX API connection.
    
    Implements singleton pattern through BaseConnectionService to ensure only one connection instance exists.
    """
    
    def __init__(self):
        """
        Initialize base service with API clients.
        Skips if already initialized (singleton pattern).
        """
        super().__init__()
        
        # API credentials
        self.api_key: Optional[str] = None
        self.secret_key: Optional[str] = None
        self.passphrase: Optional[str] = None
        self.is_sandbox: bool = False
        
        # API clients
        self.account_api: Optional[Account] = None
        self.trade_api: Optional[Trade] = None
        self.algo_api: Optional[AlgoTrade] = None
        self.public_api: Optional[PublicData] = None
        self.market_api: Optional[MarketData] = None
    
    async def connect(self, api_key: str, secret_key: str, passphrase: str, is_sandbox: bool = False) -> bool:
        """
        Connect to OKX API with credentials.
        
        Parameters:
        - api_key: OKX API key
        - secret_key: OKX secret key  
        - passphrase: OKX passphrase
        - is_sandbox: Use sandbox environment
        
        Returns:
        - bool: True if connection successful, False otherwise
        
        Raises:
        - OKXConnectionError: If API connection fails
        - AuthenticationError: If credentials are invalid
        """
        try:
            # Store credentials
            self.api_key = api_key
            self.secret_key = secret_key
            self.passphrase = passphrase
            self.is_sandbox = is_sandbox
            
            # Initialize API clients with proper SSL verification
            flag = '1' if is_sandbox else '0'
            
            self.account_api = Account(
                key=api_key,
                secret=secret_key,
                passphrase=passphrase,
                flag=flag
            )
            
            self.trade_api = Trade(
                key=api_key,
                secret=secret_key,
                passphrase=passphrase,
                flag=flag
            )
            
            self.algo_api = AlgoTrade(
                key=api_key,
                secret=secret_key,
                passphrase=passphrase,
                flag=flag
            )
            
            self.public_api = PublicData(
                key=api_key,
                secret=secret_key,
                passphrase=passphrase,
                flag=flag
            )
            
            self.market_api = MarketData(
                key=api_key,
                secret=secret_key,
                passphrase=passphrase,
                flag=flag
            )
            
            # Test connection by getting account info
            result = self.account_api.get_balance()
            if result['code'] != '0':
                error_msg = f"Failed to authenticate with OKX: {result['msg']}"
                self.logger.error(error_msg)
                raise AuthenticationError(error_msg)
            
            self._connection = {
                'account': self.account_api,
                'trade': self.trade_api,
                'algo': self.algo_api,
                'public': self.public_api,
                'market': self.market_api
            }
            
            self._initialized = True
            self.logger.info("OKX API connection established successfully")
            return True
            
        except AuthenticationError:
            # Re-raise authentication errors
            raise
        except Exception as e:
            error_msg = f"Error connecting to OKX API: {str(e)}"
            self.logger.exception(error_msg)
            raise OKXConnectionError(error_msg) from e
    
    async def disconnect(self):
        """
        Disconnect from OKX API and cleanup resources.
        """
        if self._connection:
            # Clear API clients
            self.account_api = None
            self.trade_api = None
            self.algo_api = None
            self.public_api = None
            self.market_api = None
            self._connection = None
            self.logger.info("Disconnected from OKX API")
    
    async def ensure_connected(self) -> bool:
        """
        Verify OKX API connection is active.
        
        Returns:
        - bool: True if connected, False otherwise
        """
        if not self._initialized or not self.account_api:
            return False
        
        try:
            # Test connection with a simple API call
            result = self.account_api.get_balance()
            if result['code'] != '0':
                self.logger.warning(f"OKX API connection test failed: {result['msg']}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error testing OKX connection: {e}")
            return False
    
    async def initialize(self) -> bool:
        """
        Initialize the OKX service.
        This method is called by ensure_initialized() from BaseService.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        # For OKX, initialization requires API credentials
        # This will be handled by the connect() method
        return True
    
    def make_api_request(self, api_client, method_name: str, *args, **kwargs):
        """
        Make an API request with proper error handling.
        
        Parameters:
        - api_client: The API client to use
        - method_name: The method name to call
        - args, kwargs: Arguments to pass to the method
        
        Returns:
        - API response
        
        Raises:
        - ServiceNotInitializedError: If service is not initialized
        - OKXAPIError: If API request fails
        """
        if not self._initialized:
            raise ServiceNotInitializedError("OKX service not initialized")
        
        if not api_client:
            raise ServiceNotInitializedError("API client not available")
        
        try:
            method = getattr(api_client, method_name)
            result = method(*args, **kwargs)
            
            # Check if result indicates an error
            if isinstance(result, dict) and result.get('code') != '0':
                raise OKXAPIError(
                    message=result.get('msg', 'Unknown API error'),
                    code=result.get('code'),
                    response=result
                )
            
            return result
            
        except OKXAPIError:
            # Re-raise OKX API errors
            raise
        except AttributeError as e:
            raise OKXAPIError(f"Invalid API method '{method_name}': {e}")
        except Exception as e:
            self.logger.exception(f"Unexpected error in API request: {e}")
            raise OKXAPIError(f"API request failed: {e}") from e