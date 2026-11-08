"""Command line entry point: `python -m orders import ...` and `python -m orders price ...`."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from orders.importer import load_orders
from orders.loaders import load_catalogue, load_clean_orders, load_customers
from orders.pricing import compute_order_total


def _run_import(args: argparse.Namespace) -> int:
    try:
        result = load_orders(Path(args.file), load_catalogue(), args.month)
    except NotImplementedError:
        print("error: the importer is not implemented yet (see specs/importer.md)", file=sys.stderr)
        return 2
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    print(f"valid lines:    {len(result.lines)}")
    print(f"rejected lines: {len(result.rejected)}")
    for reason, count in sorted(Counter(r.reason for r in result.rejected).items()):
        print(f"  {reason:<18}{count}")
    return 0


def _run_price(args: argparse.Namespace) -> int:
    order = load_clean_orders().get(args.order_id)
    if order is None:
        print(f"error: unknown order {args.order_id} (January 2026 orders only)", file=sys.stderr)
        return 1
    customer = load_customers()[order.customer_id]
    breakdown = compute_order_total(order, customer)
    print(f"Order {order.order_id} - {order.country} - {customer.tier} customer")
    for label in (
        "subtotal",
        "volume_discount",
        "loyalty_discount",
        "promo_discount",
        "discounted_subtotal",
        "shipping",
        "vat",
        "total",
    ):
        print(f"  {label:<20}{getattr(breakdown, label):>10.2f}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="orders", description="Northwind Supplies orders toolkit")
    commands = parser.add_subparsers(dest="command", required=True)

    importer = commands.add_parser("import", help="validate a monthly order file")
    importer.add_argument("file")
    importer.add_argument("--month", required=True, help="expected period, YYYY-MM")
    importer.set_defaults(handler=_run_import)

    price = commands.add_parser("price", help="price one January 2026 order")
    price.add_argument("order_id")
    price.set_defaults(handler=_run_price)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.handler(args)
