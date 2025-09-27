"""
Security utilities and JWT authentication middleware.

This module provides JWT token validation, authentication middleware,
and security-related utilities for the payment service.
"""

import os
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from ..integrations.auth_service import (
    get_auth_service_client,
    get_mock_auth_service_client,
    InvalidTokenError as AuthInvalidTokenError,
    AuthServiceUnavailableError
)
from ..utils.logging import get_logger


logger = get_logger()


# Security scheme for FastAPI
security = HTTPBearer()


class SecurityConfig:
    """Security configuration settings."""
    
    def __init__(self):
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.auth_service_enabled = os.getenv("AUTH_SERVICE_ENABLED", "true").lower() == "true"
        self.mock_auth_enabled = os.getenv("MOCK_AUTH_ENABLED", "false").lower() == "true"
        self.require_auth = os.getenv("REQUIRE_AUTH", "true").lower() == "true"


# Global security configuration
security_config = SecurityConfig()


class AuthenticationError(Exception):
    """Base exception for authentication errors."""
    pass


class TokenValidationError(AuthenticationError):
    """Raised when token validation fails."""
    pass


class UserInfo:
    """User information extracted from JWT token."""
    
    def __init__(self, user_id: UUID, email: str, username: str, **kwargs):
        self.user_id = user_id
        self.email = email
        self.username = username
        self.extra_data = kwargs
    
    def __str__(self):
        return f"User(id={self.user_id}, email={self.email}, username={self.username})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": str(self.user_id),
            "email": self.email,
            "username": self.username,
            **self.extra_data
        }


async def validate_jwt_token_local(token: str) -> Dict[str, Any]:
    """
    Validate JWT token locally using secret key.
    
    Args:
        token: JWT token to validate
        
    Returns:
        Token payload
        
    Raises:
        TokenValidationError: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            security_config.jwt_secret_key,
            algorithms=[security_config.jwt_algorithm]
        )
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise TokenValidationError("Token has expired")
        
        logger.debug(f"Token validated locally for user {payload.get('user_id')}")
        return payload
        
    except ExpiredSignatureError:
        logger.warning("JWT token has expired")
        raise TokenValidationError("Token has expired")
    except InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        raise TokenValidationError(f"Invalid token: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error validating JWT token: {e}")
        raise TokenValidationError(f"Token validation error: {str(e)}")


async def validate_jwt_token_remote(token: str) -> Dict[str, Any]:
    """
    Validate JWT token with auth service.
    
    Args:
        token: JWT token to validate
        
    Returns:
        User information from auth service
        
    Raises:
        TokenValidationError: If token is invalid
        AuthServiceUnavailableError: If auth service is unavailable
    """
    try:
        if security_config.mock_auth_enabled:
            auth_client = get_mock_auth_service_client()
        else:
            auth_client = get_auth_service_client()
        
        user_data = await auth_client.validate_token(token)
        logger.debug(f"Token validated remotely for user {user_data.get('user_id')}")
        return user_data
        
    except AuthInvalidTokenError as e:
        logger.warning(f"Auth service rejected token: {e}")
        raise TokenValidationError(str(e))
    except AuthServiceUnavailableError as e:
        logger.error(f"Auth service unavailable: {e}")
        # Fall back to local validation if auth service is unavailable
        logger.info("Falling back to local token validation")
        return await validate_jwt_token_local(token)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserInfo:
    """
    Get current authenticated user from JWT token.
    
    This is the main authentication dependency for FastAPI endpoints.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        UserInfo object with user details
        
    Raises:
        HTTPException: If authentication fails
    """
    if not security_config.require_auth:
        # Return mock user if authentication is disabled
        return UserInfo(
            user_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            email="test@example.com",
            username="testuser"
        )
    
    token = credentials.credentials
    
    try:
        # Validate token (remote first, then local fallback)
        if security_config.auth_service_enabled:
            user_data = await validate_jwt_token_remote(token)
        else:
            user_data = await validate_jwt_token_local(token)
        
        # Extract user information
        user_id_str = user_data.get("user_id") or user_data.get("sub")
        if not user_id_str:
            raise TokenValidationError("Token missing user ID")
        
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise TokenValidationError("Invalid user ID format")
        
        email = user_data.get("email", "")
        username = user_data.get("username", user_data.get("preferred_username", ""))
        
        # Create user info object
        user_info = UserInfo(
            user_id=user_id,
            email=email,
            username=username,
            **{k: v for k, v in user_data.items() if k not in ["user_id", "sub", "email", "username"]}
        )
        
        logger.debug(f"Authenticated user: {user_info}")
        return user_info
        
    except TokenValidationError as e:
        logger.warning(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Invalid authentication token",
                "code": "invalid_token",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"Unexpected authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Authentication service error",
                "code": "auth_service_error",
                "message": "Unable to validate authentication",
                "timestamp": datetime.utcnow().isoformat()
            }
        )


async def get_current_user_id(user: UserInfo = Depends(get_current_user)) -> UUID:
    """
    Get current user ID from authenticated user.
    
    Convenience dependency for endpoints that only need user ID.
    
    Args:
        user: Authenticated user info
        
    Returns:
        User ID
    """
    return user.user_id


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[UserInfo]:
    """
    Get current user if authenticated, None otherwise.
    
    This dependency allows endpoints to work with or without authentication.
    
    Args:
        credentials: Optional HTTP authorization credentials
        
    Returns:
        UserInfo object if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        # Create a mock credentials object for get_current_user
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=credentials.credentials
        )
        return await get_current_user(mock_credentials)
    except HTTPException:
        # If authentication fails, return None instead of raising exception
        return None


def require_permission(resource: str, action: str):
    """
    Decorator factory for requiring specific permissions.
    
    Args:
        resource: Resource name (e.g., 'payment', 'payment_method')
        action: Action name (e.g., 'create', 'read', 'update', 'delete')
        
    Returns:
        Dependency function that checks permissions
    """
    async def check_permission(user: UserInfo = Depends(get_current_user)) -> UserInfo:
        """Check if user has required permission."""
        try:
            # For now, we'll assume all authenticated users have all permissions
            # In a real implementation, this would check with the auth service
            # using either get_mock_auth_service_client() or get_auth_service_client()
            has_permission = True
            
            if not has_permission:
                logger.warning(f"User {user.user_id} denied access to {resource}:{action}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "Insufficient permissions",
                        "code": "permission_denied",
                        "message": f"Access denied for {resource}:{action}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Permission check failed",
                    "code": "permission_check_error",
                    "message": "Unable to verify permissions",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    
    return check_permission


def create_jwt_token(user_id: UUID, email: str, username: str, expires_in: int = 3600) -> str:
    """
    Create JWT token for testing purposes.
    
    Args:
        user_id: User ID
        email: User email
        username: Username
        expires_in: Token expiration time in seconds
        
    Returns:
        JWT token string
    """
    payload = {
        "user_id": str(user_id),
        "email": email,
        "username": username,
        "exp": int(datetime.utcnow().timestamp()) + expires_in,
        "iat": int(datetime.utcnow().timestamp())
    }
    
    return jwt.encode(
        payload,
        security_config.jwt_secret_key,
        algorithm=security_config.jwt_algorithm
    )


def mask_sensitive_data(data: Dict[str, Any], sensitive_fields: list = None) -> Dict[str, Any]:
    """
    Mask sensitive data in dictionary for logging.
    
    Args:
        data: Dictionary containing potentially sensitive data
        sensitive_fields: List of field names to mask
        
    Returns:
        Dictionary with sensitive fields masked
    """
    if sensitive_fields is None:
        sensitive_fields = [
            'password', 'token', 'secret', 'key', 'authorization',
            'card_number', 'cvv', 'ssn', 'account_number'
        ]
    
    masked_data = data.copy()
    
    for field in sensitive_fields:
        if field in masked_data:
            value = masked_data[field]
            if isinstance(value, str) and len(value) > 4:
                masked_data[field] = f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"
            else:
                masked_data[field] = "***"
    
    return masked_data


def generate_correlation_id() -> str:
    """
    Generate correlation ID for request tracking.
    
    Returns:
        Correlation ID string
    """
    import uuid
    return str(uuid.uuid4())


class SecurityHeaders:
    """Security headers for HTTP responses."""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get recommended security headers."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }


# Rate limiting (basic implementation)
class RateLimiter:
    """Basic rate limiter for API endpoints."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for identifier."""
        now = datetime.utcnow().timestamp()
        window_start = now - self.window_seconds
        
        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
        else:
            self.requests[identifier] = []
        
        # Check if under limit
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True
        
        return False


# Global rate limiter instance
rate_limiter = RateLimiter()


def check_rate_limit(identifier: str):
    """
    Check rate limit for identifier.
    
    Args:
        identifier: Unique identifier (e.g., user ID, IP address)
        
    Raises:
        HTTPException: If rate limit exceeded
    """
    if not rate_limiter.is_allowed(identifier):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "code": "rate_limit_exceeded",
                "message": f"Too many requests. Limit: {rate_limiter.max_requests} per {rate_limiter.window_seconds} seconds",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
