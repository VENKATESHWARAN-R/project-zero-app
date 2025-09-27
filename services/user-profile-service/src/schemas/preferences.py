from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


class PreferencesUpdateRequest(BaseModel):
    email_marketing: Optional[bool] = Field(None, description="Enable marketing emails")
    email_order_updates: Optional[bool] = Field(None, description="Enable order update emails")
    email_security_alerts: Optional[bool] = Field(None, description="Enable security alert emails")
    sms_notifications: Optional[bool] = Field(None, description="Enable SMS notifications")
    preferred_language: Optional[str] = Field(None, description="Preferred language (ISO 639-1 + ISO 3166-1)")
    preferred_currency: Optional[str] = Field(None, description="Preferred currency (ISO 4217)")
    timezone: Optional[str] = Field(None, description="Preferred timezone (IANA format)")
    profile_visibility: Optional[str] = Field(None, description="Profile visibility setting")
    data_sharing_consent: Optional[bool] = Field(None, description="Data sharing consent")

    @field_validator('preferred_language')
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Validate locale format: language-COUNTRY (e.g., en-US, fr-CA)
        if not re.match(r'^[a-z]{2}-[A-Z]{2}$', v):
            raise ValueError('Language must be in format "xx-XX" (e.g., en-US, fr-CA)')
        # Check if it's a commonly supported locale
        supported_locales = {
            'en-US', 'en-GB', 'en-CA', 'en-AU',
            'es-ES', 'es-MX', 'es-US',
            'fr-FR', 'fr-CA',
            'de-DE', 'de-AT', 'de-CH',
            'it-IT', 'pt-BR', 'pt-PT',
            'nl-NL', 'sv-SE', 'da-DK',
            'no-NO', 'fi-FI', 'pl-PL',
            'ru-RU', 'zh-CN', 'zh-TW',
            'ja-JP', 'ko-KR', 'ar-SA'
        }
        if v not in supported_locales:
            raise ValueError(f'Language "{v}" is not supported')
        return v

    @field_validator('preferred_currency')
    @classmethod
    def validate_currency(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Validate ISO 4217 currency code format
        if not re.match(r'^[A-Z]{3}$', v):
            raise ValueError('Currency must be a valid ISO 4217 code (e.g., USD, EUR, GBP)')
        # Check if it's a commonly supported currency
        supported_currencies = {
            'USD', 'EUR', 'GBP', 'CAD', 'AUD',
            'JPY', 'CHF', 'SEK', 'NOK', 'DKK',
            'PLN', 'CZK', 'HUF', 'RUB', 'CNY',
            'KRW', 'INR', 'BRL', 'MXN', 'SGD',
            'HKD', 'NZD', 'ZAR', 'THB', 'MYR'
        }
        if v not in supported_currencies:
            raise ValueError(f'Currency "{v}" is not supported')
        return v

    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Basic IANA timezone format validation
        if not re.match(r'^[A-Za-z]+/[A-Za-z_]+(?:/[A-Za-z_]+)?$', v) and v != 'UTC':
            raise ValueError('Timezone must be a valid IANA timezone identifier (e.g., America/New_York, Europe/London, UTC)')
        # Check if it's a commonly supported timezone
        supported_timezones = {
            'UTC', 'America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles',
            'America/Toronto', 'America/Vancouver', 'America/Mexico_City', 'America/Sao_Paulo',
            'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Europe/Rome', 'Europe/Madrid',
            'Europe/Amsterdam', 'Europe/Stockholm', 'Europe/Copenhagen', 'Europe/Oslo',
            'Europe/Helsinki', 'Europe/Warsaw', 'Europe/Prague', 'Europe/Budapest',
            'Europe/Moscow', 'Asia/Tokyo', 'Asia/Seoul', 'Asia/Shanghai', 'Asia/Hong_Kong',
            'Asia/Singapore', 'Asia/Mumbai', 'Asia/Dubai', 'Australia/Sydney', 'Australia/Melbourne',
            'Pacific/Auckland', 'Africa/Johannesburg', 'Africa/Cairo'
        }
        if v not in supported_timezones:
            raise ValueError(f'Timezone "{v}" is not supported')
        return v

    @field_validator('profile_visibility')
    @classmethod
    def validate_visibility(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if v not in ['public', 'private']:
            raise ValueError('Profile visibility must be either "public" or "private"')
        return v


class PreferencesResponse(BaseModel):
    id: int = Field(..., description="Preferences ID")
    user_id: int = Field(..., description="User ID")
    email_marketing: bool = Field(..., description="Marketing email preference")
    email_order_updates: bool = Field(..., description="Order update email preference")
    email_security_alerts: bool = Field(..., description="Security alert email preference")
    sms_notifications: bool = Field(..., description="SMS notification preference")
    preferred_language: str = Field(..., description="Preferred language")
    preferred_currency: str = Field(..., description="Preferred currency")
    timezone: str = Field(..., description="Preferred timezone")
    profile_visibility: str = Field(..., description="Profile visibility setting")
    data_sharing_consent: bool = Field(..., description="Data sharing consent")
    created_at: datetime = Field(..., description="Preferences creation timestamp")
    updated_at: datetime = Field(..., description="Preferences last update timestamp")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }