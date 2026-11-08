"""Order pricing for Northwind Supplies. The business rules are in specs/pricing.md."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from orders.models import Customer, Order

ZERO = Decimal("0")
CENT = Decimal("0.01")

# (minimum quantity, discount rate), highest tier first
VOLUME_TIERS = ((50, Decimal("0.10")), (10, Decimal("0.05")))
LOYALTY_RATE = Decimal("0.03")
PROMO_CODE = "WELCOME10"
PROMO_RATE = Decimal("0.10")
PROMO_CAP = Decimal("50.00")
FREE_SHIPPING_THRESHOLD = Decimal("100.00")
SHIPPING_FEE = Decimal("6.90")
VAT_RATES = {
    "FR": Decimal("0.20"),
    "DE": Decimal("0.19"),
    "ES": Decimal("0.21"),
    "BE": Decimal("0.21"),
}


@dataclass(frozen=True, slots=True)
class PriceBreakdown:
    subtotal: Decimal
    volume_discount: Decimal
    loyalty_discount: Decimal
    promo_discount: Decimal
    discounted_subtotal: Decimal
    shipping: Decimal
    vat: Decimal
    total: Decimal


def _to_cents(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def _volume_rate(quantity: int) -> Decimal:
    for min_quantity, rate in VOLUME_TIERS:
        if quantity > min_quantity:
            return rate
    return ZERO


def _promo_applies(order: Order, customer: Customer) -> bool:
    return order.promo_code == PROMO_CODE and order.order_date == customer.first_order_date


def _line_total(amount: Decimal, rate: Decimal) -> Decimal:
    return Decimal(str(round(float(amount * (1 - rate)), 2)))


def compute_order_total(order: Order, customer: Customer) -> PriceBreakdown:
    subtotal = ZERO
    after_volume = ZERO
    for line in order.lines:
        subtotal += line.amount
        after_volume += _line_total(line.amount, _volume_rate(line.quantity))
    volume_discount = subtotal - after_volume

    loyalty_discount = promo_discount = ZERO
    if _promo_applies(order, customer):
        # The promo code replaces the loyalty discount.
        promo_discount = min(after_volume * PROMO_RATE, PROMO_CAP)
    elif customer.is_gold:
        loyalty_discount = subtotal * LOYALTY_RATE

    discounted = after_volume - loyalty_discount - promo_discount
    shipping = ZERO if subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_FEE
    vat = discounted * VAT_RATES[order.country]
    total = discounted + shipping + vat

    return PriceBreakdown(
        subtotal=_to_cents(subtotal),
        volume_discount=_to_cents(volume_discount),
        loyalty_discount=_to_cents(loyalty_discount),
        promo_discount=_to_cents(promo_discount),
        discounted_subtotal=_to_cents(discounted),
        shipping=_to_cents(shipping),
        vat=_to_cents(vat),
        total=Decimal(str(round(float(total), 2))),
    )
