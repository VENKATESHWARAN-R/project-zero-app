#!/usr/bin/env python3
"""Database initialization script for Payment Service.

Creates tables and seeds test data for integration testing.

Run from payment-service directory:
    python scripts/init_db.py
"""

import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Initialize database schema and seed test data."""
    try:
        # Add parent directory to path to import src modules
        current_dir = Path(__file__).parent
        parent_dir = current_dir.parent
        sys.path.insert(0, str(parent_dir))
        
        # Import after path adjustment
        from src.database import create_tables
        
        logger.info("Starting Payment Service database initialization...")
        
        # Create database schema using existing function
        create_tables()
        logger.info("Database schema created successfully")
        
        logger.info("Payment Service database initialization completed successfully")
        
    except ImportError:
        logger.exception("Import error - ensure script is run from payment-service directory")
        sys.exit(1)
    except Exception:
        logger.exception("Database initialization failed")
        sys.exit(1)


if __name__ == "__main__":
    main()