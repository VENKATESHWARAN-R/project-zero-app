from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from ..database import get_db
from ..schemas.profile import ProfileResponse
from ..schemas.activity import ActivityListResponse, ActivityResponse
from ..schemas.preferences import PreferencesResponse
from ..schemas.address import AddressResponse
from ..services.profile_service import ProfileService
from ..services.address_service import AddressService
from ..services.preferences_service import PreferencesService
from ..services.activity_service import ActivityService
from ..dependencies import get_current_user, get_request_context, require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/profiles/{user_id}", response_model=ProfileResponse)
async def get_user_profile_admin(
    user_id: int,
    current_user: dict = Depends(require_admin),
    request_context: dict = Depends(get_request_context),
    db: Session = Depends(get_db)
):
    """Get user profile (admin only)."""
    profile_service = ProfileService(db)
    profile = profile_service.get_profile_by_user_id(user_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    # Log admin access
    activity_service = ActivityService(db)
    activity_service.log_activity(
        user_id=user_id,
        activity_type="admin_access",
        description=f"Admin user {current_user['email']} accessed profile",
        entity_type="profile",
        entity_id=profile.id,
        ip_address=request_context.get("ip_address"),
        user_agent=request_context.get("user_agent"),
        correlation_id=request_context.get("correlation_id")
    )
    db.commit()

    return ProfileResponse.from_orm(profile)


@router.get("/profiles/{user_id}/addresses", response_model=List[AddressResponse])
async def get_user_addresses_admin(
    user_id: int,
    type: Optional[str] = Query(None, description="Filter by address type"),
    current_user: dict = Depends(require_admin),
    request_context: dict = Depends(get_request_context),
    db: Session = Depends(get_db)
):
    """Get user addresses (admin only)."""
    if type and type not in ["shipping", "billing"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Address type must be 'shipping' or 'billing'"
        )

    address_service = AddressService(db)
    addresses = address_service.get_user_addresses(user_id=user_id, address_type=type)

    # Log admin access
    activity_service = ActivityService(db)
    activity_service.log_activity(
        user_id=user_id,
        activity_type="admin_access",
        description=f"Admin user {current_user['email']} accessed addresses",
        entity_type="address",
        ip_address=request_context.get("ip_address"),
        user_agent=request_context.get("user_agent"),
        correlation_id=request_context.get("correlation_id")
    )
    db.commit()

    return [AddressResponse.from_orm(address) for address in addresses]


@router.get("/profiles/{user_id}/preferences", response_model=PreferencesResponse)
async def get_user_preferences_admin(
    user_id: int,
    current_user: dict = Depends(require_admin),
    request_context: dict = Depends(get_request_context),
    db: Session = Depends(get_db)
):
    """Get user preferences (admin only)."""
    preferences_service = PreferencesService(db)
    preferences = preferences_service.get_user_preferences(user_id)

    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found"
        )

    # Log admin access
    activity_service = ActivityService(db)
    activity_service.log_activity(
        user_id=user_id,
        activity_type="admin_access",
        description=f"Admin user {current_user['email']} accessed preferences",
        entity_type="preferences",
        entity_id=preferences.id,
        ip_address=request_context.get("ip_address"),
        user_agent=request_context.get("user_agent"),
        correlation_id=request_context.get("correlation_id")
    )
    db.commit()

    return PreferencesResponse.from_orm(preferences)


@router.get("/profiles/{user_id}/activity", response_model=ActivityListResponse)
async def get_user_activity_admin(
    user_id: int,
    limit: int = Query(20, ge=1, le=100, description="Number of activities to return"),
    offset: int = Query(0, ge=0, description="Number of activities to skip"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    current_user: dict = Depends(require_admin),
    request_context: dict = Depends(get_request_context),
    db: Session = Depends(get_db)
):
    """Get user activity history (admin only)."""
    activity_service = ActivityService(db)
    activities, total = activity_service.get_user_activities(
        user_id=user_id,
        activity_type=activity_type,
        limit=limit,
        offset=offset
    )

    # Log admin access
    activity_service.log_activity(
        user_id=user_id,
        activity_type="admin_access",
        description=f"Admin user {current_user['email']} accessed activity log",
        entity_type="activity",
        ip_address=request_context.get("ip_address"),
        user_agent=request_context.get("user_agent"),
        correlation_id=request_context.get("correlation_id")
    )
    db.commit()

    return ActivityListResponse(
        activities=[ActivityResponse.from_orm(activity) for activity in activities],
        total=total,
        limit=limit,
        offset=offset
    )


@router.delete("/profiles/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_profile_admin(
    user_id: int,
    current_user: dict = Depends(require_admin),
    request_context: dict = Depends(get_request_context),
    db: Session = Depends(get_db)
):
    """Delete user profile (admin only)."""
    profile_service = ProfileService(db)

    try:
        deleted = profile_service.delete_profile(
            user_id=user_id,
            ip_address=request_context.get("ip_address"),
            user_agent=request_context.get("user_agent"),
            correlation_id=request_context.get("correlation_id")
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Log admin action
        activity_service = ActivityService(db)
        activity_service.log_activity(
            user_id=user_id,
            activity_type="admin_profile_deleted",
            description=f"Profile deleted by admin user {current_user['email']}",
            entity_type="profile",
            ip_address=request_context.get("ip_address"),
            user_agent=request_context.get("user_agent"),
            correlation_id=request_context.get("correlation_id")
        )
        db.commit()

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )