"""ActivityLog database model.

This module defines the SQLAlchemy model for activity logging,
providing an audit trail of significant account activities.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user_profile import UserProfile


class ActivityLog(Base):
    """Activity log model for audit trail of significant account activities.

    Attributes:
        id: Primary key
        user_id: Foreign key to user_profiles.user_id
        activity_type: Type of activity (predefined enum)
        description: Human-readable description of the activity
        entity_type: Type of entity affected (e.g., 'profile', 'address')
        entity_id: ID of the affected entity
        ip_address: IP address where the activity originated
        user_agent: User agent string from the request
        correlation_id: Request correlation ID for tracing
        old_values: Previous values (JSON) for change tracking
        new_values: New values (JSON) for change tracking
        created_at: Timestamp when activity occurred

    Relationships:
        user_profile: Many-to-one relationship with UserProfile
    """

    __tablename__ = "activity_logs"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key to user profile
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Activity information
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    # Request context
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv6 support
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)  # UUID v4

    # Change details (JSON)
    old_values: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    new_values: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Audit field
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # Relationships
    user_profile: Mapped["UserProfile"] = relationship(
        "UserProfile",
        back_populates="activity_logs"
    )

    def __repr__(self) -> str:
        """String representation of the ActivityLog."""
        return f"<ActivityLog(id={self.id}, type={self.activity_type}, user_id={self.user_id})>"

    def is_valid_activity_type(self) -> bool:
        """Validate that the activity type is from the predefined set."""
        valid_activity_types = {
            # Profile activities
            "profile_created",
            "profile_updated",
            "profile_viewed",

            # Address activities
            "address_created",
            "address_updated",
            "address_deleted",
            "address_default_changed",

            # Preference activities
            "preferences_updated",
            "notification_settings_changed",
            "privacy_settings_changed",

            # Authentication activities
            "profile_access_denied",
            "admin_access",
        }
        return self.activity_type in valid_activity_types

    def is_valid_entity_type(self) -> bool:
        """Validate that the entity type is valid."""
        if self.entity_type is None:
            return True  # Entity type is optional

        valid_entity_types = {"profile", "address", "preferences"}
        return self.entity_type in valid_entity_types

    def get_activity_summary(self) -> str:
        """Get a concise summary of the activity."""
        if self.entity_type and self.entity_id:
            return f"{self.activity_type} on {self.entity_type} {self.entity_id}"
        return self.activity_type

    def has_changes(self) -> bool:
        """Check if the activity represents a change (has old/new values)."""
        return self.old_values is not None or self.new_values is not None

    def get_changed_fields(self) -> set:
        """Get the set of fields that were changed."""
        if not self.has_changes():
            return set()

        old_keys = set(self.old_values.keys()) if self.old_values else set()
        new_keys = set(self.new_values.keys()) if self.new_values else set()

        return old_keys.union(new_keys)

    def get_field_change(self, field_name: str) -> Optional[dict]:
        """Get the before/after values for a specific field."""
        if not self.has_changes():
            return None

        old_value = self.old_values.get(field_name) if self.old_values else None
        new_value = self.new_values.get(field_name) if self.new_values else None

        if old_value is None and new_value is None:
            return None

        return {
            "field": field_name,
            "old_value": old_value,
            "new_value": new_value,
            "changed": old_value != new_value
        }

    def sanitize_sensitive_data(self) -> None:
        """Remove sensitive data from old_values and new_values."""
        sensitive_fields = {
            "password", "password_hash", "api_key", "secret", "token",
            "ssn", "credit_card", "bank_account", "private_key"
        }

        def sanitize_dict(data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
            if not data:
                return data

            sanitized = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in sensitive_fields):
                    sanitized[key] = "[REDACTED]"
                else:
                    sanitized[key] = value
            return sanitized

        self.old_values = sanitize_dict(self.old_values)
        self.new_values = sanitize_dict(self.new_values)

    def to_dict(self) -> dict:
        """Convert the activity log to a dictionary representation."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "activity_type": self.activity_type,
            "description": self.description,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "created_at": self.created_at.isoformat(),
            # Note: Sensitive fields like IP, user agent, and change details
            # are not included in the public dict representation
        }