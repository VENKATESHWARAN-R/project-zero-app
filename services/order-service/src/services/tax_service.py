"""
Tax calculation service.

Handles tax calculations using the configured fixed rate (8.5% default).
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from ..config import settings
from ..logging_config import get_logger

logger = get_logger(__name__)


class TaxService:
    """Service for tax calculations."""

    def __init__(self, tax_rate: Optional[float] = None):
        """
        Initialize TaxService.

        Args:
            tax_rate: Override tax rate, otherwise use configuration default
        """
        self.tax_rate = Decimal(str(tax_rate or settings.tax_rate))
        logger.info("TaxService initialized", extra={
            "tax_rate": float(self.tax_rate)
        })

    def calculate_tax(self, subtotal: Decimal) -> Decimal:
        """
        Calculate tax amount for a given subtotal.

        Args:
            subtotal: Order subtotal amount

        Returns:
            Tax amount rounded to 2 decimal places

        Raises:
            ValueError: If subtotal is negative
        """
        if subtotal < 0:
            raise ValueError("Subtotal cannot be negative")

        tax_amount = subtotal * self.tax_rate
        # Round to 2 decimal places using banker's rounding
        rounded_tax = tax_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        logger.debug("Tax calculated", extra={
            "subtotal": float(subtotal),
            "tax_rate": float(self.tax_rate),
            "tax_amount": float(rounded_tax)
        })

        return rounded_tax

    def get_tax_rate(self) -> Decimal:
        """Get current tax rate."""
        return self.tax_rate

    def calculate_tax_inclusive_total(self, tax_exclusive_amount: Decimal) -> tuple[Decimal, Decimal]:
        """
        Calculate tax amount and tax-inclusive total.

        Args:
            tax_exclusive_amount: Amount before tax

        Returns:
            Tuple of (tax_amount, total_amount)
        """
        tax_amount = self.calculate_tax(tax_exclusive_amount)
        total_amount = tax_exclusive_amount + tax_amount

        return tax_amount, total_amount

    def reverse_calculate_tax(self, tax_inclusive_amount: Decimal) -> tuple[Decimal, Decimal]:
        """
        Calculate tax-exclusive amount from tax-inclusive total.

        Args:
            tax_inclusive_amount: Total amount including tax

        Returns:
            Tuple of (tax_exclusive_amount, tax_amount)
        """
        if tax_inclusive_amount < 0:
            raise ValueError("Tax-inclusive amount cannot be negative")

        # tax_inclusive = tax_exclusive * (1 + tax_rate)
        # tax_exclusive = tax_inclusive / (1 + tax_rate)
        divisor = Decimal('1') + self.tax_rate
        tax_exclusive_amount = (tax_inclusive_amount / divisor).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        tax_amount = tax_inclusive_amount - tax_exclusive_amount

        logger.debug("Tax reverse-calculated", extra={
            "tax_inclusive_amount": float(tax_inclusive_amount),
            "tax_exclusive_amount": float(tax_exclusive_amount),
            "tax_amount": float(tax_amount),
            "tax_rate": float(self.tax_rate)
        })

        return tax_exclusive_amount, tax_amount