# Spec — Order pricing

This document is the business reference for computing the total of an order.
It was written by the sales team. When the code and this document disagree,
this document wins.

## Public API

```python
compute_order_total(order: Order, customer: Customer) -> PriceBreakdown
```

`PriceBreakdown` reports: `subtotal`, `volume_discount`, `loyalty_discount`,
`promo_discount`, `discounted_subtotal`, `shipping`, `vat`, `total`. All values are in euros.

## Rules

1. **Line amount** = `quantity × unit_price`. The **subtotal** is the sum of the line amounts.
2. **Volume discount per line:** 5% of the line amount when quantity ≥ 10,
   10% when quantity ≥ 50. The two rates are not cumulative: a line of 60 units gets 10%.
3. **Loyalty discount:** gold customers get 3% off the order subtotal *after* volume discounts.
4. **Promo code `WELCOME10`:** 10% off the subtotal, only on the customer's first order,
   capped at €50. An order is the customer's first order when its `order_date` equals the
   customer's `first_order_date`. A `WELCOME10` code on any other order is ignored.
   Promo codes cannot be combined with other discounts.
5. **Shipping:** free when the discounted subtotal (before VAT) is ≥ €100,
   otherwise €6.90.
6. **VAT** by country: FR 20%, DE 19%, ES 21%, BE 21%. VAT applies to the discounted
   subtotal *and* to shipping.
7. **Rounding:** compute with `Decimal` at full precision, and round once at the end of the
   order, to the cent, half-up. The other values of the breakdown are rounded the same way
   for display only, so they may differ from the total by one cent when added up.

## Worked example 1 — standard customer, France

| Line | Quantity | Unit price | Line amount | Volume discount | After discount |
|------|---------:|-----------:|------------:|----------------:|---------------:|
| 1 | 12 | 3.47 | 41.64 | 5% = 2.082 | 39.558 |
| 2 | 4 | 8.90 | 35.60 | none | 35.60 |

- Subtotal: 41.64 + 35.60 = **77.24**
- Volume discount: **2.082**, so subtotal after volume discount = **75.158**
- Loyalty: standard customer, none. Promo: none.
- Discounted subtotal: **75.158**, which is below 100, so shipping = **6.90**
- VAT base: 75.158 + 6.90 = 82.058; VAT 20% = **16.4116**
- Total at full precision: 82.058 + 16.4116 = 98.4696, rounded: **98.47**

## Worked example 2 — gold customer, Germany

| Line | Quantity | Unit price | Line amount | Volume discount | After discount |
|------|---------:|-----------:|------------:|----------------:|---------------:|
| 1 | 50 | 1.25 | 62.50 | 10% = 6.25 | 56.25 |
| 2 | 2 | 19.99 | 39.98 | none | 39.98 |

- Subtotal: 62.50 + 39.98 = **102.48**
- Volume discount: **6.25**, so subtotal after volume discount = **96.23**
- Loyalty: 3% of 96.23 = **2.8869**. Promo: none.
- Discounted subtotal: 96.23 − 2.8869 = **93.3431**, which is below 100, so shipping = **6.90**
- VAT base: 93.3431 + 6.90 = 100.2431; VAT 19% = **19.046189**
- Total at full precision: 100.2431 + 19.046189 = 119.289289, rounded: **119.29**
