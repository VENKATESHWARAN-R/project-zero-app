"""
Pydantic models for authentication API requests and responses.
Based on the API contract in auth-api.yml.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """Login request model."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }
    }


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str = Field(..., description="JWT access token for API authentication")
    refresh_token: str = Field(..., description="JWT refresh token for obtaining new access tokens")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900
            }
        }
    }


class RefreshRequest(BaseModel):
    """Token refresh request model."""
    refresh_token: str = Field(..., description="Valid refresh token")

    model_config = {
        "json_schema_extra": {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    }


class RefreshResponse(BaseModel):
    """Token refresh response model."""
    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900
            }
        }
    }


class LogoutRequest(BaseModel):
    """Logout request model."""
    refresh_token: str = Field(..., description="Refresh token to invalidate")

    model_config = {
        "json_schema_extra": {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    }


class LogoutResponse(BaseModel):
    """Logout response model."""
    message: str = Field(..., description="Logout confirmation message")

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Successfully logged out"
            }
        }
    }


class VerifyResponse(BaseModel):
    """Token verification response model."""
    valid: bool = Field(..., description="Whether the token is valid")
    user_id: int = Field(..., description="ID of the authenticated user")
    email: Optional[str] = Field(None, description="Email of the authenticated user")

    model_config = {
        "json_schema_extra": {
            "example": {
                "valid": True,
                "user_id": 123,
                "email": "user@example.com"
            }
        }
    }


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service health status")
    timestamp: datetime = Field(..., description="Current timestamp")
    database: Optional[str] = Field(None, description="Database connection status")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "timestamp": "2025-09-23T10:30:00Z",
                "database": "connected"
            }
        }
    }


class RegisterRequest(BaseModel):
    """User registration request model."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "newuser@example.com",
                "password": "SecurePass123"
            }
        }
    }


class RegisterResponse(BaseModel):
    """User registration response model."""
    user_id: int = Field(..., description="ID of the newly created user")
    email: str = Field(..., description="Email of the registered user")
    message: str = Field(..., description="Registration confirmation message")

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": 123,
                "email": "newuser@example.com",
                "message": "User registered successfully"
            }
        }
    }


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str = Field(..., description="Error message describing what went wrong")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")

    model_config = {
        "json_schema_extra": {
            "example": {
                "detail": "Invalid email or password",
                "error_code": "INVALID_CREDENTIALS"
            }
        }
    }