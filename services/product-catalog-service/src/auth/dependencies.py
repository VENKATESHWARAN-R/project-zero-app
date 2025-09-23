"""Authentication dependencies for admin endpoints."""

import logging

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.config import settings

logger = logging.getLogger(__name__)

# Security scheme for Bearer token
security = HTTPBearer()


async def verify_admin_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Verify JWT token with auth service for admin operations.

    Args:
        credentials: Bearer token credentials

    Returns:
        User info from auth service

    Raises:
        HTTPException: If token is invalid or auth service is unreachable

    """
    token = credentials.credentials

    try:
        # Call auth service to verify token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/auth/verify",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0,
            )

            if response.status_code == 200:
                user_info = response.json()
                logger.info(
                    f"Token verified for user: {user_info.get('email', 'unknown')}"
                )
                return user_info
            if response.status_code == 401:
                logger.warning("Invalid token provided")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            logger.error(f"Auth service error: {response.status_code}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication service error",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except httpx.TimeoutException:
        logger.error("Auth service timeout")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        )
    except httpx.RequestError as e:
        logger.error(f"Auth service connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in token verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# Dependency alias for easier use
AdminRequired = Depends(verify_admin_token)
