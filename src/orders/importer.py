"""Import of monthly order files. The rules are in specs/importer.md."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from orders.models import OrderLine, Product

REQUIRED_COLUMNS = (
    "order_id",
    "order_line_id",
    "order_date",
    "customer_id",
    "product_id",
    "quantity",
    "unit_price",
    "country",
)

REASON_CODES = (
    "missing_value",
    "bad_date",
    "out_of_period",
    "bad_quantity",
    "bad_price",
    "unknown_product",
    "inactive_product",
    "bad_country",
    "duplicate_line",
)


class MissingColumnError(ValueError):
    """The file header lacks one or more required columns."""


@dataclass(frozen=True, slots=True)
class RejectedLine:
    line_number: int
    reason: str
    raw: dict[str, str]


@dataclass(slots=True)
class ImportResult:
    lines: list[OrderLine] = field(default_factory=list)
    rejected: list[RejectedLine] = field(default_factory=list)


def load_orders(path: Path, catalogue: dict[str, Product], month: str) -> ImportResult:
    raise NotImplementedError("load_orders is not implemented yet")
