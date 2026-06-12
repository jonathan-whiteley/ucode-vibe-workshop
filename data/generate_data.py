"""Generate synthetic data for the LCE Operator Command Center workshop.

Writes 5 tables to `ioc_sandbox.vibe_workshop` via Databricks Connect:
- dims_stores       (20 rows)
- dims_items        (~50 rows)
- facts_labor_daily (365 days x 20 stores x ~4 roles = ~30K rows)
- facts_sales_inventory_daily (365 days x 20 stores x 50 SKUs = ~365K rows)
- facts_customer_feedback (~1000 rows)

Usage:
    pip install databricks-connect faker
    python generate_data.py --profile DEFAULT --catalog ioc_sandbox --schema vibe_workshop
"""
from __future__ import annotations

import argparse
import random
from datetime import date, timedelta
from decimal import Decimal

from faker import Faker

REGIONS = ["West", "Central", "East"]
ROLES = ["manager", "cashier", "prep", "cleaner"]
CATEGORIES = ["proteins", "produce", "bakery", "beverages", "household", "frozen"]
FEEDBACK_CHANNELS = ["review", "survey", "social", "in-store"]

REVIEW_TEMPLATES = [
    "Great experience at {city}, staff was friendly.",
    "Long wait at the {city} store today, but food was solid.",
    "Items were out of stock at {city} again, frustrating.",
    "Loved the new menu at {city}!",
    "Manager at {city} went above and beyond.",
    "Quality has slipped at {city} lately.",
    "{city} is my go-to. Consistent and clean.",
    "Cashier at {city} was rude. Disappointed.",
]


def build_spark(profile: str):
    from databricks.connect import DatabricksSession  # type: ignore
    return DatabricksSession.builder.profile(profile).serverless().getOrCreate()


def gen_stores(fake: Faker, n: int = 20):
    rows = []
    for i in range(n):
        sid = f"S{i+1:03d}"
        rows.append({
            "store_id": sid,
            "store_name": f"LCE {fake.city()}",
            "region": random.choice(REGIONS),
            "city": fake.city(),
            "state": fake.state_abbr(),
            "square_footage": random.randint(1500, 6000),
        })
    return rows


def gen_items(fake: Faker, n: int = 50):
    rows = []
    for i in range(n):
        cost = round(random.uniform(0.5, 12.0), 2)
        retail = round(cost * random.uniform(1.5, 3.0), 2)
        rows.append({
            "sku": f"SKU-{i+1:04d}",
            "item_name": fake.word().title() + " " + random.choice(["Pack", "Bundle", "Single", "Family"]),
            "category": random.choice(CATEGORIES),
            "retail_price": Decimal(str(retail)),
            "cost": Decimal(str(cost)),
        })
    return rows


def gen_labor(stores: list[dict], days: int = 365):
    today = date.today()
    rows = []
    for d in range(days):
        cur = today - timedelta(days=d)
        for s in stores:
            for role in ROLES:
                head = random.randint(1, 4) if role != "manager" else 1
                hours = round(head * random.uniform(6, 9), 1)
                cost = round(hours * random.uniform(15, 30), 2)
                rows.append({
                    "date": cur,
                    "store_id": s["store_id"],
                    "role": role,
                    "headcount": head,
                    "total_hours": hours,
                    "labor_cost": Decimal(str(cost)),
                })
    return rows


def gen_sales_inventory(stores: list[dict], items: list[dict], days: int = 365):
    today = date.today()
    rows = []
    for d in range(days):
        cur = today - timedelta(days=d)
        for s in stores:
            for it in items:
                units = max(0, int(random.gauss(20, 8)))
                rev = round(units * float(it["retail_price"]), 2)
                on_hand = max(0, random.randint(0, 80))
                reorder = random.choice([10, 20, 30])
                rows.append({
                    "date": cur,
                    "store_id": s["store_id"],
                    "sku": it["sku"],
                    "units_sold": units,
                    "revenue": Decimal(str(rev)),
                    "on_hand_eod": on_hand,
                    "reorder_point": reorder,
                })
    return rows


def gen_feedback(fake: Faker, stores: list[dict], n: int = 1000):
    today = date.today()
    rows = []
    for i in range(n):
        s = random.choice(stores)
        ch = random.choice(FEEDBACK_CHANNELS)
        rating = random.choices([1, 2, 3, 4, 5], weights=[1, 1, 2, 4, 4])[0]
        template = random.choice(REVIEW_TEMPLATES)
        rows.append({
            "feedback_id": f"FB-{i+1:06d}",
            "date": today - timedelta(days=random.randint(0, 365)),
            "store_id": s["store_id"],
            "channel": ch,
            "rating": rating,
            "feedback_text": template.format(city=s["city"]),
            "nps": (rating * 25 - 50) if ch == "survey" else None,
        })
    return rows


def write_table(spark, rows: list[dict], table: str):
    if not rows:
        return
    df = spark.createDataFrame(rows)
    print(f"writing {table}: {df.count():,} rows")
    df.write.mode("overwrite").saveAsTable(table)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="DEFAULT")
    ap.add_argument("--catalog", default="ioc_sandbox")
    ap.add_argument("--schema", default="vibe_workshop")
    ap.add_argument("--stores", type=int, default=20)
    ap.add_argument("--items", type=int, default=50)
    ap.add_argument("--days", type=int, default=365)
    ap.add_argument("--feedback", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    random.seed(args.seed)
    fake = Faker()
    Faker.seed(args.seed)

    spark = build_spark(args.profile)
    spark.sql(f"USE CATALOG {args.catalog}")
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {args.schema}")
    spark.sql(f"USE SCHEMA {args.schema}")

    stores = gen_stores(fake, args.stores)
    items = gen_items(fake, args.items)
    write_table(spark, stores, "dims_stores")
    write_table(spark, items, "dims_items")
    write_table(spark, gen_labor(stores, args.days), "facts_labor_daily")
    write_table(spark, gen_sales_inventory(stores, items, args.days), "facts_sales_inventory_daily")
    write_table(spark, gen_feedback(fake, stores, args.feedback), "facts_customer_feedback")

    print("done.")


if __name__ == "__main__":
    main()
