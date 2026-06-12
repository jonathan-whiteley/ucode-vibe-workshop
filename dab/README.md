# Facilitator Setup Bundle

This is the **facilitator's** one-shot bundle. Deploy it in the target workspace before the workshop to set up the data, the Lakebase, and reference copies of the Genie space / dashboard / App that attendees will rebuild themselves.

> Attendees do NOT run this bundle. Their reference is the prompts in `docs/lab-companion-guide.md`. This bundle is your safety net + a working end-state to demo at the start.

## What it deploys

| Resource | Purpose |
|---|---|
| **Setup job** `command_center_setup` | 3 sequential tasks: generate data → init Lakebase tables → create Genie space |
| **Lakebase instance** `command-center-lakebase` | Shared write-back Postgres for purchase orders, review replies, schedule approvals |
| **Reference dashboard** `command_center_dash` | 4 datasets + widgets (labor %, sales by daypart, stock health, sentiment timeline) |
| **Reference App** `command_center_app` | Operator Command Center prototype served via FastAPI; wired live to the 8 workshop tables, Lakebase, and the Genie space the setup job creates |

## Prereqs

- Databricks CLI ≥ 0.281.0
- A profile for each target (`DEFAULT` for dev, `lce` for production)
- The deploying user must be a **workspace admin** (or have permission to create Lakebase instances). If you aren't, see "Lakebase binding fallback" below.
- A SQL warehouse named `Serverless Starter Warehouse` (override with `--var warehouse_id=<id>` if your warehouse has a different name)

## Order of operations (new workspace)

The resources have hard dependencies on each other. Run the steps in this order:

```bash
cd dab

# 1) Sanity-check the bundle
databricks bundle validate -t lce

# 2) Create the Lakebase instance, job, dashboard, App resource
#    (the App is registered but NOT started; it can't query data yet)
databricks bundle deploy -t lce

# 3) Run the setup job (data gen + Lakebase DDL + Genie space)
#    Takes ~3-4 min. Must succeed before the App will be useful.
databricks bundle run command_center_setup -t lce

# 4) Start the App. The wiring banner shows live counts + Genie space.
databricks bundle run command_center_app -t lce
```

### Why this order matters

| Step | Depends on | Failure mode if skipped |
|---|---|---|
| `bundle deploy` creates the Lakebase instance | Workspace admin to create the instance | App deploy fails because its `lakebase` resource binding can't bind to a non-existent instance |
| `command_center_setup` job creates Lakebase **tables** | Lakebase instance exists | App's `/api/writes/*` endpoints 502 with "relation does not exist" |
| `command_center_setup` job creates the Genie space | Data exists in UC tables | App's `/api/genie` shows "no matching space" |
| `command_center_app` start | All of the above | Wiring banner shows 0 counts and "Genie: not yet wired" |

The App will still load (and the banner will gracefully say "disconnected") even if step 3 hasn't run yet, so you can deploy + verify the App scaffolding first if you want to test deployment.

## Variables

Override at deploy time with `--var <key>=<value>`:

| Variable | Default | Notes |
|---|---|---|
| `catalog` | `ioc_sandbox` (lce) / `jdub_demo` (dev) | UC catalog where the 8 workshop tables land |
| `schema` | `vibe_workshop` | UC schema |
| `warehouse_id` | looked up by name | Override with the warehouse ID if the lookup name doesn't match |
| `fmapi_endpoint` | `databricks-meta-llama-3-3-70b-instruct` | Foundation Model API endpoint for `ai_query()` calls |
| `data_end_date` | `2026-06-22` | Latest date in the synthetic data; anchors `current_date()`-style queries |
| `attendee_group` | `users` | Workspace group that gets SELECT on tables + CAN_USE on the App |
| `company` | `lce` | Brand config for synthetic data (lce / qsr_mexican); see `data/generate_data.py` |

## App env vars (in `src/app/app.yaml`)

The reference App reads catalog/schema/Lakebase from env. DAB does NOT substitute `${var.*}` in `app.yaml` source files, so:

- **Dev** uses the hardcoded values in `app.yaml` (`CC_CATALOG=jdub_demo`).
- **lce** needs a post-deploy override:
  ```bash
  databricks apps update command-center-lce --no-compute \
    --json '{"resources":[...],"env":[{"name":"CC_CATALOG","value":"ioc_sandbox"}, ...]}'
  ```
  Or hand-edit `dab/src/app/app.yaml` before the lce deploy. (Future: lift this into a per-target `presets` block.)

## Layout

```
dab/
├── databricks.yml             # bundle config + targets (dev / lce)
├── resources/
│   ├── job.yml                # setup job (3 sequential tasks, serverless notebooks)
│   ├── lakebase.yml           # database_instances resource (lce-only)
│   ├── dashboard.yml          # Lakeview dashboard resource
│   └── app.yml                # apps resource w/ warehouse + Lakebase + 8 table bindings
└── src/
    ├── notebooks/
    │   ├── 01_generate_data.py     # synthesizes 8 workshop tables (company-configurable)
    │   ├── 02_init_lakebase.py     # DDL for purchase_orders_released, review_replies, schedules_approved
    │   └── 03_create_genie_space.py  # REST API call to create reference Genie space ("Command Center reference")
    ├── dashboards/
    │   └── operator_command_center.lvdash.json
    └── app/
        ├── app.py                  # FastAPI entrypoint; mounts the routers below
        ├── app.yaml                # Apps runtime config (start command + env vars)
        ├── requirements.txt
        ├── lib/                    # config, deps (warehouse + Lakebase), sql_utils
        ├── routers/                # /api/wiring, /api/today, /api/labor, /api/inventory, /api/feedback, /api/genie, /api/writes
        └── static/                 # Copy of app/reference-prototype (Homebase HTML/JSX/CSS) + wiring-banner.js
```

## Lakebase binding fallback

If `bundle deploy` fails on the `database_instances` resource with a permission error, you're not a workspace admin. Two workarounds:

1. Have an admin create `command-center-lakebase` in the workspace UI (Compute → Database instances → Create). Then redeploy the bundle — it'll see the existing instance.
2. Or comment out `resources/lakebase.yml` (move the instance definition out of the lce target in `databricks.yml`), deploy the rest, and provision the Lakebase manually. The `02_init_lakebase` notebook still creates the tables once the instance exists.

## Refreshing the static App copy

When `app/reference-prototype/` changes (e.g. design refresh), refresh the static copy and redeploy:

```bash
cd dab
rm -rf src/app/static/{Homebase.html,colors_and_type.css,tweaks-panel.jsx,app,assets,fonts,wiring-banner.js}
cp ../app/reference-prototype/Homebase.html src/app/static/
cp ../app/reference-prototype/colors_and_type.css src/app/static/
cp ../app/reference-prototype/tweaks-panel.jsx src/app/static/
cp ../app/reference-prototype/wiring-banner.js src/app/static/
cp -R ../app/reference-prototype/app src/app/static/
cp -R ../app/reference-prototype/assets src/app/static/
cp -R ../app/reference-prototype/fonts src/app/static/

databricks bundle deploy -t lce
databricks bundle run command_center_app -t lce
```

## Tearing it down

```bash
databricks bundle destroy -t dev --auto-approve
databricks bundle destroy -t lce --auto-approve  # admin only
```

This drops the App, dashboard, and job. The Lakebase instance and Unity Catalog tables are NOT dropped by `bundle destroy` — clean those up manually if you need a fresh slate.
