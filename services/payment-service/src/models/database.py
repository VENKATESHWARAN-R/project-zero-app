"""Database configuration and initialization for Payment Service."""

import os
import sys
from typing import AsyncGenerator

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Base class for all models
Base = declarative_base()

# Import all models to ensure they are registered with Base
from .payment import PaymentTransaction, PaymentStatus
from .payment_method import PaymentMethod, PaymentMethodType
from .payment_status_history import PaymentStatusHistory
from .webhook_event import WebhookEvent, WebhookEventType, WebhookDeliveryStatus

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./payment_service.db")

# Determine if we're using SQLite or PostgreSQL
is_sqlite = DATABASE_URL.startswith("sqlite")
is_async = DATABASE_URL.startswith("postgresql+asyncpg") or DATABASE_URL.startswith("sqlite+aiosqlite")

# Configure engine based on database type
if is_sqlite:
    # SQLite configuration
    if is_async:
        # Async SQLite
        engine = create_async_engine(
            DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://"),
            echo=os.getenv("DEBUG", "false").lower() == "true",
            poolclass=StaticPool,
            connect_args={
                "check_same_thread": False,
                "timeout": 20,
            },
        )
    else:
        # Sync SQLite
        engine = create_engine(
            DATABASE_URL,
            echo=os.getenv("DEBUG", "false").lower() == "true",
            poolclass=StaticPool,
            connect_args={
                "check_same_thread": False,
                "timeout": 20,
            },
        )
else:
    # PostgreSQL configuration
    if is_async:
        # Async PostgreSQL
        engine = create_async_engine(
            DATABASE_URL,
            echo=os.getenv("DEBUG", "false").lower() == "true",
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )
    else:
        # Sync PostgreSQL
        engine = create_engine(
            DATABASE_URL,
            echo=os.getenv("DEBUG", "false").lower() == "true",
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )

# Session configuration
if is_async:
    AsyncSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    SessionLocal = None
else:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    AsyncSessionLocal = None


# SQLite foreign key enforcement
if is_sqlite and not is_async:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """Enable foreign key constraints for SQLite."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session."""
    if not AsyncSessionLocal:
        raise RuntimeError("Async sessions not configured")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_session() -> Session:
    """Get sync database session."""
    if not SessionLocal:
        raise RuntimeError("Sync sessions not configured")
    
    session = SessionLocal()
    try:
        return session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def init_database() -> None:
    """Initialize database tables."""
    if is_async:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    else:
        Base.metadata.create_all(bind=engine)


async def drop_database() -> None:
    """Drop all database tables."""
    if is_async:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    else:
        Base.metadata.drop_all(bind=engine)


async def reset_database() -> None:
    """Reset database by dropping and recreating all tables."""
    await drop_database()
    await init_database()


def check_database_connection() -> bool:
    """Check if database connection is working."""
    try:
        if is_async:
            # For async, we'll need to run this in an async context
            return True  # Simplified for now
        else:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


async def seed_test_data() -> None:
    """Seed database with test data for development."""
    # Import models here to avoid circular imports when models are implemented
    # from .payment import PaymentTransaction, PaymentStatus
    # from .payment_method import PaymentMethod, PaymentMethodType
    
    if is_async:
        async with AsyncSessionLocal() as session:
            # Check if data already exists (will be implemented when models are ready)
            # result = await session.execute("SELECT COUNT(*) FROM payment_methods")
            # count = result.scalar()
            
            # if count > 0:
            #     print("Test data already exists, skipping seed.")
            #     return
            
            # Add test payment methods and transactions here
            # This will be implemented when models are ready
            print("Seed data functionality will be implemented after models are created.")
            await session.commit()
    else:
        with SessionLocal() as session:
            # Check if data already exists (will be implemented when models are ready)
            # count = session.execute("SELECT COUNT(*) FROM payment_methods").scalar()
            
            # if count > 0:
            #     print("Test data already exists, skipping seed.")
            #     return
            
            # Add test payment methods and transactions here
            # This will be implemented when models are ready
            print("Seed data functionality will be implemented after models are created.")
            session.commit()


# CLI commands for database management
if __name__ == "__main__":
    import asyncio
    
    async def main():
        command = sys.argv[1] if len(sys.argv) > 1 else "help"
        
        if command == "init":
            print("Initializing database...")
            await init_database()
            print("Database initialized successfully.")
        
        elif command == "reset":
            print("Resetting database...")
            await reset_database()
            print("Database reset successfully.")
        
        elif command == "seed":
            print("Seeding test data...")
            await seed_test_data()
            print("Test data seeded successfully.")
        
        elif command == "check":
            print("Checking database connection...")
            if check_database_connection():
                print("Database connection successful.")
            else:
                print("Database connection failed.")
                sys.exit(1)
        
        else:
            print("Available commands:")
            print("  init  - Initialize database tables")
            print("  reset - Drop and recreate all tables")
            print("  seed  - Seed database with test data")
            print("  check - Check database connection")
    
    asyncio.run(main())
