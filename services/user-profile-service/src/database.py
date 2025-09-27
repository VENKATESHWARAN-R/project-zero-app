"""Database configuration and session management.

This module provides database connection, session management,
and initialization utilities for the user profile service.
"""

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models.base import Base

# Get database URL from environment or use SQLite default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./user_profile_service.db"
)

# Create engine with appropriate configuration
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Required for SQLite with FastAPI
        echo=False  # Set to True for SQL debugging
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
        pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
        pool_recycle=3600,  # Recycle connections every hour
        echo=False  # Set to True for SQL debugging
    )

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_database_session() -> Generator[Session, None, None]:
    """Get a database session for dependency injection.

    This function is used as a FastAPI dependency to provide
    database sessions to route handlers.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.get("/profiles")
        def get_profile(db: Session = Depends(get_database_session)):
            # Use db session here
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Create all database tables.

    This function creates all tables defined in the models.
    Should be called during application startup.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """Drop all database tables.

    This function drops all tables. Should only be used
    in development or testing environments.
    """
    Base.metadata.drop_all(bind=engine)


def init_database() -> None:
    """Initialize the database.

    Creates all tables and performs any necessary setup.
    This is the main initialization function to call.
    """
    create_tables()


def get_database_info() -> dict:
    """Get information about the database connection.

    Returns:
        dict: Database connection information
    """
    return {
        "url": DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL,
        "engine": str(engine.url).split("@")[-1] if "@" in str(engine.url) else str(engine.url),
        "pool_size": getattr(engine.pool, "size", lambda: "N/A")(),
        "checked_out": getattr(engine.pool, "checkedout", lambda: "N/A")(),
        "overflow": getattr(engine.pool, "overflow", lambda: "N/A")(),
    }


def check_database_connection() -> bool:
    """Check if the database connection is working.

    Returns:
        bool: True if connection is working, False otherwise
    """
    try:
        with engine.connect() as connection:
            # Simple query to test connection
            connection.execute("SELECT 1")
        return True
    except Exception:
        return False


def get_database_health() -> dict:
    """Get database health information.

    Returns:
        dict: Database health status and metrics
    """
    try:
        is_connected = check_database_connection()
        info = get_database_info()

        return {
            "status": "connected" if is_connected else "disconnected",
            "url": info["url"],
            "pool_info": {
                "size": info["pool_size"],
                "checked_out": info["checked_out"],
                "overflow": info["overflow"],
            } if info["pool_size"] != "N/A" else None
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


# Database session dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    """Alias for get_database_session for convenience."""
    yield from get_database_session()