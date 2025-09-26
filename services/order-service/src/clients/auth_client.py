"""
Authentication service client.

Handles JWT token validation and user role verification.
"""

import asyncio
from typing import Dict, Optional, Any
import httpx
from jose import JWTError, jwt

from ..config import settings
from ..logging_config import get_logger, get_correlation_id

logger = get_logger(__name__)


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class AuthorizationError(Exception):
    """Raised when user lacks required permissions."""
    pass


class AuthClient:
    """Client for authentication service interactions."""

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize AuthClient.

        Args:
            base_url: Auth service base URL, defaults to config setting
        """
        self.base_url = (base_url or settings.auth_service_url).rstrip('/')
        self.timeout = httpx.Timeout(10.0)  # 10 second timeout
        logger.info("AuthClient initialized", extra={
            "base_url": self.base_url
        })

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token with auth service.

        Args:
            token: JWT token to verify

        Returns:
            Dictionary containing user information

        Raises:
            AuthenticationError: If token is invalid or expired
            httpx.RequestError: If auth service is unavailable
        """
        if not token:
            raise AuthenticationError("Token is required")

        # First try to decode and validate JWT locally
        try:
            payload = self._decode_token_locally(token)
            logger.debug("Token decoded locally", extra={
                "user_id": payload.get("user_id"),
                "email": payload.get("email"),
                "role": payload.get("role")
            })
            return payload
        except JWTError as e:
            logger.warning("Local token validation failed", extra={
                "error": str(e)
            })
            # Fallback to remote validation
            return await self._verify_token_remotely(token)

    def _decode_token_locally(self, token: str) -> Dict[str, Any]:
        """
        Decode JWT token locally using shared secret.

        Args:
            token: JWT token to decode

        Returns:
            Token payload

        Raises:
            JWTError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )

            # Validate required fields
            required_fields = ["user_id", "email"]
            for field in required_fields:
                if field not in payload:
                    raise JWTError(f"Missing required field: {field}")

            return payload

        except JWTError as e:
            logger.debug("JWT decode failed", extra={
                "error": str(e),
                "algorithm": settings.jwt_algorithm
            })
            raise

    async def _verify_token_remotely(self, token: str) -> Dict[str, Any]:
        """
        Verify token with remote auth service.

        Args:
            token: JWT token to verify

        Returns:
            User information from auth service

        Raises:
            AuthenticationError: If token is invalid
            httpx.RequestError: If service is unavailable
        """
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        correlation_id = get_correlation_id()
        if correlation_id:
            headers["x-correlation-id"] = correlation_id

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/auth/verify",
                    headers=headers
                )

                if response.status_code == 200:
                    user_data = response.json()
                    logger.info("Token verified remotely", extra={
                        "user_id": user_data.get("user_id"),
                        "email": user_data.get("email")
                    })
                    return user_data

                elif response.status_code == 401:
                    logger.warning("Token verification failed", extra={
                        "status_code": response.status_code,
                        "response": response.text[:200]
                    })
                    raise AuthenticationError("Invalid or expired token")

                else:
                    logger.error("Auth service error", extra={
                        "status_code": response.status_code,
                        "response": response.text[:200]
                    })
                    raise AuthenticationError(f"Auth service error: {response.status_code}")

        except httpx.RequestError as e:
            logger.error("Failed to connect to auth service", extra={
                "error": str(e),
                "base_url": self.base_url
            })
            raise

    def check_admin_role(self, user_data: Dict[str, Any]) -> bool:
        """
        Check if user has admin role.

        Args:
            user_data: User data from token verification

        Returns:
            True if user has admin role
        """
        role = user_data.get("role", "user")
        is_admin = role in ["admin", "order_admin", "super_admin"]

        logger.debug("Admin role check", extra={
            "user_id": user_data.get("user_id"),
            "role": role,
            "is_admin": is_admin
        })

        return is_admin

    def require_admin_role(self, user_data: Dict[str, Any]) -> None:
        """
        Require user to have admin role.

        Args:
            user_data: User data from token verification

        Raises:
            AuthorizationError: If user lacks admin role
        """
        if not self.check_admin_role(user_data):
            logger.warning("Admin access denied", extra={
                "user_id": user_data.get("user_id"),
                "role": user_data.get("role")
            })
            raise AuthorizationError("Admin privileges required")

    def check_order_owner(self, user_data: Dict[str, Any], order_user_id: int) -> bool:
        """
        Check if user owns the order or has admin privileges.

        Args:
            user_data: User data from token verification
            order_user_id: User ID that owns the order

        Returns:
            True if user can access the order
        """
        user_id = user_data.get("user_id")
        is_owner = user_id == order_user_id
        is_admin = self.check_admin_role(user_data)

        can_access = is_owner or is_admin

        logger.debug("Order access check", extra={
            "user_id": user_id,
            "order_user_id": order_user_id,
            "is_owner": is_owner,
            "is_admin": is_admin,
            "can_access": can_access
        })

        return can_access

    def require_order_owner(self, user_data: Dict[str, Any], order_user_id: int) -> None:
        """
        Require user to own the order or have admin privileges.

        Args:
            user_data: User data from token verification
            order_user_id: User ID that owns the order

        Raises:
            AuthorizationError: If user cannot access the order
        """
        if not self.check_order_owner(user_data, order_user_id):
            logger.warning("Order access denied", extra={
                "user_id": user_data.get("user_id"),
                "order_user_id": order_user_id
            })
            raise AuthorizationError("Access denied - not order owner")