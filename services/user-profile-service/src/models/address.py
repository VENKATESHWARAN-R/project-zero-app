"""Address database model.

This module defines the SQLAlchemy model for user addresses,
supporting both shipping and billing addresses with default management.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Literal, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user_profile import UserProfile

AddressType = Literal["shipping", "billing"]


class Address(Base):
    """Address model for shipping and billing addresses.

    Attributes:
        id: Primary key
        user_id: Foreign key to user_profiles.user_id
        address_type: Type of address ('shipping' or 'billing')
        street_address: Street address line 1
        address_line_2: Street address line 2 (optional)
        city: City name
        state_province: State or province (optional)
        postal_code: Postal/ZIP code
        country: ISO 3166-1 alpha-2 country code
        label: Human-readable label (e.g., 'Home', 'Work')
        is_default: Whether this is the default address for this type
        created_at: Timestamp when address was created
        updated_at: Timestamp when address was last updated

    Relationships:
        user_profile: Many-to-one relationship with UserProfile
    """

    __tablename__ = "addresses"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key to user profile
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Address information
    address_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    street_address: Mapped[str] = mapped_column(Text, nullable=False)
    address_line_2: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state_province: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)  # ISO 3166-1 alpha-2

    # Address metadata
    label: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

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
        back_populates="addresses"
    )

    def __repr__(self) -> str:
        """String representation of the Address."""
        return f"<Address(id={self.id}, type={self.address_type}, city={self.city}, default={self.is_default})>"

    def get_formatted_address(self) -> str:
        """Get a formatted address string for display."""
        lines = [self.street_address]

        if self.address_line_2:
            lines.append(self.address_line_2)

        # City, State/Province Postal Code
        city_line = self.city
        if self.state_province:
            city_line += f", {self.state_province}"
        city_line += f" {self.postal_code}"
        lines.append(city_line)

        # Country (if not US, show country name)
        if self.country != "US":
            lines.append(self.get_country_name())

        return "\n".join(lines)

    def get_country_name(self) -> str:
        """Get the full country name from the country code."""
        # Basic country code mapping - could be expanded
        country_names = {
            "US": "United States",
            "CA": "Canada",
            "GB": "United Kingdom",
            "FR": "France",
            "DE": "Germany",
            "JP": "Japan",
            "AU": "Australia",
        }
        return country_names.get(self.country, self.country)

    def is_valid_address_type(self) -> bool:
        """Validate that the address type is valid."""
        return self.address_type in ["shipping", "billing"]

    def is_valid_country_code(self) -> bool:
        """Validate that the country code is a valid ISO 3166-1 alpha-2 code."""
        # Basic validation - could be expanded with full ISO list
        valid_countries = {
            "US", "CA", "GB", "FR", "DE", "JP", "AU", "IT", "ES", "NL",
            "SE", "NO", "DK", "FI", "BE", "CH", "AT", "IE", "PT", "GR",
            "CZ", "PL", "HU", "SK", "SI", "HR", "EE", "LV", "LT", "MT",
            "CY", "LU", "BG", "RO", "MX", "BR", "AR", "CL", "CO", "PE",
            "CN", "IN", "KR", "TH", "SG", "MY", "ID", "PH", "VN", "TW",
            "HK", "MO", "NZ", "ZA", "EG", "IL", "TR", "RU", "UA", "BY"
        }
        return self.country in valid_countries

    def to_dict(self) -> dict:
        """Convert the address to a dictionary representation."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "address_type": self.address_type,
            "street_address": self.street_address,
            "address_line_2": self.address_line_2,
            "city": self.city,
            "state_province": self.state_province,
            "postal_code": self.postal_code,
            "country": self.country,
            "label": self.label,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }