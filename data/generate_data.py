"""Generate synthetic data for the ucode Vibe Coding workshop.

Writes 8 tables to a target Databricks catalog/schema via Databricks Connect:
- dims_stores                       (default 20 rows)
- dims_items                        (default 50 rows)
- dims_employees                    (~12/store)
- facts_sales_daypart               (days x stores x 4 dayparts)
- facts_labor_daypart               (days x stores x 4 dayparts x 4 roles)
- facts_sales_inventory_daily       (days x stores x SKUs)
- facts_purchase_orders             (~5 staged POs per store)
- facts_customer_feedback           (default 1000 rows, with pre-staged sentiment/theme/ai_drafted_reply)

Usage:
    pip install databricks-connect faker
    python generate_data.py --profile DEFAULT --catalog ioc_sandbox --schema vibe_workshop
"""
from __future__ import annotations

import argparse
import random
from datetime import date, datetime, timedelta
from decimal import Decimal

from faker import Faker


def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()

REGIONS = ["West", "Central", "East"]
ROLES = ["cook", "cashier", "lead", "manager"]
ROLE_RATES = {"cook": 18.50, "cashier": 17.25, "lead": 21.00, "manager": 28.00}

DAYPARTS = [
    ("breakfast", 6, 10, 0.14, 220),
    ("lunch",     11, 14, 0.54, 760),
    ("dinner",    17, 20, 0.19, 280),
    ("late",      20, 23, 0.13, 180),
]

# Role mix per daypart matches the design's planner. Tuples sum to 1.0.
ROLE_MIX = {
    "breakfast": {"cook": 0.40, "cashier": 0.40, "lead": 0.20, "manager": 0.00},
    "lunch":     {"cook": 0.45, "cashier": 0.35, "lead": 0.13, "manager": 0.07},
    "dinner":    {"cook": 0.45, "cashier": 0.33, "lead": 0.15, "manager": 0.07},
    "late":      {"cook": 0.43, "cashier": 0.43, "lead": 0.14, "manager": 0.00},
}
ROLE_FLOORS = {
    "breakfast": {"cook": 1, "cashier": 1, "lead": 1, "manager": 0},
    "lunch":     {"cook": 2, "cashier": 1, "lead": 1, "manager": 1},
    "dinner":    {"cook": 2, "cashier": 1, "lead": 1, "manager": 1},
    "late":      {"cook": 1, "cashier": 1, "lead": 1, "manager": 0},
}
TARGET_RPLH = {"breakfast": 80, "lunch": 100, "dinner": 85, "late": 60}

CATEGORIES = ["produce", "proteins", "dry_goods", "beverage"]
ITEM_NAMES = {
    "produce":   ["Hass Avocado", "Romaine Hearts", "Roma Tomato", "Yellow Onion", "Jalapeno", "Cilantro", "Lime", "Bell Pepper", "Garlic", "Lemon"],
    "proteins":  ["Grilled Chicken", "Carnitas", "Carne Asada", "Black Beans", "Pinto Beans", "Tofu", "Ground Beef", "Shrimp", "Chorizo", "Eggs"],
    "dry_goods": ["Rice", "Tortilla (Flour)", "Tortilla (Corn)", "Cheese (Cheddar)", "Sour Cream", "Salsa Verde", "Chips (Tortilla)", "Guacamole", "Pickled Onion", "Hot Sauce"],
    "beverage":  ["Agua Fresca", "Bottled Water", "Cola", "Lemonade", "Cold Brew", "Iced Tea", "Margarita Mix", "Sparkling Water", "Mexican Coke", "Horchata"],
}
VENDORS = {
    "produce":   ("Bay Produce Co.", 1),
    "proteins":  ("Golden Gate Proteins", 2),
    "dry_goods": ("Pacific Dry Goods", 3),
    "beverage":  ("Coastal Beverage Supply", 2),
}

FEEDBACK_CHANNELS = ["google", "yelp", "app", "survey", "social"]
THEMES = ["pickup_wait", "stockout", "friendly_staff", "freshness", "value", "other"]

REVIEW_TEMPLATES_BY_THEME = {
    "pickup_wait":    [
        "Mobile order said ready but I waited {n} min at the {city} pickup window.",
        "Friday lunch at {city} was understaffed at mobile pickup. Slow.",
        "Waited too long for an online order at {city}. Food was fine once it arrived.",
    ],
    "stockout":       [
        "{city} was out of guac again. Second time this month.",
        "Carnitas was 86'd by 1pm at {city}. Disappointing.",
        "No agua fresca at {city} today. Hard pass on the swap.",
    ],
    "friendly_staff": [
        "Cashier at {city} remembered my usual. Best service in town.",
        "Manager at {city} went above and beyond when my order got mixed up.",
        "Staff at {city} is always upbeat. Keeps me coming back.",
    ],
    "freshness":      [
        "Lunch bowl at {city} was perfect. Fresh and bright.",
        "Salsa at {city} tastes house-made. Great quality.",
        "Tortillas at {city} were warm and fresh today.",
    ],
    "value":          [
        "Portion sizes at {city} have shrunk. Same price though.",
        "Decent value at {city} for the lunch combo.",
        "{city} bowl filled me up. Worth the money.",
    ],
    "other":          [
        "Quick visit at {city}. Nothing remarkable, nothing wrong.",
        "Stopped at {city} on a road trip. Standard.",
        "{city} location is clean and easy parking.",
    ],
}
THEME_WEIGHTS = {"pickup_wait": 0.15, "stockout": 0.10, "friendly_staff": 0.25, "freshness": 0.20, "value": 0.10, "other": 0.20}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_spark(profile: str):
    from databricks.connect import DatabricksSession  # type: ignore
    return DatabricksSession.builder.profile(profile).serverless().getOrCreate()


def write_table(spark, rows, table):
    if not rows:
        return
    df = spark.createDataFrame(rows)
    print(f"writing {table}: {df.count():,} rows")
    df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(table)


def dec(x):
    return Decimal(f"{x:.2f}")


# ---------------------------------------------------------------------------
# Dim generators
# ---------------------------------------------------------------------------

def gen_stores(fake: Faker, n: int):
    rows = []
    for i in range(n):
        rows.append({
            "store_id": f"S{i+1:03d}",
            "store_name": f"#{i+1:04d} · {fake.city()}",
            "region": random.choice(REGIONS),
            "city": fake.city(),
            "state": fake.state_abbr(),
            "square_footage": random.randint(1500, 6000),
        })
    return rows


def gen_items(n: int):
    rows = []
    sku_n = 1
    while len(rows) < n:
        cat = random.choice(CATEGORIES)
        name = random.choice(ITEM_NAMES[cat])
        cost = round(random.uniform(0.5, 12.0), 2)
        retail = round(cost * random.uniform(1.5, 3.0), 2)
        rows.append({
            "sku": f"SKU-{sku_n:04d}",
            "item_name": name,
            "category": cat,
            "retail_price": dec(retail),
            "cost": dec(cost),
        })
        sku_n += 1
    return rows


def gen_employees(fake: Faker, stores: list[dict], end_date):
    rows = []
    eid = 1
    for s in stores:
        # ~12 per store: 5 cooks, 4 cashiers, 2 leads, 1 manager
        plan = [("cook", 5), ("cashier", 4), ("lead", 2), ("manager", 1)]
        for role, count in plan:
            for _ in range(count):
                rows.append({
                    "employee_id": f"E{eid:05d}",
                    "store_id": s["store_id"],
                    "name": fake.name(),
                    "role": role,
                    "hourly_rate": dec(ROLE_RATES[role] + random.uniform(-1.0, 2.0)),
                    "hire_date": end_date - timedelta(days=random.randint(30, 5*365)),
                })
                eid += 1
    return rows


# ---------------------------------------------------------------------------
# Fact generators
# ---------------------------------------------------------------------------

def gen_sales_daypart(stores, days, end_date):
    rows = []
    for d in range(days):
        cur = end_date - timedelta(days=d)
        weekday_factor = 1.15 if cur.weekday() in (4, 5) else 0.95 if cur.weekday() == 1 else 1.0
        # Each store has its own daily total around $14-18k
        for s in stores:
            store_total = random.uniform(13000, 18000) * weekday_factor
            store_traffic = int(random.uniform(450, 700) * weekday_factor)
            for daypart, hs, he, rev_share, traffic_share in DAYPARTS:
                # actuals (with noise on share)
                share = rev_share + random.uniform(-0.02, 0.02)
                rev = max(0.0, store_total * share)
                traffic = int(store_traffic * (traffic_share / 1440.0))  # rough
                # forecast = actual + small noise (forecast made the day before)
                fcast_rev = rev * random.uniform(0.92, 1.08)
                fcast_traffic = int(traffic * random.uniform(0.92, 1.08))
                rows.append({
                    "date": cur,
                    "store_id": s["store_id"],
                    "daypart": daypart,
                    "hour_start": hs,
                    "hour_end": he,
                    "revenue": dec(rev),
                    "forecast_revenue": dec(fcast_rev),
                    "traffic": traffic,
                    "forecast_traffic": fcast_traffic,
                })
    return rows


def _staffing(revenue, daypart):
    """Compute headcount, hours, cost for a daypart given revenue."""
    hours_per_shift = (DAYPARTS[[d[0] for d in DAYPARTS].index(daypart)][2] -
                       DAYPARTS[[d[0] for d in DAYPARTS].index(daypart)][1])
    labor_hours = max(0.0, revenue / TARGET_RPLH[daypart])
    headcount = max(0, int(round(labor_hours / hours_per_shift)))

    floors = ROLE_FLOORS[daypart]
    mix = ROLE_MIX[daypart]
    assigned = {r: floors[r] for r in ROLES}
    remaining = max(0, headcount - sum(assigned.values()))
    # Allocate remaining by mix order
    order = sorted(ROLES, key=lambda r: -mix[r])
    i = 0
    while remaining > 0:
        assigned[order[i % len(order)]] += 1
        remaining -= 1
        i += 1

    rows_per_role = {}
    for r, hc in assigned.items():
        hours = hc * hours_per_shift
        cost = hours * ROLE_RATES[r]
        rows_per_role[r] = (hc, round(hours, 1), round(cost, 2))
    return rows_per_role


def gen_labor_daypart(sales_dp_rows):
    rows = []
    for sr in sales_dp_rows:
        dp = sr["daypart"]
        actual = _staffing(float(sr["revenue"]), dp)
        forecast = _staffing(float(sr["forecast_revenue"]), dp)
        for role in ROLES:
            ah, ahours, acost = actual[role]
            fh, fhours, fcost = forecast[role]
            rows.append({
                "date": sr["date"],
                "store_id": sr["store_id"],
                "daypart": dp,
                "role": role,
                "headcount": ah,
                "total_hours": ahours,
                "labor_cost": dec(acost),
                "forecast_headcount": fh,
                "forecast_labor_cost": dec(fcost),
            })
    return rows


def gen_sales_inventory(stores, items, days, end_date):
    rows = []
    for d in range(days):
        cur = end_date - timedelta(days=d)
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
                    "revenue": dec(rev),
                    "on_hand_eod": on_hand,
                    "reorder_point": reorder,
                })
    return rows


def gen_purchase_orders(stores, items, inventory_rows, end_date, pos_per_store: int = 5):
    """Generate staged POs by pulling the most recent low-stock items per store
    and grouping into a small number of POs per vendor category.
    """
    now = datetime.combine(end_date, datetime.min.time()).replace(hour=13)
    # Items grouped by category
    items_by_sku = {it["sku"]: it for it in items}
    # Latest inventory snapshot per (store, sku)
    latest = {}
    for r in inventory_rows:
        key = (r["store_id"], r["sku"])
        if key not in latest or r["date"] > latest[key]["date"]:
            latest[key] = r

    rows = []
    po_n = 1
    for s in stores:
        # Items currently below par (on_hand < reorder_point), grouped by category
        low_items = []
        for sku, it in items_by_sku.items():
            snap = latest.get((s["store_id"], sku))
            if snap and snap["on_hand_eod"] < snap["reorder_point"]:
                low_items.append((it, snap))
        if not low_items:
            continue
        # Group by category, pick up to `pos_per_store` POs
        by_cat: dict[str, list] = {}
        for it, snap in low_items:
            by_cat.setdefault(it["category"], []).append((it, snap))
        cats_to_use = list(by_cat.keys())[:pos_per_store]
        for cat in cats_to_use:
            vendor_name, lead = VENDORS[cat]
            po_id = f"PO-{po_n:06d}"
            po_n += 1
            created = now - timedelta(hours=random.randint(2, 20))
            eta = created + timedelta(days=lead, hours=random.randint(-2, 6))
            status = random.choices(["staged", "released", "delivered"], weights=[6, 3, 1])[0]
            for it, snap in by_cat[cat][:6]:  # cap line count per PO
                par = snap["reorder_point"]
                qty = max(1, par - snap["on_hand_eod"] + random.randint(0, 4))
                line_total = round(qty * float(it["cost"]), 2)
                trend = random.choices(["+22% usage", "+18% usage", "+9% usage", "steady", "steady"], k=1)[0]
                rows.append({
                    "po_id": po_id,
                    "store_id": s["store_id"],
                    "vendor_name": vendor_name,
                    "vendor_category": cat,
                    "lead_time_days": lead,
                    "sku": it["sku"],
                    "qty": qty,
                    "unit_cost": dec(float(it["cost"])),
                    "line_total": dec(line_total),
                    "on_hand_at_creation": snap["on_hand_eod"],
                    "par": par,
                    "usage_trend": trend,
                    "created_at": created,
                    "eta": eta,
                    "status": status,
                })
    return rows


# Pre-baked reply templates so attendees see immediately-useful drafts. The
# real workshop swaps these for ai_query() at runtime if they want to.
def _drafted_reply(rating, theme, city):
    if rating >= 4:
        return f"Thanks for the kind words about our {city} location! We'll share this with the team."
    if rating == 3 and theme == "stockout":
        return f"Hi, sorry we ran out at {city}. We've bumped the order and you should be covered next time."
    if rating == 3 and theme == "pickup_wait":
        return f"Thanks for the patience at {city}. We're adding a runner for that pickup window."
    if rating == 3:
        return f"Appreciate the feedback. We'd love to make your next {city} visit even better."
    if theme == "pickup_wait":
        return f"Hi, sorry we held you up at {city}. Friday lunch caught us short-staffed at mobile pickup; we've added a runner for that window."
    if theme == "stockout":
        return f"Hi, sorry the item was out at {city}. We've increased the order so you'll be covered on your next visit."
    return f"Hi — we're sorry your {city} visit fell short. Reach out to our store manager and we'll make it right."


def gen_feedback(fake: Faker, stores, n: int, end_date):
    rows = []
    themes_list = list(THEME_WEIGHTS.keys())
    weights = list(THEME_WEIGHTS.values())
    for i in range(n):
        s = random.choice(stores)
        ch = random.choice(FEEDBACK_CHANNELS)
        rating = random.choices([1, 2, 3, 4, 5], weights=[1, 1, 2, 4, 4])[0]
        theme = random.choices(themes_list, weights=weights)[0]
        if rating >= 4 and theme in ("pickup_wait", "stockout", "value"):
            theme = "friendly_staff" if random.random() < 0.5 else "freshness"
        if rating <= 2 and theme in ("friendly_staff", "freshness"):
            theme = random.choices(["pickup_wait", "stockout", "value"], k=1)[0]
        sent = "pos" if rating >= 4 else ("neg" if rating <= 2 else "neu")
        templates = REVIEW_TEMPLATES_BY_THEME[theme]
        feedback_text = random.choice(templates).format(city=s["city"], n=random.randint(10, 25))
        needs_reply = (rating <= 3 and random.random() < 0.6) or random.random() < 0.05
        rows.append({
            "feedback_id": f"FB-{i+1:06d}",
            "date": end_date - timedelta(days=random.randint(0, 60)),
            "store_id": s["store_id"],
            "channel": ch,
            "rating": rating,
            "feedback_text": feedback_text,
            "sentiment_label": sent,
            "theme": theme,
            "nps": (rating * 25 - 50) if ch == "survey" else None,
            "needs_reply": needs_reply,
            "ai_drafted_reply": _drafted_reply(rating, theme, s["city"]),
        })
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="DEFAULT")
    ap.add_argument("--catalog", default="ioc_sandbox")
    ap.add_argument("--schema", default="vibe_workshop")
    ap.add_argument("--stores", type=int, default=20)
    ap.add_argument("--items", type=int, default=50)
    ap.add_argument("--days", type=int, default=60)
    ap.add_argument("--end-date", type=parse_date, default=date.today(),
                    help="Latest date in the generated data, YYYY-MM-DD. Defaults to today.")
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

    print(f"generating with end_date={args.end_date}, days={args.days}")
    stores = gen_stores(fake, args.stores)
    items = gen_items(args.items)
    employees = gen_employees(fake, stores, args.end_date)
    write_table(spark, stores, "dims_stores")
    write_table(spark, items, "dims_items")
    write_table(spark, employees, "dims_employees")

    sales_dp = gen_sales_daypart(stores, args.days, args.end_date)
    write_table(spark, sales_dp, "facts_sales_daypart")

    labor_dp = gen_labor_daypart(sales_dp)
    write_table(spark, labor_dp, "facts_labor_daypart")

    inventory = gen_sales_inventory(stores, items, args.days, args.end_date)
    write_table(spark, inventory, "facts_sales_inventory_daily")

    pos = gen_purchase_orders(stores, items, inventory, args.end_date)
    write_table(spark, pos, "facts_purchase_orders")

    feedback = gen_feedback(fake, stores, args.feedback, args.end_date)
    write_table(spark, feedback, "facts_customer_feedback")

    print("done.")


if __name__ == "__main__":
    main()
