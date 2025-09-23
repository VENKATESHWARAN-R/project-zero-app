"""
JWT token generation and validation utilities.
Implements JWT specifications from research.md.
"""
import jwt
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)

# JWT Configuration from research.md
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15 minutes as per specification
REFRESH_TOKEN_EXPIRE_DAYS = 7     # 7 days as per specification


def create_access_token(user_id: int) -> Dict[str, Any]:
    """
    Create an access token for a user.

    Args:
        user_id (int): User ID to encode in token

    Returns:
        Dict[str, Any]: Token data with token, type, and expiration
    """
    try:
        # Token expiration
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        # JWT claims
        to_encode = {
            "user_id": user_id,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": str(uuid.uuid4())  # Unique token ID for blacklisting
        }

        # Encode token
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

        return {
            "access_token": encoded_jwt,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
        }

    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise ValueError("Failed to create access token")


def create_refresh_token(user_id: int) -> str:
    """
    Create a refresh token for a user.

    Args:
        user_id (int): User ID to encode in token

    Returns:
        str: Refresh token
    """
    try:
        # Token expiration
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        # JWT claims
        to_encode = {
            "user_id": user_id,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": str(uuid.uuid4())  # Unique token ID for blacklisting
        }

        # Encode token
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt

    except Exception as e:
        logger.error(f"Error creating refresh token: {e}")
        raise ValueError("Failed to create refresh token")


def create_token_pair(user_id: int) -> Dict[str, Any]:
    """
    Create both access and refresh tokens for a user.

    Args:
        user_id (int): User ID to encode in tokens

    Returns:
        Dict[str, Any]: Complete token response
    """
    try:
        # Create access token
        access_token_data = create_access_token(user_id)

        # Create refresh token
        refresh_token = create_refresh_token(user_id)

        return {
            "access_token": access_token_data["access_token"],
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": access_token_data["expires_in"]
        }

    except Exception as e:
        logger.error(f"Error creating token pair: {e}")
        raise ValueError("Failed to create tokens")


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token (str): JWT token to decode

    Returns:
        Dict[str, Any]: Decoded token payload

    Raises:
        jwt.ExpiredSignatureError: If token is expired
        jwt.InvalidTokenError: If token is invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise

    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise

    except Exception as e:
        logger.error(f"Error decoding token: {e}")
        raise jwt.InvalidTokenError("Failed to decode token")


def validate_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Validate an access token and return user data.

    Args:
        token (str): Access token to validate

    Returns:
        Optional[Dict[str, Any]]: User data if valid, None otherwise
    """
    try:
        payload = decode_token(token)

        # Check token type
        if payload.get("type") != "access":
            logger.warning("Wrong token type for access validation")
            return None

        # Check required fields
        if "user_id" not in payload:
            logger.warning("Access token missing user_id")
            return None

        return {
            "user_id": payload["user_id"],
            "jti": payload.get("jti"),
            "exp": payload.get("exp"),
            "iat": payload.get("iat")
        }

    except jwt.ExpiredSignatureError:
        logger.info("Access token expired")
        return None

    except jwt.InvalidTokenError:
        logger.info("Invalid access token")
        return None

    except Exception as e:
        logger.error(f"Error validating access token: {e}")
        return None


def validate_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Validate a refresh token and return user data.

    Args:
        token (str): Refresh token to validate

    Returns:
        Optional[Dict[str, Any]]: User data if valid, None otherwise
    """
    try:
        payload = decode_token(token)

        # Check token type
        if payload.get("type") != "refresh":
            logger.warning("Wrong token type for refresh validation")
            return None

        # Check required fields
        if "user_id" not in payload:
            logger.warning("Refresh token missing user_id")
            return None

        return {
            "user_id": payload["user_id"],
            "jti": payload.get("jti"),
            "exp": payload.get("exp"),
            "iat": payload.get("iat")
        }

    except jwt.ExpiredSignatureError:
        logger.info("Refresh token expired")
        return None

    except jwt.InvalidTokenError:
        logger.info("Invalid refresh token")
        return None

    except Exception as e:
        logger.error(f"Error validating refresh token: {e}")
        return None


def extract_token_from_header(authorization_header: str) -> Optional[str]:
    """
    Extract JWT token from Authorization header.

    Args:
        authorization_header (str): Authorization header value

    Returns:
        Optional[str]: Extracted token or None if invalid format
    """
    try:
        if not authorization_header:
            return None

        # Expected format: "Bearer <token>"
        parts = authorization_header.split()

        if len(parts) != 2:
            return None

        scheme, token = parts

        if scheme.lower() != "bearer":
            return None

        return token

    except Exception as e:
        logger.error(f"Error extracting token from header: {e}")
        return None


def get_token_jti(token: str) -> Optional[str]:
    """
    Get the JTI (JWT ID) from a token without full validation.

    Args:
        token (str): JWT token

    Returns:
        Optional[str]: JTI if present, None otherwise
    """
    try:
        # Decode without verification to get JTI for blacklisting
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload.get("jti")

    except Exception as e:
        logger.error(f"Error extracting JTI from token: {e}")
        return None