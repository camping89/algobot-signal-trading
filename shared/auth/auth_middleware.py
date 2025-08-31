"""
Authentication middleware and dependencies for FastAPI.
"""

import logging
from typing import Optional, List, Callable
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader

from .jwt_handler import jwt_handler, TokenData
from .api_key_handler import api_key_handler, APIKeyInfo

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class UserRoles:
    ADMIN = "admin"
    READ = "read"
    WRITE = "write"


class Permissions:
    TRADING = "trading"
    
    SIGNALS = "signals"
    
    ACCOUNTS = "accounts"
    
    ADMIN = "admin"


ROLE_PERMISSIONS = {
    UserRoles.ADMIN: [
        Permissions.ADMIN,
        Permissions.TRADING,
        Permissions.SIGNALS,
        Permissions.ACCOUNTS
    ],
    UserRoles.WRITE: [
        Permissions.TRADING,
        Permissions.SIGNALS,
        Permissions.ACCOUNTS
    ],
    UserRoles.READ: [
        # Read role gets no permissions - endpoints will check role directly
    ]
}


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> Optional[TokenData]:
    """
    Get current user from JWT token.
    
    Args:
        credentials: Bearer token credentials
        
    Returns:
        TokenData if authenticated, None otherwise
        
    Raises:
        HTTPException: If token is invalid
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    
    # Decode and validate token
    token_data = jwt_handler.decode_token(token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    logger.debug(f"Authenticated user: {token_data.username}")
    
    return token_data


async def get_api_key_info(
    api_key: Optional[str] = Depends(api_key_header)
) -> Optional[APIKeyInfo]:
    """
    Get API key information from header.
    
    Args:
        api_key: API key from header
        
    Returns:
        APIKeyInfo if valid, None otherwise
        
    Raises:
        HTTPException: If API key is invalid
    """
    if not api_key:
        return None
    
    # Validate API key
    key_info = api_key_handler.validate_api_key(api_key)
    
    if not key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    logger.debug(f"Authenticated API key: {key_info.name}")
    
    return key_info


async def require_auth(
    token_data: Optional[TokenData] = Depends(get_current_user),
    api_key_info: Optional[APIKeyInfo] = Depends(get_api_key_info)
) -> dict:
    """
    Require authentication (JWT or API key).
    
    Args:
        token_data: JWT token data
        api_key_info: API key information
        
    Returns:
        Authentication context
        
    Raises:
        HTTPException: If not authenticated
    """
    if not token_data and not api_key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer, ApiKey"}
        )
    
    # Build authentication context
    auth_context = {
        "authenticated": True,
        "auth_type": "jwt" if token_data else "api_key"
    }
    
    if token_data:
        auth_context.update({
            "username": token_data.username,
            "user_id": token_data.user_id,
            "roles": token_data.roles,
            "permissions": token_data.permissions
        })
    elif api_key_info:
        auth_context.update({
            "key_id": api_key_info.key_id,
            "key_name": api_key_info.name,
            "roles": api_key_info.roles,
            "permissions": api_key_info.permissions
        })
    
    return auth_context


async def require_api_key(
    api_key_info: APIKeyInfo = Depends(get_api_key_info)
) -> APIKeyInfo:
    """
    Require API key authentication only.
    
    Args:
        api_key_info: API key information
        
    Returns:
        API key information
        
    Raises:
        HTTPException: If API key not provided or invalid
    """
    if not api_key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    return api_key_info


def require_roles(roles: List[str]) -> Callable:
    """
    Create dependency to require specific roles.
    
    Args:
        roles: List of required roles (any match)
        
    Returns:
        FastAPI dependency
    """
    async def role_checker(
        auth_context: dict = Depends(require_auth)
    ) -> dict:
        """Check if user has required roles."""
        user_roles = auth_context.get("roles", [])
        
        # Check if user has any of the required roles
        if not any(role in user_roles for role in roles):
            logger.warning(
                f"Access denied. Required roles: {roles}, "
                f"User roles: {user_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role privileges"
            )
        
        return auth_context
    
    return role_checker


def require_permissions(permissions: List[str]) -> Callable:
    """
    Create dependency to require specific permissions.
    
    Args:
        permissions: List of required permissions (all must match)
        
    Returns:
        FastAPI dependency
    """
    async def permission_checker(
        auth_context: dict = Depends(require_auth)
    ) -> dict:
        """Check if user has required permissions."""
        user_permissions = auth_context.get("permissions", [])
        user_roles = auth_context.get("roles", [])
        
        # Expand permissions based on roles
        expanded_permissions = set(user_permissions)
        for role in user_roles:
            if role in ROLE_PERMISSIONS:
                expanded_permissions.update(ROLE_PERMISSIONS[role])
        
        # Check for admin permission
        if Permissions.ADMIN in expanded_permissions:
            return auth_context
        
        # Check if user has all required permissions
        missing_permissions = set(permissions) - expanded_permissions
        
        if missing_permissions:
            logger.warning(
                f"Access denied. Missing permissions: {missing_permissions}, "
                f"User permissions: {expanded_permissions}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {', '.join(missing_permissions)}"
            )
        
        return auth_context
    
    return permission_checker


class RateLimitMiddleware:
    """
    Rate limiting middleware for API keys.
    """
    
    def __init__(self):
        """Initialize rate limiter."""
        self.request_counts = {}  # key_id -> (count, reset_time)
    
    async def check_rate_limit(
        self,
        request: Request,
        api_key_info: Optional[APIKeyInfo] = Depends(get_api_key_info)
    ):
        """
        Check and enforce rate limits.
        
        Args:
            request: FastAPI request
            api_key_info: API key information
            
        Raises:
            HTTPException: If rate limit exceeded
        """
        if not api_key_info:
            return  # No rate limiting for JWT auth
        
        import time
        current_time = time.time()
        key_id = api_key_info.key_id
        
        # Get or initialize counter
        if key_id not in self.request_counts:
            self.request_counts[key_id] = (0, current_time + 60)
        
        count, reset_time = self.request_counts[key_id]
        
        # Reset counter if time window passed
        if current_time > reset_time:
            self.request_counts[key_id] = (1, current_time + 60)
            return
        
        # Increment counter
        count += 1
        self.request_counts[key_id] = (count, reset_time)
        
        # Check rate limit
        if count > api_key_info.rate_limit:
            logger.warning(f"Rate limit exceeded for key: {key_id}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(api_key_info.rate_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(reset_time))
                }
            )
        
        # Add rate limit headers to response
        request.state.rate_limit_headers = {
            "X-RateLimit-Limit": str(api_key_info.rate_limit),
            "X-RateLimit-Remaining": str(api_key_info.rate_limit - count),
            "X-RateLimit-Reset": str(int(reset_time))
        }


# Global rate limiter instance
rate_limiter = RateLimitMiddleware()