from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..models.address import Address
from ..schemas.address import AddressCreateRequest, AddressUpdateRequest
from .activity_service import ActivityService


class AddressService:
    def __init__(self, db: Session):
        self.db = db
        self.activity_service = ActivityService(db)

    def get_user_addresses(self, user_id: int, address_type: Optional[str] = None) -> List[Address]:
        """Get all addresses for a user, optionally filtered by type."""
        query = self.db.query(Address).filter(Address.user_id == user_id)
        if address_type:
            query = query.filter(Address.address_type == address_type)
        return query.order_by(Address.is_default.desc(), Address.created_at.desc()).all()

    def get_address_by_id(self, user_id: int, address_id: int) -> Optional[Address]:
        """Get a specific address by ID for a user."""
        return self.db.query(Address).filter(
            Address.id == address_id,
            Address.user_id == user_id
        ).first()

    def get_default_address(self, user_id: int, address_type: str) -> Optional[Address]:
        """Get the default address for a user and type."""
        return self.db.query(Address).filter(
            Address.user_id == user_id,
            Address.address_type == address_type,
            Address.is_default == True
        ).first()

    def create_address(self, user_id: int, address_data: AddressCreateRequest, ip_address: Optional[str] = None, user_agent: Optional[str] = None, correlation_id: Optional[str] = None) -> Address:
        """Create a new address for a user."""
        # If this is the first address of this type, make it default
        existing_addresses = self.get_user_addresses(user_id, address_data.address_type)
        if not existing_addresses:
            address_data.is_default = True

        # If setting as default, unset other defaults
        if address_data.is_default:
            self._unset_default_addresses(user_id, address_data.address_type)

        address = Address(
            user_id=user_id,
            address_type=address_data.address_type,
            street_address=address_data.street_address,
            address_line_2=address_data.address_line_2,
            city=address_data.city,
            state_province=address_data.state_province,
            postal_code=address_data.postal_code,
            country=address_data.country,
            label=address_data.label,
            is_default=address_data.is_default
        )

        try:
            self.db.add(address)
            self.db.flush()  # Get the ID without committing

            # Log the activity
            self.activity_service.log_activity(
                user_id=user_id,
                activity_type="address_created",
                description=f"New {address_data.address_type} address added: {address_data.label or 'Unlabeled'}",
                entity_type="address",
                entity_id=address.id,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                new_values={
                    "address_type": address_data.address_type,
                    "street_address": address_data.street_address,
                    "city": address_data.city,
                    "state_province": address_data.state_province,
                    "postal_code": address_data.postal_code,
                    "country": address_data.country,
                    "label": address_data.label,
                    "is_default": address_data.is_default
                }
            )

            self.db.commit()
            return address

        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to create address: {str(e)}")

    def update_address(self, user_id: int, address_id: int, address_data: AddressUpdateRequest, ip_address: Optional[str] = None, user_agent: Optional[str] = None, correlation_id: Optional[str] = None) -> Optional[Address]:
        """Update an existing address."""
        address = self.get_address_by_id(user_id, address_id)
        if not address:
            return None

        # Store old values for activity log
        old_values = {
            "street_address": address.street_address,
            "address_line_2": address.address_line_2,
            "city": address.city,
            "state_province": address.state_province,
            "postal_code": address.postal_code,
            "country": address.country,
            "label": address.label
        }

        # Update fields only if provided
        if address_data.street_address is not None:
            address.street_address = address_data.street_address
        if address_data.address_line_2 is not None:
            address.address_line_2 = address_data.address_line_2
        if address_data.city is not None:
            address.city = address_data.city
        if address_data.state_province is not None:
            address.state_province = address_data.state_province
        if address_data.postal_code is not None:
            address.postal_code = address_data.postal_code
        if address_data.country is not None:
            address.country = address_data.country
        if address_data.label is not None:
            address.label = address_data.label

        address.updated_at = datetime.utcnow()

        # Store new values for activity log
        new_values = {
            "street_address": address.street_address,
            "address_line_2": address.address_line_2,
            "city": address.city,
            "state_province": address.state_province,
            "postal_code": address.postal_code,
            "country": address.country,
            "label": address.label
        }

        try:
            # Log the activity
            self.activity_service.log_activity(
                user_id=user_id,
                activity_type="address_updated",
                description=f"Address updated: {address.label or 'Unlabeled'}",
                entity_type="address",
                entity_id=address.id,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                old_values=old_values,
                new_values=new_values
            )

            self.db.commit()
            return address

        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to update address: {str(e)}")

    def delete_address(self, user_id: int, address_id: int, ip_address: Optional[str] = None, user_agent: Optional[str] = None, correlation_id: Optional[str] = None) -> bool:
        """Delete an address."""
        address = self.get_address_by_id(user_id, address_id)
        if not address:
            return False

        # Check if address is being used in active orders (future integration)
        # For now, we'll allow deletion of any address

        try:
            # Log the activity before deletion
            self.activity_service.log_activity(
                user_id=user_id,
                activity_type="address_deleted",
                description=f"Address deleted: {address.label or 'Unlabeled'}",
                entity_type="address",
                entity_id=address.id,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                old_values={
                    "address_type": address.address_type,
                    "street_address": address.street_address,
                    "city": address.city,
                    "state_province": address.state_province,
                    "postal_code": address.postal_code,
                    "country": address.country,
                    "label": address.label,
                    "is_default": address.is_default
                }
            )

            # If deleting the default address, set another address as default
            if address.is_default:
                remaining_addresses = self.db.query(Address).filter(
                    Address.user_id == user_id,
                    Address.address_type == address.address_type,
                    Address.id != address_id
                ).first()

                if remaining_addresses:
                    remaining_addresses.is_default = True
                    remaining_addresses.updated_at = datetime.utcnow()

            self.db.delete(address)
            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to delete address: {str(e)}")

    def set_default_address(self, user_id: int, address_id: int, ip_address: Optional[str] = None, user_agent: Optional[str] = None, correlation_id: Optional[str] = None) -> Optional[Address]:
        """Set an address as the default for its type."""
        address = self.get_address_by_id(user_id, address_id)
        if not address:
            return None

        if address.is_default:
            return address  # Already default

        try:
            # Unset other default addresses of the same type
            self._unset_default_addresses(user_id, address.address_type)

            # Set this address as default
            address.is_default = True
            address.updated_at = datetime.utcnow()

            # Log the activity
            self.activity_service.log_activity(
                user_id=user_id,
                activity_type="address_default_changed",
                description=f"Default {address.address_type} address changed to: {address.label or 'Unlabeled'}",
                entity_type="address",
                entity_id=address.id,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                new_values={"is_default": True}
            )

            self.db.commit()
            return address

        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to set default address: {str(e)}")

    def _unset_default_addresses(self, user_id: int, address_type: str):
        """Unset all default addresses for a user and type."""
        self.db.query(Address).filter(
            Address.user_id == user_id,
            Address.address_type == address_type,
            Address.is_default == True
        ).update({"is_default": False, "updated_at": datetime.utcnow()})