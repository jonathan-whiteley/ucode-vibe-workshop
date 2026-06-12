# Workshop Data

5 tables under `ioc_sandbox.vibe_workshop`, designed to feed the Genie space, AI/BI dashboard, and FMAPI insights with realistic operations data.

## Volume targets

- 20 stores
- ~50 SKUs
- 365 days of history
- ~1000 customer feedback rows

Total: ~365K rows across all facts. Small enough to be fast, large enough to be interesting.

## Tables

### Facts

**`facts_labor_daily`** (Labor pillar)

| Column | Type | Notes |
|---|---|---|
| `date` | DATE | |
| `store_id` | STRING | FK to `dims_stores` |
| `role` | STRING | manager, cashier, prep, etc. |
| `headcount` | INT | |
| `total_hours` | DOUBLE | |
| `labor_cost` | DECIMAL(10,2) | |

**`facts_sales_inventory_daily`** (Sales & Inventory pillar)

| Column | Type | Notes |
|---|---|---|
| `date` | DATE | |
| `store_id` | STRING | FK |
| `sku` | STRING | FK to `dims_items` |
| `units_sold` | INT | |
| `revenue` | DECIMAL(10,2) | |
| `on_hand_eod` | INT | End-of-day inventory |
| `reorder_point` | INT | |

**`facts_customer_feedback`** (Sentiment pillar)

| Column | Type | Notes |
|---|---|---|
| `feedback_id` | STRING | |
| `date` | DATE | |
| `store_id` | STRING | FK |
| `channel` | STRING | review, survey, social, in-store |
| `rating` | INT | 1-5 |
| `feedback_text` | STRING | free-text customer feedback |
| `nps` | INT | -100 to 100, nullable (only for survey channel) |

### Dims

**`dims_stores`**

| Column | Type |
|---|---|
| `store_id` | STRING |
| `store_name` | STRING |
| `region` | STRING |
| `city` | STRING |
| `state` | STRING |
| `square_footage` | INT |

**`dims_items`**

| Column | Type |
|---|---|
| `sku` | STRING |
| `item_name` | STRING |
| `category` | STRING |
| `retail_price` | DECIMAL(10,2) |
| `cost` | DECIMAL(10,2) |

## Regenerating the data

```bash
# Install deps
pip install -r requirements.txt

# Run generation against the workspace (uses your databricks profile)
python generate_data.py --profile DEFAULT --catalog ioc_sandbox --schema vibe_workshop
```

See `generate_data.py` for options.

## Granting access

After generation, grant the attendee group `SELECT` on all 5 tables and `USE CATALOG` / `USE SCHEMA`:

```sql
GRANT USE CATALOG ON CATALOG ioc_sandbox TO `<attendee_group>`;
GRANT USE SCHEMA ON SCHEMA ioc_sandbox.vibe_workshop TO `<attendee_group>`;
GRANT SELECT ON SCHEMA ioc_sandbox.vibe_workshop TO `<attendee_group>`;
```
