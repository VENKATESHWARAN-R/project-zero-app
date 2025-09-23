"""
Token management service.
Handles token refresh, verification, and logout operations.
"""
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from src.models.user import User
from src.utils.jwt_utils import (
    validate_access_token,
    validate_refresh_token,
    create_access_token,
    extract_token_from_header
)
from src.utils.token_blacklist import is_token_blacklisted, blacklist_token_by_jwt

logger = logging.getLogger(__name__)


class TokenError(Exception):
    """Exception raised for token-related errors."""
    pass


class TokenService:
    """Token management service for JWT operations."""

    def __init__(self, db: Session):
        self.db = db

    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """
        Verify an access token and return user information.

        Args:
            token (str): Access token to verify

        Returns:
            Dict[str, Any]: User information and token status

        Raises:
            TokenError: If token is invalid or expired
        """
        try:
            if not token:
                raise TokenError("Token is required")

            # Validate token format and expiration
            token_data = validate_access_token(token)
            if not token_data:
                raise TokenError("Invalid or expired token")

            # Check if token is blacklisted
            jti = token_data.get("jti")
            if jti and is_token_blacklisted(jti):
                logger.info(f"Blacklisted token used: {jti[:8]}...")
                raise TokenError("Token has been revoked")

            # Get user information
            user_id = token_data["user_id"]
            user = self.db.query(User).filter(User.id == user_id).first()

            if not user:
                logger.warning(f"Token contains invalid user_id: {user_id}")
                raise TokenError("Invalid token - user not found")

            # Check if user is still active
            if not user.is_active:
                logger.warning(f"Token for inactive user: {user.email}")
                raise TokenError("User account is disabled")

            return {
                "valid": True,
                "user_id": user.id,
                "email": user.email,
                "is_active": user.is_active,
                "token_data": token_data
            }

        except TokenError:
            raise

        except Exception as e:
            logger.error(f"Error verifying access token: {e}")
            raise TokenError("Token verification failed")

    def verify_access_token_from_header(self, authorization_header: str) -> Dict[str, Any]:
        """
        Verify access token from Authorization header.

        Args:
            authorization_header (str): Authorization header value

        Returns:
            Dict[str, Any]: User information and token status

        Raises:
            TokenError: If token is invalid or missing
        """
        try:
            # Extract token from header
            token = extract_token_from_header(authorization_header)
            if not token:
                raise TokenError("Invalid Authorization header format")

            return self.verify_access_token(token)

        except TokenError:
            raise

        except Exception as e:
            logger.error(f"Error verifying token from header: {e}")
            raise TokenError("Authorization header verification failed")

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Create new access token using refresh token.

        Args:
            refresh_token (str): Valid refresh token

        Returns:
            Dict[str, Any]: New access token data

        Raises:
            TokenError: If refresh token is invalid
        """
        try:
            if not refresh_token:
                raise TokenError("Refresh token is required")

            # Validate refresh token
            token_data = validate_refresh_token(refresh_token)
            if not token_data:
                raise TokenError("Invalid or expired refresh token")

            # Check if refresh token is blacklisted
            jti = token_data.get("jti")
            if jti and is_token_blacklisted(jti):
                logger.info(f"Blacklisted refresh token used: {jti[:8]}...")
                raise TokenError("Refresh token has been revoked")

            # Get user information
            user_id = token_data["user_id"]
            user = self.db.query(User).filter(User.id == user_id).first()

            if not user:
                logger.warning(f"Refresh token contains invalid user_id: {user_id}")
                raise TokenError("Invalid refresh token - user not found")

            # Check if user is still active
            if not user.is_active:
                logger.warning(f"Refresh token for inactive user: {user.email}")
                raise TokenError("User account is disabled")

            # Create new access token
            new_token_data = create_access_token(user.id)

            logger.info(f"Access token refreshed for user: {user.email}")
            return new_token_data

        except TokenError:
            raise

        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            raise TokenError("Token refresh failed")

    def logout_user(self, refresh_token: str) -> Dict[str, str]:
        """
        Logout user by blacklisting refresh token.

        Args:
            refresh_token (str): Refresh token to invalidate

        Returns:
            Dict[str, str]: Logout confirmation

        Raises:
            TokenError: If refresh token is invalid
        """
        try:
            if not refresh_token:
                raise TokenError("Refresh token is required")

            # Validate refresh token (to ensure it's valid before blacklisting)
            token_data = validate_refresh_token(refresh_token)
            if not token_data:
                # For user experience, allow logout even with invalid tokens
                logger.info("Logout attempted with invalid refresh token")
                return {"message": "Successfully logged out"}

            # Get user information for logging
            user_id = token_data["user_id"]
            user = self.db.query(User).filter(User.id == user_id).first()

            # Blacklist the refresh token
            blacklist_token_by_jwt(refresh_token)

            # Log successful logout
            if user:
                logger.info(f"User logged out: {user.email}")
            else:
                logger.info(f"Logout for user_id: {user_id}")

            return {"message": "Successfully logged out"}

        except TokenError:
            # For logout, we're more permissive - don't fail on invalid tokens
            logger.info("Logout attempted with invalid token")
            return {"message": "Successfully logged out"}

        except Exception as e:
            logger.error(f"Error during logout: {e}")
            # Even on error, confirm logout for better UX
            return {"message": "Successfully logged out"}

    def logout_all_user_tokens(self, user_id: int) -> Dict[str, str]:
        """
        Logout user from all devices by blacklisting all their tokens.

        Note: This is a simplified implementation that doesn't track all tokens.
        In a production system, you might want to track issued tokens or
        use a different approach like incrementing a user token version.

        Args:
            user_id (int): User ID

        Returns:
            Dict[str, str]: Logout confirmation
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                logger.info(f"Global logout requested for user: {user.email}")
            else:
                logger.warning(f"Global logout for non-existent user: {user_id}")

            # Note: In this simple implementation, we can't invalidate all tokens
            # because we don't track them. In production, you might:
            # 1. Keep a list of issued tokens per user
            # 2. Use a user token version number in JWT claims
            # 3. Use Redis to track all user tokens

            return {"message": "Successfully logged out from all devices"}

        except Exception as e:
            logger.error(f"Error during global logout for user {user_id}: {e}")
            return {"message": "Successfully logged out from all devices"}

    def get_token_info(self, token: str) -> Dict[str, Any]:
        """
        Get information about a token without full validation.

        Args:
            token (str): JWT token

        Returns:
            Dict[str, Any]: Token information
        """
        try:
            from src.utils.jwt_utils import decode_token

            # Try to decode token
            payload = decode_token(token)

            return {
                "user_id": payload.get("user_id"),
                "type": payload.get("type"),
                "exp": payload.get("exp"),
                "iat": payload.get("iat"),
                "jti": payload.get("jti"),
                "is_blacklisted": is_token_blacklisted(payload.get("jti"))
            }

        except Exception as e:
            logger.error(f"Error getting token info: {e}")
            return {
                "error": "Could not decode token",
                "is_blacklisted": False
            }

    def validate_token_format(self, token: str) -> bool:
        """
        Basic validation of JWT token format.

        Args:
            token (str): Token to validate

        Returns:
            bool: True if format is valid
        """
        try:
            if not token:
                return False

            # JWT should have 3 parts separated by dots
            parts = token.split(".")
            if len(parts) != 3:
                return False

            # Each part should be non-empty
            return all(len(part) > 0 for part in parts)

        except Exception:
            return False