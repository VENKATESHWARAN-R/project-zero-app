from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from ..models.user_preferences import UserPreferences
from ..schemas.preferences import PreferencesUpdateRequest
from .activity_service import ActivityService


class PreferencesService:
    def __init__(self, db: Session):
        self.db = db
        self.activity_service = ActivityService(db)

    def get_user_preferences(self, user_id: int) -> Optional[UserPreferences]:
        """Get user preferences by user_id."""
        return self.db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()

    def get_or_create_preferences(self, user_id: int) -> UserPreferences:
        """Get existing preferences or create default ones for a user."""
        preferences = self.get_user_preferences(user_id)
        if not preferences:
            preferences = self.create_default_preferences(user_id)
        return preferences

    def create_default_preferences(self, user_id: int) -> UserPreferences:
        """Create default preferences for a user."""
        preferences = UserPreferences(user_id=user_id)

        try:
            self.db.add(preferences)
            self.db.flush()  # Get the ID without committing

            # Log the activity
            self.activity_service.log_activity(
                user_id=user_id,
                activity_type="preferences_created",
                description="Default user preferences created",
                entity_type="preferences",
                entity_id=preferences.id,
                new_values={
                    "email_marketing": preferences.email_marketing,
                    "email_order_updates": preferences.email_order_updates,
                    "email_security_alerts": preferences.email_security_alerts,
                    "sms_notifications": preferences.sms_notifications,
                    "preferred_language": preferences.preferred_language,
                    "preferred_currency": preferences.preferred_currency,
                    "timezone": preferences.timezone,
                    "profile_visibility": preferences.profile_visibility,
                    "data_sharing_consent": preferences.data_sharing_consent
                }
            )

            self.db.commit()
            return preferences

        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to create default preferences: {str(e)}")

    def update_preferences(self, user_id: int, preferences_data: PreferencesUpdateRequest, ip_address: Optional[str] = None, user_agent: Optional[str] = None, correlation_id: Optional[str] = None) -> UserPreferences:
        """Update user preferences."""
        preferences = self.get_or_create_preferences(user_id)

        # Store old values for activity log
        old_values = {
            "email_marketing": preferences.email_marketing,
            "email_order_updates": preferences.email_order_updates,
            "email_security_alerts": preferences.email_security_alerts,
            "sms_notifications": preferences.sms_notifications,
            "preferred_language": preferences.preferred_language,
            "preferred_currency": preferences.preferred_currency,
            "timezone": preferences.timezone,
            "profile_visibility": preferences.profile_visibility,
            "data_sharing_consent": preferences.data_sharing_consent
        }

        # Track what changed for the activity log
        changed_fields = []

        # Update fields only if provided
        if preferences_data.email_marketing is not None:
            if preferences.email_marketing != preferences_data.email_marketing:
                changed_fields.append("email_marketing")
            preferences.email_marketing = preferences_data.email_marketing

        if preferences_data.email_order_updates is not None:
            if preferences.email_order_updates != preferences_data.email_order_updates:
                changed_fields.append("email_order_updates")
            preferences.email_order_updates = preferences_data.email_order_updates

        if preferences_data.email_security_alerts is not None:
            if preferences.email_security_alerts != preferences_data.email_security_alerts:
                changed_fields.append("email_security_alerts")
            preferences.email_security_alerts = preferences_data.email_security_alerts

        if preferences_data.sms_notifications is not None:
            if preferences.sms_notifications != preferences_data.sms_notifications:
                changed_fields.append("sms_notifications")
            preferences.sms_notifications = preferences_data.sms_notifications

        if preferences_data.preferred_language is not None:
            if preferences.preferred_language != preferences_data.preferred_language:
                changed_fields.append("preferred_language")
            preferences.preferred_language = preferences_data.preferred_language

        if preferences_data.preferred_currency is not None:
            if preferences.preferred_currency != preferences_data.preferred_currency:
                changed_fields.append("preferred_currency")
            preferences.preferred_currency = preferences_data.preferred_currency

        if preferences_data.timezone is not None:
            if preferences.timezone != preferences_data.timezone:
                changed_fields.append("timezone")
            preferences.timezone = preferences_data.timezone

        if preferences_data.profile_visibility is not None:
            if preferences.profile_visibility != preferences_data.profile_visibility:
                changed_fields.append("profile_visibility")
            preferences.profile_visibility = preferences_data.profile_visibility

        if preferences_data.data_sharing_consent is not None:
            if preferences.data_sharing_consent != preferences_data.data_sharing_consent:
                changed_fields.append("data_sharing_consent")
            preferences.data_sharing_consent = preferences_data.data_sharing_consent

        preferences.updated_at = datetime.utcnow()

        # Store new values for activity log
        new_values = {
            "email_marketing": preferences.email_marketing,
            "email_order_updates": preferences.email_order_updates,
            "email_security_alerts": preferences.email_security_alerts,
            "sms_notifications": preferences.sms_notifications,
            "preferred_language": preferences.preferred_language,
            "preferred_currency": preferences.preferred_currency,
            "timezone": preferences.timezone,
            "profile_visibility": preferences.profile_visibility,
            "data_sharing_consent": preferences.data_sharing_consent
        }

        try:
            # Log the activity only if something changed
            if changed_fields:
                activity_type = "notification_settings_changed" if any(field.startswith('email_') or field == 'sms_notifications' for field in changed_fields) else "preferences_updated"
                if "profile_visibility" in changed_fields or "data_sharing_consent" in changed_fields:
                    activity_type = "privacy_settings_changed"

                self.activity_service.log_activity(
                    user_id=user_id,
                    activity_type=activity_type,
                    description=f"User preferences updated: {', '.join(changed_fields)}",
                    entity_type="preferences",
                    entity_id=preferences.id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    correlation_id=correlation_id,
                    old_values=old_values,
                    new_values=new_values
                )

            self.db.commit()
            return preferences

        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to update preferences: {str(e)}")

    def reset_preferences_to_default(self, user_id: int, ip_address: Optional[str] = None, user_agent: Optional[str] = None, correlation_id: Optional[str] = None) -> UserPreferences:
        """Reset user preferences to default values."""
        preferences = self.get_user_preferences(user_id)
        if not preferences:
            return self.create_default_preferences(user_id)

        # Store old values for activity log
        old_values = {
            "email_marketing": preferences.email_marketing,
            "email_order_updates": preferences.email_order_updates,
            "email_security_alerts": preferences.email_security_alerts,
            "sms_notifications": preferences.sms_notifications,
            "preferred_language": preferences.preferred_language,
            "preferred_currency": preferences.preferred_currency,
            "timezone": preferences.timezone,
            "profile_visibility": preferences.profile_visibility,
            "data_sharing_consent": preferences.data_sharing_consent
        }

        # Reset to defaults (match UserPreferences model defaults)
        preferences.email_marketing = True
        preferences.email_order_updates = True
        preferences.email_security_alerts = True
        preferences.sms_notifications = False
        preferences.preferred_language = "en-US"
        preferences.preferred_currency = "USD"
        preferences.timezone = "UTC"
        preferences.profile_visibility = "private"
        preferences.data_sharing_consent = False
        preferences.updated_at = datetime.utcnow()

        new_values = {
            "email_marketing": preferences.email_marketing,
            "email_order_updates": preferences.email_order_updates,
            "email_security_alerts": preferences.email_security_alerts,
            "sms_notifications": preferences.sms_notifications,
            "preferred_language": preferences.preferred_language,
            "preferred_currency": preferences.preferred_currency,
            "timezone": preferences.timezone,
            "profile_visibility": preferences.profile_visibility,
            "data_sharing_consent": preferences.data_sharing_consent
        }

        try:
            # Log the activity
            self.activity_service.log_activity(
                user_id=user_id,
                activity_type="preferences_reset",
                description="User preferences reset to default values",
                entity_type="preferences",
                entity_id=preferences.id,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                old_values=old_values,
                new_values=new_values
            )

            self.db.commit()
            return preferences

        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to reset preferences: {str(e)}")