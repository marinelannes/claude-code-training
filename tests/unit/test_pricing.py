from datetime import date
from decimal import Decimal

from orders.models import Customer, Order, OrderLine, Tier
from orders.pricing import PriceBreakdown, compute_order_total


def make_customer(tier=Tier.STANDARD):
    return Customer(
        "C-1", "Alex Sample", "alex@example.com", "+33 6 00 00 00 01", "FR", tier, date(2025, 6, 1)
    )


def make_order(lines, country="FR"):
    return Order.from_lines(
        [
            OrderLine(
                "O-1",
                f"L-{i}",
                date(2026, 1, 10),
                "C-1",
                f"P-{i:04d}",
                quantity,
                Decimal(price),
                country,
            )
            for i, (quantity, price) in enumerate(lines, start=1)
        ]
    )


def test_happy_path():
    order = make_order([(2, "45.00"), (1, "20.00")])
    result = compute_order_total(order, make_customer())
    assert result.total == Decimal("132.00")


def test_returns_a_breakdown():
    result = compute_order_total(make_order([(3, "9.99")]), make_customer())
    assert isinstance(result, PriceBreakdown)
    assert result.total > 0


def test_total_for_gold_customer_with_volume():
    order = make_order([(20, "10.00"), (60, "2.50")], country="DE")
    customer = make_customer(Tier.GOLD)
    expected = compute_order_total(order, customer).total
    assert compute_order_total(order, customer).total == expected


def test_vat_germany():
    result = compute_order_total(make_order([(3, "40.00")], country="DE"), make_customer())
    assert result.vat == Decimal("22.80")
