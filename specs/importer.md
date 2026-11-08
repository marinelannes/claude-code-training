# Spec — Order file importer

Northwind Supplies receives one CSV file of order lines per month from its web shop.
The importer reads such a file, keeps the valid lines and reports the invalid ones.
An invalid line must never stop the import.

## Public API

```python
load_orders(path: Path, catalogue: dict[str, Product], month: str) -> ImportResult
```

- `path`: the CSV file (UTF-8, comma-separated, one header row).
- `catalogue`: products by `product_id` (see `orders.loaders.load_catalogue`).
- `month`: the expected period, formatted `YYYY-MM` (for example `2026-02`).
- Returns an `ImportResult` with `lines` (valid `OrderLine` objects, in file order) and
  `rejected` (`RejectedLine` objects, in file order).

## Columns

Required columns: `order_id`, `order_line_id`, `order_date`, `customer_id`, `product_id`,
`quantity`, `unit_price`, `country`.

Optional column: `promo_code`. When the column is absent or the value is empty,
`OrderLine.promo_code` is `None`.

If any required column is missing from the header, `load_orders` raises
`MissingColumnError`, naming the missing columns. Extra columns are ignored.

## Normalisation

Before validation, every value is stripped of surrounding whitespace, and the country code
is upper-cased. `fr` and `" FR "` are therefore both valid and become `FR`.

## Validation rules

Checks run in this order. A line is rejected with the reason code of the **first** check
that fails.

| # | Rule | Reason code |
|---|------|-------------|
| 1 | Every required value is non-empty | `missing_value` |
| 2 | `order_date` is a valid date written exactly `YYYY-MM-DD` | `bad_date` |
| 3 | `order_date` falls inside `month` | `out_of_period` |
| 4 | `quantity` is an integer written with digits only, and is > 0 | `bad_quantity` |
| 5 | `unit_price` is a decimal number (`.` as separator) and is ≥ 0 | `bad_price` |
| 6 | `product_id` exists in the catalogue | `unknown_product` |
| 7 | The product is active | `inactive_product` |
| 8 | `country` is one of `FR`, `DE`, `ES`, `BE` | `bad_country` |
| 9 | `order_line_id` has not already been accepted earlier in the file | `duplicate_line` |

Notes:

- A price of `0.00` is valid (free samples).
- For rule 9, the first valid occurrence is kept and every later line with the same
  `order_line_id` is rejected.
- The unit price of the line is used as is. It is not compared with the catalogue price.
- Customers are not checked by the importer.

## Rejected lines

Each `RejectedLine` holds:

- `line_number`: the physical line number in the file, where the header is line 1
  (so the first data row is line 2);
- `reason`: one of the reason codes above;
- `raw`: the row exactly as read from the file (a `dict` of column → original string,
  before stripping).
