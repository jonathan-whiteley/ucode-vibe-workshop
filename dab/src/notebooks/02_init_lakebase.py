# Databricks notebook source
# MAGIC %md
# MAGIC # Init Lakebase: workshop write-back tables
# MAGIC
# MAGIC Creates 3 Postgres tables in the shared `command-center-lakebase`
# MAGIC instance. All attendee Apps' SPs get INSERT/SELECT on these so the
# MAGIC Release / Reply / Approve actions in the UI persist somewhere.
# MAGIC
# MAGIC Tables:
# MAGIC - `purchase_orders_released` — Reorders module Release button
# MAGIC - `review_replies` — Guest Feedback Send Reply button
# MAGIC - `schedules_approved` — Labor planner Approve Schedule button

# COMMAND ----------
dbutils.widgets.text("lakebase_instance_name", "command-center-lakebase")
dbutils.widgets.text("attendee_group", "users")
LAKEBASE_NAME = dbutils.widgets.get("lakebase_instance_name")
ATTENDEE_GROUP = dbutils.widgets.get("attendee_group")

# COMMAND ----------
# MAGIC %pip install -q psycopg2-binary databricks-sdk

# COMMAND ----------
dbutils.library.restartPython()

# COMMAND ----------
import os
from databricks.sdk import WorkspaceClient
import psycopg2

w = WorkspaceClient()

# Look up the Lakebase instance to get its connection details.
# If the instance doesn't exist yet (DAB-created instance binding can fail
# for non-admin deployers), surface a clear error message.
try:
    instance = w.database.get_database_instance(name=LAKEBASE_NAME)
except Exception as e:
    raise RuntimeError(
        f"Lakebase instance '{LAKEBASE_NAME}' not found. "
        f"Either the bundle deploy failed to create it (admin required), or it was named differently. "
        f"Create it manually in the workspace UI and rerun this task. Underlying error: {e}"
    )

print(f"Lakebase instance: {instance.name}")
print(f"  read_write_dns: {instance.read_write_dns}")

# Get a credential for the current user / job runner.
cred = w.database.generate_database_credential(
    instance_names=[LAKEBASE_NAME],
    request_id="workshop-setup",
)

# COMMAND ----------
# Connect via psycopg2 and apply DDL + grants.
conn = psycopg2.connect(
    host=instance.read_write_dns,
    port=5432,
    database="databricks_postgres",  # default Lakebase db
    user=w.current_user.me().user_name,
    password=cred.token,
    sslmode="require",
)
conn.autocommit = True
cur = conn.cursor()

DDL = [
    """CREATE TABLE IF NOT EXISTS purchase_orders_released (
         event_id SERIAL PRIMARY KEY,
         po_id TEXT NOT NULL,
         store_id TEXT NOT NULL,
         total_amount NUMERIC,
         released_by TEXT NOT NULL,
         released_at TIMESTAMP DEFAULT NOW()
       )""",
    """CREATE TABLE IF NOT EXISTS review_replies (
         event_id SERIAL PRIMARY KEY,
         feedback_id TEXT NOT NULL,
         store_id TEXT NOT NULL,
         reply_text TEXT NOT NULL,
         replied_by TEXT NOT NULL,
         replied_at TIMESTAMP DEFAULT NOW()
       )""",
    """CREATE TABLE IF NOT EXISTS schedules_approved (
         event_id SERIAL PRIMARY KEY,
         schedule_date DATE NOT NULL,
         store_id TEXT NOT NULL,
         total_hours NUMERIC,
         approved_by TEXT NOT NULL,
         approved_at TIMESTAMP DEFAULT NOW()
       )""",
]
for stmt in DDL:
    cur.execute(stmt)
    print(f"applied: {stmt.split('(')[0].strip()}")

# Grant INSERT/SELECT to the attendee group.
# (In Lakebase, group access is mapped through the workspace SP layer.
# For per-attendee write access, the recommended pattern is to use the App's
# SP. See branding/lce/README.md or the data audit doc for details.)
GRANTS = [
    f"GRANT INSERT, SELECT ON purchase_orders_released TO PUBLIC",
    f"GRANT INSERT, SELECT ON review_replies TO PUBLIC",
    f"GRANT INSERT, SELECT ON schedules_approved TO PUBLIC",
]
for stmt in GRANTS:
    try:
        cur.execute(stmt)
        print(f"granted: {stmt}")
    except Exception as e:
        print(f"grant warning ({stmt}): {e}")

cur.close()
conn.close()
print("done.")
