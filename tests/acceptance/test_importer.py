"""Acceptance tests for the importer (Lab 1). They define the expected behaviour of
`load_orders`, as described in specs/importer.md.

Run them with: uv run pytest tests/acceptance -q
"""

from collections import Counter
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from orders.importer import MissingColumnError, load_orders
from orders.loaders import load_catalogue

DATA = Path(__file__).resolve().parents[2] / "data"
FEBRUARY = DATA / "orders_2026_02_raw.csv"
HEADER = "order_id,order_line_id,order_date,customer_id,product_id,quantity,unit_price,country,promo_code"
VALID = "O-1,L-1,2026-02-10,C-0001,P-0001,2,117.06,FR,"


@pytest.fixture(scope="module")
def catalogue():
    return load_catalogue(DATA / "products.csv")


def write_csv(tmp_path: Path, *rows: str, header: str = HEADER) -> Path:
    path = tmp_path / "orders.csv"
    path.write_text("\n".join([header, *rows]) + "\n", encoding="utf-8")
    return path


def test_february_file_counts(catalogue):
    result = load_orders(FEBRUARY, catalogue, "2026-02")
    assert len(result.lines) == 437
    assert len(result.rejected) == 38


def test_february_file_counts_per_reason(catalogue):
    result = load_orders(FEBRUARY, catalogue, "2026-02")
    assert Counter(r.reason for r in result.rejected) == {
        "missing_value": 5,
        "bad_date": 4,
        "out_of_period": 4,
        "bad_quantity": 5,
        "bad_price": 4,
        "unknown_product": 4,
        "inactive_product": 4,
        "bad_country": 4,
        "duplicate_line": 4,
    }


def test_valid_line_is_parsed_into_typed_order_line(tmp_path, catalogue):
    path = write_csv(tmp_path, VALID.replace(",FR,", ",FR,WELCOME10"))
    result = load_orders(path, catalogue, "2026-02")
    assert result.rejected == []
    [line] = result.lines
    assert line.order_date == date(2026, 2, 10)
    assert line.quantity == 2
    assert line.unit_price == Decimal("117.06")
    assert line.promo_code == "WELCOME10"


def test_empty_promo_code_becomes_none(tmp_path, catalogue):
    [line] = load_orders(write_csv(tmp_path, VALID), catalogue, "2026-02").lines
    assert line.promo_code is None


def test_missing_required_column_raises(tmp_path, catalogue):
    path = write_csv(
        tmp_path,
        "O-1,L-1,2026-02-10,C-0001,P-0001,2,FR",
        header="order_id,order_line_id,order_date,customer_id,product_id,quantity,country",
    )
    with pytest.raises(MissingColumnError):
        load_orders(path, catalogue, "2026-02")


def test_promo_code_column_is_optional(tmp_path, catalogue):
    path = write_csv(
        tmp_path,
        "O-1,L-1,2026-02-10,C-0001,P-0001,2,117.06,FR",
        header=HEADER.removesuffix(",promo_code"),
    )
    result = load_orders(path, catalogue, "2026-02")
    assert len(result.lines) == 1


def test_whitespace_and_lowercase_country_are_normalised(tmp_path, catalogue):
    row = " O-1 , L-1 , 2026-02-10 , C-0001 ,  P-0001 , 3 , 117.06 , fr ,"
    [line] = load_orders(write_csv(tmp_path, row), catalogue, "2026-02").lines
    assert (line.order_id, line.product_id) == ("O-1", "P-0001")
    assert (line.quantity, line.country) == (3, "FR")


def test_zero_price_is_accepted(tmp_path, catalogue):
    result = load_orders(write_csv(tmp_path, VALID.replace("117.06", "0.00")), catalogue, "2026-02")
    assert result.rejected == []
    assert result.lines[0].unit_price == Decimal("0.00")


@pytest.mark.parametrize(
    ("row", "reason"),
    [
        ("O-1,L-1,2026-02-10,,P-0001,2,117.06,FR,", "missing_value"),
        ("O-1,L-1,10/02/2026,C-0001,P-0001,2,117.06,FR,", "bad_date"),
        ("O-1,L-1,2026-02-30,C-0001,P-0001,2,117.06,FR,", "bad_date"),
        ("O-1,L-1,2026-03-01,C-0001,P-0001,2,117.06,FR,", "out_of_period"),
        ("O-1,L-1,2026-02-10,C-0001,P-0001,0,117.06,FR,", "bad_quantity"),
        ("O-1,L-1,2026-02-10,C-0001,P-0001,1.5,117.06,FR,", "bad_quantity"),
        ("O-1,L-1,2026-02-10,C-0001,P-0001,2,-1.00,FR,", "bad_price"),
        ("O-1,L-1,2026-02-10,C-0001,P-9999,2,117.06,FR,", "unknown_product"),
        ("O-1,L-1,2026-02-10,C-0001,P-0002,2,248.37,FR,", "inactive_product"),
        ("O-1,L-1,2026-02-10,C-0001,P-0001,2,117.06,IT,", "bad_country"),
    ],
)
def test_each_rule_gives_its_reason_code(tmp_path, catalogue, row, reason):
    result = load_orders(write_csv(tmp_path, row), catalogue, "2026-02")
    assert result.lines == []
    assert [r.reason for r in result.rejected] == [reason]


def test_first_failing_rule_wins(tmp_path, catalogue):
    # Bad date AND unknown product: the date check comes first.
    row = "O-1,L-1,2026-13-01,C-0001,P-9999,2,117.06,FR,"
    result = load_orders(write_csv(tmp_path, row), catalogue, "2026-02")
    assert result.rejected[0].reason == "bad_date"


def test_duplicate_keeps_first_occurrence(tmp_path, catalogue):
    second = VALID.replace(",2,", ",5,")
    result = load_orders(write_csv(tmp_path, VALID, second, VALID), catalogue, "2026-02")
    assert [line.quantity for line in result.lines] == [2]
    assert [r.reason for r in result.rejected] == ["duplicate_line", "duplicate_line"]


def test_rejected_line_keeps_line_number_and_raw_row(tmp_path, catalogue):
    bad = "O-2,L-2,2026-02-11,C-0001,P-0001,2,117.06, it ,"
    result = load_orders(write_csv(tmp_path, VALID, bad), catalogue, "2026-02")
    [rejected] = result.rejected
    assert rejected.line_number == 3  # header is line 1
    assert rejected.raw["country"] == " it "
    assert rejected.raw["order_line_id"] == "L-2"


def test_invalid_lines_are_not_fatal_and_order_is_kept(tmp_path, catalogue):
    rows = [
        VALID,
        "O-2,L-2,2026-02-11,C-0001,P-0001,x,117.06,FR,",
        VALID.replace("L-1", "L-3").replace(",2,", ",7,"),
    ]
    result = load_orders(write_csv(tmp_path, *rows), catalogue, "2026-02")
    assert [line.order_line_id for line in result.lines] == ["L-1", "L-3"]
    assert [r.line_number for r in result.rejected] == [3]
