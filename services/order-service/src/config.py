import os
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./order_service.db",
        description="Database connection URL - SQLite for dev, PostgreSQL for prod"
    )

    # JWT Configuration (inherited from auth service)
    jwt_secret_key: str = Field(
        default="change-me-in-production",
        description="JWT secret key for token validation"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )

    # Service URLs for inter-service communication
    auth_service_url: str = Field(
        default="http://localhost:8001",
        description="Auth service base URL"
    )
    cart_service_url: str = Field(
        default="http://localhost:8007",
        description="Cart service base URL"
    )
    product_service_url: str = Field(
        default="http://localhost:8004",
        description="Product catalog service base URL"
    )

    # Business Configuration
    tax_rate: float = Field(
        default=0.085,
        description="Fixed tax rate (8.5%)"
    )

    # Server Configuration
    host: str = Field(
        default="0.0.0.0",
        description="Server bind host"
    )
    port: int = Field(
        default=8008,
        description="Server port"
    )

    # Environment
    environment: str = Field(
        default="development",
        description="Environment: development, testing, production"
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )

    # CORS Configuration - store as string and parse manually
    cors_origins_str: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="CORS allowed origins (comma-separated)",
        alias="cors_origins"
    )

    @property
    def cors_origins(self) -> list[str]:
        """Parse comma-separated CORS origins string into list"""
        return [origin.strip() for origin in self.cors_origins_str.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_database_url() -> str:
    """Get database URL with environment-specific handling."""
    if settings.environment == "testing":
        return "sqlite:///./test_order_service.db"
    return settings.database_url


def is_production() -> bool:
    """Check if running in production environment."""
    return settings.environment.lower() == "production"


def is_development() -> bool:
    """Check if running in development environment."""
    return settings.environment.lower() == "development"