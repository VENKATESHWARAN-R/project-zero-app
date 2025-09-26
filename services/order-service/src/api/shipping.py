"""
Shipping calculation API endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Header, status
from ..services.shipping_service import ShippingService, ShippingItem
from ..schemas.shipping import (
    ShippingCalculateRequest,
    ShippingCalculateResponse,
    ShippingRatesResponse,
    ShippingRate
)
from ..utils.validation import create_error_response
from ..logging_config import get_logger, set_correlation_id

logger = get_logger(__name__)

router = APIRouter(prefix="/shipping", tags=["shipping"])


@router.post(
    "/calculate",
    response_model=ShippingCalculateResponse,
    summary="Calculate shipping cost",
    description="Calculate shipping cost for items and address"
)
async def calculate_shipping_cost(
    request: ShippingCalculateRequest,
    x_correlation_id: Optional[str] = Header(None)
):
    """Calculate shipping cost for items and delivery address."""
    if x_correlation_id:
        set_correlation_id(x_correlation_id)

    try:
        shipping_service = ShippingService()

        # Convert request items to ShippingItem objects
        shipping_items = [
            shipping_service.create_shipping_item(item.weight, item.quantity)
            for item in request.items
        ]

        # Calculate shipping cost
        shipping_cost, shipping_tier, total_weight = shipping_service.calculate_shipping_for_address(
            items=shipping_items,
            address=request.address.model_dump()
        )

        logger.info("Shipping cost calculated", extra={
            "total_weight": float(total_weight),
            "tier": shipping_tier.value,
            "cost": float(shipping_cost)
        })

        return ShippingCalculateResponse(
            shipping_cost=float(shipping_cost),
            shipping_tier=shipping_tier.value,
            total_weight=float(total_weight),
            zone="Local"  # Simplified for now
        )

    except ValueError as e:
        logger.warning("Invalid shipping calculation request", extra={"error": str(e)})
        raise create_error_response(
            "invalid_request",
            str(e),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    except Exception as e:
        logger.error("Error calculating shipping cost", extra={"error": str(e)})
        raise create_error_response(
            "calculation_error",
            "Failed to calculate shipping cost",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get(
    "/rates",
    response_model=ShippingRatesResponse,
    summary="Get available shipping rates",
    description="List available shipping options and rates"
)
async def get_shipping_rates(
    x_correlation_id: Optional[str] = Header(None)
):
    """Get list of available shipping rates."""
    if x_correlation_id:
        set_correlation_id(x_correlation_id)

    try:
        shipping_service = ShippingService()
        rates_data = shipping_service.get_available_rates()

        rates = [
            ShippingRate(
                name=rate["name"],
                max_weight=rate["max_weight"],
                base_rate=rate["base_rate"]
            )
            for rate in rates_data
        ]

        return ShippingRatesResponse(rates=rates)

    except Exception as e:
        logger.error("Error retrieving shipping rates", extra={"error": str(e)})
        raise create_error_response(
            "retrieval_error",
            "Failed to retrieve shipping rates",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )