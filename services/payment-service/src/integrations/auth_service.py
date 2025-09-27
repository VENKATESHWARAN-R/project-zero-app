"""
Auth Service Integration Client.

This module provides integration with the authentication service
for user validation, JWT token verification, and user information retrieval.
"""

import os
from typing import Optional, Dict, Any
from uuid import UUID
import httpx
from datetime import datetime

from ..utils.logging import get_logger


logger = get_logger()


class AuthServiceError(Exception):
    """Base exception for auth service errors."""
    pass


class AuthServiceUnavailableError(AuthServiceError):
    """Raised when auth service is unavailable."""
    pass


class InvalidTokenError(AuthServiceError):
    """Raised when JWT token is invalid."""
    pass


class UserNotFoundError(AuthServiceError):
    """Raised when user is not found."""
    pass


class AuthServiceClient:
    """
    Client for integrating with the authentication service.
    
    Provides methods for JWT token validation, user information retrieval,
    and authentication status checking.
    """
    
    def __init__(self, base_url: Optional[str] = None, timeout: float = 10.0):
        """
        Initialize auth service client.
        
        Args:
            base_url: Base URL of the auth service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
        self.timeout = timeout
        self._client = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token with auth service.
        
        Args:
            token: JWT token to validate
            
        Returns:
            User information from token
            
        Raises:
            InvalidTokenError: If token is invalid
            AuthServiceUnavailableError: If auth service is unavailable
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/validate-token",
                    json={"token": token},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    logger.info(f"Token validated successfully for user {user_data.get('user_id')}")
                    return user_data
                elif response.status_code == 401:
                    logger.warning("Invalid token provided")
                    raise InvalidTokenError("Invalid or expired token")
                else:
                    logger.error(f"Auth service returned status {response.status_code}: {response.text}")
                    raise AuthServiceUnavailableError(f"Auth service error: {response.status_code}")
                    
        except httpx.TimeoutException:
            logger.error("Auth service request timed out")
            raise AuthServiceUnavailableError("Auth service timeout")
        except httpx.ConnectError:
            logger.error("Failed to connect to auth service")
            raise AuthServiceUnavailableError("Auth service unavailable")
        except Exception as e:
            logger.error(f"Unexpected error validating token: {e}")
            raise AuthServiceUnavailableError(f"Auth service error: {str(e)}")
    
    async def get_user_info(self, user_id: UUID, token: str) -> Dict[str, Any]:
        """
        Get user information by user ID.
        
        Args:
            user_id: User ID to retrieve information for
            token: Valid JWT token for authorization
            
        Returns:
            User information
            
        Raises:
            UserNotFoundError: If user is not found
            InvalidTokenError: If token is invalid
            AuthServiceUnavailableError: If auth service is unavailable
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/users/{user_id}",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    logger.info(f"Retrieved user info for user {user_id}")
                    return user_data
                elif response.status_code == 404:
                    logger.warning(f"User {user_id} not found")
                    raise UserNotFoundError(f"User {user_id} not found")
                elif response.status_code == 401:
                    logger.warning("Invalid token for user info request")
                    raise InvalidTokenError("Invalid or expired token")
                else:
                    logger.error(f"Auth service returned status {response.status_code}: {response.text}")
                    raise AuthServiceUnavailableError(f"Auth service error: {response.status_code}")
                    
        except httpx.TimeoutException:
            logger.error("Auth service request timed out")
            raise AuthServiceUnavailableError("Auth service timeout")
        except httpx.ConnectError:
            logger.error("Failed to connect to auth service")
            raise AuthServiceUnavailableError("Auth service unavailable")
        except (UserNotFoundError, InvalidTokenError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting user info: {e}")
            raise AuthServiceUnavailableError(f"Auth service error: {str(e)}")
    
    async def check_user_permissions(self, user_id: UUID, resource: str, action: str, token: str) -> bool:
        """
        Check if user has permission for a specific action on a resource.
        
        Args:
            user_id: User ID to check permissions for
            resource: Resource name (e.g., 'payment', 'payment_method')
            action: Action name (e.g., 'create', 'read', 'update', 'delete')
            token: Valid JWT token for authorization
            
        Returns:
            True if user has permission, False otherwise
            
        Raises:
            InvalidTokenError: If token is invalid
            AuthServiceUnavailableError: If auth service is unavailable
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/check-permission",
                    json={
                        "user_id": str(user_id),
                        "resource": resource,
                        "action": action
                    },
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    has_permission = result.get("has_permission", False)
                    logger.info(f"Permission check for user {user_id}: {resource}:{action} = {has_permission}")
                    return has_permission
                elif response.status_code == 401:
                    logger.warning("Invalid token for permission check")
                    raise InvalidTokenError("Invalid or expired token")
                else:
                    logger.error(f"Auth service returned status {response.status_code}: {response.text}")
                    raise AuthServiceUnavailableError(f"Auth service error: {response.status_code}")
                    
        except httpx.TimeoutException:
            logger.error("Auth service request timed out")
            raise AuthServiceUnavailableError("Auth service timeout")
        except httpx.ConnectError:
            logger.error("Failed to connect to auth service")
            raise AuthServiceUnavailableError("Auth service unavailable")
        except InvalidTokenError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error checking permissions: {e}")
            raise AuthServiceUnavailableError(f"Auth service error: {str(e)}")
    
    async def health_check(self) -> bool:
        """
        Check if auth service is healthy and responding.
        
        Returns:
            True if auth service is healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception:
            return False


# Global auth service client instance
_auth_client = None


def get_auth_service_client() -> AuthServiceClient:
    """
    Get global auth service client instance.
    
    Returns:
        AuthServiceClient instance
    """
    global _auth_client
    if _auth_client is None:
        _auth_client = AuthServiceClient()
    return _auth_client


async def validate_jwt_token(token: str) -> Dict[str, Any]:
    """
    Validate JWT token and return user information.
    
    Convenience function for token validation.
    
    Args:
        token: JWT token to validate
        
    Returns:
        User information from token
        
    Raises:
        InvalidTokenError: If token is invalid
        AuthServiceUnavailableError: If auth service is unavailable
    """
    client = get_auth_service_client()
    return await client.validate_token(token)


async def get_user_by_id(user_id: UUID, token: str) -> Dict[str, Any]:
    """
    Get user information by user ID.
    
    Convenience function for user retrieval.
    
    Args:
        user_id: User ID to retrieve
        token: Valid JWT token for authorization
        
    Returns:
        User information
        
    Raises:
        UserNotFoundError: If user is not found
        InvalidTokenError: If token is invalid
        AuthServiceUnavailableError: If auth service is unavailable
    """
    client = get_auth_service_client()
    return await client.get_user_info(user_id, token)


async def check_auth_service_health() -> bool:
    """
    Check if auth service is healthy.
    
    Convenience function for health checking.
    
    Returns:
        True if auth service is healthy, False otherwise
    """
    client = get_auth_service_client()
    return await client.health_check()


# Mock implementation for development/testing
class MockAuthServiceClient(AuthServiceClient):
    """
    Mock auth service client for development and testing.
    
    Provides realistic responses without requiring actual auth service.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mock_users = {
            "123e4567-e89b-12d3-a456-426614174000": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "test@example.com",
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
                "is_active": True,
                "created_at": "2025-01-01T00:00:00Z"
            }
        }
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Mock token validation."""
        # Simple mock: accept any token that starts with 'valid_'
        if token.startswith('valid_'):
            user_id = "123e4567-e89b-12d3-a456-426614174000"
            return {
                "user_id": user_id,
                "email": "test@example.com",
                "username": "testuser",
                "exp": int(datetime.utcnow().timestamp()) + 3600  # 1 hour from now
            }
        else:
            raise InvalidTokenError("Invalid token")
    
    async def get_user_info(self, user_id: UUID, token: str) -> Dict[str, Any]:
        """Mock user info retrieval."""
        user_str = str(user_id)
        if user_str in self.mock_users:
            return self.mock_users[user_str]
        else:
            raise UserNotFoundError(f"User {user_id} not found")
    
    async def check_user_permissions(self, user_id: UUID, resource: str, action: str, token: str) -> bool:
        """Mock permission checking."""
        # For mock, allow all permissions for valid tokens
        if token.startswith('valid_'):
            return True
        else:
            raise InvalidTokenError("Invalid token")
    
    async def health_check(self) -> bool:
        """Mock health check."""
        return True


def get_mock_auth_service_client() -> MockAuthServiceClient:
    """
    Get mock auth service client for development/testing.
    
    Returns:
        MockAuthServiceClient instance
    """
    return MockAuthServiceClient()
