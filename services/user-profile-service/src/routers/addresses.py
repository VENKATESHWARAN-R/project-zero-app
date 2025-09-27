from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from ..database import get_db
from ..schemas.address import AddressCreateRequest, AddressUpdateRequest, AddressResponse
from ..services.address_service import AddressService
from ..dependencies import get_current_user, get_request_context

router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.get("", response_model=List[AddressResponse])
async def get_addresses(
    type: Optional[str] = Query(None, description="Filter by address type (shipping or billing)"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's addresses."""
    if type and type not in ["shipping", "billing"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Address type must be 'shipping' or 'billing'"
        )

    address_service = AddressService(db)
    addresses = address_service.get_user_addresses(
        user_id=current_user["user_id"],
        address_type=type
    )

    return [AddressResponse.from_orm(address) for address in addresses]


@router.post("", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(
    address_data: AddressCreateRequest,
    current_user: dict = Depends(get_current_user),
    request_context: dict = Depends(get_request_context),
    db: Session = Depends(get_db)
):
    """Add new address."""
    address_service = AddressService(db)

    try:
        address = address_service.create_address(
            user_id=current_user["user_id"],
            address_data=address_data,
            ip_address=request_context.get("ip_address"),
            user_agent=request_context.get("user_agent"),
            correlation_id=request_context.get("correlation_id")
        )
        return AddressResponse.from_orm(address)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{address_id}", response_model=AddressResponse)
async def get_address(
    address_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific address."""
    address_service = AddressService(db)
    address = address_service.get_address_by_id(
        user_id=current_user["user_id"],
        address_id=address_id
    )

    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )

    return AddressResponse.from_orm(address)


@router.put("/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: int,
    address_data: AddressUpdateRequest,
    current_user: dict = Depends(get_current_user),
    request_context: dict = Depends(get_request_context),
    db: Session = Depends(get_db)
):
    """Update address."""
    address_service = AddressService(db)

    try:
        address = address_service.update_address(
            user_id=current_user["user_id"],
            address_id=address_id,
            address_data=address_data,
            ip_address=request_context.get("ip_address"),
            user_agent=request_context.get("user_agent"),
            correlation_id=request_context.get("correlation_id")
        )

        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found"
            )

        return AddressResponse.from_orm(address)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: int,
    current_user: dict = Depends(get_current_user),
    request_context: dict = Depends(get_request_context),
    db: Session = Depends(get_db)
):
    """Delete address."""
    address_service = AddressService(db)

    try:
        deleted = address_service.delete_address(
            user_id=current_user["user_id"],
            address_id=address_id,
            ip_address=request_context.get("ip_address"),
            user_agent=request_context.get("user_agent"),
            correlation_id=request_context.get("correlation_id")
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found"
            )

    except ValueError as e:
        if "in use" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


@router.put("/{address_id}/default", response_model=AddressResponse)
async def set_default_address(
    address_id: int,
    current_user: dict = Depends(get_current_user),
    request_context: dict = Depends(get_request_context),
    db: Session = Depends(get_db)
):
    """Set address as default."""
    address_service = AddressService(db)

    try:
        address = address_service.set_default_address(
            user_id=current_user["user_id"],
            address_id=address_id,
            ip_address=request_context.get("ip_address"),
            user_agent=request_context.get("user_agent"),
            correlation_id=request_context.get("correlation_id")
        )

        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found"
            )

        return AddressResponse.from_orm(address)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )