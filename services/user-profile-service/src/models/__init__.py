"""Database models package.

This package contains all SQLAlchemy models for the user profile service.
Import all models here to ensure they are registered with SQLAlchemy.
"""

from .activity_log import ActivityLog
from .address import Address
from .base import Base
from .user_preferences import UserPreferences
from .user_profile import UserProfile

# Export all models for easy imports
__all__ = [
    "Base",
    "UserProfile",
    "Address",
    "UserPreferences",
    "ActivityLog",
]