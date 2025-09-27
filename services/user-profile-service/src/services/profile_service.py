from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..models.user_profile import UserProfile
from ..models.user_preferences import UserPreferences
from ..schemas.profile import ProfileCreateRequest, ProfileUpdateRequest, ProfileResponse
from .activity_service import ActivityService


class ProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.activity_service = ActivityService(db)

    def get_profile_by_user_id(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile by user_id."""
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    def create_profile(self, user_id: int, profile_data: ProfileCreateRequest, ip_address: Optional[str] = None, user_agent: Optional[str] = None, correlation_id: Optional[str] = None) -> UserProfile:
        """Create a new user profile."""
        # Check if profile already exists
        existing_profile = self.get_profile_by_user_id(user_id)
        if existing_profile:
            raise ValueError(f"Profile already exists for user_id {user_id}")

        # Create new profile
        profile = UserProfile(
            user_id=user_id,
            first_name=profile_data.first_name,
            last_name=profile_data.last_name,
            phone=profile_data.phone,
            date_of_birth=profile_data.date_of_birth,
            profile_picture_url=str(profile_data.profile_picture_url) if profile_data.profile_picture_url else None
        )

        try:
            self.db.add(profile)
            self.db.flush()  # Get the ID without committing

            # Create default preferences for the user
            preferences = UserPreferences(user_id=user_id)
            self.db.add(preferences)

            # Log the activity
            self.activity_service.log_activity(
                user_id=user_id,
                activity_type="profile_created",
                description="User profile created",
                entity_type="profile",
                entity_id=profile.id,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                new_values={
                    "first_name": profile_data.first_name,
                    "last_name": profile_data.last_name,
                    "phone": profile_data.phone,
                    "date_of_birth": profile_data.date_of_birth.isoformat() if profile_data.date_of_birth else None,
                    "profile_picture_url": str(profile_data.profile_picture_url) if profile_data.profile_picture_url else None
                }
            )

            self.db.commit()
            return profile

        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to create profile: {str(e)}")

    def update_profile(self, user_id: int, profile_data: ProfileUpdateRequest, ip_address: Optional[str] = None, user_agent: Optional[str] = None, correlation_id: Optional[str] = None) -> Optional[UserProfile]:
        """Update an existing user profile."""
        profile = self.get_profile_by_user_id(user_id)
        if not profile:
            return None

        # Store old values for activity log
        old_values = {
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "phone": profile.phone,
            "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
            "profile_picture_url": profile.profile_picture_url
        }

        # Update fields only if provided
        if profile_data.first_name is not None:
            profile.first_name = profile_data.first_name
        if profile_data.last_name is not None:
            profile.last_name = profile_data.last_name
        if profile_data.phone is not None:
            profile.phone = profile_data.phone
        if profile_data.date_of_birth is not None:
            profile.date_of_birth = profile_data.date_of_birth
        if profile_data.profile_picture_url is not None:
            profile.profile_picture_url = str(profile_data.profile_picture_url)

        profile.updated_at = datetime.utcnow()

        # Store new values for activity log
        new_values = {
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "phone": profile.phone,
            "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
            "profile_picture_url": profile.profile_picture_url
        }

        try:
            # Log the activity
            self.activity_service.log_activity(
                user_id=user_id,
                activity_type="profile_updated",
                description="User profile updated",
                entity_type="profile",
                entity_id=profile.id,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                old_values=old_values,
                new_values=new_values
            )

            self.db.commit()
            return profile

        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to update profile: {str(e)}")

    def delete_profile(self, user_id: int, ip_address: Optional[str] = None, user_agent: Optional[str] = None, correlation_id: Optional[str] = None) -> bool:
        """Delete a user profile and all associated data."""
        profile = self.get_profile_by_user_id(user_id)
        if not profile:
            return False

        try:
            # Log the activity before deletion
            self.activity_service.log_activity(
                user_id=user_id,
                activity_type="profile_deleted",
                description="User profile deleted",
                entity_type="profile",
                entity_id=profile.id,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                old_values={
                    "first_name": profile.first_name,
                    "last_name": profile.last_name,
                    "phone": profile.phone,
                    "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
                    "profile_picture_url": profile.profile_picture_url
                }
            )

            # Delete the profile (cascade will handle related data)
            self.db.delete(profile)
            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to delete profile: {str(e)}")

    def get_profile_completion_status(self, user_id: int) -> dict:
        """Get profile completion status and missing fields."""
        profile = self.get_profile_by_user_id(user_id)
        if not profile:
            return {"complete": False, "missing_fields": ["profile does not exist"]}

        required_fields = ["first_name", "last_name"]
        missing_fields = []

        for field in required_fields:
            value = getattr(profile, field)
            if not value or (isinstance(value, str) and not value.strip()):
                missing_fields.append(field)

        return {
            "complete": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "completion_percentage": ((len(required_fields) - len(missing_fields)) / len(required_fields)) * 100
        }