"""UserProfile database model.

This module defines the SQLAlchemy model for user profiles,
following the data model specification.
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .address import Address
    from .activity_log import ActivityLog
    from .user_preferences import UserPreferences


class UserProfile(Base):
    """User profile model containing personal information and preferences.

    Attributes:
        id: Primary key
        user_id: Links to auth service user (unique)
        first_name: User's first name (optional)
        last_name: User's last name (optional)
        phone: Phone number in E.164 format (optional)
        date_of_birth: Date of birth (optional)
        profile_picture_url: URL to profile picture (optional)
        created_at: Timestamp when profile was created
        updated_at: Timestamp when profile was last updated

    Relationships:
        addresses: One-to-many relationship with Address
        preferences: One-to-one relationship with UserPreferences
        activity_logs: One-to-many relationship with ActivityLog
    """

    __tablename__ = "user_profiles"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key to auth service user
    user_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)

    # Personal information (all optional)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False), nullable=True)
    profile_picture_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    addresses: Mapped[List["Address"]] = relationship(
        "Address",
        back_populates="user_profile",
        cascade="all, delete-orphan"
    )

    preferences: Mapped[Optional["UserPreferences"]] = relationship(
        "UserPreferences",
        back_populates="user_profile",
        uselist=False,
        cascade="all, delete-orphan"
    )

    activity_logs: Mapped[List["ActivityLog"]] = relationship(
        "ActivityLog",
        back_populates="user_profile",
        cascade="all, delete-orphan",
        order_by="ActivityLog.created_at.desc()"
    )

    def __repr__(self) -> str:
        """String representation of the UserProfile."""
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, name='{self.first_name} {self.last_name}')>"

    def get_full_name(self) -> Optional[str]:
        """Get the full name of the user."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return None

    def is_profile_complete(self) -> bool:
        """Check if the profile has all basic information filled out."""
        return bool(
            self.first_name and
            self.last_name and
            self.phone
        )

    def to_dict(self) -> dict:
        """Convert the profile to a dictionary representation."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "profile_picture_url": self.profile_picture_url,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }