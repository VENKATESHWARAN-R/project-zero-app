import jwt
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class JWTAuth:
    """JWT authentication utility class."""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            # Check token expiration
            exp = payload.get('exp')
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(tz=timezone.utc):
                logger.warning("Token has expired")
                return None

            # Validate required fields
            if not payload.get('user_id'):
                logger.warning("Token missing user_id")
                return None

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Token decode error: {str(e)}")
            return None

    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate token and return payload or raise HTTPException."""
        payload = self.decode_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return payload

    def extract_user_info(self, token: str) -> Dict[str, Any]:
        """Extract user information from token."""
        payload = self.validate_token(token)

        return {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "roles": payload.get("roles", []),
            "exp": payload.get("exp"),
            "iat": payload.get("iat")
        }

    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired without raising an exception."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}  # Don't verify expiration during decode
            )

            exp = payload.get('exp')
            if not exp:
                return True  # No expiration means invalid

            return datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(tz=timezone.utc)

        except jwt.InvalidTokenError:
            return True  # Invalid token is considered expired
        except Exception:
            return True  # Any other error is considered expired