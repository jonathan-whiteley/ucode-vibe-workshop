# LCE Workshop: Operator Command Center: Facilitator Plan

**Workshop:** Build an AI-powered Command Center using vibe coding agents (UCode + Claude Code / Codex) routed through Databricks AI Gateway.
**Audience:** LCE engineers and analysts (8-15 attendees recommended).
**Duration:** 3 hours, 1:00-4:00 PM ET.
**End state:** Each attendee has their own deployed Databricks App that surfaces a Genie space, an AI/BI dashboard, and FMAPI-driven recommendations across three operational pillars: **Labor, Inventory, Guest Feedback**. Everything is packaged as a Databricks Asset Bundle.

### Quick Links

- **Workshop repo:** [github.com/jonathan-whiteley/ucode-vibe-workshop](https://github.com/jonathan-whiteley/ucode-vibe-workshop)
- **ucode:** [github.com/databricks/ucode](https://github.com/databricks/ucode)
- **ai-dev-kit:** [github.com/databricks-solutions/ai-dev-kit](https://github.com/databricks-solutions/ai-dev-kit/tree/main)
- **LCE workspace:** [adb-30827331698809.9.azuredatabricks.net](https://adb-30827331698809.9.azuredatabricks.net) (lce-analytics-dev-adb)
- **Catalog.schema:** `ioc_sandbox.vibe_workshop`

---

## 📅 Agenda (1:00 - 4:00 PM ET)

| Time | Module | Duration | Outcome |
|---|---|---|---|
| 12:30-1:00 | Pre-workshop setup (async) | 30 min | `ucode` installed, IDE configured, ai-dev-kit skills pulled |
| 1:00-1:10 | Welcome + finished-app demo | 10 min | Attendees see what they'll build; environment table reviewed |
| 1:10-1:20 | Module 1: Explore the data | 10 min | Each attendee has schema summary for all 8 tables |
| 1:20-1:40 | Module 2: Scaffold the App shell | 20 min | Empty AppKit app deployed and visible in browser |
| 1:40-2:00 | Module 3: Build the Genie space | 20 min | Genie space answers natural-language questions over the 3 pillars |
| 2:00-2:20 | Module 4: Build the AI/BI dashboard | 20 min | Dashboard with one widget per pillar |
| 2:20-2:30 | Break | 10 min | |
| 2:30-3:10 | Module 5: Integrate + AI insights + LCE branding | 40 min | App embeds Genie + dashboard, FMAPI "Recommended Actions" panel, LCE colors/logo |
| 3:10-3:40 | Module 6: DAB + multi-task Job + CI-CD | 30 min | Bundle deployed to dev target; multi-task job runs end-to-end |
| 3:40-3:55 | Demo round-robin | 15 min | Each attendee shows their App URL |
| 3:55-4:00 | Wrap + take-home | 5 min | Slack channel, post-workshop office hours |

---

## 📋 Pre-Workshop Checklist

> **Source of truth:** [`dab/README.md`](../dab/README.md) holds the deploy commands and gotchas. This section is everything that has to be true **before** you run that runbook.

### 📅 T-1 week: features + permissions + deploy

#### 🧱 Features the LCE admin must enable

| Feature | Why |
|---|---|
| **Databricks Apps** | Hosts the Command Center App |
| **Genie spaces** (Previews) | Natural-language Q&A pillar |
| **Foundation Model API** | `ai_query()` calls (`databricks-meta-llama-3-3-70b-instruct`) |
| **AI Gateway** access to `databricks-claude-sonnet-4-6` | Powers the ucode coding agent for attendees |
| **Lakebase** (Postgres preview) | Write-back persistence (release POs, replies, schedule approvals) |

#### 🔑 Who needs what permission

**🛠️ Facilitator (deployer)**
- **Workspace admin** — required to create the Lakebase instance + bind App resources
- Authenticated CLI profile (`databricks auth login --host <url> --profile lce`)
- **Fallback if you're not admin:** see [`dab/README.md` § "Lakebase binding fallback"](../dab/README.md#lakebase-binding-fallback) — admin pre-creates the instance, you deploy with `lakebase.yml` commented out

**🤖 Reference App's service principal**
- `CAN_USE` on the warehouse · `SELECT` on the 8 UC tables · access to the Lakebase instance
- ✅ Auto-granted at deploy time via [`dab/resources/app.yml`](../dab/resources/app.yml). The bootstrap step (T-1 week) must pre-create the tables, or bindings fail to validate.

**👥 Attendee group** (e.g. `workshop-attendees`)
- Databricks SQL entitlement · workspace access · serverless jobs entitlement
- `SELECT` on `ioc_sandbox.vibe_workshop.*` · `CAN_USE` on the shared warehouse
- `CAN_VIEW` on the reference Genie space · `CAN_USE` on the FMAPI endpoint
- `CAN_CREATE` for new Apps in their own scope
- ✅ Setup notebook auto-grants the SCHEMA SELECT (`--var attendee_group=<group>`); LCE admin handles the rest

**👤 Each attendee's App SP** (created in Module 2)
- Same shape as the reference App SP, scoped to attendee's own resources
- ai-dev-kit scaffolds the `app.yaml` resources block; attendee runs `apps update --json` then `apps deploy` (drilled in Module 2)

#### 🎨 Other prep

- [ ] LCE branding assets in `branding/lce/` (logo SVG + brand color hex) ✅ already shipped
- [ ] Workspace quotas verified — defaults fit; rare exceptions in [`dab/README.md` § Common gotchas](../dab/README.md#common-deploy-gotchas)

---

### 🚀 Deploy the reference build

Full runbook with explanations: [`dab/README.md`](../dab/README.md). After `databricks auth login --profile lce`, from the repo's `dab/` directory:

```bash
# 1️⃣  Pre-create catalog/schema + 8 empty UC tables (once per workspace).
#     Required because App resource bindings are validated at deploy time.
python3 scripts/bootstrap.py --profile lce --warehouse-id <id> --catalog ioc_sandbox

# 2️⃣  Validate (pass --var warehouse_id if the default lookup name doesn't match)
databricks bundle validate -t lce --var warehouse_id=<id>

# 3️⃣  Provision Lakebase + job + dashboard + App resource
databricks bundle deploy -t lce --var warehouse_id=<id>

# 4️⃣  Run the setup job (~3-4 min): data → Lakebase DDL → Genie space → config JSON
databricks bundle run command_center_setup -t lce

# 5️⃣  Start the App
databricks bundle run command_center_app -t lce
```

**✅ Smoke-test the result:**
- [ ] All 5 steps exit clean
- [ ] Reference dashboard renders 4 widgets with data
- [ ] App's wiring banner is **green** with live counts + "Genie: Command Center reference"
- [ ] One Ask Genie suggestion answers correctly

**📦 What you just deployed:**

| Resource | Notes |
|---|---|
| 8-table dataset in `ioc_sandbox.vibe_workshop` | 60 days, anchored to workshop date · `company=lce` brand config |
| Lakebase instance `command-center-lakebase` | 3 write-back tables · sequence grants applied |
| Genie space "Command Center reference" | 6 sample Qs · 4 example SQLs · scoped instructions |
| AI/BI dashboard | 4 widgets: labor % · sales-by-daypart · stock health · sentiment |
| Reference App `command-center-<target>` | FastAPI + 7 routers · live KPIs · Lakebase writes · Homebase UI |

The App reads `/Workspace/Shared/command-center/config.json` (written by the setup job) at startup, so the same `app.yaml` ships dev and prod with no hand-edits.

---

### 📨 T-1 day: attendee comms + final warmup

- [ ] Attendee perms confirmed (everyone can reach the workspace + has the entitlements above)
- [ ] Send attendees the **Lab Companion Guide** + workshop env values: workspace URL, catalog, warehouse name, AI Gateway endpoint, FMAPI endpoint, LCE branding folder (`branding/lce/`)
- [ ] Warm the SQL warehouse by running the reference dashboard once
- [ ] Smoke-test reference Genie with 2-3 questions per pillar

---

## 🗄️ Synthetic Data Schema (8 tables: 3 dims + 5 facts)

Materialized in `ioc_sandbox.vibe_workshop` (dev mirror at `jdub_demo.vibe_workshop`). 60 days of history anchored to **2026-06-22** so `current_date()` queries on workshop day return real rows. Every chart and AI insight in the reference design has a backing column or table; nothing is computed on-the-fly via AI calls.

**Dims (3):**
- `dims_stores` — 20 stores at real LCE-presence locations (Detroit, Chicago, Houston, etc.)
- `dims_items` — 50 SKUs (pizza ingredients, beverages, packaging)
- `dims_employees` — ~12 per store (cook / cashier / lead / manager mix)

**Facts (5):**
- `facts_sales_daypart` — daypart-grain revenue + forecast (breakfast / lunch / dinner / late)
- `facts_labor_daypart` — daypart × role-grain crew + cost + forecast
- `facts_sales_inventory_daily` — SKU-grain inventory + per-SKU sales
- `facts_purchase_orders` — pre-staged POs with vendor info
- `facts_customer_feedback` — guest reviews with pre-staged `sentiment_label`, `theme`, and `ai_drafted_reply` columns

Item catalog and store roster are driven by a `company` config in the data generator. Default is `lce` (Little Caesars items + locations); swap to `qsr_mexican` or add a new entry in `COMPANY_CONFIGS` to re-skin for another customer.

See `data/README.md` and `docs/data-audit.md` for column-level details.

---

## 🎓 Pre-Workshop: Attendee Setup (30 min, async)

Single source of truth: **[Lab Companion Guide § Prereqs prompts](lab-companion-guide.md#prereqs-prompts-run-these-before-the-workshop)**. Send that section to attendees 1-3 days out. Stragglers ping the workshop Slack channel before 1pm ET.

---

## 🧩 Module-by-Module Plan

Prompt text lives in the **[Lab Companion Guide § Day-of prompts](lab-companion-guide.md#-day-of-prompts-run-these-in-the-workshop-in-order)** (single source of truth). This section is the **facilitator's** at-a-glance: goal, what to drill, what to capture.

| Module | Time | Goal | Drill / Capture |
|---|---|---|---|
| 🔍 **1. Explore the data** | 1:10-1:20 | Ground the agent in the actual schema before building anything | — |
| 🏗️ **2. App shell** | 1:20-1:40 | Get an empty App deployed and visible **before** Genie/dashboard, so permission errors surface early | 🔥 **Drill** `apps update --json` → `apps deploy` order — #1 failure if attendees shortcut. ai-dev-kit handles it; reference App at `dab/src/app/` shows the pattern. |
| 🧞 **3. Genie space** | 1:40-2:00 | NL Q&A over the 3 pillars | 📌 **Capture:** Genie space ID for Module 5 |
| 📊 **4. AI/BI dashboard** | 2:00-2:20 | One widget per pillar, published | 📌 **Capture:** Dashboard ID for Module 5 |
| ☕ Break | 2:20-2:30 | | |
| 🔗 **5. Integrate + AI + LCE branding** | 2:30-3:10 | Wire dashboard tiles, Ask Genie tab, FMAPI recommendations, LCE colors | ⏰ **If running long:** drop per-tab embeds onto a single "Overview" tab. Genie + Recommended Actions are higher-impact. |
| 📦 **6. DAB + Job + CI-CD** | 3:10-3:40 | Clone the workshop DAB, repoint at their own assets, add a daily job, deploy | Starter is fully working; attendees customize, not build from scratch. |

### 🏎️ Module 5 reference patterns (if attendees ask)

The reference App in [`dab/src/app/`](../dab/src/app/) already implements all of Module 5. Cribs:
- **SQL warehouse access:** `lib/deps.get_warehouse_client()` (`databricks-sql-connector` + SDK OAuth)
- **TTL-cached reads:** `lib/sql_utils.fetch_all()` — 24h cache, one-shot retry on warehouse cold-starts
- **Lakebase writes:** `lib/deps.get_lakebase_pool()` — per-pool OAuth tokens (Lakebase has no static passwords)
- **Per-target config:** `/Workspace/Shared/command-center/config.json` at startup (see `lib/config.py`) — avoids hardcoding catalog/schema/genie_id in `app.yaml`

---

### 🎤 Demo + Wrap (20 min, 3:40-4:00)

- 1 min per attendee: share App URL, show one Genie answer, show one Recommended Action
- Workshop Slack channel for ongoing questions
- Optional office hours follow-up 1 week later

---

## ⚠️ Risk Register

Sorted by likelihood. Highest-impact items first.

### 🔴 High likelihood

| Risk | Mitigation |
|---|---|
| **First-time deploy fails:** `SCHEMA_DOES_NOT_EXIST` / `TABLE_OR_VIEW_NOT_FOUND` | Run `scripts/bootstrap.py` **before** `bundle deploy`. App's `uc_securable` bindings are validated at deploy time, so the 8 tables must exist (even empty). |
| **App deploy fails on first run:** resources not registered | Drill `apps update --json` → `apps deploy` order. The ai-dev-kit skill handles this; reference App in `dab/` shows the working pattern. |
| **Attendees skip pre-workshop setup** | Send reminder 24h before; reserve 15 min at workshop start for stragglers (cuts into Module 1). |
| **AI Gateway not granted to all attendees** | Test 1 week before; have facilitator's account as backup. |

### 🟡 Medium likelihood

| Risk | Mitigation |
|---|---|
| **Warehouse name lookup fails** on `bundle deploy` | The bundle's `warehouse_id` is a `lookup` by name (`Serverless Starter Warehouse`); not every workspace has one. Always pass `--var warehouse_id=<id>`. |
| **SQL warehouse 500s** after idle / cold-start | Reference App's `sql_utils.py` retries on `RequestError` / session expiry — attendees writing their own backend should mirror that pattern. |
| **Facilitator isn't workspace admin** (can't create Lakebase) | Two fallbacks in [`dab/README.md` § Lakebase binding fallback](../dab/README.md#lakebase-binding-fallback): admin pre-creates the instance, or comment out `lakebase.yml`. |
| **Lakebase write-back fails** (perm / sequence grants) | Setup job grants `INSERT/SELECT` on tables AND `USAGE/SELECT` on SERIAL sequences. If attendee's App can't write, fall back to read-only demo. |
| **Genie space not visible** to App's SP | App's `/api/genie` discovers by title; if SP lacks `CAN_VIEW`, the workspace config JSON provides the ID directly. |
| **FMAPI endpoint slow / over quota** | Pre-warm; have a backup endpoint identified. |

### 🟢 Low likelihood

| Risk | Mitigation |
|---|---|
| **Synthetic data has bad joins / null columns** | Reference Genie + dashboard exercise the schema during T-1 week setup. |
| **DAB module overruns** | Starter at `dab/` is fully working; attendees customize, not build from scratch. |
| **SDK version drift** in serverless notebook runtime | Setup notebooks pin `databricks-sdk>=0.40` + raw REST fallback (`/api/2.0/database/{instances,credentials}`). |

---

## 🏷️ Per-Attendee Asset Naming Convention

All attendee-created assets include their initials to avoid collisions:

| Asset | Naming |
|---|---|
| App name | `<initials>-command-center` |
| Genie space | `<initials> Command Center` |
| Dashboard | `<initials> Operator Insights` |
| DAB bundle | `<initials>-command-center` |
| Job name | `<initials>-command-center-refresh` |
| Sandbox schema (optional) | `ioc_sandbox.<initials>_sandbox` (only if attendees write derived tables) |

The shared workshop schema `ioc_sandbox.vibe_workshop` and the shared `command-center-lakebase` are read+write for all attendees (Lakebase) and read-only (UC tables).

---

## 📚 Companion Documents

| | |
|---|---|
| 👥 **Lab Companion Guide** (attendee-facing) | [`docs/lab-companion-guide.md`](lab-companion-guide.md) · [Google Doc mirror](https://docs.google.com/document/d/1r4urTIP6c1veje6WIE7iLS0n-qxQXP551YLlrv1eaJ8/edit) |
| 🛡️ **Workshop Prerequisites** (admin-facing) | [Google Doc](https://docs.google.com/document/d/10SRD1IfHHkqajmbExR2iswtbH2jjy2jtblq6el_pA0M/edit) |
| 🚀 **Operational runbook** (deploy commands, gotchas, fallbacks) | [`dab/README.md`](../dab/README.md) — source of truth for ops; Google Docs are mirrors |
| 💻 **Repo** | https://github.com/jonathan-whiteley/ucode-vibe-workshop |
