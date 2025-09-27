from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid

from .services.auth_service import AuthService
from .config import get_auth_service

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """Get current authenticated user from JWT token."""
    try:
        user_data = await auth_service.verify_token(credentials.credentials)
        return user_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


async def require_admin(
    current_user: Dict[str, Any] = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """Require admin privileges for the current user."""
    if not auth_service.is_admin_user(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for this operation"
        )
    return current_user


def get_request_context(request: Request) -> Dict[str, Any]:
    """Extract request context for logging and audit purposes."""
    # Get client IP address
    ip_address = request.client.host if request.client else None
    if not ip_address and hasattr(request, 'headers'):
        # Check for forwarded IP in common proxy headers
        ip_address = (
            request.headers.get('x-forwarded-for') or
            request.headers.get('x-real-ip') or
            request.headers.get('cf-connecting-ip')
        )
        if ip_address and ',' in ip_address:
            # Take the first IP if there are multiple
            ip_address = ip_address.split(',')[0].strip()

    # Get user agent
    user_agent = request.headers.get('user-agent')

    # Get or generate correlation ID
    correlation_id = (
        request.headers.get('x-correlation-id') or
        request.headers.get('x-request-id') or
        str(uuid.uuid4())
    )

    return {
        "ip_address": ip_address,
        "user_agent": user_agent,
        "correlation_id": correlation_id,
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path
    }