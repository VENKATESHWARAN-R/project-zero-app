from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..schemas.profile import ProfileCreateRequest, ProfileUpdateRequest, ProfileResponse
from ..schemas.error import ErrorResponse, NotFoundErrorResponse, ConflictErrorResponse
from ..services.profile_service import ProfileService
from ..dependencies import get_current_user, get_request_context

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile."""
    profile_service = ProfileService(db)
    profile = profile_service.get_profile_by_user_id(current_user["user_id"])

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return ProfileResponse.from_orm(profile)


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreateRequest,
    current_user: dict = Depends(get_current_user),
    request_context: dict = Depends(get_request_context),
    db: Session = Depends(get_db)
):
    """Create user profile."""
    profile_service = ProfileService(db)

    try:
        profile = profile_service.create_profile(
            user_id=current_user["user_id"],
            profile_data=profile_data,
            ip_address=request_context.get("ip_address"),
            user_agent=request_context.get("user_agent"),
            correlation_id=request_context.get("correlation_id")
        )
        return ProfileResponse.from_orm(profile)

    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


@router.put("", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
    request_context: dict = Depends(get_request_context),
    db: Session = Depends(get_db)
):
    """Update user profile."""
    profile_service = ProfileService(db)

    try:
        profile = profile_service.update_profile(
            user_id=current_user["user_id"],
            profile_data=profile_data,
            ip_address=request_context.get("ip_address"),
            user_agent=request_context.get("user_agent"),
            correlation_id=request_context.get("correlation_id")
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        return ProfileResponse.from_orm(profile)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    current_user: dict = Depends(get_current_user),
    request_context: dict = Depends(get_request_context),
    db: Session = Depends(get_db)
):
    """Delete user profile."""
    profile_service = ProfileService(db)

    try:
        deleted = profile_service.delete_profile(
            user_id=current_user["user_id"],
            ip_address=request_context.get("ip_address"),
            user_agent=request_context.get("user_agent"),
            correlation_id=request_context.get("correlation_id")
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/completion", response_model=dict)
async def get_profile_completion(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get profile completion status."""
    profile_service = ProfileService(db)
    completion_status = profile_service.get_profile_completion_status(current_user["user_id"])
    return completion_status