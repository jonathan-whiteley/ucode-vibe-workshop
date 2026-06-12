# LCE Operator Command Center: Workshop

A 3-hour vibe-coding workshop where each attendee builds **Operator Command Center**: a Databricks App that surfaces AI insights across **Labor, Sales & Inventory, and Sentiment** for LCE's store operations.

## What gets built

- A Databricks App (AppKit) with 3 pillar tabs + Genie + AI/BI dashboard embed + FMAPI "Recommended Actions" sidebar
- A Genie space over a curated 5-table schema
- An AI/BI (Lakeview) dashboard with one tile per pillar
- A DAB packaging it all up, with a daily multi-task Job

All built with **ucode** + **ai-dev-kit** skills routed through Databricks AI Gateway. No API keys.

## Important links

- **ucode:** https://github.com/databricks/ucode
- **ai-dev-kit:** https://github.com/databricks-solutions/ai-dev-kit/tree/main
- **Workspace:** https://adb-30827331698809.9.azuredatabricks.net (lce-analytics-dev-adb)
- **Catalog.schema:** `ioc_sandbox.vibe_workshop`

## Repo layout

```
lce-occ-workshop/
├── docs/
│   ├── facilitator-plan.md       # Pre-workshop checklist, agenda, risk register, prompts
│   └── lab-companion-guide.md    # Attendee-facing: setup, modules, prompts
├── data/
│   ├── README.md                 # Schema, how to regenerate
│   ├── ddl.sql                   # CREATE TABLE statements
│   └── generate_data.py          # Synthetic data generation
├── dab/                          # Starter DAB skeleton (Module 6)
└── app/                          # Reference solution App (Modules 2-5)
```

## Workshop schema (5 tables)

Facts (3) and dims (2) under `ioc_sandbox.vibe_workshop`:

- `facts_labor_daily` (Labor)
- `facts_sales_inventory_daily` (Sales & Inventory)
- `facts_customer_feedback` (Sentiment)
- `dims_stores` (shared)
- `dims_items` (shared)

See `data/README.md` for column details.

## Workshop logistics

- **Duration:** 3 hours, 1:00-4:00 PM ET
- **Audience:** 8-15 LCE engineers/analysts
- **Pre-work:** 30 min async setup (ucode + IDE + ai-dev-kit)
- **Facilitator:** Jonathan Whiteley
