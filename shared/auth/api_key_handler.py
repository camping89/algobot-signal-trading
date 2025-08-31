"""
API key authentication handler for service-to-service communication.
"""

import os
import hashlib
import secrets
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class APIKey(BaseModel):
    """API key model."""
    key_id: str
    key_hash: str
    name: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    roles: List[str] = []
    permissions: List[str] = []
    rate_limit: int = 100  # Requests per minute
    is_active: bool = True
    last_used: Optional[datetime] = None
    usage_count: int = 0
    
    
class APIKeyInfo(BaseModel):
    """API key information (without sensitive data)."""
    key_id: str
    name: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    roles: List[str] = []
    permissions: List[str] = []
    rate_limit: int = 100
    is_active: bool = True
    

class APIKeyHandler:
    """
    API key handler for service authentication.
    
    Features:
    - Secure API key generation
    - Key validation and verification
    - Rate limiting support
    - Key expiration handling
    - Role and permission management
    """
    
    def __init__(self):
        """Initialize API key handler."""
        self.keys_storage: Dict[str, APIKey] = {}
        self._load_keys_from_env()
    
    def _load_keys_from_env(self):
        """Load API keys from environment variables."""
        # Load master API key if configured
        master_key = os.getenv("MASTER_API_KEY")
        if master_key:
            self._store_key(
                key_id="master",
                api_key=master_key,
                name="Master API Key",
                roles=["admin"],
                permissions=["all"]
            )
            logger.info("Loaded master API key from environment")
    
    def generate_api_key(
        self,
        name: str,
        roles: List[str] = None,
        permissions: List[str] = None,
        expires_in_days: Optional[int] = None,
        rate_limit: int = 100
    ) -> tuple[str, APIKeyInfo]:
        """
        Generate a new API key.
        
        Args:
            name: Descriptive name for the API key
            roles: Associated roles
            permissions: Associated permissions
            expires_in_days: Expiration time in days
            rate_limit: Rate limit (requests per minute)
            
        Returns:
            Tuple of (api_key, api_key_info)
        """
        # Generate secure random key
        api_key = f"tk_{secrets.token_urlsafe(32)}"
        key_id = secrets.token_hex(8)
        
        # Hash the key for storage
        key_hash = self._hash_key(api_key)
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create API key object
        api_key_obj = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            roles=roles or [],
            permissions=permissions or [],
            rate_limit=rate_limit,
            is_active=True
        )
        
        # Store in memory (in production, use database)
        self.keys_storage[key_id] = api_key_obj
        
        logger.info(f"Generated API key '{name}' with ID: {key_id}")
        
        # Return key and info
        key_info = APIKeyInfo(
            key_id=key_id,
            name=name,
            created_at=api_key_obj.created_at,
            expires_at=expires_at,
            roles=api_key_obj.roles,
            permissions=api_key_obj.permissions,
            rate_limit=rate_limit,
            is_active=True
        )
        
        return api_key, key_info
    
    def validate_api_key(self, api_key: str) -> Optional[APIKeyInfo]:
        """
        Validate an API key.
        
        Args:
            api_key: API key to validate
            
        Returns:
            APIKeyInfo if valid, None otherwise
        """
        if not api_key:
            logger.warning("Empty API key provided")
            return None
        
        # Hash the provided key
        key_hash = self._hash_key(api_key)
        
        # Search for matching key
        for key_id, stored_key in self.keys_storage.items():
            if stored_key.key_hash == key_hash:
                # Check if key is active
                if not stored_key.is_active:
                    logger.warning(f"Inactive API key used: {key_id}")
                    return None
                
                # Check expiration
                if stored_key.expires_at and datetime.utcnow() > stored_key.expires_at:
                    logger.warning(f"Expired API key used: {key_id}")
                    return None
                
                # Update usage statistics
                stored_key.last_used = datetime.utcnow()
                stored_key.usage_count += 1
                
                # Return key info
                return APIKeyInfo(
                    key_id=key_id,
                    name=stored_key.name,
                    created_at=stored_key.created_at,
                    expires_at=stored_key.expires_at,
                    roles=stored_key.roles,
                    permissions=stored_key.permissions,
                    rate_limit=stored_key.rate_limit,
                    is_active=stored_key.is_active
                )
        
        logger.warning("Invalid API key provided")
        return None
    
    def revoke_api_key(self, key_id: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            key_id: ID of the key to revoke
            
        Returns:
            True if revoked, False if not found
        """
        if key_id in self.keys_storage:
            self.keys_storage[key_id].is_active = False
            logger.info(f"Revoked API key: {key_id}")
            return True
        
        logger.warning(f"API key not found for revocation: {key_id}")
        return False
    
    def check_rate_limit(self, key_id: str, current_usage: int) -> bool:
        """
        Check if API key is within rate limit.
        
        Args:
            key_id: API key ID
            current_usage: Current usage count in the time window
            
        Returns:
            True if within limit, False otherwise
        """
        if key_id not in self.keys_storage:
            return False
        
        api_key = self.keys_storage[key_id]
        
        if current_usage >= api_key.rate_limit:
            logger.warning(f"Rate limit exceeded for key: {key_id}")
            return False
        
        return True
    
    def check_permissions(
        self,
        key_info: APIKeyInfo,
        required_permissions: List[str]
    ) -> bool:
        """
        Check if API key has required permissions.
        
        Args:
            key_info: API key information
            required_permissions: List of required permissions
            
        Returns:
            True if has all permissions, False otherwise
        """
        if not required_permissions:
            return True
        
        # Admin role has all permissions
        if "admin" in key_info.roles:
            return True
        
        # Check for "all" permission
        if "all" in key_info.permissions:
            return True
        
        key_permissions = set(key_info.permissions)
        required = set(required_permissions)
        
        return required.issubset(key_permissions)
    
    def check_roles(
        self,
        key_info: APIKeyInfo,
        required_roles: List[str]
    ) -> bool:
        """
        Check if API key has any of the required roles.
        
        Args:
            key_info: API key information
            required_roles: List of required roles
            
        Returns:
            True if has any role, False otherwise
        """
        if not required_roles:
            return True
        
        key_roles = set(key_info.roles)
        required = set(required_roles)
        
        return bool(key_roles.intersection(required))
    
    def list_api_keys(self) -> List[APIKeyInfo]:
        """
        List all API keys (without sensitive data).
        
        Returns:
            List of API key information
        """
        keys = []
        
        for key_id, api_key in self.keys_storage.items():
            keys.append(APIKeyInfo(
                key_id=key_id,
                name=api_key.name,
                created_at=api_key.created_at,
                expires_at=api_key.expires_at,
                roles=api_key.roles,
                permissions=api_key.permissions,
                rate_limit=api_key.rate_limit,
                is_active=api_key.is_active
            ))
        
        return keys
    
    def get_api_key_info(self, key_id: str) -> Optional[APIKeyInfo]:
        """
        Get API key information by ID.
        
        Args:
            key_id: API key ID
            
        Returns:
            APIKeyInfo if found, None otherwise
        """
        if key_id not in self.keys_storage:
            return None
        
        api_key = self.keys_storage[key_id]
        
        return APIKeyInfo(
            key_id=key_id,
            name=api_key.name,
            created_at=api_key.created_at,
            expires_at=api_key.expires_at,
            roles=api_key.roles,
            permissions=api_key.permissions,
            rate_limit=api_key.rate_limit,
            is_active=api_key.is_active
        )
    
    def _hash_key(self, api_key: str) -> str:
        """
        Hash an API key for secure storage.
        
        Args:
            api_key: API key to hash
            
        Returns:
            Hashed key
        """
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def _store_key(
        self,
        key_id: str,
        api_key: str,
        name: str,
        roles: List[str] = None,
        permissions: List[str] = None
    ):
        """
        Store a pre-existing API key.
        
        Args:
            key_id: Key identifier
            api_key: The API key
            name: Key name
            roles: Associated roles
            permissions: Associated permissions
        """
        key_hash = self._hash_key(api_key)
        
        self.keys_storage[key_id] = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            created_at=datetime.utcnow(),
            roles=roles or [],
            permissions=permissions or [],
            is_active=True
        )


# Global API key handler instance
api_key_handler = APIKeyHandler()