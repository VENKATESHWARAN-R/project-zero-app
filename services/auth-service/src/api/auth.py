"""
Authentication API endpoints.
Implements POST /auth/login, POST /auth/logout, POST /auth/refresh, GET /auth/verify.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.auth import (
    LoginRequest, LoginResponse,
    LogoutRequest, LogoutResponse,
    RefreshRequest, RefreshResponse,
    VerifyResponse, ErrorResponse
)
from src.services.auth_service import AuthService, AuthenticationError, RateLimitError, ValidationError
from src.services.token_service import TokenService, TokenError

logger = logging.getLogger(__name__)

router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def get_client_ip(request: Request) -> str:
    """Get client IP address from request."""
    return request.client.host if request.client else "unknown"


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    User login endpoint.
    Authenticates user with email and password, returns JWT tokens.
    """
    try:
        auth_service = AuthService(db)
        client_ip = get_client_ip(request)

        # Authenticate user
        tokens = auth_service.authenticate_user(
            email=login_data.email,
            password=login_data.password,
            client_ip=client_ip
        )

        return LoginResponse(**tokens)

    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded for {login_data.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )

    except AuthenticationError as e:
        logger.info(f"Authentication failed for {login_data.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

    except ValidationError as e:
        logger.info(f"Validation error for {login_data.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

    except Exception as e:
        logger.error(f"Unexpected error during login for {login_data.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    logout_data: LogoutRequest,
    db: Session = Depends(get_db)
):
    """
    User logout endpoint.
    Invalidates refresh token by adding it to blacklist.
    """
    try:
        token_service = TokenService(db)

        # Logout user (blacklist refresh token)
        result = token_service.logout_user(logout_data.refresh_token)

        return LogoutResponse(**result)

    except TokenError as e:
        logger.info(f"Token error during logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        logger.error(f"Unexpected error during logout: {e}")
        # For logout, we're more permissive - still confirm logout
        return LogoutResponse(message="Successfully logged out")


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    refresh_data: RefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Token refresh endpoint.
    Creates new access token using valid refresh token.
    """
    try:
        token_service = TokenService(db)

        # Refresh access token
        new_token_data = token_service.refresh_access_token(refresh_data.refresh_token)

        return RefreshResponse(**new_token_data)

    except TokenError as e:
        logger.info(f"Token error during refresh: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/verify", response_model=VerifyResponse)
async def verify_token(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Token verification endpoint.
    Validates JWT token and returns user information.
    """
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing",
                headers={"WWW-Authenticate": "Bearer"}
            )

        token_service = TokenService(db)

        # Verify access token
        verification_result = token_service.verify_access_token(token)

        return VerifyResponse(
            valid=verification_result["valid"],
            user_id=verification_result["user_id"],
            email=verification_result["email"]
        )

    except TokenError as e:
        logger.info(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )