"""Regenerate every CSV file in data/ from a fixed seed.

Usage: uv run python scripts/generate_data.py

All data is synthetic: names, e-mails and phone numbers are fake.
Running the script twice produces byte-identical files.
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 2026
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

ORDER_COLUMNS = [
    "order_id",
    "order_line_id",
    "order_date",
    "customer_id",
    "product_id",
    "quantity",
    "unit_price",
    "country",
    "promo_code",
]

CATALOGUE = {
    "Furniture": (
        [
            "Desk",
            "Office Chair",
            "Bookshelf",
            "Filing Cabinet",
            "Standing Desk",
            "Meeting Table",
            "Drawer Unit",
            "Footrest",
            "Monitor Arm",
            "Coat Stand",
        ],
        (3900, 42000),
    ),
    "Paper": (
        [
            "A4 Paper Ream",
            "A3 Paper Ream",
            "Sticky Notes",
            "Notebook A5",
            "Envelopes C4",
            "Printer Labels",
            "Flip Chart Pad",
            "Index Cards",
            "Graph Paper",
            "Card Stock",
        ],
        (150, 2400),
    ),
    "Electronics": (
        [
            "Wireless Mouse",
            "Keyboard",
            "USB-C Hub",
            "Webcam",
            "Headset",
            "Desk Lamp",
            "Label Printer",
            "Shredder",
            "Calculator",
            "Power Strip",
        ],
        (900, 18000),
    ),
    "Supplies": (
        [
            "Ballpoint Pens (10)",
            "Stapler",
            "Staples (5000)",
            "Highlighters (4)",
            "Scissors",
            "Tape Dispenser",
            "Paper Clips (100)",
            "Whiteboard Markers",
            "Desk Organizer",
            "Binder Clips (24)",
        ],
        (90, 1900),
    ),
}

FIRST_NAMES = [
    "Alex",
    "Sam",
    "Jordan",
    "Robin",
    "Camille",
    "Noa",
    "Charlie",
    "Dominique",
    "Morgan",
    "Lou",
    "Eden",
    "Sacha",
    "Andrea",
    "Kim",
    "Maxime",
    "Toni",
]
LAST_NAMES = [
    "Sample",
    "Example",
    "Placeholder",
    "Testwell",
    "Mockford",
    "Dummett",
    "Fakeley",
    "Demoreau",
    "Fictivo",
    "Specimen",
    "Notreal",
    "Madeup",
]
COUNTRIES = ["FR", "DE", "ES", "BE"]
COUNTRY_WEIGHTS = [40, 30, 15, 15]
PHONE_PREFIX = {"FR": "+33 6 00 00", "DE": "+49 150 0000", "ES": "+34 600 000", "BE": "+32 470 00"}


def money(cents: int) -> str:
    return f"{cents // 100}.{cents % 100:02d}"


def random_day(rng: random.Random, start: date, end: date) -> date:
    return start + timedelta(days=rng.randint(0, (end - start).days))


def make_products(rng: random.Random) -> list[dict]:
    products = []
    for category, (names, (low, high)) in CATALOGUE.items():
        for name in names:
            products.append(
                {
                    "product_id": f"P-{len(products) + 1:04d}",
                    "name": name,
                    "category": category,
                    "unit_price": money(rng.randint(low, high)),
                    "active": "true",
                }
            )
    for index in rng.sample(range(len(products)), 4):
        products[index]["active"] = "false"
    return products


def make_customers(rng: random.Random) -> list[dict]:
    customers = []
    for i in range(1, 151):
        first, last = rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES)
        country = rng.choices(COUNTRIES, COUNTRY_WEIGHTS)[0]
        customers.append(
            {
                "customer_id": f"C-{i:04d}",
                "full_name": f"{first} {last}",
                "email": f"{first}.{last}.{i:03d}@example.com".lower(),
                "phone": f"{PHONE_PREFIX[country]} {i:04d}",
                "country": country,
                "tier": "gold" if rng.random() < 0.2 else "standard",
                "first_order_date": random_day(
                    rng, date(2024, 1, 1), date(2025, 12, 31)
                ).isoformat(),
            }
        )
    return customers


def pick_quantity(rng: random.Random) -> int:
    roll = rng.random()
    if roll < 0.70:
        return rng.randint(1, 9)
    if roll < 0.93:
        return 10 if rng.random() < 0.15 else rng.randint(10, 49)
    return 50 if rng.random() < 0.25 else rng.randint(50, 120)


def make_orders(rng, month_start, month_end, prefix, customers, new_ids, products, n_orders):
    """Generate valid order lines; new customers get their first order in this month."""
    eligible = [c for c in customers if c["first_order_date"] < month_start.isoformat()]
    eligible += [c for c in customers if c["customer_id"] in new_ids]
    by_id = {c["customer_id"]: c for c in customers}
    n_random = n_orders - len(new_ids)
    buyers = sorted(new_ids) + [rng.choice(eligible)["customer_id"] for _ in range(n_random)]
    orders = sorted(
        ((random_day(rng, month_start, month_end), customer_id) for customer_id in buyers),
        key=lambda item: item[0],
    )
    active = [p for p in products if p["active"] == "true"]
    first_seen: dict[str, date] = {}
    rows, line_no = [], 0
    for order_no, (order_date, customer_id) in enumerate(orders, start=1):
        customer = by_id[customer_id]
        promo = ""
        if customer_id in new_ids and customer_id not in first_seen:
            first_seen[customer_id] = order_date
            customer["first_order_date"] = order_date.isoformat()
            promo = "WELCOME10" if rng.random() < 0.8 else ""
        elif customer_id not in new_ids and rng.random() < 0.01:
            promo = "WELCOME10"  # not a first order: the code must be ignored
        n_lines = rng.choices([1, 2, 3, 4, 5, 6], [20, 25, 25, 15, 10, 5])[0]
        for product in rng.sample(active, n_lines):
            line_no += 1
            rows.append(
                {
                    "order_id": f"O-{prefix}-{order_no:04d}",
                    "order_line_id": f"L-{prefix}-{line_no:05d}",
                    "order_date": order_date.isoformat(),
                    "customer_id": customer_id,
                    "product_id": product["product_id"],
                    "quantity": str(pick_quantity(rng)),
                    "unit_price": product["unit_price"],
                    "country": customer["country"],
                    "promo_code": promo,
                }
            )
    return rows


CORRUPTIONS = {
    "missing_value": [
        ("customer_id", ""),
        ("product_id", ""),
        ("quantity", ""),
        ("order_date", ""),
        ("country", ""),
    ],
    "bad_date": [
        ("order_date", "2026/02/14"),
        ("order_date", "14-02-2026"),
        ("order_date", "2026-02-30"),
        ("order_date", "Feb 3 2026"),
    ],
    "out_of_period": [
        ("order_date", "2026-01-31"),
        ("order_date", "2026-03-01"),
        ("order_date", "2025-02-10"),
        ("order_date", "2026-03-15"),
    ],
    "bad_quantity": [
        ("quantity", "0"),
        ("quantity", "-3"),
        ("quantity", "2.5"),
        ("quantity", "two"),
        ("quantity", "-1"),
    ],
    "bad_price": [
        ("unit_price", "-4.50"),
        ("unit_price", "-0.01"),
        ("unit_price", "12,50"),
        ("unit_price", "n/a"),
    ],
    "unknown_product": [
        ("product_id", "P-9999"),
        ("product_id", "P-0000"),
        ("product_id", "P-0412"),
        ("product_id", "X-0001"),
    ],
    "bad_country": [("country", "IT"), ("country", "UK"), ("country", "NL"), ("country", "XX")],
}


def dirty_february(rng: random.Random, rows: list[dict], products: list[dict]) -> list[dict]:
    """Inject invalid lines and valid edge cases into a clean list of rows."""
    rows = [dict(row) for row in rows]
    free = list(range(len(rows)))
    rng.shuffle(free)

    def take(n: int) -> list[int]:
        return [free.pop() for _ in range(n)]

    for changes in CORRUPTIONS.values():
        for index, (column, value) in zip(take(len(changes)), changes, strict=True):
            rows[index][column] = value
    inactive = [p for p in products if p["active"] == "false"]
    for index, product in zip(take(4), inactive, strict=True):
        rows[index]["product_id"] = product["product_id"]
        rows[index]["unit_price"] = product["unit_price"]
    # Valid edge cases that must NOT be rejected.
    for index in take(3):
        rows[index]["unit_price"] = "0.00"  # free sample
    for index in take(6):
        for column in ("product_id", "quantity", "country"):
            rows[index][column] = f"  {rows[index][column]} "
    for index in take(5):
        rows[index]["country"] = rows[index]["country"].lower()
    # Duplicates: exact copies of untouched valid lines, inserted later in the file.
    for index in sorted(take(4), reverse=True):
        position = rng.randint(index + 1, len(rows))
        rows.insert(position, dict(rows[index]))
    return rows


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rng = random.Random(SEED)
    products = make_products(rng)
    customers = make_customers(rng)
    ids = [c["customer_id"] for c in customers]
    new_jan = set(rng.sample(ids, 15))
    new_feb = set(rng.sample(sorted(set(ids) - new_jan), 10))
    for customer in customers:  # placeholder until their first order is generated
        if customer["customer_id"] in new_jan | new_feb:
            customer["first_order_date"] = "2099-01-01"

    january = make_orders(
        rng,
        date(2026, 1, 1),
        date(2026, 1, 31),
        "202601",
        customers,
        new_jan,
        products,
        n_orders=525,
    )
    february = make_orders(
        rng,
        date(2026, 2, 1),
        date(2026, 2, 28),
        "202602",
        customers,
        new_feb,
        products,
        n_orders=172,
    )
    february = dirty_february(rng, february, products)

    DATA_DIR.mkdir(exist_ok=True)
    write_csv(DATA_DIR / "products.csv", list(products[0]), products)
    write_csv(DATA_DIR / "customers_pii.csv", list(customers[0]), customers)
    write_csv(DATA_DIR / "orders_2026_01.csv", ORDER_COLUMNS, january)
    write_csv(DATA_DIR / "orders_2026_02_raw.csv", ORDER_COLUMNS, february)
    print(
        f"products={len(products)} customers={len(customers)} "
        f"january_lines={len(january)} february_lines={len(february)}"
    )


if __name__ == "__main__":
    main()
