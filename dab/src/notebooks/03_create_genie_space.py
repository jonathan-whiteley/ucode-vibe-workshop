# Databricks notebook source
# MAGIC %md
# MAGIC # Create reference Genie space over the workshop tables
# MAGIC
# MAGIC Creates a Genie space called "OCC reference: Operator Command Center"
# MAGIC over all 8 workshop tables, bound to the chosen SQL warehouse, with a
# MAGIC pre-baked set of sample questions and metric instructions.
# MAGIC
# MAGIC Idempotent: if a space with the same title exists in the current
# MAGIC workspace, it's updated rather than duplicated.

# COMMAND ----------
dbutils.widgets.text("catalog", "ioc_sandbox")
dbutils.widgets.text("schema", "vibe_workshop")
dbutils.widgets.text("warehouse_id", "")

# COMMAND ----------
# MAGIC %pip install -q databricks-sdk

# COMMAND ----------
dbutils.library.restartPython()

# COMMAND ----------
# Re-read widgets after the Python restart wipes the global namespace.
CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
WAREHOUSE_ID = dbutils.widgets.get("warehouse_id")

if not WAREHOUSE_ID:
    raise ValueError("warehouse_id task parameter is required")

SPACE_TITLE = "Command Center reference"

import json
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

TABLES = [
    "dims_stores",
    "dims_items",
    "dims_employees",
    "facts_sales_daypart",
    "facts_labor_daypart",
    "facts_sales_inventory_daily",
    "facts_purchase_orders",
    "facts_customer_feedback",
]

SAMPLE_QUESTIONS = [
    "What were yesterday's sales by daypart?",
    "Which 5 stores had the lowest labor % of sales last week?",
    "Show me the days-of-cover for produce items at store S001 right now.",
    "What's the trend in negative reviews over the last 30 days?",
    "How many staged purchase orders are waiting to be released?",
    "Which themes drove the most negative feedback this week?",
]

METRIC_INSTRUCTIONS = """
Operator Command Center metric definitions:

1. Labor cost % of sales = SUM(facts_labor_daypart.labor_cost) / SUM(facts_sales_daypart.revenue), aggregated over the same date and store. Target band: 22%-26%.
2. Days of cover = facts_sales_inventory_daily.on_hand_eod / rolling 7-day avg of units_sold per (store_id, sku).
3. Sell-through rate = SUM(units_sold) / NULLIF(SUM(units_sold + on_hand_eod), 0) per (store_id, sku) over a window.
4. Net sentiment score = (COUNT(*) FILTER (WHERE sentiment_label='pos') - COUNT(*) FILTER (WHERE sentiment_label='neg')) / COUNT(*) over a window in facts_customer_feedback.

Joining conventions:
- facts_sales_daypart and facts_labor_daypart share (date, store_id, daypart).
- facts_sales_inventory_daily joins dims_items on sku and dims_stores on store_id.
- facts_purchase_orders joins dims_items on sku.
- facts_customer_feedback joins dims_stores on store_id; theme and sentiment_label are pre-staged.
""".strip()

# COMMAND ----------
# The Genie REST API is in /api/2.0/genie. The SDK exposes it as
# `w.genie` on recent versions. If your SDK is older, fall back to raw HTTP.
import requests

host = w.config.host.rstrip("/")
token = w.config.token if w.config.token else None
if token is None:
    # In a job context, prefer the SDK's auth chain
    headers = w.config.authenticate()
else:
    headers = {"Authorization": f"Bearer {token}"}
headers["Content-Type"] = "application/json"

# 1) See if a space with our title already exists.
list_resp = requests.get(f"{host}/api/2.0/genie/spaces", headers=headers)
list_resp.raise_for_status()
existing = [s for s in list_resp.json().get("spaces", []) if s.get("title") == SPACE_TITLE]

table_ids = [f"{CATALOG}.{SCHEMA}.{t}" for t in TABLES]
payload = {
    "title": SPACE_TITLE,
    "description": "Reference Genie space for the ucode Vibe Coding workshop. Spans all 8 workshop tables.",
    "warehouse_id": WAREHOUSE_ID,
    "table_identifiers": table_ids,
    "instructions": METRIC_INSTRUCTIONS,
    "sample_questions": SAMPLE_QUESTIONS,
}

if existing:
    space_id = existing[0]["space_id"]
    print(f"updating existing Genie space {space_id}")
    resp = requests.patch(f"{host}/api/2.0/genie/spaces/{space_id}", headers=headers, data=json.dumps(payload))
else:
    print("creating new Genie space")
    resp = requests.post(f"{host}/api/2.0/genie/spaces", headers=headers, data=json.dumps(payload))

if resp.status_code >= 400:
    print(f"WARNING: Genie space API returned {resp.status_code}: {resp.text}")
    print("If the Genie REST API surface differs in your workspace, create the space")
    print("manually in the workspace UI using the tables, questions, and instructions")
    print("printed above. The DAB will still deploy the App + Dashboard.")
else:
    result = resp.json()
    space_id = result.get("space_id") or result.get("id")
    print(f"Genie space ready: {space_id}")
    print(f"URL: {host}/genie/spaces/{space_id}")
