# ucode Vibe Coding Workshop

![Databricks](https://img.shields.io/badge/Databricks-FF3621?logo=databricks&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=black)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Workshop](https://img.shields.io/badge/format-3%20hr%20workshop-1F9E73)
![Status](https://img.shields.io/badge/state-deployed-2272B4)

> A 3-hour workshop where each attendee uses **ucode** + **ai-dev-kit** to build a working Databricks app end-to-end — Databricks App + Genie space + AI/BI dashboard + FMAPI insights + a packaged DAB — all routed through Databricks AI Gateway. **No API keys.**

The reference build is **Command Center**, a store-operations console for a single-store operator. It surfaces analytics and AI insights across three pillars — **Labor**, **Inventory**, and **Guest Feedback** — over an LCE-flavored synthetic dataset. Drop in a different schema and the same format works for any domain.

---

## At a glance

| | |
|---|---|
| **Duration** | 3 hours (1:00 - 4:00 PM ET) |
| **Audience** | 8 - 15 engineers / analysts per cohort |
| **Pre-work** | 30 min async (ucode + IDE + ai-dev-kit) |
| **Modules** | 6 modules: Explore → App shell → Genie → Dashboard → Integrate → DAB |
| **Stack** | Databricks Apps · AppKit · Genie · AI/BI Dashboards · Lakebase · DABs · FMAPI |
| **Default brand** | Little Caesars (swap via `company` config in the data generator) |

---

## Quick start (facilitator)

```bash
git clone https://github.com/jonathan-whiteley/ucode-vibe-workshop
cd ucode-vibe-workshop/dab

databricks bundle validate -t lce
databricks bundle deploy  -t lce              # Lakebase + job + dashboard + App resources
databricks bundle run command_center_setup -t lce   # data + Lakebase DDL + Genie space
databricks bundle run command_center_app -t lce     # start the App
```

Three steps from a fresh workspace to a fully-wired demo. See [`dab/README.md`](dab/README.md) for the order-of-ops details + Lakebase admin caveat.

## Quick start (attendee, pre-workshop)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
brew install node                              # or see nodejs.org
uv tool install git+https://github.com/databricks/ucode
ucode claude                                   # OAuth into the workshop workspace
ucode configure mcp                            # pick Databricks SQL + Managed MCPs
```

Full attendee setup + module-by-module prompts: [`docs/lab-companion-guide.md`](docs/lab-companion-guide.md).

---

## Important links

| | |
|---|---|
| ucode | https://github.com/databricks/ucode |
| ai-dev-kit | https://github.com/databricks-solutions/ai-dev-kit |
| Workshop repo | https://github.com/jonathan-whiteley/ucode-vibe-workshop |

---

## What's in this repo

```
ucode-vibe-workshop/
├── docs/                              📘 Guides
│   ├── facilitator-plan.md            # Pre-workshop checklist, agenda, risks, prompts
│   ├── lab-companion-guide.md         # Attendee-facing: setup, modules, prompts
│   └── data-audit.md                  # Design → schema mapping; gaps + scope cuts
│
├── data/                              📊 Synthetic data
│   ├── README.md
│   ├── ddl.sql                        # CREATE TABLE statements for the 8 workshop tables
│   ├── generate_data.py               # Faker + Databricks Connect; --company lce | qsr_mexican
│   └── requirements.txt
│
├── dab/                               🚀 Facilitator's deployable bundle
│   ├── databricks.yml                 # Targets: dev (jdub_demo), lce (ioc_sandbox)
│   ├── resources/                     # job · lakebase · dashboard · app YAMLs
│   └── src/
│       ├── notebooks/                 # 3 setup tasks: gen data · init Lakebase · create Genie
│       ├── dashboards/                # operator_command_center.lvdash.json
│       └── app/                       # FastAPI + Homebase static UI, fully wired
│           ├── app.py · app.yaml · requirements.txt
│           ├── lib/                   # config (w/ workspace-file override), deps, sql_utils
│           ├── routers/               # /api/wiring, /today, /labor, /inventory, /feedback, /writes, /genie
│           └── static/                # Homebase HTML/JSX + wiring-banner.js
│
├── app/
│   └── reference-prototype/           # 🎨 Homebase design source of truth (standalone, mock data)
│
└── branding/lce/                      # 🍕 Opt-in LCE branding (logo, favicon, palette guide)
```

---

## Reference schema (8 tables)

3 dims + 5 facts under `ioc_sandbox.vibe_workshop` (dev mirror: `jdub_demo.vibe_workshop`):

| Table | Grain | Rows | Purpose |
|---|---|---|---|
| `dims_stores` | store | 20 | 20 real LCE-presence locations (Detroit, Chicago, Houston, …) |
| `dims_items` | sku | 50 | Pizza ingredients, beverages, packaging |
| `dims_employees` | employee | ~240 | ~12 per store (cook / cashier / lead / manager) |
| `facts_sales_daypart` | date × store × daypart | 4,800 | Revenue + traffic, actual + forecast |
| `facts_labor_daypart` | date × store × daypart × role | 19,200 | Crew + hours + cost, actual + forecast |
| `facts_sales_inventory_daily` | date × store × sku | 60,000 | Units sold + on-hand + reorder point |
| `facts_purchase_orders` | po line | ~250 | Pre-staged POs with vendor info |
| `facts_customer_feedback` | feedback | 1,000 | Reviews with pre-staged `sentiment_label`, `theme`, `ai_drafted_reply` |

60 days of history, anchored to **2026-06-22**. Item catalog + store roster driven by a `company` config in the generator — defaults to `lce`. Add a new entry in `COMPANY_CONFIGS` to re-skin for another customer.

Column-level detail: [`data/README.md`](data/README.md). Design-to-schema mapping: [`docs/data-audit.md`](docs/data-audit.md).

---

## What the bundle deploys

| Resource | What it is |
|---|---|
| `command_center_setup` job | 3 sequential tasks: synthesize 8 tables → init Lakebase write-back tables → create Genie space |
| `command-center-lakebase` Lakebase instance | Shared Postgres with `purchase_orders_released` · `review_replies` · `schedules_approved` |
| `command_center_dash` AI/BI dashboard | 4 KPI counters + line/bar charts (labor %, sales by daypart, stock health, sentiment timeline) |
| `command_center_app` Databricks App | FastAPI + Homebase UI; wired live to all 8 tables + Lakebase + Genie via 7 API routers |

The App's catalog/schema/Genie-ID is published to `/Workspace/Shared/command-center/config.json` by the setup job and read by the App at startup — same `app.yaml` ships dev and prod with no hand-edits.

---

## Reference design (Homebase prototype)

The HTML/CSS/JSX design — Genie-first home, day-part Labor planner, stock-health donut, sentiment timeline, AI-drafted replies — lives standalone in [`app/reference-prototype/`](app/reference-prototype/). Serve it locally to see the design without any Databricks dependency:

```bash
cd app/reference-prototype
python3 -m http.server 8765
open http://localhost:8765/Homebase.html
```

The same files ship into `dab/src/app/static/` and are deployed as the wired reference App when you run the facilitator bundle.

---

## Reusing for another customer

1. Add an entry to `COMPANY_CONFIGS` in `data/generate_data.py` (store roster + item catalog + review templates)
2. Drop logo + colors into `branding/<customer>/`
3. Deploy with `--var company=<key>` (e.g. `databricks bundle deploy -t prod --var company=acme`)
4. Genie space title, App resources, dashboard widgets, and write-back semantics stay constant; the brand surface is the only delta
