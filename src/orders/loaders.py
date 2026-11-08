"""Readers for the reference files (catalogue, customers) and for already-validated orders."""

from __future__ import annotations

import csv
from collections.abc import Iterator
from datetime import date
from decimal import Decimal
from pathlib import Path

from orders.models import Category, Customer, Order, OrderLine, Product, Tier

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def _rows(path: Path) -> Iterator[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        yield from csv.DictReader(handle)


def load_catalogue(path: Path = DATA_DIR / "products.csv") -> dict[str, Product]:
    return {
        row["product_id"]: Product(
            product_id=row["product_id"],
            name=row["name"],
            category=Category(row["category"]),
            unit_price=Decimal(row["unit_price"]),
            active=row["active"] == "true",
        )
        for row in _rows(path)
    }


def load_customers(path: Path = DATA_DIR / "customers_pii.csv") -> dict[str, Customer]:
    return {
        row["customer_id"]: Customer(
            customer_id=row["customer_id"],
            full_name=row["full_name"],
            email=row["email"],
            phone=row["phone"],
            country=row["country"],
            tier=Tier(row["tier"]),
            first_order_date=date.fromisoformat(row["first_order_date"]),
        )
        for row in _rows(path)
    }


def load_clean_orders(path: Path = DATA_DIR / "orders_2026_01.csv") -> dict[str, Order]:
    """Read a file that is known to be valid (no checks) and group its lines by order."""
    grouped: dict[str, list[OrderLine]] = {}
    for row in _rows(path):
        line = OrderLine(
            order_id=row["order_id"],
            order_line_id=row["order_line_id"],
            order_date=date.fromisoformat(row["order_date"]),
            customer_id=row["customer_id"],
            product_id=row["product_id"],
            quantity=int(row["quantity"]),
            unit_price=Decimal(row["unit_price"]),
            country=row["country"],
            promo_code=row["promo_code"] or None,
        )
        grouped.setdefault(line.order_id, []).append(line)
    return {order_id: Order.from_lines(lines) for order_id, lines in grouped.items()}
