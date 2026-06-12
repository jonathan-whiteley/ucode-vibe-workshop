# ucode Vibe Coding Workshop

A 3-hour workshop format where each attendee uses **ucode** + **ai-dev-kit** to build a working Databricks app end-to-end: a Databricks App (AppKit) with a Genie space, an AI/BI dashboard, FMAPI-powered insights, and a packaged DAB with a multi-task Job — all routed through Databricks AI Gateway. No API keys.

The reference build in this repo is **Operator Command Center**, a store-operations console for a fictional QSR chain. It surfaces analytics and AI insights across **Labor, Inventory, and Guest Feedback**. Drop in a different schema and the workshop format works for any domain.

## Important links

- **ucode:** https://github.com/databricks/ucode
- **ai-dev-kit:** https://github.com/databricks-solutions/ai-dev-kit/tree/main

## Repo layout

```
ucode-vibe-workshop/
├── docs/
│   ├── facilitator-plan.md       # Pre-workshop checklist, agenda, risk register, prompts
│   ├── lab-companion-guide.md    # Attendee-facing: setup, modules, prompts
│   └── data-audit.md             # Maps the Homebase design to the workshop schema
├── data/
│   ├── README.md                 # Schema, how to regenerate
│   ├── ddl.sql                   # CREATE TABLE statements
│   ├── generate_data.py          # Synthetic data generation (Databricks Connect + Faker)
│   └── requirements.txt
├── dab/                          # Facilitator's setup bundle
│   ├── databricks.yml
│   ├── resources/                # job, lakebase, dashboard, app
│   └── src/                      # notebooks, dashboard JSON, app code
├── app/
│   └── reference-prototype/      # Homebase design (HTML/JSX, design source of truth)
└── branding/lce/                 # Opt-in LCE branding (logo, favicon, palette guide)
```

## Reference schema (8 tables)

3 dims + 5 facts under `ioc_sandbox.vibe_workshop` (dev: `jdub_demo.vibe_workshop`):

- `dims_stores`, `dims_items`, `dims_employees`
- `facts_sales_daypart` (daypart-grain sales + forecast)
- `facts_labor_daypart` (daypart × role-grain labor + forecast)
- `facts_sales_inventory_daily` (sku-grain inventory + sales)
- `facts_purchase_orders` (pre-staged, flattened, vendor denormalized)
- `facts_customer_feedback` (with pre-staged sentiment, theme, ai_drafted_reply)

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

See `dab/README.md` for the full flow including the Lakebase admin caveat.
