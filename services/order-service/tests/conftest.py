"""Test configuration and fixtures for the order service."""

import asyncio
import pytest
import pytest_asyncio
from decimal import Decimal
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from src.database import Base, get_db
from src.config import Settings
from src.models import Order, OrderItem, ShippingAddress, OrderModification, OrderStatus
from main import app


# Test database configuration
TEST_DATABASE_URL = "sqlite:///./test_order_service.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_db_engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def test_client(test_db_session):
    """Create a test client with overridden database dependency."""

    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass  # Session is managed by test_db_session fixture

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_test_client(test_db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with overridden database dependency."""

    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()


# Test data fixtures
@pytest.fixture
def sample_order_data():
    """Sample order creation data."""
    return {
        "shipping_address": {
            "recipient_name": "John Doe",
            "address_line_1": "123 Main Street",
            "address_line_2": "Apt 4B",
            "city": "San Francisco",
            "state_province": "CA",
            "postal_code": "94105",
            "country": "US",
            "phone": "+1-555-123-4567"
        },
        "notes": "Please leave at front door"
    }


@pytest.fixture
def sample_shipping_calculation_data():
    """Sample shipping calculation data."""
    return {
        "items": [
            {"weight": 0.5, "quantity": 2},
            {"weight": 1.2, "quantity": 1}
        ],
        "address": {
            "recipient_name": "John Doe",
            "address_line_1": "123 Main Street",
            "city": "San Francisco",
            "state_province": "CA",
            "postal_code": "94105",
            "country": "US"
        }
    }


@pytest.fixture
def sample_order_modification_data():
    """Sample order modification data."""
    return {
        "shipping_address": {
            "recipient_name": "Jane Doe",
            "address_line_1": "456 Oak Avenue",
            "city": "Oakland",
            "state_province": "CA",
            "postal_code": "94601",
            "country": "US",
            "phone": "+1-555-987-6543"
        }
    }


@pytest.fixture
def sample_status_update_data():
    """Sample status update data."""
    return {
        "status": "CONFIRMED",
        "notes": "Payment processed successfully"
    }


@pytest.fixture
def created_order(test_db_session: Session):
    """Create a sample order in the database for testing."""
    # Create order
    order = Order(
        user_id=42,
        order_number="TEST-ORD-001",
        status=OrderStatus.PENDING,
        subtotal=Decimal("89.97"),
        tax_rate=Decimal("0.085"),
        tax_amount=Decimal("7.65"),
        shipping_cost=Decimal("8.99"),
        total=Decimal("106.61"),
        notes="Test order"
    )
    test_db_session.add(order)
    test_db_session.flush()  # Get the ID

    # Create order items
    item1 = OrderItem(
        order_id=order.id,
        product_id=2,
        product_name="Test Product 1",
        product_sku="TEST-001",
        quantity=2,
        unit_price=Decimal("29.99"),
        total_price=Decimal("59.98"),
        weight=Decimal("0.5")
    )
    item2 = OrderItem(
        order_id=order.id,
        product_id=3,
        product_name="Test Product 2",
        product_sku="TEST-002",
        quantity=1,
        unit_price=Decimal("29.99"),
        total_price=Decimal("29.99"),
        weight=Decimal("1.2")
    )
    test_db_session.add_all([item1, item2])

    # Create shipping address
    shipping_address = ShippingAddress(
        order_id=order.id,
        recipient_name="John Doe",
        address_line_1="123 Main Street",
        address_line_2="Apt 4B",
        city="San Francisco",
        state_province="CA",
        postal_code="94105",
        country="US",
        phone="+1-555-123-4567"
    )
    test_db_session.add(shipping_address)

    test_db_session.commit()
    return order


@pytest.fixture
def mock_jwt_token():
    """Mock JWT token for authentication testing."""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo0MiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwicm9sZSI6InVzZXIiLCJleHAiOjk5OTk5OTk5OTl9.mock_signature"


@pytest.fixture
def mock_admin_jwt_token():
    """Mock admin JWT token for admin endpoint testing."""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6ImFkbWluQGV4YW1wbGUuY29tIiwicm9sZSI6ImFkbWluIiwiZXhwIjo5OTk5OTk5OTk5fQ.mock_admin_signature"


# Mock external service responses
@pytest.fixture
def mock_cart_response():
    """Mock cart service response."""
    return {
        "user_id": 42,
        "items": [
            {
                "product_id": 2,
                "quantity": 2,
                "product": {
                    "id": 2,
                    "name": "Test Product 1",
                    "sku": "TEST-001",
                    "price": 29.99,
                    "weight": 0.5
                }
            },
            {
                "product_id": 3,
                "quantity": 1,
                "product": {
                    "id": 3,
                    "name": "Test Product 2",
                    "sku": "TEST-002",
                    "price": 29.99,
                    "weight": 1.2
                }
            }
        ],
        "subtotal": 89.97
    }


@pytest.fixture
def mock_empty_cart_response():
    """Mock empty cart service response."""
    return {
        "user_id": 42,
        "items": [],
        "subtotal": 0.0
    }