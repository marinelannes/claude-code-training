"""Domain models for the Northwind Supplies orders toolkit.

All money amounts are `Decimal` values in euros. Dates are `datetime.date`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import StrEnum

ALLOWED_COUNTRIES: tuple[str, ...] = ("FR", "DE", "ES", "BE")


class Category(StrEnum):
    FURNITURE = "Furniture"
    PAPER = "Paper"
    ELECTRONICS = "Electronics"
    SUPPLIES = "Supplies"


class Tier(StrEnum):
    STANDARD = "standard"
    GOLD = "gold"


@dataclass(frozen=True, slots=True)
class Product:
    product_id: str
    name: str
    category: Category
    unit_price: Decimal
    active: bool


@dataclass(frozen=True, slots=True)
class Customer:
    customer_id: str
    full_name: str
    email: str
    phone: str
    country: str
    tier: Tier
    first_order_date: date

    @property
    def is_gold(self) -> bool:
        return self.tier is Tier.GOLD


@dataclass(frozen=True, slots=True)
class OrderLine:
    order_id: str
    order_line_id: str
    order_date: date
    customer_id: str
    product_id: str
    quantity: int
    unit_price: Decimal
    country: str
    promo_code: str | None = None

    @property
    def amount(self) -> Decimal:
        """Gross line amount, before any discount."""
        return self.quantity * self.unit_price


@dataclass(slots=True)
class Order:
    order_id: str
    customer_id: str
    order_date: date
    country: str
    promo_code: str | None = None
    lines: list[OrderLine] = field(default_factory=list)

    @classmethod
    def from_lines(cls, lines: list[OrderLine]) -> Order:
        """Build an order from its lines. All lines must share the same order_id."""
        if not lines:
            raise ValueError("an order needs at least one line")
        first = lines[0]
        if any(line.order_id != first.order_id for line in lines):
            raise ValueError("all lines must belong to the same order")
        return cls(
            order_id=first.order_id,
            customer_id=first.customer_id,
            order_date=first.order_date,
            country=first.country,
            promo_code=first.promo_code,
            lines=list(lines),
        )
