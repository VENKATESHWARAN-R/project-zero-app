"""Product model using SQLAlchemy."""

from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import VARCHAR, TypeDecorator

Base = declarative_base()


class CategoryEnum(Enum):
    """Product category enumeration."""

    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    BOOKS = "books"
    HOME_GOODS = "home_goods"


class SQLiteEnum(TypeDecorator):
    """SQLite-compatible enum column type."""

    impl = VARCHAR
    cache_ok = True

    def __init__(self, enum_class, **kwargs):
        self.enum_class = enum_class
        super().__init__(**kwargs)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, self.enum_class):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.enum_class(value)


class Product(Base):
    """Product model representing items in the catalog."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(SQLiteEnum(CategoryEnum), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', category='{self.category.value}')>"

    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": float(self.price),
            "category": self.category.value,
            "image_url": self.image_url,
            "stock_quantity": self.stock_quantity,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() + "Z",
            "updated_at": self.updated_at.isoformat() + "Z",
        }
