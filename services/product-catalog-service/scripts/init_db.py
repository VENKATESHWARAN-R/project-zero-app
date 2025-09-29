#!/usr/bin/env python3
"""
Database initialization script for Product Catalog Service.
Creates tables and seeds sample product data for integration testing.

Run from product-catalog-service directory:
    python scripts/init_db.py
"""

import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main initialization function."""
    try:
        # Add parent directory to path to import src modules
        current_dir = Path(__file__).parent
        parent_dir = current_dir.parent
        sys.path.insert(0, str(parent_dir))
        
        # Import after path adjustment
        from src.database import init_database
        
        logger.info("Starting Product Catalog Service database initialization...")
        
        # Initialize database and seed data using existing function
        init_database()
        
        logger.info("Product Catalog Service database initialization completed successfully")
        
    except ImportError as e:
        logger.error("Import error - ensure script is run from product-catalog-service directory: %s", str(e))
        sys.exit(1)
    except Exception as e:
        logger.error("Database initialization failed: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()