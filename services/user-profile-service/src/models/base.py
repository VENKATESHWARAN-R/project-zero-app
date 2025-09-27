"""Base model configuration.

This module provides the base SQLAlchemy declarative base
and common model configuration.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models.

    This class provides the declarative base for all models
    and can be extended with common functionality.
    """

    pass