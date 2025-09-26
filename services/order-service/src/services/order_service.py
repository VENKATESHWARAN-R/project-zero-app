"""
Order service - Core business logic for order management.

Handles order creation, modification, status management, and lifecycle operations.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models import Order, OrderItem, ShippingAddress, OrderModification, OrderStatus
from ..clients.auth_client import AuthClient, AuthenticationError, AuthorizationError
from ..clients.cart_client import CartClient, CartServiceError
from ..clients.product_client import ProductClient, ProductServiceError, ProductUnavailableError
from ..services.tax_service import TaxService
from ..services.shipping_service import ShippingService, ShippingItem
from ..logging_config import get_logger

logger = get_logger(__name__)


class OrderServiceError(Exception):
    """Base exception for order service operations."""
    pass


class InvalidOrderStateError(OrderServiceError):
    """Raised when order state transition is invalid."""
    pass


class InsufficientPermissionsError(OrderServiceError):
    """Raised when user lacks required permissions."""
    pass


class OrderService:
    """Core service for order management operations."""

    def __init__(
        self,
        db: Session,
        auth_client: Optional[AuthClient] = None,
        cart_client: Optional[CartClient] = None,
        product_client: Optional[ProductClient] = None,
        tax_service: Optional[TaxService] = None,
        shipping_service: Optional[ShippingService] = None
    ):
        """
        Initialize OrderService with dependencies.

        Args:
            db: Database session
            auth_client: Authentication service client
            cart_client: Cart service client
            product_client: Product catalog service client
            tax_service: Tax calculation service
            shipping_service: Shipping calculation service
        """
        self.db = db
        self.auth_client = auth_client or AuthClient()
        self.cart_client = cart_client or CartClient()
        self.product_client = product_client or ProductClient()
        self.tax_service = tax_service or TaxService()
        self.shipping_service = shipping_service or ShippingService()

        logger.info("OrderService initialized")

    async def create_order(
        self,
        user_data: Dict[str, Any],
        shipping_address_data: Dict[str, Any],
        auth_token: str,
        notes: Optional[str] = None
    ) -> Order:
        """
        Create a new order from user's cart.

        Args:
            user_data: Authenticated user data
            shipping_address_data: Shipping address information
            auth_token: JWT token for service calls
            notes: Optional order notes

        Returns:
            Created Order instance

        Raises:
            OrderServiceError: If order creation fails
            CartServiceError: If cart operations fail
            ProductServiceError: If product validation fails
        """
        user_id = user_data["user_id"]

        try:
            # Step 1: Retrieve and validate cart
            cart_data = await self.cart_client.get_cart(user_id, auth_token)
            await self.cart_client.validate_cart_items(cart_data)

            # Step 2: Extract order items and validate products
            order_items_data = self.cart_client.extract_order_items_from_cart(cart_data)
            validated_items = await self.product_client.validate_order_items(order_items_data)

            # Step 3: Calculate shipping cost
            shipping_items = [
                ShippingItem(
                    weight=Decimal(str(item["weight"])),
                    quantity=item["quantity"]
                )
                for item in validated_items
            ]

            shipping_cost, shipping_tier, total_weight = self.shipping_service.calculate_shipping_for_address(
                shipping_items, shipping_address_data
            )

            # Step 4: Calculate totals
            subtotal = sum(Decimal(str(item["total_price"])) for item in validated_items)
            tax_amount = self.tax_service.calculate_tax(subtotal)
            total = subtotal + tax_amount + shipping_cost

            # Step 5: Create order in database transaction
            order = await self._create_order_transaction(
                user_id=user_id,
                user_email=user_data.get("email"),
                order_items_data=validated_items,
                shipping_address_data=shipping_address_data,
                subtotal=subtotal,
                tax_amount=tax_amount,
                shipping_cost=shipping_cost,
                total=total,
                notes=notes
            )

            # Step 6: Clear cart after successful order creation
            try:
                await self.cart_client.clear_cart(user_id, auth_token)
                logger.info("Cart cleared after order creation", extra={
                    "order_id": order.id,
                    "user_id": user_id
                })
            except CartServiceError as e:
                # Log warning but don't fail the order
                logger.warning("Failed to clear cart after order creation", extra={
                    "order_id": order.id,
                    "user_id": user_id,
                    "error": str(e)
                })

            logger.info("Order created successfully", extra={
                "order_id": order.id,
                "order_number": order.order_number,
                "user_id": user_id,
                "total": float(order.total),
                "item_count": len(validated_items)
            })

            return order

        except (CartServiceError, ProductServiceError) as e:
            logger.error("Order creation failed", extra={
                "user_id": user_id,
                "error": str(e)
            })
            raise OrderServiceError(f"Order creation failed: {str(e)}")

        except SQLAlchemyError as e:
            logger.error("Database error during order creation", extra={
                "user_id": user_id,
                "error": str(e)
            })
            self.db.rollback()
            raise OrderServiceError("Database error during order creation")

    async def _create_order_transaction(
        self,
        user_id: int,
        user_email: Optional[str],
        order_items_data: List[Dict[str, Any]],
        shipping_address_data: Dict[str, Any],
        subtotal: Decimal,
        tax_amount: Decimal,
        shipping_cost: Decimal,
        total: Decimal,
        notes: Optional[str]
    ) -> Order:
        """Create order and related entities in a database transaction."""

        try:
            # Generate unique order number
            order_number = self._generate_order_number()

            # Create order
            order = Order(
                user_id=user_id,
                order_number=order_number,
                status=OrderStatus.PENDING,
                subtotal=subtotal,
                tax_rate=self.tax_service.get_tax_rate(),
                tax_amount=tax_amount,
                shipping_cost=shipping_cost,
                total=total,
                currency="USD",
                notes=notes
            )

            self.db.add(order)
            self.db.flush()  # Get order.id

            # Create order items
            for item_data in order_items_data:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item_data["product_id"],
                    product_name=item_data["product_name"],
                    product_sku=item_data.get("product_sku"),
                    quantity=item_data["quantity"],
                    unit_price=Decimal(str(item_data["unit_price"])),
                    total_price=Decimal(str(item_data["total_price"])),
                    weight=Decimal(str(item_data["weight"]))
                )
                self.db.add(order_item)

            # Create shipping address
            shipping_address = ShippingAddress(
                order_id=order.id,
                recipient_name=shipping_address_data["recipient_name"],
                company=shipping_address_data.get("company"),
                address_line_1=shipping_address_data["address_line_1"],
                address_line_2=shipping_address_data.get("address_line_2"),
                city=shipping_address_data["city"],
                state_province=shipping_address_data["state_province"],
                postal_code=shipping_address_data["postal_code"],
                country=shipping_address_data["country"],
                phone=shipping_address_data.get("phone"),
                delivery_instructions=shipping_address_data.get("delivery_instructions")
            )
            self.db.add(shipping_address)

            # Create initial order modification record
            modification = OrderModification.create_status_change(
                order_id=order.id,
                user_id=user_id,
                user_email=user_email,
                old_status="NONE",
                new_status="PENDING",
                reason="Order created"
            )
            self.db.add(modification)

            self.db.commit()
            return order

        except SQLAlchemyError:
            self.db.rollback()
            raise

    def _generate_order_number(self) -> str:
        """Generate a unique order number."""
        timestamp = datetime.utcnow().strftime("%Y%m")
        unique_part = str(uuid.uuid4())[:8].upper()
        return f"ORD-{timestamp}-{unique_part}"

    async def update_order_status(
        self,
        order_id: int,
        new_status: OrderStatus,
        user_data: Dict[str, Any],
        notes: Optional[str] = None
    ) -> Order:
        """
        Update order status with proper validation and audit trail.

        Args:
            order_id: Order ID to update
            new_status: New status to set
            user_data: Authenticated user data
            notes: Optional notes for status change

        Returns:
            Updated Order instance

        Raises:
            OrderServiceError: If update fails
            InvalidOrderStateError: If status transition is invalid
            InsufficientPermissionsError: If user lacks permissions
        """
        # Admin privileges required for status updates
        self.auth_client.require_admin_role(user_data)

        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise OrderServiceError(f"Order {order_id} not found")

        # Validate status transition
        if not order.can_transition_to(new_status):
            raise InvalidOrderStateError(
                f"Cannot transition from {order.status} to {new_status}"
            )

        try:
            old_status = order.status
            order.status = new_status
            order.modification_count += 1

            # Create audit record
            modification = OrderModification.create_status_change(
                order_id=order.id,
                user_id=user_data["user_id"],
                user_email=user_data.get("email"),
                old_status=old_status.value,
                new_status=new_status.value,
                reason=notes
            )
            self.db.add(modification)

            self.db.commit()

            logger.info("Order status updated", extra={
                "order_id": order_id,
                "old_status": old_status.value,
                "new_status": new_status.value,
                "updated_by": user_data.get("email")
            })

            return order

        except SQLAlchemyError as e:
            logger.error("Database error during status update", extra={
                "order_id": order_id,
                "error": str(e)
            })
            self.db.rollback()
            raise OrderServiceError("Database error during status update")

    def get_user_orders(
        self,
        user_id: int,
        status_filter: Optional[OrderStatus] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Order], int]:
        """
        Get orders for a specific user with pagination.

        Args:
            user_id: User ID to filter by
            status_filter: Optional status filter
            limit: Maximum orders to return
            offset: Number of orders to skip

        Returns:
            Tuple of (orders, total_count)
        """
        query = self.db.query(Order).filter(Order.user_id == user_id)

        if status_filter:
            query = query.filter(Order.status == status_filter)

        total_count = query.count()
        orders = query.order_by(Order.created_at.desc()).offset(offset).limit(limit).all()

        logger.debug("User orders retrieved", extra={
            "user_id": user_id,
            "status_filter": status_filter.value if status_filter else None,
            "count": len(orders),
            "total": total_count
        })

        return orders, total_count

    def get_order_by_id(self, order_id: int, user_data: Dict[str, Any]) -> Optional[Order]:
        """
        Get order by ID with access control.

        Args:
            order_id: Order ID to retrieve
            user_data: Authenticated user data

        Returns:
            Order instance if found and accessible

        Raises:
            InsufficientPermissionsError: If user cannot access order
        """
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return None

        # Check access permissions
        self.auth_client.require_order_owner(user_data, order.user_id)

        return order