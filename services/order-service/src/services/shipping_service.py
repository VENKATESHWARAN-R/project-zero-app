"""
Shipping cost calculation service.

Handles shipping cost calculations based on weight tiers and zones.
"""

from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from ..logging_config import get_logger

logger = get_logger(__name__)


class ShippingTier(str, Enum):
    """Shipping weight tiers."""
    LIGHT = "Light"      # ≤1 lb
    MEDIUM = "Medium"    # ≤5 lb
    HEAVY = "Heavy"      # ≤20 lb
    FREIGHT = "Freight"  # >20 lb


class ShippingZone(str, Enum):
    """Shipping zones with multipliers."""
    LOCAL = "Local"          # 1.0x
    REGIONAL = "Regional"    # 1.2x
    NATIONAL = "National"    # 1.5x
    EXPEDITED = "Expedited"  # 2.0x


@dataclass
class ShippingItem:
    """Item for shipping calculation."""
    weight: Decimal
    quantity: int

    def total_weight(self) -> Decimal:
        """Calculate total weight for this item."""
        return self.weight * Decimal(str(self.quantity))


@dataclass
class ShippingRate:
    """Shipping rate configuration."""
    name: str
    max_weight: Decimal
    base_rate: Decimal
    tier: ShippingTier


class ShippingService:
    """Service for shipping cost calculations."""

    # Weight tier rates (base rates in USD)
    SHIPPING_RATES = [
        ShippingRate("Light Package", Decimal('1.0'), Decimal('5.99'), ShippingTier.LIGHT),
        ShippingRate("Medium Package", Decimal('5.0'), Decimal('8.99'), ShippingTier.MEDIUM),
        ShippingRate("Heavy Package", Decimal('20.0'), Decimal('15.99'), ShippingTier.HEAVY),
        ShippingRate("Freight Package", Decimal('999.0'), Decimal('25.99'), ShippingTier.FREIGHT),
    ]

    # Zone multipliers
    ZONE_MULTIPLIERS = {
        ShippingZone.LOCAL: Decimal('1.0'),
        ShippingZone.REGIONAL: Decimal('1.2'),
        ShippingZone.NATIONAL: Decimal('1.5'),
        ShippingZone.EXPEDITED: Decimal('2.0'),
    }

    def __init__(self):
        """Initialize ShippingService."""
        logger.info("ShippingService initialized", extra={
            "shipping_tiers": len(self.SHIPPING_RATES),
            "zones": list(self.ZONE_MULTIPLIERS.keys())
        })

    def calculate_shipping_cost(
        self,
        items: List[ShippingItem],
        zone: ShippingZone = ShippingZone.LOCAL,
        address: Optional[Dict] = None
    ) -> Tuple[Decimal, ShippingTier, Decimal]:
        """
        Calculate shipping cost based on items and zone.

        Args:
            items: List of shipping items
            zone: Shipping zone (affects multiplier)
            address: Delivery address (for future zone detection)

        Returns:
            Tuple of (shipping_cost, tier, total_weight)

        Raises:
            ValueError: If items list is empty or contains invalid data
        """
        if not items:
            raise ValueError("Items list cannot be empty")

        # Calculate total weight
        total_weight = sum(item.total_weight() for item in items)

        if total_weight <= 0:
            raise ValueError("Total weight must be positive")

        # Determine shipping tier based on weight
        tier = self._determine_shipping_tier(total_weight)

        # Get base rate for tier
        base_rate = self._get_base_rate_for_tier(tier)

        # Apply zone multiplier
        zone_multiplier = self.ZONE_MULTIPLIERS[zone]
        shipping_cost = (base_rate * zone_multiplier).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

        logger.info("Shipping cost calculated", extra={
            "total_weight": float(total_weight),
            "tier": tier,
            "zone": zone,
            "base_rate": float(base_rate),
            "zone_multiplier": float(zone_multiplier),
            "shipping_cost": float(shipping_cost)
        })

        return shipping_cost, tier, total_weight

    def _determine_shipping_tier(self, total_weight: Decimal) -> ShippingTier:
        """Determine shipping tier based on total weight."""
        for rate in self.SHIPPING_RATES:
            if total_weight <= rate.max_weight:
                return rate.tier

        # Should never reach here due to freight tier having high max_weight
        return ShippingTier.FREIGHT

    def _get_base_rate_for_tier(self, tier: ShippingTier) -> Decimal:
        """Get base shipping rate for a given tier."""
        for rate in self.SHIPPING_RATES:
            if rate.tier == tier:
                return rate.base_rate

        raise ValueError(f"Unknown shipping tier: {tier}")

    def get_available_rates(self) -> List[Dict]:
        """Get list of available shipping rates."""
        return [
            {
                "name": rate.name,
                "max_weight": float(rate.max_weight),
                "base_rate": float(rate.base_rate),
                "tier": rate.tier
            }
            for rate in self.SHIPPING_RATES
        ]

    def calculate_shipping_for_address(self, items: List[ShippingItem], address: Dict) -> Tuple[Decimal, ShippingTier, Decimal]:
        """
        Calculate shipping cost with automatic zone detection based on address.

        Args:
            items: List of shipping items
            address: Delivery address

        Returns:
            Tuple of (shipping_cost, tier, total_weight)
        """
        # Simple zone detection based on country and state
        zone = self._detect_zone_from_address(address)

        return self.calculate_shipping_cost(items, zone, address)

    def _detect_zone_from_address(self, address: Dict) -> ShippingZone:
        """
        Detect shipping zone from address.

        This is a simplified implementation for demo purposes.
        Real implementation would use carrier APIs or zip code databases.
        """
        country = address.get('country', '').upper()
        state = address.get('state_province', '').upper()

        # Simple logic for demonstration
        if country == 'US':
            # California - local/regional
            if state in ['CA', 'NV', 'OR', 'WA', 'AZ']:
                return ShippingZone.LOCAL
            # Neighboring states - regional
            elif state in ['TX', 'CO', 'UT', 'ID', 'MT']:
                return ShippingZone.REGIONAL
            # Other US states - national
            else:
                return ShippingZone.NATIONAL
        else:
            # International - expedited
            return ShippingZone.EXPEDITED

    def create_shipping_item(self, weight: float, quantity: int) -> ShippingItem:
        """Helper method to create ShippingItem from basic types."""
        if weight <= 0:
            raise ValueError("Weight must be positive")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        return ShippingItem(
            weight=Decimal(str(weight)),
            quantity=quantity
        )