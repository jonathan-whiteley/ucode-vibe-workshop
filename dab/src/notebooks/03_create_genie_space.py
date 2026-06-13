# Databricks notebook source
# MAGIC %md
# MAGIC # Create reference Genie space over the workshop tables
# MAGIC
# MAGIC Creates a Genie space titled "Command Center reference" with the 8
# MAGIC workshop tables and pre-baked sample questions / metric instructions /
# MAGIC example SQLs. Idempotent: if a space with the same title already exists
# MAGIC in this workspace, it's PATCHed in place.
# MAGIC
# MAGIC Lifted from the lakehouse-market 06_ensure_genie_space pattern
# MAGIC (proto schema v2, sorted ids for stable diffs).

# COMMAND ----------
dbutils.widgets.text("catalog", "ioc_sandbox")
dbutils.widgets.text("schema", "vibe_workshop")
dbutils.widgets.text("warehouse_id", "")
dbutils.widgets.text("space_id", "")

# COMMAND ----------
# MAGIC %pip install -q --upgrade "databricks-sdk>=0.40"

# COMMAND ----------
dbutils.library.restartPython()

# COMMAND ----------
# Re-read widgets after the Python restart.
CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
WAREHOUSE_ID = dbutils.widgets.get("warehouse_id")
EXISTING_SPACE_ID = dbutils.widgets.get("space_id").strip()

if not WAREHOUSE_ID:
    raise ValueError("warehouse_id task parameter is required")

TITLE = "Command Center reference"
DESCRIPTION = (
    "Reference Genie space for the ucode Vibe Coding workshop. Answers questions "
    "about labor, inventory, and guest feedback across 20 stores. Powers the "
    "Ask Genie panel in the Command Center app."
)
INSTRUCTIONS = (
    "You are answering questions for an operator using the Command Center app. "
    "The dataset has 20 stores; if the user doesn't specify a store_id, default "
    "to comparison-friendly answers across stores. Dayparts are: breakfast, "
    "lunch, dinner, late. The three operational pillars are Labor (sales_daypart, "
    "labor_daypart, employees), Inventory (sales_inventory_daily, purchase_orders, "
    "items), and Guest Feedback (customer_feedback). Data ends 2026-06-22 — "
    "anchor 'today' to MAX(date) in the relevant fact table, not current_date()."
)

import json
from uuid import uuid4

from databricks.sdk import WorkspaceClient

TABLES = [
    f"{CATALOG}.{SCHEMA}.dims_stores",
    f"{CATALOG}.{SCHEMA}.dims_items",
    f"{CATALOG}.{SCHEMA}.dims_employees",
    f"{CATALOG}.{SCHEMA}.facts_sales_daypart",
    f"{CATALOG}.{SCHEMA}.facts_labor_daypart",
    f"{CATALOG}.{SCHEMA}.facts_sales_inventory_daily",
    f"{CATALOG}.{SCHEMA}.facts_purchase_orders",
    f"{CATALOG}.{SCHEMA}.facts_customer_feedback",
]

SAMPLE_QUESTIONS = [
    "What were yesterday's sales by daypart?",
    "Which 5 stores had the lowest labor % of sales last week?",
    "Show me the days-of-cover for items at store S001 right now.",
    "What's the trend in negative reviews over the last 30 days?",
    "How many purchase orders are staged for release?",
    "Which themes drove the most negative feedback this week?",
]

EXAMPLE_SQLS = [
    {
        "title": "Sales by daypart for the most recent date",
        "sql": (
            "WITH a AS (SELECT MAX(date) AS d FROM "
            f"{CATALOG}.{SCHEMA}.facts_sales_daypart) "
            "SELECT daypart, SUM(revenue) AS revenue "
            f"FROM {CATALOG}.{SCHEMA}.facts_sales_daypart, a "
            "WHERE date = a.d "
            "GROUP BY daypart "
            "ORDER BY MIN(hour_start)"
        ),
    },
    {
        "title": "Labor % of sales over the last 14 days",
        "sql": (
            "WITH s AS (SELECT date, SUM(revenue) AS rev FROM "
            f"{CATALOG}.{SCHEMA}.facts_sales_daypart "
            "WHERE date >= date_sub((SELECT MAX(date) FROM "
            f"{CATALOG}.{SCHEMA}.facts_sales_daypart), 14) GROUP BY date), "
            "l AS (SELECT date, SUM(labor_cost) AS cost FROM "
            f"{CATALOG}.{SCHEMA}.facts_labor_daypart "
            "WHERE date >= date_sub((SELECT MAX(date) FROM "
            f"{CATALOG}.{SCHEMA}.facts_labor_daypart), 14) GROUP BY date) "
            "SELECT s.date, ROUND(l.cost / NULLIF(s.rev, 0) * 100, 1) AS labor_pct "
            "FROM s JOIN l USING (date) ORDER BY s.date"
        ),
    },
    {
        "title": "SKUs below reorder point right now",
        "sql": (
            "WITH latest AS (SELECT * FROM "
            f"{CATALOG}.{SCHEMA}.facts_sales_inventory_daily "
            "WHERE date = (SELECT MAX(date) FROM "
            f"{CATALOG}.{SCHEMA}.facts_sales_inventory_daily)) "
            "SELECT i.category, COUNT(*) AS below_par "
            "FROM latest l "
            f"JOIN {CATALOG}.{SCHEMA}.dims_items i USING (sku) "
            "WHERE l.on_hand_eod < l.reorder_point "
            "GROUP BY i.category ORDER BY below_par DESC"
        ),
    },
    {
        "title": "Top theme drivers of negative feedback, last 7 days",
        "sql": (
            "SELECT theme, COUNT(*) AS n "
            f"FROM {CATALOG}.{SCHEMA}.facts_customer_feedback "
            "WHERE sentiment_label = 'neg' "
            "AND date >= date_sub((SELECT MAX(date) FROM "
            f"{CATALOG}.{SCHEMA}.facts_customer_feedback), 7) "
            "GROUP BY theme ORDER BY n DESC"
        ),
    },
]


def build_serialized_space() -> dict:
    example_sqls = sorted(
        [
            {"id": uuid4().hex, "question": [e["title"]], "sql": [e["sql"]]}
            for e in EXAMPLE_SQLS
        ],
        key=lambda x: x["id"],
    )
    sample_qs = sorted(
        [{"id": uuid4().hex, "question": [q]} for q in SAMPLE_QUESTIONS],
        key=lambda x: x["id"],
    )
    return {
        "version": 2,
        "data_sources": {
            "tables": sorted(
                [{"identifier": t} for t in TABLES],
                key=lambda x: x["identifier"],
            )
        },
        "instructions": {
            "text_instructions": [{"id": uuid4().hex, "content": [INSTRUCTIONS]}],
            "example_question_sqls": example_sqls,
        },
        "config": {"sample_questions": sample_qs},
    }


# COMMAND ----------
w = WorkspaceClient()

# Look for an existing space with our title (idempotent).
space_id = EXISTING_SPACE_ID
if not space_id:
    try:
        listing = w.api_client.do("GET", "/api/2.0/genie/spaces") or {}
        for sp in listing.get("spaces", []):
            if sp.get("title") == TITLE:
                space_id = sp.get("space_id", "")
                break
    except Exception as e:
        print(f"WARNING: could not list existing spaces ({e}); will attempt create")

payload = {
    "title": TITLE,
    "description": DESCRIPTION,
    "warehouse_id": WAREHOUSE_ID,
    "serialized_space": json.dumps(build_serialized_space()),
}

if space_id:
    print(f"Patching existing Genie space {space_id} ...")
    resp = w.api_client.do("PATCH", f"/api/2.0/genie/spaces/{space_id}", body=payload)
    final_space_id = resp.get("space_id") or space_id
    print(f"Patched: {resp.get('title')} ({final_space_id})")
else:
    print("Creating new Genie space ...")
    resp = w.api_client.do("POST", "/api/2.0/genie/spaces", body=payload)
    final_space_id = resp.get("space_id")
    print(f"Created: {resp.get('title')} ({final_space_id})")
    print(f"  URL: {w.config.host}/genie/rooms/{final_space_id}")

# Publish the resolved config to a known workspace file so the App can pick
# it up at startup without any app.yaml hand-edit or env-var rewiring.
import base64
config_path = "/Workspace/Shared/command-center/config.json"
config_payload = {
    "catalog": CATALOG,
    "schema": SCHEMA,
    "warehouse_id": WAREHOUSE_ID,
    "genie_space_id": final_space_id,
}
config_json = json.dumps(config_payload, indent=2)
# Ensure parent dir exists. mkdirs is idempotent.
try:
    w.api_client.do("POST", "/api/2.0/workspace/mkdirs", body={"path": "/Workspace/Shared/command-center"})
except Exception:
    pass
w.api_client.do(
    "POST",
    "/api/2.0/workspace/import",
    body={
        "path": config_path,
        "format": "AUTO",
        "content": base64.b64encode(config_json.encode()).decode(),
        "overwrite": True,
    },
)
print()
print(f"  Wrote {config_path}:")
print(config_json)
print()
print("  Restart the App (`databricks bundle run command_center_app -t <target>`)")
print("  to pick up the new config.")
