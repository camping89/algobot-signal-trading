"""
JWT authentication handler for secure API access.
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []
    
    
class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    
    
class JWTHandler:
    """
    JWT token handler for authentication and authorization.
    
    Features:
    - Access token generation with expiration
    - Refresh token support
    - Role-based access control (RBAC)
    - Token validation and decoding
    - Password hashing and verification
    """
    
    def __init__(self, secret_key: str = SECRET_KEY, algorithm: str = ALGORITHM):
        """
        Initialize JWT handler.
        
        Args:
            secret_key: Secret key for JWT encoding/decoding
            algorithm: Algorithm for JWT (HS256, RS256, etc.)
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.pwd_context = pwd_context
        
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Payload data to encode
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        logger.info(f"Created access token for user: {data.get('sub', 'unknown')}")
        
        return encoded_jwt
    
    def create_refresh_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT refresh token.
        
        Args:
            data: Payload data to encode
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT refresh token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        logger.info(f"Created refresh token for user: {data.get('sub', 'unknown')}")
        
        return encoded_jwt
    
    def create_tokens(
        self,
        username: str,
        user_id: str,
        roles: List[str] = None,
        permissions: List[str] = None
    ) -> Token:
        """
        Create both access and refresh tokens.
        
        Args:
            username: Username for the token
            user_id: User ID
            roles: User roles
            permissions: User permissions
            
        Returns:
            Token object with access and refresh tokens
        """
        token_data = {
            "sub": username,
            "user_id": user_id,
            "roles": roles or [],
            "permissions": permissions or []
        }
        
        access_token = self.create_access_token(data=token_data)
        refresh_token = self.create_refresh_token(data=token_data)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    def decode_token(self, token: str) -> Optional[TokenData]:
        """
        Decode and validate a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            TokenData if valid, None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            username: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            roles: List[str] = payload.get("roles", [])
            permissions: List[str] = payload.get("permissions", [])
            
            if username is None:
                logger.warning("Token missing username (sub)")
                return None
            
            token_data = TokenData(
                username=username,
                user_id=user_id,
                roles=roles,
                permissions=permissions
            )
            
            return token_data
            
        except JWTError as e:
            logger.error(f"JWT decode error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected token decode error: {str(e)}")
            return None
    
    def verify_token(self, token: str, required_type: str = "access") -> bool:
        """
        Verify token validity and type.
        
        Args:
            token: JWT token string
            required_type: Expected token type (access/refresh)
            
        Returns:
            True if valid, False otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            token_type = payload.get("type")
            
            if token_type != required_type:
                logger.warning(f"Token type mismatch. Expected: {required_type}, Got: {token_type}")
                return False
            
            return True
            
        except JWTError as e:
            logger.error(f"Token verification failed: {str(e)}")
            return False
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token if valid, None otherwise
        """
        if not self.verify_token(refresh_token, required_type="refresh"):
            logger.warning("Invalid refresh token")
            return None
        
        token_data = self.decode_token(refresh_token)
        if not token_data:
            return None
        
        new_token_data = {
            "sub": token_data.username,
            "user_id": token_data.user_id,
            "roles": token_data.roles,
            "permissions": token_data.permissions
        }
        
        new_access_token = self.create_access_token(data=new_token_data)
        
        logger.info(f"Refreshed access token for user: {token_data.username}")
        
        return new_access_token
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password for storage.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password from storage
            
        Returns:
            True if password matches, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def check_permissions(
        self,
        token_data: TokenData,
        required_permissions: List[str]
    ) -> bool:
        """
        Check if token has required permissions.
        
        Args:
            token_data: Decoded token data
            required_permissions: List of required permissions
            
        Returns:
            True if has all permissions, False otherwise
        """
        if not required_permissions:
            return True
        
        user_permissions = set(token_data.permissions)
        required = set(required_permissions)
        
        return required.issubset(user_permissions)
    
    def check_roles(
        self,
        token_data: TokenData,
        required_roles: List[str]
    ) -> bool:
        """
        Check if token has any of the required roles.
        
        Args:
            token_data: Decoded token data
            required_roles: List of required roles (any match)
            
        Returns:
            True if has any role, False otherwise
        """
        if not required_roles:
            return True
        
        user_roles = set(token_data.roles)
        required = set(required_roles)
        
        return bool(user_roles.intersection(required))


# Global JWT handler instance
jwt_handler = JWTHandler()