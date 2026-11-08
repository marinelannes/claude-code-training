# Monthly report - Northwind Supplies
# Run from the repo root: python scripts/monthly_report.py
# Finance imports out/report_2026_01.csv every month, DO NOT change the format!!
# (last touched before the pricing module existed, so prices are computed here)

import os
import sys

import pandas as pd

DATA = "data"
OUT = "out"
MONTH = "2026_01"

df = None
prods = None
custs = None
rows = []
nb = 0


def load():
    global df, prods, custs
    df = pd.read_csv(DATA + "/orders_" + MONTH + ".csv", dtype={"promo_code": str})
    prods = pd.read_csv(DATA + "/products.csv")
    custs = pd.read_csv(DATA + "/customers_pii.csv")
    print("loaded", len(df), "order lines,", len(prods), "products,", len(custs), "customers")


def vol(q):
    # volume discount
    if q >= 50:
        return 0.10
    elif q >= 10:
        return 0.05
    return 0.0


def old_discount(amount, qty):
    # rule used before 2025, keep it in case sales want it back
    if qty > 20:
        return amount * 0.93
    if qty > 5:
        return amount * 0.97
    return amount


def fmt(x):
    return "%.2f" % x


def add(section, key, label, value):
    rows.append([section, key, label, value])


def main():
    global nb
    load()

    # lookups
    cat = {}
    for i, r in prods.iterrows():
        cat[r["product_id"]] = (r["category"], r["name"])
    tier = {}
    for i, r in custs.iterrows():
        tier[r["customer_id"]] = r["tier"]

    # group lines by order
    data = {}
    for i, r in df.iterrows():
        oid = r["order_id"]
        if oid not in data:
            data[oid] = {"customer": r["customer_id"], "country": r["country"], "lines": []}
        data[oid]["lines"].append((r["product_id"], int(r["quantity"]), float(r["unit_price"])))
    nb = len(data)
    print("orders:", nb)
    # TODO promo codes (WELCOME10) are not handled here yet

    # ---------------- FR ----------------
    fr_net = 0.0
    fr_ship = 0.0
    fr_vat = 0.0
    fr_n = 0
    for oid in data:
        o = data[oid]
        if o["country"] != "FR":
            continue
        s = 0.0
        for p, q, up in o["lines"]:
            s = s + q * up * (1 - vol(q))
        if tier[o["customer"]] == "gold":
            s = s * 0.97
        ship = 0.0
        if s < 100:
            ship = 6.90
        fr_net += s
        fr_ship += ship
        fr_vat += (s + ship) * 0.20
        fr_n += 1
    print("FR:", fr_n, "orders, net", fmt(fr_net))
    add("country", "FR", "orders", str(fr_n))
    add("country", "FR", "net", fmt(fr_net))
    add("country", "FR", "shipping", fmt(fr_ship))
    add("country", "FR", "vat", fmt(fr_vat))
    add("country", "FR", "gross", fmt(fr_net + fr_ship + fr_vat))

    # ---------------- DE ----------------
    de_net = 0.0
    de_ship = 0.0
    de_vat = 0.0
    de_n = 0
    for oid in data:
        order = data[oid]
        if order["country"] == "DE":
            total = 0.0
            for p, q, up in order["lines"]:
                total = total + q * up * (1 - vol(q))
            if tier[order["customer"]] == "gold":
                total = total * 0.97
            shipping = 6.90 if total < 100 else 0.0
            de_net += total
            de_ship += shipping
            de_vat += (total + shipping) * 0.19
            de_n = de_n + 1
    print("DE:", de_n, "orders, net", fmt(de_net))
    add("country", "DE", "orders", str(de_n))
    add("country", "DE", "net", fmt(de_net))
    add("country", "DE", "shipping", fmt(de_ship))
    add("country", "DE", "vat", fmt(de_vat))
    add("country", "DE", "gross", fmt(de_net + de_ship + de_vat))

    # ---------------- ES ----------------
    es_net = 0.0
    es_ship = 0.0
    es_vat = 0.0
    es_n = 0
    for oid in data:
        o = data[oid]
        if o["country"] != "ES":
            continue
        s = 0.0
        for p, q, up in o["lines"]:
            s = s + q * up * (1 - vol(q))
        if tier[o["customer"]] == "gold":
            s = s * 0.97
        ship = 0.0
        if s < 100:
            ship = 6.90
        es_net += s
        es_ship += ship
        es_vat += (s + ship) * 0.21
        es_n += 1
    print("ES:", es_n, "orders, net", fmt(es_net))
    add("country", "ES", "orders", str(es_n))
    add("country", "ES", "net", fmt(es_net))
    add("country", "ES", "shipping", fmt(es_ship))
    add("country", "ES", "vat", fmt(es_vat))
    add("country", "ES", "gross", fmt(es_net + es_ship + es_vat))

    # ---------------- BE ----------------
    # same as ES (21%)
    be_net = 0.0
    be_ship = 0.0
    be_vat = 0.0
    be_n = 0
    for oid in data:
        o = data[oid]
        if o["country"] != "BE":
            continue
        s = 0.0
        for p, q, up in o["lines"]:
            s += q * up * (1 - vol(q))
        if tier[o["customer"]] == "gold":
            s = s * 0.97
        ship = 0.0
        if s < 100:
            ship = 6.90
        be_net += s
        be_ship += ship
        be_vat += (s + ship) * 0.21
        be_n += 1
    print("BE:", be_n, "orders, net", fmt(be_net))
    add("country", "BE", "orders", str(be_n))
    add("country", "BE", "net", fmt(be_net))
    add("country", "BE", "shipping", fmt(be_ship))
    add("country", "BE", "vat", fmt(be_vat))
    add("country", "BE", "gross", fmt(be_net + be_ship + be_vat))

    # categories (net of volume discount, before loyalty)
    bycat = {}
    for oid in data:
        for p, q, up in data[oid]["lines"]:
            c = cat[p][0]
            bycat[c] = bycat.get(c, 0.0) + q * up * (1 - vol(q))
    for c in sorted(bycat):
        print("  ", c, fmt(bycat[c]))
        add("category", c, "net", fmt(bycat[c]))

    # top 10 products
    tmp = {}
    for oid in data:
        for p, q, up in data[oid]["lines"]:
            tmp[p] = tmp.get(p, 0.0) + q * up * (1 - vol(q))
    best = sorted(tmp.items(), key=lambda x: (-round(x[1], 2), x[0]))[:10]
    k = 1
    for p, v in best:
        add("top_product", "%02d" % k, p + " " + cat[p][1], fmt(v))
        print("  #%d" % k, p, cat[p][1], fmt(v))
        k += 1

    # kpis
    gross = (
        fr_net + fr_ship + fr_vat + de_net + de_ship + de_vat
        + es_net + es_ship + es_vat + be_net + be_ship + be_vat
    )
    big = 0
    for oid in data:
        s = 0.0
        for p, q, up in data[oid]["lines"]:
            s = s + q * up * (1 - vol(q))
        if tier[data[oid]["customer"]] == "gold":
            s = s * 0.97
        if s >= 100:
            big += 1
    data = sorted(set(df["customer_id"]))
    g = 0
    for c in data:
        if tier[c] == "gold":
            g += 1
    add("kpi", "orders", "count", str(nb))
    add("kpi", "gross_revenue", "eur", fmt(gross))
    add("kpi", "average_basket", "eur", fmt(gross / nb))
    add("kpi", "orders_over_100", "count", str(big))
    add("kpi", "customers", "count", str(len(data)))
    add("kpi", "gold_share", "percent", fmt(100.0 * g / len(data)))

    if not os.path.exists(OUT):
        os.makedirs(OUT)
    f = open(OUT + "/report_" + MONTH + ".csv", "w", newline="")
    f.write("section,key,label,value\n")
    for r in rows:
        f.write(",".join(r) + "\n")
    f.close()

    print("=" * 40)
    print("Monthly report", MONTH)
    print("orders:", nb)
    print("gross revenue:", fmt(gross))
    print("average basket:", fmt(gross / nb))
    print("orders over 100:", big)
    print("gold customers: %s%%" % fmt(100.0 * g / len(data)))
    print("written:", OUT + "/report_" + MONTH + ".csv")


if __name__ == "__main__":
    main()
