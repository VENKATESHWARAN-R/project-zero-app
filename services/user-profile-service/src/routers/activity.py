from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..schemas.activity import ActivityListResponse, ActivityResponse
from ..services.activity_service import ActivityService
from ..dependencies import get_current_user

router = APIRouter(prefix="/activity", tags=["Activity"])


@router.get("", response_model=ActivityListResponse)
async def get_activity_history(
    limit: int = Query(20, ge=1, le=100, description="Number of activities to return"),
    offset: int = Query(0, ge=0, description="Number of activities to skip"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user activity history."""
    activity_service = ActivityService(db)
    activities, total = activity_service.get_user_activities(
        user_id=current_user["user_id"],
        activity_type=activity_type,
        limit=limit,
        offset=offset
    )

    return ActivityListResponse(
        activities=[ActivityResponse.from_orm(activity) for activity in activities],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/summary")
async def get_activity_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to include in summary"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activity summary for the last N days."""
    activity_service = ActivityService(db)
    summary = activity_service.get_activity_summary(
        user_id=current_user["user_id"],
        days=days
    )

    return {
        "summary": summary,
        "total_activities": sum(summary.values()),
        "days": days
    }


@router.get("/types")
async def get_activity_types():
    """Get available activity types."""
    return {
        "profile_activities": [
            "profile_created",
            "profile_updated",
            "profile_viewed",
            "profile_deleted"
        ],
        "address_activities": [
            "address_created",
            "address_updated",
            "address_deleted",
            "address_default_changed"
        ],
        "preference_activities": [
            "preferences_created",
            "preferences_updated",
            "preferences_reset",
            "notification_settings_changed",
            "privacy_settings_changed"
        ],
        "authentication_activities": [
            "profile_access_denied",
            "admin_access"
        ]
    }