from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator
import re


class ProfileCreateRequest(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100, description="User's first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User's last name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number in E.164 format")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    profile_picture_url: Optional[HttpUrl] = Field(None, description="URL to profile picture")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # E.164 format validation
        if not re.match(r'^\+[1-9]\d{1,14}$', v):
            raise ValueError('Phone number must be in E.164 format')
        return v

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Allow alphanumeric characters, spaces, hyphens, apostrophes
        if not re.match(r'^[a-zA-Z0-9\s\-\']+$', v.strip()):
            raise ValueError('Name contains invalid characters')
        return v.strip()

    @field_validator('date_of_birth')
    @classmethod
    def validate_date_of_birth(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return v
        # Check if date is not in the future
        if v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        # Check reasonable age limits (13-120 years old)
        age = (date.today() - v).days / 365.25
        if age < 13 or age > 120:
            raise ValueError('Age must be between 13 and 120 years')
        return v


class ProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100, description="User's first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User's last name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number in E.164 format")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    profile_picture_url: Optional[HttpUrl] = Field(None, description="URL to profile picture")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # E.164 format validation
        if not re.match(r'^\+[1-9]\d{1,14}$', v):
            raise ValueError('Phone number must be in E.164 format')
        return v

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Allow alphanumeric characters, spaces, hyphens, apostrophes
        if not re.match(r'^[a-zA-Z0-9\s\-\']+$', v.strip()):
            raise ValueError('Name contains invalid characters')
        return v.strip()

    @field_validator('date_of_birth')
    @classmethod
    def validate_date_of_birth(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return v
        # Check if date is not in the future
        if v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        # Check reasonable age limits (13-120 years old)
        age = (date.today() - v).days / 365.25
        if age < 13 or age > 120:
            raise ValueError('Age must be between 13 and 120 years')
        return v


class ProfileResponse(BaseModel):
    id: int = Field(..., description="Profile ID")
    user_id: int = Field(..., description="User ID from auth service")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    phone: Optional[str] = Field(None, description="Phone number")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    profile_picture_url: Optional[str] = Field(None, description="URL to profile picture")
    created_at: datetime = Field(..., description="Profile creation timestamp")
    updated_at: datetime = Field(..., description="Profile last update timestamp")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }