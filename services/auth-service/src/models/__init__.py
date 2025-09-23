"""
Database models initialization and migrations.
"""
from src.models.user import User
from src.database import Base, engine
import logging

logger = logging.getLogger(__name__)

# Make models available for import
__all__ = ["User"]


def create_all_tables():
    """
    Create all database tables.
    This is called during application startup.
    """
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_all_tables():
    """
    Drop all database tables.
    Used for testing and development reset.
    """
    try:
        logger.info("Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


# Initialize tables on import (for development)
# In production, this would be handled by migration scripts
if __name__ != "__main__":
    try:
        create_all_tables()
    except Exception as e:
        logger.warning(f"Could not create tables on import: {e}")
        # Don't fail the import, tables might already exist