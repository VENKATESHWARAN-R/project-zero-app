from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.preferences import PreferencesUpdateRequest, PreferencesResponse
from ..services.preferences_service import PreferencesService
from ..dependencies import get_current_user, get_request_context

router = APIRouter(prefix="/preferences", tags=["Preferences"])


@router.get("", response_model=PreferencesResponse)
async def get_preferences(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user preferences."""
    preferences_service = PreferencesService(db)
    preferences = preferences_service.get_or_create_preferences(current_user["user_id"])

    return PreferencesResponse.from_orm(preferences)


@router.put("", response_model=PreferencesResponse)
async def update_preferences(
    preferences_data: PreferencesUpdateRequest,
    current_user: dict = Depends(get_current_user),
    request_context: dict = Depends(get_request_context),
    db: Session = Depends(get_db)
):
    """Update user preferences."""
    preferences_service = PreferencesService(db)

    try:
        preferences = preferences_service.update_preferences(
            user_id=current_user["user_id"],
            preferences_data=preferences_data,
            ip_address=request_context.get("ip_address"),
            user_agent=request_context.get("user_agent"),
            correlation_id=request_context.get("correlation_id")
        )

        return PreferencesResponse.from_orm(preferences)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/reset", response_model=PreferencesResponse)
async def reset_preferences(
    current_user: dict = Depends(get_current_user),
    request_context: dict = Depends(get_request_context),
    db: Session = Depends(get_db)
):
    """Reset user preferences to default values."""
    preferences_service = PreferencesService(db)

    try:
        preferences = preferences_service.reset_preferences_to_default(
            user_id=current_user["user_id"],
            ip_address=request_context.get("ip_address"),
            user_agent=request_context.get("user_agent"),
            correlation_id=request_context.get("correlation_id")
        )

        return PreferencesResponse.from_orm(preferences)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )