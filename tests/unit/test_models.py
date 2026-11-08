from datetime import date
from decimal import Decimal

import pytest

from orders.models import Order, OrderLine


def line(order_id="O-1", quantity=3, price="2.50"):
    return OrderLine(
        order_id, "L-1", date(2026, 1, 5), "C-1", "P-0001", quantity, Decimal(price), "FR"
    )


def test_line_amount():
    assert line().amount == Decimal("7.50")


def test_order_from_lines_rejects_mixed_orders():
    with pytest.raises(ValueError):
        Order.from_lines([line("O-1"), line("O-2")])
