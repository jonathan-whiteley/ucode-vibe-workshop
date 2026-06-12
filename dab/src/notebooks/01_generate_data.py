# Databricks notebook source
# MAGIC %md
# MAGIC # ucode Vibe Workshop: Generate Synthetic Data
# MAGIC
# MAGIC Materializes the 8-table workshop schema in the target catalog/schema.
# MAGIC Runs the same generation logic as `data/generate_data.py` but uses the
# MAGIC notebook's built-in Spark session (no Databricks Connect needed).

# COMMAND ----------
# MAGIC %pip install -q faker

# COMMAND ----------
dbutils.library.restartPython()

# COMMAND ----------
dbutils.widgets.text("catalog", "ioc_sandbox")
dbutils.widgets.text("schema", "vibe_workshop")
dbutils.widgets.text("end_date", "2026-06-22")
dbutils.widgets.text("days", "60")
dbutils.widgets.text("stores", "20")
dbutils.widgets.text("items", "50")
dbutils.widgets.text("feedback", "1000")
dbutils.widgets.text("seed", "42")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
END_DATE = dbutils.widgets.get("end_date")
DAYS = int(dbutils.widgets.get("days"))
N_STORES = int(dbutils.widgets.get("stores"))
N_ITEMS = int(dbutils.widgets.get("items"))
N_FEEDBACK = int(dbutils.widgets.get("feedback"))
SEED = int(dbutils.widgets.get("seed"))

# COMMAND ----------
import random
from datetime import date, datetime, timedelta
from decimal import Decimal
from faker import Faker

random.seed(SEED)
fake = Faker()
Faker.seed(SEED)

end_date = datetime.strptime(END_DATE, "%Y-%m-%d").date()

spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
spark.sql(f"USE SCHEMA {SCHEMA}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Constants (mirrors data/generate_data.py)

# COMMAND ----------
REGIONS = ["West", "Central", "East"]
ROLES = ["cook", "cashier", "lead", "manager"]
ROLE_RATES = {"cook": 18.50, "cashier": 17.25, "lead": 21.00, "manager": 28.00}

DAYPARTS = [
    ("breakfast", 6, 10, 0.14, 220),
    ("lunch",     11, 14, 0.54, 760),
    ("dinner",    17, 20, 0.19, 280),
    ("late",      20, 23, 0.13, 180),
]

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
THEME_WEIGHTS = {"pickup_wait": 0.15, "stockout": 0.10, "friendly_staff": 0.25, "freshness": 0.20, "value": 0.10, "other": 0.20}

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

dec = lambda x: Decimal(f"{x:.2f}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Dim + fact generators
# MAGIC
# MAGIC (Identical to `data/generate_data.py`. If you change generation logic,
# MAGIC update both files.)

# COMMAND ----------
def gen_stores():
    rows = []
    for i in range(N_STORES):
        rows.append({
            "store_id": f"S{i+1:03d}",
            "store_name": f"#{i+1:04d} · {fake.city()}",
            "region": random.choice(REGIONS),
            "city": fake.city(),
            "state": fake.state_abbr(),
            "square_footage": random.randint(1500, 6000),
        })
    return rows

def gen_items():
    rows = []
    for i in range(N_ITEMS):
        cat = random.choice(CATEGORIES)
        cost = round(random.uniform(0.5, 12.0), 2)
        retail = round(cost * random.uniform(1.5, 3.0), 2)
        rows.append({
            "sku": f"SKU-{i+1:04d}",
            "item_name": random.choice(ITEM_NAMES[cat]),
            "category": cat,
            "retail_price": dec(retail),
            "cost": dec(cost),
        })
    return rows

def gen_employees(stores):
    rows = []
    eid = 1
    plan = [("cook", 5), ("cashier", 4), ("lead", 2), ("manager", 1)]
    for s in stores:
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

def gen_sales_daypart(stores):
    rows = []
    for d in range(DAYS):
        cur = end_date - timedelta(days=d)
        wd_factor = 1.15 if cur.weekday() in (4, 5) else 0.95 if cur.weekday() == 1 else 1.0
        for s in stores:
            store_total = random.uniform(13000, 18000) * wd_factor
            store_traffic = int(random.uniform(450, 700) * wd_factor)
            for daypart, hs, he, rev_share, traffic_share in DAYPARTS:
                share = rev_share + random.uniform(-0.02, 0.02)
                rev = max(0.0, store_total * share)
                traffic = int(store_traffic * (traffic_share / 1440.0))
                fcast_rev = rev * random.uniform(0.92, 1.08)
                fcast_traffic = int(traffic * random.uniform(0.92, 1.08))
                rows.append({
                    "date": cur, "store_id": s["store_id"], "daypart": daypart,
                    "hour_start": hs, "hour_end": he,
                    "revenue": dec(rev), "forecast_revenue": dec(fcast_rev),
                    "traffic": traffic, "forecast_traffic": fcast_traffic,
                })
    return rows

def staffing(revenue, daypart):
    hours_per_shift = [d for d in DAYPARTS if d[0]==daypart][0][2] - [d for d in DAYPARTS if d[0]==daypart][0][1]
    labor_hours = max(0.0, revenue / TARGET_RPLH[daypart])
    headcount = max(0, int(round(labor_hours / hours_per_shift)))
    floors = ROLE_FLOORS[daypart]
    mix = ROLE_MIX[daypart]
    assigned = {r: floors[r] for r in ROLES}
    remaining = max(0, headcount - sum(assigned.values()))
    order = sorted(ROLES, key=lambda r: -mix[r])
    i = 0
    while remaining > 0:
        assigned[order[i % len(order)]] += 1
        remaining -= 1
        i += 1
    out = {}
    for r, hc in assigned.items():
        h = hc * hours_per_shift
        c = h * ROLE_RATES[r]
        out[r] = (hc, round(h, 1), round(c, 2))
    return out

def gen_labor_daypart(sales_dp_rows):
    rows = []
    for sr in sales_dp_rows:
        dp = sr["daypart"]
        actual = staffing(float(sr["revenue"]), dp)
        forecast = staffing(float(sr["forecast_revenue"]), dp)
        for role in ROLES:
            ah, ahours, acost = actual[role]
            fh, fhours, fcost = forecast[role]
            rows.append({
                "date": sr["date"], "store_id": sr["store_id"], "daypart": dp, "role": role,
                "headcount": ah, "total_hours": ahours, "labor_cost": dec(acost),
                "forecast_headcount": fh, "forecast_labor_cost": dec(fcost),
            })
    return rows

def gen_sales_inventory(stores, items):
    rows = []
    for d in range(DAYS):
        cur = end_date - timedelta(days=d)
        for s in stores:
            for it in items:
                units = max(0, int(random.gauss(20, 8)))
                rev = round(units * float(it["retail_price"]), 2)
                on_hand = max(0, random.randint(0, 80))
                reorder = random.choice([10, 20, 30])
                rows.append({
                    "date": cur, "store_id": s["store_id"], "sku": it["sku"],
                    "units_sold": units, "revenue": dec(rev),
                    "on_hand_eod": on_hand, "reorder_point": reorder,
                })
    return rows

def gen_purchase_orders(stores, items, inventory_rows, pos_per_store=5):
    now = datetime.combine(end_date, datetime.min.time()).replace(hour=13)
    items_by_sku = {it["sku"]: it for it in items}
    latest = {}
    for r in inventory_rows:
        key = (r["store_id"], r["sku"])
        if key not in latest or r["date"] > latest[key]["date"]:
            latest[key] = r
    rows = []
    po_n = 1
    for s in stores:
        low = []
        for sku, it in items_by_sku.items():
            snap = latest.get((s["store_id"], sku))
            if snap and snap["on_hand_eod"] < snap["reorder_point"]:
                low.append((it, snap))
        if not low:
            continue
        by_cat = {}
        for it, snap in low:
            by_cat.setdefault(it["category"], []).append((it, snap))
        for cat in list(by_cat.keys())[:pos_per_store]:
            vendor_name, lead = VENDORS[cat]
            po_id = f"PO-{po_n:06d}"
            po_n += 1
            created = now - timedelta(hours=random.randint(2, 20))
            eta = created + timedelta(days=lead, hours=random.randint(-2, 6))
            status = random.choices(["staged", "released", "delivered"], weights=[6, 3, 1])[0]
            for it, snap in by_cat[cat][:6]:
                par = snap["reorder_point"]
                qty = max(1, par - snap["on_hand_eod"] + random.randint(0, 4))
                line_total = round(qty * float(it["cost"]), 2)
                trend = random.choices(["+22% usage", "+18% usage", "+9% usage", "steady", "steady"], k=1)[0]
                rows.append({
                    "po_id": po_id, "store_id": s["store_id"],
                    "vendor_name": vendor_name, "vendor_category": cat, "lead_time_days": lead,
                    "sku": it["sku"], "qty": qty,
                    "unit_cost": dec(float(it["cost"])), "line_total": dec(line_total),
                    "on_hand_at_creation": snap["on_hand_eod"], "par": par, "usage_trend": trend,
                    "created_at": created, "eta": eta, "status": status,
                })
    return rows

def drafted_reply(rating, theme, city):
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

def gen_feedback(stores):
    rows = []
    themes_list = list(THEME_WEIGHTS.keys())
    weights = list(THEME_WEIGHTS.values())
    for i in range(N_FEEDBACK):
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
        text = random.choice(templates).format(city=s["city"], n=random.randint(10, 25))
        needs_reply = (rating <= 3 and random.random() < 0.6) or random.random() < 0.05
        rows.append({
            "feedback_id": f"FB-{i+1:06d}",
            "date": end_date - timedelta(days=random.randint(0, 60)),
            "store_id": s["store_id"], "channel": ch, "rating": rating,
            "feedback_text": text, "sentiment_label": sent, "theme": theme,
            "nps": (rating * 25 - 50) if ch == "survey" else None,
            "needs_reply": needs_reply,
            "ai_drafted_reply": drafted_reply(rating, theme, s["city"]),
        })
    return rows

# COMMAND ----------
# MAGIC %md
# MAGIC ## Write tables

# COMMAND ----------
def write_table(rows, table):
    if not rows:
        return
    df = spark.createDataFrame(rows)
    print(f"writing {table}: {df.count():,} rows")
    df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(table)

stores = gen_stores()
items = gen_items()
employees = gen_employees(stores)
write_table(stores, "dims_stores")
write_table(items, "dims_items")
write_table(employees, "dims_employees")

sales_dp = gen_sales_daypart(stores)
write_table(sales_dp, "facts_sales_daypart")

labor_dp = gen_labor_daypart(sales_dp)
write_table(labor_dp, "facts_labor_daypart")

inventory = gen_sales_inventory(stores, items)
write_table(inventory, "facts_sales_inventory_daily")

pos = gen_purchase_orders(stores, items, inventory)
write_table(pos, "facts_purchase_orders")

feedback = gen_feedback(stores)
write_table(feedback, "facts_customer_feedback")

print("done.")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Grant attendee SELECT
# MAGIC
# MAGIC The setup job runs as the facilitator (workspace admin). Grants here
# MAGIC propagate to the attendee group so their Apps + Genie + Dashboards can
# MAGIC read the data.

# COMMAND ----------
attendee_group = dbutils.widgets.get("attendee_group") if "attendee_group" in [w.name for w in dbutils.widgets.getAll()] else "users"
spark.sql(f"GRANT USE CATALOG ON CATALOG {CATALOG} TO `{attendee_group}`")
spark.sql(f"GRANT USE SCHEMA ON SCHEMA {CATALOG}.{SCHEMA} TO `{attendee_group}`")
spark.sql(f"GRANT SELECT ON SCHEMA {CATALOG}.{SCHEMA} TO `{attendee_group}`")
print(f"granted USE CATALOG / USE SCHEMA / SELECT on {CATALOG}.{SCHEMA} to {attendee_group}")
