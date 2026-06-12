# Facilitator Setup Bundle

This is the **facilitator's** one-shot bundle. Deploy it in the target workspace before the workshop to set up the data, the Lakebase, and reference copies of the Genie / dashboard / App that attendees will rebuild themselves.

> Attendees do NOT run this bundle. Their reference is the prompts in `docs/lab-companion-guide.md`. This bundle is your safety net + a working end-state to demo at the start.

## What it deploys

| Resource | Purpose |
|---|---|
| **Setup job** `workshop_setup` | 3 sequential tasks: generate data, init Lakebase, create reference Genie space |
| **Lakebase instance** `vibe-workshop-lakebase` | Shared write-back Postgres for purchase orders, review replies, schedule approvals |
| **Reference dashboard** `occ_reference_dashboard` | 4 datasets (labor %, sales by daypart, stock health, sentiment timeline) ready to drag onto the canvas |
| **Reference App** `occ_reference_app` | Operator Command Center prototype served via FastAPI |

## Prereqs

- Databricks CLI ≥ 0.281.0
- A profile for each target (`DEFAULT` for dev, `lce` for production)
- The deploying user must be a **workspace admin** for the Lakebase resource binding. If you aren't, see "Lakebase binding fallback" below.
- A SQL warehouse named `Serverless Starter Warehouse` (override with `--var warehouse_id=<id>` if your warehouse has a different name)

## Deploy

```bash
cd dab
databricks bundle validate                            # dev target by default
databricks bundle deploy                              # deploy to dev
databricks bundle run workshop_setup                  # run the setup job
databricks bundle run occ_reference_app               # start the App (apps need an explicit run after deploy)
```

For LCE production:

```bash
databricks bundle validate -t lce
databricks bundle deploy -t lce --var attendee_group=lce-workshop-attendees
databricks bundle run workshop_setup -t lce
databricks bundle run occ_reference_app -t lce
```

## Variables

Override at deploy time with `--var <key>=<value>`:

| Variable | Default | Notes |
|---|---|---|
| `catalog` | `ioc_sandbox` (lce) / `jdub_demo` (dev) | UC catalog |
| `schema` | `vibe_workshop` | UC schema |
| `warehouse_id` | looked up by name | Override with the warehouse ID if the name differs |
| `fmapi_endpoint` | `databricks-meta-llama-3-3-70b-instruct` | FMAPI endpoint used by `ai_query()` |
| `data_end_date` | `2026-06-22` | Latest date in the synthetic data |
| `attendee_group` | `users` | Workspace group that gets SELECT on tables + CAN_USE on the App |

## Layout

```
dab/
├── databricks.yml             # bundle config + targets
├── resources/
│   ├── job.yml                # setup job (3 tasks)
│   ├── lakebase.yml           # database_instances resource
│   ├── dashboard.yml          # Lakeview dashboard resource
│   └── app.yml                # apps resource
└── src/
    ├── notebooks/
    │   ├── 01_generate_data.py     # data gen (mirrors data/generate_data.py)
    │   ├── 02_init_lakebase.py     # DDL for write-back Postgres tables
    │   └── 03_create_genie_space.py  # REST API call to create reference Genie space
    ├── dashboards/
    │   └── operator_insights.lvdash.json
    └── app/
        ├── app.py              # FastAPI static-file server
        ├── app.yaml            # Apps runtime config
        ├── requirements.txt
        └── static/             # Copy of app/reference-prototype (Homebase.html + JSX/CSS/assets)
```

## Lakebase binding fallback

If `bundle deploy` fails on the `database_instances` resource with a permission error, you're not a workspace admin. Two workarounds:

1. Have an admin create `vibe-workshop-lakebase` in the workspace UI (Compute → Database instances → Create). Then redeploy the bundle — it'll see the existing instance and skip creation.
2. Or, comment out `resources/lakebase.yml`, deploy the rest, and provision the Lakebase manually. The `02_init_lakebase` notebook still creates the tables once the instance exists.

## Refreshing the static App copy

When `app/reference-prototype/` changes (e.g. design refresh), refresh the static copy and redeploy:

```bash
cd dab
rm -rf src/app/static/{Homebase.html,colors_and_type.css,tweaks-panel.jsx,app,assets,fonts}
cp ../app/reference-prototype/Homebase.html src/app/static/
cp ../app/reference-prototype/colors_and_type.css src/app/static/
cp ../app/reference-prototype/tweaks-panel.jsx src/app/static/
cp -R ../app/reference-prototype/app src/app/static/
cp -R ../app/reference-prototype/assets src/app/static/
cp -R ../app/reference-prototype/fonts src/app/static/

databricks bundle deploy -t lce
databricks bundle run occ_reference_app -t lce
```

## Tearing it down

```bash
databricks bundle destroy -t dev --auto-approve
databricks bundle destroy -t lce --auto-approve  # admin only
```

This drops the App, dashboard, and job. The Lakebase instance and Unity Catalog tables are NOT dropped by `bundle destroy` — clean those up manually if you need a fresh slate.
