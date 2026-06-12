# ucode Vibe Coding Workshop

A 3-hour workshop format where each attendee uses **ucode** + **ai-dev-kit** to build a working Databricks app end-to-end: a Databricks App (AppKit) with a Genie space, an AI/BI dashboard, FMAPI-powered insights, and a packaged DAB with a multi-task Job — all routed through Databricks AI Gateway. No API keys.

The reference build in this repo is **Command Center**, a store-operations console with the Lakehouse Market design treatment. It surfaces analytics and AI insights across **Labor, Inventory, and Guest Feedback**. Drop in a different schema and the workshop format works for any domain.

## Important links

- **ucode:** https://github.com/databricks/ucode
- **ai-dev-kit:** https://github.com/databricks-solutions/ai-dev-kit/tree/main

## Repo layout

```
ucode-vibe-workshop/
├── docs/
│   ├── facilitator-plan.md       # Pre-workshop checklist, agenda, risk register, prompts
│   ├── lab-companion-guide.md    # Attendee-facing: setup, modules, prompts
│   └── data-audit.md             # Design → schema mapping; gaps + cuts
├── data/
│   ├── README.md                 # Schema, how to regenerate
│   ├── ddl.sql                   # CREATE TABLE statements
│   ├── generate_data.py          # Synthetic data generation (company-configurable)
│   └── requirements.txt
├── dab/                          # Facilitator's setup bundle
│   ├── databricks.yml            # Bundle config, variables, targets (dev / lce)
│   ├── resources/                # job, lakebase, dashboard, app YAMLs
│   └── src/                      # setup notebooks, dashboard JSON, app source
├── app/
│   └── reference-prototype/      # Homebase design (HTML/JSX, design source of truth)
└── branding/lce/                 # Opt-in LCE branding (logo, favicon, palette guide)
```

## Reference schema (8 tables)

3 dims + 5 facts under `ioc_sandbox.vibe_workshop` (dev mirror: `jdub_demo.vibe_workshop`):

- `dims_stores`, `dims_items`, `dims_employees`
- `facts_sales_daypart` — daypart-grain sales + forecast
- `facts_labor_daypart` — daypart × role-grain labor + forecast
- `facts_sales_inventory_daily` — sku-grain inventory + per-sku sales
- `facts_purchase_orders` — pre-staged POs, flattened
- `facts_customer_feedback` — guest reviews with pre-staged `sentiment_label`, `theme`, `ai_drafted_reply`

60 days of history, anchored to **2026-06-22** so `current_date()` queries on workshop day return real rows. Item catalog, store locations, and review language are driven by a `company` config in the generator — defaults to `lce` (Little Caesars items + real LCE-presence stores). Add new entries in `COMPANY_CONFIGS` to re-skin for another customer.

See `data/README.md` for column details, `docs/data-audit.md` for the design-to-schema mapping.

## Workshop logistics

- **Duration:** 3 hours
- **Audience:** 8-15 engineers/analysts
- **Pre-work:** 30 min async (ucode + IDE + ai-dev-kit)

Specific deployment values (target workspace, catalog, branding) live in the guides under `docs/`.

## Facilitator setup

```bash
cd dab
databricks bundle validate -t lce
databricks bundle deploy -t lce
databricks bundle run command_center_setup -t lce
databricks bundle run command_center_app -t lce
```

Deploys:

- **`command_center_setup`** job — 3 sequential tasks: synthesize the 8-table dataset, init the Lakebase write-back tables, create a reference Genie space over the workshop schema
- **`command-center-lakebase`** Lakebase instance — shared Postgres for write-back (purchase orders released, review replies, schedule approvals)
- **`command_center_dash`** AI/BI dashboard — 4 KPI counters + 4 charts (labor %, sales by daypart, stock health, sentiment timeline)
- **`command_center_app`** Databricks App — the Homebase design served via FastAPI; SP gets SELECT on the 8 tables, `CAN_USE` on the warehouse, `CAN_CONNECT_AND_CREATE` on the Lakebase

See `dab/README.md` for the full flow including the Lakebase admin caveat.

## Reference design

The full Homebase prototype (HTML/CSS/JSX) lives in `app/reference-prototype/`. Serve it locally:

```bash
cd app/reference-prototype
python3 -m http.server 8765
open http://localhost:8765/Homebase.html
```

The same files are bundled into `dab/src/app/static/` and deployed as the reference App when you run the facilitator bundle.
