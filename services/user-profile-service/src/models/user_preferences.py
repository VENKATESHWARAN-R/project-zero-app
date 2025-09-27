"""UserPreferences database model.

This module defines the SQLAlchemy model for user preferences,
including notification, language, and privacy settings.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Literal, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user_profile import UserProfile

ProfileVisibility = Literal["public", "private"]


class UserPreferences(Base):
    """User preferences model for notification, communication, and account settings.

    Attributes:
        id: Primary key
        user_id: Foreign key to user_profiles.user_id (unique)
        email_marketing: Email marketing notifications enabled
        email_order_updates: Email order update notifications enabled
        email_security_alerts: Email security alert notifications enabled
        sms_notifications: SMS notifications enabled
        preferred_language: ISO 639-1 + ISO 3166-1 language code
        preferred_currency: ISO 4217 currency code
        timezone: IANA timezone identifier
        profile_visibility: Profile visibility setting
        data_sharing_consent: Data sharing consent flag
        created_at: Timestamp when preferences were created
        updated_at: Timestamp when preferences were last updated

    Relationships:
        user_profile: One-to-one relationship with UserProfile
    """

    __tablename__ = "user_preferences"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key to user profile (unique for one-to-one relationship)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )

    # Notification preferences
    email_marketing: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    email_order_updates: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    email_security_alerts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sms_notifications: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Account preferences
    preferred_language: Mapped[str] = mapped_column(String(5), default="en-US", nullable=False)
    preferred_currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)

    # Privacy settings
    profile_visibility: Mapped[str] = mapped_column(String(20), default="private", nullable=False)
    data_sharing_consent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    user_profile: Mapped["UserProfile"] = relationship(
        "UserProfile",
        back_populates="preferences"
    )

    def __repr__(self) -> str:
        """String representation of the UserPreferences."""
        return f"<UserPreferences(id={self.id}, user_id={self.user_id}, language={self.preferred_language})>"

    def is_valid_language_code(self) -> bool:
        """Validate that the language code follows ISO 639-1 + ISO 3166-1 format."""
        # Basic validation for language-country format
        if len(self.preferred_language) != 5:
            return False

        parts = self.preferred_language.split("-")
        if len(parts) != 2:
            return False

        language_code, country_code = parts
        if len(language_code) != 2 or len(country_code) != 2:
            return False

        # Basic validation - could be expanded with full ISO lists
        valid_languages = {
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh",
            "ar", "hi", "th", "vi", "tr", "pl", "nl", "sv", "da", "no",
            "fi", "cs", "hu", "he", "id", "ms", "tl", "uk", "bg", "hr"
        }

        valid_countries = {
            "US", "CA", "GB", "FR", "DE", "JP", "AU", "IT", "ES", "NL",
            "SE", "NO", "DK", "FI", "BE", "CH", "AT", "IE", "PT", "GR",
            "CZ", "PL", "HU", "SK", "SI", "HR", "EE", "LV", "LT", "MT",
            "CY", "LU", "BG", "RO", "MX", "BR", "AR", "CL", "CO", "PE",
            "CN", "IN", "KR", "TH", "SG", "MY", "ID", "PH", "VN", "TW"
        }

        return language_code.lower() in valid_languages and country_code.upper() in valid_countries

    def is_valid_currency_code(self) -> bool:
        """Validate that the currency code is a valid ISO 4217 code."""
        # Basic validation for common currencies
        valid_currencies = {
            "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY",
            "SEK", "NOK", "DKK", "PLN", "CZK", "HUF", "RON", "BGN",
            "HRK", "RUB", "TRY", "ZAR", "BRL", "MXN", "INR", "KRW",
            "THB", "SGD", "MYR", "IDR", "PHP", "VND", "TWD", "HKD",
            "NZD", "ILS", "AED", "SAR", "EGP", "QAR", "KWD", "BHD"
        }
        return self.preferred_currency in valid_currencies

    def is_valid_timezone(self) -> bool:
        """Validate that the timezone is a valid IANA timezone identifier."""
        # Basic validation - could be expanded with full IANA list
        valid_timezones = {
            "UTC",
            "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles",
            "America/Toronto", "America/Vancouver", "America/Mexico_City", "America/Sao_Paulo",
            "Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Rome", "Europe/Madrid",
            "Europe/Amsterdam", "Europe/Stockholm", "Europe/Oslo", "Europe/Helsinki",
            "Europe/Warsaw", "Europe/Prague", "Europe/Budapest", "Europe/Bucharest",
            "Asia/Tokyo", "Asia/Seoul", "Asia/Shanghai", "Asia/Hong_Kong", "Asia/Singapore",
            "Asia/Bangkok", "Asia/Jakarta", "Asia/Manila", "Asia/Kolkata", "Asia/Dubai",
            "Australia/Sydney", "Australia/Melbourne", "Australia/Perth",
            "Pacific/Auckland", "Africa/Johannesburg", "Africa/Cairo"
        }
        return self.timezone in valid_timezones

    def is_valid_profile_visibility(self) -> bool:
        """Validate that the profile visibility is a valid option."""
        return self.profile_visibility in ["public", "private"]

    def get_notification_summary(self) -> dict:
        """Get a summary of notification preferences."""
        return {
            "email_enabled": any([
                self.email_marketing,
                self.email_order_updates,
                self.email_security_alerts
            ]),
            "sms_enabled": self.sms_notifications,
            "marketing_enabled": self.email_marketing,
            "order_updates_enabled": self.email_order_updates,
            "security_alerts_enabled": self.email_security_alerts
        }

    def to_dict(self) -> dict:
        """Convert the preferences to a dictionary representation."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "email_marketing": self.email_marketing,
            "email_order_updates": self.email_order_updates,
            "email_security_alerts": self.email_security_alerts,
            "sms_notifications": self.sms_notifications,
            "preferred_language": self.preferred_language,
            "preferred_currency": self.preferred_currency,
            "timezone": self.timezone,
            "profile_visibility": self.profile_visibility,
            "data_sharing_consent": self.data_sharing_consent,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }