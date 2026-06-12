# ucode Vibe Coding Workshop

A 3-hour workshop format where each attendee uses **ucode** + **ai-dev-kit** to build a working Databricks app end-to-end: a Databricks App (AppKit) with a Genie space, an AI/BI dashboard, FMAPI-powered insights, and a packaged DAB with a multi-task Job — all routed through Databricks AI Gateway. No API keys.

The reference build in this repo is **Homebase**, a store-operations console for a fictional QSR chain. It surfaces analytics and AI insights across **Labor, Inventory, and Guest Feedback**. Drop in a different schema and the workshop format works for any domain.

## Important links

- **ucode:** https://github.com/databricks/ucode
- **ai-dev-kit:** https://github.com/databricks-solutions/ai-dev-kit/tree/main

## Repo layout

```
ucode-vibe-workshop/
├── docs/
│   ├── facilitator-plan.md       # Pre-workshop checklist, agenda, risk register, prompts
│   └── lab-companion-guide.md    # Attendee-facing: setup, modules, prompts
├── data/
│   ├── README.md                 # Schema, how to regenerate
│   ├── ddl.sql                   # CREATE TABLE statements
│   ├── generate_data.py          # Synthetic data generation (Databricks Connect + Faker)
│   └── requirements.txt
├── dab/                          # Starter DAB skeleton (Module 6)
└── app/                          # Reference solution App (Modules 2-5)
```

## Reference schema (5 tables)

The sample build uses 3 facts + 2 shared dims:

- `facts_labor_daily` (Labor)
- `facts_sales_inventory_daily` (Sales & Inventory)
- `facts_customer_feedback` (Sentiment)
- `dims_stores` (shared)
- `dims_items` (shared)

See `data/README.md` for column details. Default target catalog/schema is `jdub_demo.vibe_workshop` (override with CLI flags on `generate_data.py`).

## Workshop logistics

- **Duration:** 3 hours
- **Audience:** 8-15 engineers/analysts
- **Pre-work:** 30 min async (ucode + IDE + ai-dev-kit)

Specific deployment values (target workspace, catalog, branding) are in the guides under `docs/`.
