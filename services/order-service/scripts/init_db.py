#!/usr/bin/env python3
"""Database initialization script for Order Service.

Creates tables and seeds test data for integration testing.

Run from order-service directory:
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
        
        logger.info("Starting Order Service database initialization...")
        
        # Create database schema using existing function
        create_tables()
        logger.info("Database schema created successfully")
        
        logger.info(
            "Order Service database initialization completed successfully"
        )
        
    except ImportError as e:
        logger.exception(
            "Import error - ensure script is run from order-service directory: %s",
            str(e)
        )
        sys.exit(1)
    except Exception as e:
        logger.exception("Database initialization failed: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()