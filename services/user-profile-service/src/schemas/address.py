from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


class AddressCreateRequest(BaseModel):
    address_type: str = Field(..., description="Address type: shipping or billing")
    street_address: str = Field(..., max_length=255, description="Street address")
    address_line_2: Optional[str] = Field(None, max_length=255, description="Apartment, suite, etc.")
    city: str = Field(..., max_length=100, description="City name")
    state_province: Optional[str] = Field(None, max_length=100, description="State or province")
    postal_code: str = Field(..., max_length=20, description="Postal/ZIP code")
    country: str = Field(..., description="ISO 3166-1 alpha-2 country code")
    label: Optional[str] = Field(None, max_length=50, description="Address label (e.g., Home, Work)")
    is_default: bool = Field(False, description="Whether this is the default address for its type")

    @field_validator('address_type')
    @classmethod
    def validate_address_type(cls, v: str) -> str:
        if v not in ['shipping', 'billing']:
            raise ValueError('Address type must be either "shipping" or "billing"')
        return v

    @field_validator('country')
    @classmethod
    def validate_country(cls, v: str) -> str:
        # ISO 3166-1 alpha-2 country code validation
        if not re.match(r'^[A-Z]{2}$', v):
            raise ValueError('Country must be a valid ISO 3166-1 alpha-2 code (e.g., US, CA, GB)')
        return v

    @field_validator('city')
    @classmethod
    def validate_city(cls, v: str) -> str:
        # Allow alphanumeric characters, spaces, hyphens, apostrophes
        if not re.match(r'^[a-zA-Z0-9\s\-\'\.]+$', v.strip()):
            raise ValueError('City name contains invalid characters')
        return v.strip()

    @field_validator('state_province')
    @classmethod
    def validate_state_province(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Allow alphanumeric characters, spaces, hyphens
        if not re.match(r'^[a-zA-Z0-9\s\-]+$', v.strip()):
            raise ValueError('State/province contains invalid characters')
        return v.strip()

    @field_validator('label')
    @classmethod
    def validate_label(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Allow alphanumeric characters, spaces, hyphens
        if not re.match(r'^[a-zA-Z0-9\s\-]+$', v.strip()):
            raise ValueError('Label contains invalid characters')
        return v.strip()


class AddressUpdateRequest(BaseModel):
    street_address: Optional[str] = Field(None, max_length=255, description="Street address")
    address_line_2: Optional[str] = Field(None, max_length=255, description="Apartment, suite, etc.")
    city: Optional[str] = Field(None, max_length=100, description="City name")
    state_province: Optional[str] = Field(None, max_length=100, description="State or province")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal/ZIP code")
    country: Optional[str] = Field(None, description="ISO 3166-1 alpha-2 country code")
    label: Optional[str] = Field(None, max_length=50, description="Address label")

    @field_validator('country')
    @classmethod
    def validate_country(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # ISO 3166-1 alpha-2 country code validation
        if not re.match(r'^[A-Z]{2}$', v):
            raise ValueError('Country must be a valid ISO 3166-1 alpha-2 code (e.g., US, CA, GB)')
        return v

    @field_validator('city')
    @classmethod
    def validate_city(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Allow alphanumeric characters, spaces, hyphens, apostrophes
        if not re.match(r'^[a-zA-Z0-9\s\-\'\.]+$', v.strip()):
            raise ValueError('City name contains invalid characters')
        return v.strip()

    @field_validator('state_province')
    @classmethod
    def validate_state_province(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Allow alphanumeric characters, spaces, hyphens
        if not re.match(r'^[a-zA-Z0-9\s\-]+$', v.strip()):
            raise ValueError('State/province contains invalid characters')
        return v.strip()

    @field_validator('label')
    @classmethod
    def validate_label(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Allow alphanumeric characters, spaces, hyphens
        if not re.match(r'^[a-zA-Z0-9\s\-]+$', v.strip()):
            raise ValueError('Label contains invalid characters')
        return v.strip()


class AddressResponse(BaseModel):
    id: int = Field(..., description="Address ID")
    user_id: int = Field(..., description="User ID")
    address_type: str = Field(..., description="Address type")
    street_address: str = Field(..., description="Street address")
    address_line_2: Optional[str] = Field(None, description="Apartment, suite, etc.")
    city: str = Field(..., description="City name")
    state_province: Optional[str] = Field(None, description="State or province")
    postal_code: str = Field(..., description="Postal/ZIP code")
    country: str = Field(..., description="ISO 3166-1 alpha-2 country code")
    label: Optional[str] = Field(None, description="Address label")
    is_default: bool = Field(..., description="Whether this is the default address")
    created_at: datetime = Field(..., description="Address creation timestamp")
    updated_at: datetime = Field(..., description="Address last update timestamp")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }