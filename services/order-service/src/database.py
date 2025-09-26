from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .config import get_database_url, is_production


def create_database_engine():
    """Create database engine with environment-specific configuration."""
    database_url = get_database_url()

    if database_url.startswith("sqlite"):
        # SQLite configuration for development/testing
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=not is_production(),
        )
    else:
        # PostgreSQL configuration for production
        engine = create_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
            echo=not is_production(),
        )

    return engine


# Database engine
engine = create_database_engine()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

# Metadata for schema operations
metadata = MetaData()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    # Import all models to ensure they're registered with SQLAlchemy
    from .models import order, order_item, shipping_address, order_modification  # noqa: F401

    # Create all tables
    Base.metadata.create_all(bind=engine)


def close_db():
    """Close database connections."""
    engine.dispose()