from pydantic_settings import BaseSettings
from typing import Optional
import secrets
from functools import lru_cache

from .services.auth_service import AuthService


class Settings(BaseSettings):
    """Application settings and configuration."""

    # Service Configuration
    service_name: str = "user-profile-service"
    version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8002

    # Database Configuration
    database_url: str = "sqlite:///./user_profile_service.db"

    # JWT Configuration
    jwt_secret_key: str = secrets.token_urlsafe(32)
    jwt_algorithm: str = "HS256"

    # External Service URLs
    auth_service_url: str = "http://localhost:8001"

    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "text"

    # CORS Configuration
    cors_allow_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:8008"
    ]

    # Security Configuration
    trusted_hosts: list[str] = [
        "localhost",
        "127.0.0.1",
        "0.0.0.0"
    ]

    # Performance Configuration
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600

    # Rate Limiting Configuration (future use)
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    # Feature Flags
    enable_admin_endpoints: bool = True
    enable_activity_logging: bool = True
    enable_preference_validation: bool = True

    # Health Check Configuration
    health_check_timeout: float = 5.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def get_database_url(self) -> str:
        """Get database URL with proper formatting."""
        return self.database_url

    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.debug and self.log_level.upper() in ["WARNING", "ERROR", "CRITICAL"]

    def get_cors_origins(self) -> list[str]:
        """Get CORS allowed origins."""
        if self.debug:
            # In debug mode, allow additional development origins
            return self.cors_allow_origins + [
                "http://localhost:3001",
                "http://localhost:3002",
                "http://localhost:8080"
            ]
        return self.cors_allow_origins

    def get_log_config(self) -> dict:
        """Get logging configuration."""
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
                "json": {
                    "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
                }
            },
            "handlers": {
                "default": {
                    "formatter": self.log_format,
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": self.log_level.upper(),
                "handlers": ["default"],
            },
            "loggers": {
                "uvicorn": {
                    "level": "INFO",
                    "handlers": ["default"],
                    "propagate": False,
                },
                "sqlalchemy": {
                    "level": "WARNING",
                    "handlers": ["default"],
                    "propagate": False,
                },
            }
        }
        return config


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


@lru_cache()
def get_auth_service() -> AuthService:
    """Get configured auth service instance."""
    settings = get_settings()
    return AuthService(
        auth_service_url=settings.auth_service_url,
        jwt_secret_key=settings.jwt_secret_key,
        jwt_algorithm=settings.jwt_algorithm
    )