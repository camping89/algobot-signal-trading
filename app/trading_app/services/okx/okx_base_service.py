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
import requests
import urllib3

# Fix SSL certificate verification
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# Disable SSL warnings and verification for OKX (temporary fix)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()

# Monkey patch requests to disable SSL verification
old_request = requests.Session.request
def new_request(self, method, url, **kwargs):
    if 'okx.com' in url:
        kwargs['verify'] = False
    return old_request(self, method, url, **kwargs)
requests.Session.request = new_request

logger = logging.getLogger(__name__)

class OKXBaseService:
    """
    Base service for OKX API connection management.
    Handles initialization, authentication, and cleanup of OKX API connection.
    
    Implements singleton pattern to ensure only one connection instance exists.
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OKXBaseService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize base service with API clients.
        Skips if already initialized (singleton pattern).
        """
        if self._initialized:
            return
            
        self.api_key: Optional[str] = None
        self.secret_key: Optional[str] = None
        self.passphrase: Optional[str] = None
        self.is_sandbox: bool = False
        
        self.account_api: Optional[Account] = None
        self.trade_api: Optional[Trade] = None
        self.algo_api: Optional[AlgoTrade] = None
        self.public_api: Optional[PublicData] = None
        self.market_api: Optional[MarketData] = None
        
    @property
    def initialized(self):
        """Check if OKX API connection is initialized"""
        return self._initialized
        
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
        """
        try:
            self.api_key = api_key
            self.secret_key = secret_key
            self.passphrase = passphrase
            self.is_sandbox = is_sandbox
            
            # Initialize API clients
            # Optional: Disable SSL verification for testing (not recommended for production)
            # import urllib3
            # urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            self.account_api = Account(
                key=api_key,
                secret=secret_key,
                passphrase=passphrase,
                flag='0' if not is_sandbox else '1'
            )
            
            self.trade_api = Trade(
                key=api_key,
                secret=secret_key,
                passphrase=passphrase,
                flag='0' if not is_sandbox else '1'
            )
            
            self.algo_api = AlgoTrade(
                key=api_key,
                secret=secret_key,
                passphrase=passphrase,
                flag='0' if not is_sandbox else '1'
            )
            
            self.public_api = PublicData(
                key=api_key,
                secret=secret_key,
                passphrase=passphrase,
                flag='0' if not is_sandbox else '1'
            )
            
            self.market_api = MarketData(
                key=api_key,
                secret=secret_key,
                passphrase=passphrase,
                flag='0' if not is_sandbox else '1'
            )
            
            # Test connection by getting account info
            result = self.account_api.get_balance()
            if result['code'] != '0':
                logger.error(f"Failed to connect to OKX: {result['msg']}")
                return False
                
            self._initialized = True
            logger.info("OKX API connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to OKX API: {str(e)}")
            return False

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
            return result['code'] == '0'
        except Exception:
            return False

    async def shutdown(self):
        """
        Shutdown OKX API connection and cleanup resources.
        Logs connection closure for monitoring.
        """
        if self._initialized:
            self.account_api = None
            self.trade_api = None
            self.algo_api = None
            self.public_api = None
            self.market_api = None
            self._initialized = False
            logger.info("OKX API connection closed")

    def __del__(self):
        """
        Cleanup method called when service is destroyed.
        Ensures OKX API connection is properly closed.
        """
        if self._initialized:
            self.account_api = None
            self.trade_api = None
            self.algo_api = None
            self.public_api = None
            self.market_api = None
            self._initialized = False