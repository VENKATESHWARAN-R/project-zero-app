#!/usr/bin/env python3
"""
Database initialization script for Auth Service.
Creates tables and seeds test user data for integration testing.

Run from auth-service directory:
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
        from src.database import SessionLocal, create_tables
        from src.models.user import User
        from src.services.auth_service import hash_password
        
        logger.info("Starting Auth Service database initialization...")
        
        # Create database schema using existing function
        create_tables()
        logger.info("Database schema created successfully")
        
        # Seed test users
        db = SessionLocal()
        try:
            # Check if test users already exist
            existing_user = db.query(User).filter(User.email == "test@example.com").first()
            if existing_user:
                logger.info("Test users already exist, skipping seeding")
                return
            
            logger.info("Seeding test users...")
            
            # Create test users for integration testing
            test_users = [
                {
                    "email": "test@example.com",
                    "password": "testpassword123",
                    "is_active": True
                },
                {
                    "email": "admin@example.com", 
                    "password": "adminpassword123",
                    "is_active": True
                },
                {
                    "email": "user@example.com",
                    "password": "userpassword123", 
                    "is_active": True
                }
            ]
            
            for user_data in test_users:
                hashed_password = hash_password(user_data["password"])
                user = User(
                    email=user_data["email"],
                    hashed_password=hashed_password,
                    is_active=user_data["is_active"]
                )
                db.add(user)
            
            db.commit()
            logger.info("Successfully seeded %d test users", len(test_users))
            
        except Exception as e:
            logger.error("Error seeding test users: %s", str(e))
            db.rollback()
            raise
        finally:
            db.close()
        
        logger.info("Auth Service database initialization completed successfully")
        
    except ImportError as e:
        logger.error("Import error - ensure script is run from auth-service directory: %s", str(e))
        sys.exit(1)
    except Exception as e:
        logger.error("Database initialization failed: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()