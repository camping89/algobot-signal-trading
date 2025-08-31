"""
Request signing for sensitive operations.
"""

import hashlib
import hmac
import time
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RequestSigner:
    """
    Request signing for secure API operations.
    
    Features:
    - HMAC-SHA256 signing
    - Timestamp validation
    - Nonce tracking for replay protection
    - Request body integrity verification
    """
    
    def __init__(self, secret_key: str = None, max_age_seconds: int = 300):
        """
        Initialize request signer.
        
        Args:
            secret_key: Secret key for signing
            max_age_seconds: Maximum age for valid signatures (5 minutes default)
        """
        self.secret_key = secret_key or "default-secret-change-in-production"
        self.max_age_seconds = max_age_seconds
        self.used_nonces = set()  # Track used nonces to prevent replay
        self._cleanup_interval = 600  # Cleanup old nonces every 10 minutes
        self._last_cleanup = time.time()
    
    def sign_request(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        timestamp: Optional[int] = None,
        nonce: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Sign a request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            body: Request body (for POST/PUT)
            timestamp: Unix timestamp (current time if not provided)
            nonce: Unique nonce (generated if not provided)
            
        Returns:
            Dictionary with signature headers
        """
        import secrets
        
        if timestamp is None:
            timestamp = int(time.time())
        
        if nonce is None:
            nonce = secrets.token_hex(16)
        signing_parts = [
            method.upper(),
            path,
            str(timestamp),
            nonce
        ]
        if body:
            body_json = json.dumps(body, sort_keys=True, separators=(',', ':'))
            body_hash = hashlib.sha256(body_json.encode()).hexdigest()
            signing_parts.append(body_hash)
        
        signing_string = '\n'.join(signing_parts)
        
        # Generate signature
        signature = hmac.new(
            self.secret_key.encode(),
            signing_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Return signature headers
        headers = {
            "X-Signature": signature,
            "X-Timestamp": str(timestamp),
            "X-Nonce": nonce
        }
        
        if body:
            headers["X-Body-Hash"] = body_hash
        
        logger.debug(f"Signed request: {method} {path}")
        
        return headers
    
    def verify_signature(
        self,
        method: str,
        path: str,
        signature: str,
        timestamp: str,
        nonce: str,
        body: Optional[Dict[str, Any]] = None,
        body_hash: Optional[str] = None
    ) -> bool:
        """
        Verify a request signature.
        
        Args:
            method: HTTP method
            path: Request path
            signature: Provided signature
            timestamp: Provided timestamp
            nonce: Provided nonce
            body: Request body (for verification)
            body_hash: Provided body hash
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Cleanup old nonces periodically
            self._cleanup_nonces()
            
            # Check timestamp age
            request_time = int(timestamp)
            current_time = int(time.time())
            
            if abs(current_time - request_time) > self.max_age_seconds:
                logger.warning(f"Signature expired. Age: {abs(current_time - request_time)}s")
                return False
            
            # Check nonce for replay protection
            nonce_key = f"{timestamp}:{nonce}"
            if nonce_key in self.used_nonces:
                logger.warning(f"Nonce already used: {nonce}")
                return False
            
            # Recreate signing string
            signing_parts = [
                method.upper(),
                path,
                timestamp,
                nonce
            ]
            
            # Verify body hash if present
            if body_hash:
                if body:
                    body_json = json.dumps(body, sort_keys=True, separators=(',', ':'))
                    calculated_hash = hashlib.sha256(body_json.encode()).hexdigest()
                    
                    if calculated_hash != body_hash:
                        logger.warning("Body hash mismatch")
                        return False
                
                signing_parts.append(body_hash)
            elif body:
                # Body present but no hash provided
                logger.warning("Body present but no hash provided")
                return False
            
            signing_string = '\n'.join(signing_parts)
            
            # Calculate expected signature
            expected_signature = hmac.new(
                self.secret_key.encode(),
                signing_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures (constant time)
            if not hmac.compare_digest(signature, expected_signature):
                logger.warning("Signature mismatch")
                return False
            
            # Mark nonce as used
            self.used_nonces.add(nonce_key)
            
            logger.debug(f"Signature verified: {method} {path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Signature verification error: {str(e)}")
            return False
    
    def _cleanup_nonces(self):
        """Clean up old nonces to prevent memory growth."""
        current_time = time.time()
        
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        # Remove nonces older than max_age
        cutoff_time = current_time - self.max_age_seconds
        
        old_nonces = set()
        for nonce_key in self.used_nonces:
            try:
                timestamp_str = nonce_key.split(':')[0]
                timestamp = int(timestamp_str)
                
                if timestamp < cutoff_time:
                    old_nonces.add(nonce_key)
            except:
                # Invalid nonce format, remove it
                old_nonces.add(nonce_key)
        
        self.used_nonces -= old_nonces
        self._last_cleanup = current_time
        
        if old_nonces:
            logger.debug(f"Cleaned up {len(old_nonces)} old nonces")
    
    def sign_webhook_payload(
        self,
        payload: Dict[str, Any],
        webhook_secret: str = None
    ) -> str:
        """
        Sign a webhook payload.
        
        Args:
            payload: Webhook payload
            webhook_secret: Webhook-specific secret (uses default if not provided)
            
        Returns:
            Signature string
        """
        secret = webhook_secret or self.secret_key
        
        payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        
        signature = hmac.new(
            secret.encode(),
            payload_json.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    def verify_webhook_signature(
        self,
        payload: Dict[str, Any],
        signature: str,
        webhook_secret: str = None
    ) -> bool:
        """
        Verify a webhook signature.
        
        Args:
            payload: Webhook payload
            signature: Provided signature
            webhook_secret: Webhook-specific secret
            
        Returns:
            True if signature is valid, False otherwise
        """
        secret = webhook_secret or self.secret_key
        
        # Remove prefix if present
        if signature.startswith("sha256="):
            signature = signature[7:]
        
        expected_signature = self.sign_webhook_payload(payload, secret)
        
        if expected_signature.startswith("sha256="):
            expected_signature = expected_signature[7:]
        
        return hmac.compare_digest(signature, expected_signature)


# Global request signer instance
request_signer = RequestSigner()


def require_signed_request(secret_key: str = None):
    """
    FastAPI dependency to require signed requests.
    
    Args:
        secret_key: Optional custom secret key
        
    Returns:
        FastAPI dependency
    """
    from fastapi import Request, HTTPException, status
    
    async def verify_signature(request: Request) -> bool:
        """Verify request signature."""
        # Get signature headers
        signature = request.headers.get("X-Signature")
        timestamp = request.headers.get("X-Timestamp")
        nonce = request.headers.get("X-Nonce")
        body_hash = request.headers.get("X-Body-Hash")
        
        if not all([signature, timestamp, nonce]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing signature headers"
            )
        
        # Get request body if present
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.json()
            except:
                pass
        
        # Create signer with custom key if provided
        signer = RequestSigner(secret_key) if secret_key else request_signer
        
        # Verify signature
        is_valid = signer.verify_signature(
            method=request.method,
            path=str(request.url.path),
            signature=signature,
            timestamp=timestamp,
            nonce=nonce,
            body=body,
            body_hash=body_hash
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid request signature"
            )
        
        return True
    
    return verify_signature