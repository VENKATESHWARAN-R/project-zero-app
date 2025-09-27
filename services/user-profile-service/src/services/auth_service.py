import httpx
import jwt
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, auth_service_url: str, jwt_secret_key: str, jwt_algorithm: str = "HS256"):
        self.auth_service_url = auth_service_url.rstrip('/')
        self.jwt_secret_key = jwt_secret_key
        self.jwt_algorithm = jwt_algorithm
        self.timeout = 5.0  # 5 second timeout for auth service calls

    def verify_token_local(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token locally using the shared secret."""
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret_key,
                algorithms=[self.jwt_algorithm]
            )

            # Check token expiration
            exp = payload.get('exp')
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(tz=timezone.utc):
                logger.warning("Token has expired")
                return None

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return None

    async def verify_token_remote(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify token with the auth service (fallback method)."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.auth_service_url}/auth/verify",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "user_id": data.get("user_id"),
                        "email": data.get("email"),
                        "verified": True
                    }
                else:
                    logger.warning(f"Auth service returned status {response.status_code}")
                    return None

        except httpx.TimeoutException:
            logger.error("Auth service timeout")
            return None
        except Exception as e:
            logger.error(f"Auth service error: {str(e)}")
            return None

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify token using local verification with remote fallback."""
        # Try local verification first
        payload = self.verify_token_local(token)

        if payload:
            return {
                "user_id": payload.get("user_id"),
                "email": payload.get("email"),
                "verified": True,
                "method": "local"
            }

        # Fallback to remote verification
        logger.info("Local token verification failed, trying remote verification")
        payload = await self.verify_token_remote(token)

        if payload:
            payload["method"] = "remote"
            return payload

        # Both methods failed
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    def extract_user_id(self, token: str) -> int:
        """Extract user ID from token (synchronous method for quick access)."""
        payload = self.verify_token_local(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token does not contain user_id"
            )

        return int(user_id)

    def is_admin_user(self, token_payload: Dict[str, Any]) -> bool:
        """Check if the user has admin privileges."""
        # For now, check if email contains 'admin' or if there's an admin role
        email = token_payload.get("email", "")
        roles = token_payload.get("roles", [])

        return "admin" in email.lower() or "admin" in roles

    async def check_auth_service_health(self) -> bool:
        """Check if the auth service is healthy."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.auth_service_url}/health")
                return response.status_code == 200
        except Exception:
            return False