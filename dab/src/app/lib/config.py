"""App settings sourced from environment variables.

The Databricks App runtime sets DATABRICKS_HOST and (via the `warehouse` resource
binding) DATABRICKS_WAREHOUSE_ID. Lakebase host/user/password come from the
`lakebase` resource binding as PGHOST/PGUSER/PGPASSWORD/PGDATABASE; we fall
back to LAKEBASE_* env vars for local dev or manual overrides.

GENIE_SPACE_ID is currently set as a static env var. After the setup job
creates the reference Genie space, run:
  databricks apps update command-center-dev --json @app.json
with the new ID baked in, then redeploy. (Future: auto-publish ID from the
setup notebook back into the App env.)
"""
from __future__ import annotations

import os
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    databricks_host: str = ""
    warehouse_id: str = ""
    catalog: str = "ioc_sandbox"
    schema_name: str = "vibe_workshop"
    lakebase_host: str = ""
    lakebase_db: str = "databricks_postgres"
    lakebase_user: str = ""
    lakebase_password: str = ""
    lakebase_instance: str = ""
    genie_space_id: str = ""
    fmapi_endpoint: str = "databricks-meta-llama-3-3-70b-instruct"
    # Synthetic data ends 2026-06-22; queries anchor here so KPIs populate
    # regardless of when the App is loaded.
    anchor_date: str = "2026-06-22"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        databricks_host=os.getenv("DATABRICKS_HOST", ""),
        warehouse_id=os.getenv("DATABRICKS_WAREHOUSE_ID", ""),
        catalog=os.getenv("CC_CATALOG", "ioc_sandbox"),
        schema_name=os.getenv("CC_SCHEMA", "vibe_workshop"),
        lakebase_host=os.getenv("LAKEBASE_HOST") or os.getenv("PGHOST", ""),
        lakebase_db=os.getenv("LAKEBASE_DB") or os.getenv("PGDATABASE", "databricks_postgres"),
        lakebase_user=os.getenv("LAKEBASE_USER") or os.getenv("PGUSER", ""),
        lakebase_password=os.getenv("LAKEBASE_PASSWORD") or os.getenv("PGPASSWORD", ""),
        lakebase_instance=os.getenv("LAKEBASE_INSTANCE", "command-center-lakebase"),
        genie_space_id=os.getenv("GENIE_SPACE_ID", ""),
        fmapi_endpoint=os.getenv("FMAPI_ENDPOINT", "databricks-meta-llama-3-3-70b-instruct"),
        anchor_date=os.getenv("ANCHOR_DATE", "2026-06-22"),
    )
