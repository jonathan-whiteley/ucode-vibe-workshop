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

## Agenda (1:00 - 4:00 PM ET)

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

## Pre-Workshop Checklist (Facilitator)

> The operational runbook (exact deploy commands, ordering caveats, gotchas) is **[`dab/README.md`](../dab/README.md)**. This section enumerates what needs to be true *before* you run that runbook.

### T-2 weeks: workspace + permissions

#### Workspace features the LCE admin must enable

- [ ] **Databricks Apps enabled** in the workspace
- [ ] **Genie spaces enabled** (Account Console → Settings → Previews)
- [ ] **Foundation Model API** endpoint accessible to attendees (`databricks-meta-llama-3-3-70b-instruct` via `ai_query()`)
- [ ] **AI Gateway enabled** with attendee group access to `databricks-claude-sonnet-4-6` (or chosen endpoint, for the ucode coding agent)
- [ ] **Lakebase** Postgres preview enabled (required by the reference write-back; the setup job will create one instance per workshop)

#### Permissions matrix

| Principal | Needs | How it gets granted |
|---|---|---|
| **Facilitator (deployer)** | Workspace admin (to create the Lakebase instance + bind App resources) | LCE admin grants ahead of T-1 week. If you can't get admin, see `dab/README.md` § "Lakebase binding fallback" — admin pre-creates the instance, you bundle-deploy with `lakebase.yml` commented out |
| **Facilitator's CLI auth** | Profile authenticated to the target workspace (`databricks auth login --host <url> --profile lce`) | `databricks auth login` on the facilitator's laptop |
| **Reference App's service principal** | `CAN_USE` warehouse · `SELECT` on the 8 UC tables · access to the Lakebase instance | Auto-granted at deploy time via the `resources` block in `dab/resources/app.yml`. The bootstrap step (T-1 week) must pre-create the tables for these bindings to validate. |
| **Attendee group** (e.g. `workshop-attendees`) | Databricks SQL entitlement · workspace access · serverless jobs entitlement · `SELECT` on `ioc_sandbox.vibe_workshop.*` · `CAN_USE` on the shared warehouse · `CAN_VIEW` on the reference Genie space · `CAN_USE` on the Foundation Model endpoint · `CAN_CREATE` for new Apps in their own scope | LCE admin grants on the group; the setup notebook also runs `GRANT SELECT ON SCHEMA <catalog>.vibe_workshop TO <attendee_group>` (configurable via `--var attendee_group=<group>`) |
| **Each attendee's App SP** (created during the workshop, per attendee) | Same as the reference App's SP, scoped to attendee's own resources | ai-dev-kit scaffolds the app.yaml resources block; the attendee runs `apps update --json` + `apps deploy` (drilled in Module 2) |

#### Other T-2 prep

- [ ] LCE branding assets received: logo SVG, primary brand color hex (already in `branding/lce/`)
- [ ] Workspace-level quotas verified (the workshop nearly always fits inside defaults; rare exceptions in `dab/README.md` § "Common deploy gotchas")

### T-1 week: bootstrap → deploy → setup → smoke-test

Use the exact 5-step sequence in **[`dab/README.md`](../dab/README.md) § "Order of operations (new workspace)"**. The short version, run from the repo's `dab/` directory after `databricks auth login --profile lce`:

```bash
# 1) Pre-create catalog/schema + 8 empty UC tables (required ONCE per workspace; the App's
#    uc_securable bindings are validated at deploy time, so the tables must exist)
python3 scripts/bootstrap.py --profile lce --warehouse-id <id> --catalog ioc_sandbox

# 2) Sanity-check the bundle (pass --var warehouse_id if the default "Serverless Starter
#    Warehouse" lookup name doesn't match your warehouse)
databricks bundle validate -t lce --var warehouse_id=<id>

# 3) Provision Lakebase + job + dashboard + App resource (App registered but not yet useful)
databricks bundle deploy -t lce --var warehouse_id=<id>

# 4) Run the setup job (~3-4 min): synthesize data → init Lakebase tables + sequence grants
#    → create the reference Genie space → write workspace config JSON
databricks bundle run command_center_setup -t lce

# 5) Start the App. The wiring banner (bottom-left of sidebar) should show live table counts
#    and "Genie: Command Center reference" — if not, see dab/README.md § Common gotchas.
databricks bundle run command_center_app -t lce
```

- [ ] Steps 1-5 complete with no errors
- [ ] Reference dashboard renders 4 widgets with data
- [ ] Reference App's wiring banner is **green** with live counts + Genie title
- [ ] One Ask Genie suggestion answers correctly end-to-end

The bundle creates:
- **8-table workshop dataset** under `ioc_sandbox.vibe_workshop` (60 days, ending the workshop date so `current_date()`-style queries return real rows; item catalog + store locations driven by a `company` config in the generator, defaults to `lce`)
- **Shared Lakebase instance** `command-center-lakebase` with write-back tables (`purchase_orders_released`, `review_replies`, `schedules_approved`) — DDL + sequence grants applied by the setup job
- **Reference Genie space** "Command Center reference" — v2 spec with the 8 tables, 6 sample questions, 4 example SQLs, scoped instructions
- **Reference AI/BI dashboard** with 4 widgets (labor %, sales-by-daypart, stock health, sentiment timeline)
- **Reference App** "command-center-${target}" — a fully wired FastAPI build with 7 API routers (`/api/wiring`, `/api/today/kpis`, `/api/labor/tomorrow`, `/api/inventory/{health,by-category,watched,purchase-orders}`, `/api/feedback/{themes,sentiment-timeline,reviews}`, `/api/writes/*`, `/api/genie`). Live KPIs on every tab, Lakebase persistence for Release/Reply/Approve actions, a wiring banner that shows live counts + Genie ID, and the Homebase prototype as the UI. This is genuinely demo-able as the "end state" you can show at the start.

The App self-configures per target via a JSON file the setup job writes to `/Workspace/Shared/command-center/config.json` (catalog, schema, warehouse_id, genie_space_id). The App reads it at startup, so the same `app.yaml` ships dev and prod without per-target hand-edits.

### T-3 days: confirm tooling

- [ ] Verify all attendees have access to the LCE workspace and the attendee group has the entitlements above
- [ ] Smoke-test the reference Genie space with 2-3 questions per pillar
- [ ] Run the reference dashboard once to warm the SQL warehouse
- [ ] Send the **Lab Companion Guide** (separate Google Doc) to attendees with the pre-workshop setup steps

### T-1 day: send attendees

- [ ] Workspace URL, catalog name, warehouse name, AI Gateway model endpoint, FMAPI endpoint name
- [ ] LCE branding folder path in the repo (`branding/lce/`) — opt-in
- [ ] Pre-workshop setup instructions (Step 0 in the Lab Companion Guide)

---

## Synthetic Data Schema (8 tables: 3 dims + 5 facts)

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

## Pre-Workshop: Attendee Setup (30 min, async)

Send this to attendees 1-3 days before. The Lab Companion Guide has the same instructions.

1. Install `uv`: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Install `npm` if not already (`brew install node` on macOS)
3. Install `ucode`: `uv tool install git+https://github.com/databricks/ucode`
4. Open VSCode (or IDE of choice). Open a terminal.
5. Pick a coding agent: `ucode claude` (or `ucode codex`). On first launch, enter the workspace URL, complete OAuth.
6. Add Databricks MCP servers: `ucode configure mcp`. Pick **Databricks SQL** and **Managed Databricks MCPs**.
7. Pull the ai-dev-kit skills: prompt the agent to set up the skills from https://github.com/databricks-solutions/ai-dev-kit/tree/main.
8. Verify: ask the agent "List the tables in `ioc_sandbox.vibe_workshop`". If you see 8 tables (3 `dims_*`, 5 `facts_*`), you're ready.

If any of these fail, contact the facilitator in the workshop Slack channel **before** the workshop starts.

---

## Module-by-Module Plan

Prompts are intentionally terse. ai-dev-kit gives the agent the playbook for each step; we don't need to spell out flags or SQL. The facilitator's job is to **emphasize reading what the agent generates** before running it.

### Module 1: Explore the data (10 min, 1:10-1:20)

**Goal:** Ground the agent in the actual schema.

**Prompt:**

> Explore `ioc_sandbox.vibe_workshop`. Show me schemas, row counts, sample rows for all 8 tables. Save a summary as `schema_summary.md`.

---

### Module 2: Scaffold the App shell (20 min, 1:20-1:40)

**Goal:** Get an empty App deployed and visible. **Do this before Genie/dashboard** so attendees hit permission errors with time to spare.

**Prompt:**

> Scaffold an AppKit app called `<initials>-command-center` with 3 tabs (Labor, Inventory, Guest Feedback) and placeholder content. The app's service principal needs SELECT on the 8 tables in `ioc_sandbox.vibe_workshop` and `CAN_USE` on warehouse `<WAREHOUSE_NAME>`. Deploy and open the URL.

**Critical:** Drill the `apps update --json` then `apps deploy` order. The ai-dev-kit skills handle this, but it's the #1 failure point if attendees try to shortcut.

**Tip for attendees who want a head start:** the workshop repo's reference App at `dab/src/app/` is fully wired — they can study the `lib/` (config + warehouse + Lakebase pool) and `routers/` patterns when wiring their own.

---

### Module 3: Genie space (20 min, 1:40-2:00)

**Prompt:**

> Create a Genie space `<initials> Command Center` over all tables in `ioc_sandbox.vibe_workshop`, warehouse `<WAREHOUSE_NAME>`. Add 6 sample questions (2 per pillar: Labor / Inventory / Guest Feedback) and 4 metric definitions. Test it.

**Capture:** Genie space ID for Module 5.

---

### Module 4: AI/BI dashboard (20 min, 2:00-2:20)

**Prompt:**

> Create an AI/BI dashboard `<initials> Operator Insights`, warehouse `<WAREHOUSE_NAME>`. Tiles for: labor % of sales over time, sales by daypart today, SKUs below par by category, and sentiment timeline. Publish.

**Capture:** Dashboard ID for Module 5.

---

### Break (10 min, 2:20-2:30)

---

### Module 5: Integrate + AI insights + LCE branding (40 min, 2:30-3:10)

**Prompts:**

> Embed dashboard `<DASHBOARD_ID>` into the App, one tile per pillar tab.

> Add an "Ask Genie" tab embedding Genie space `<GENIE_SPACE_ID>`.

> Add a "Recommended Actions" sidebar that uses `ai_query()` against `<FMAPI_ENDPOINT>` to recommend top 3 actions for today, based on the 3-pillar KPIs. Store dropdown.

> Apply LCE branding from `branding/lce/` in the workshop repo: logo `branding/lce/logo.svg`, primary color `#FF671B`. Dark navbar. Page title "Command Center | LCE".

> Redeploy.

**Reference patterns:** the reference App in `dab/src/app/` already implements all of this. Attendees can borrow:
- SQL warehouse access pattern: `lib/deps.get_warehouse_client()` using `databricks-sql-connector` + SDK OAuth
- TTL-cached read helpers: `lib/sql_utils.fetch_all()` (24h cache survives warehouse cold-starts via a one-shot retry filter)
- Lakebase write pattern: `lib/deps.get_lakebase_pool()` mints per-pool OAuth tokens (Lakebase doesn't support static passwords)
- Per-target config: read `/Workspace/Shared/command-center/config.json` at startup (see `lib/config.py`) instead of hardcoding catalog/schema/genie_id in `app.yaml`

**If running long:** cut per-tab embed; put all 3 tiles on an "Overview" tab. Genie + Recommended Actions are the high-impact pieces.

---

### Module 6: DAB + multi-task Job + CI-CD (30 min, 3:10-3:40)

**Pre-built starter:** The workshop repo contains a working DAB at `dab/`. Attendees clone, customize, and deploy.

**Prompts:**

> Clone https://github.com/jonathan-whiteley/ucode-vibe-workshop. Open `dab/`. Customize `databricks.yml` and the resource files to point at my App `<initials>-command-center`, my Genie space `<GENIE_SPACE_ID>`, and my dashboard `<DASHBOARD_ID>` instead of the reference copies.

> Add a daily job at 6am ET with 3 tasks: refresh sandbox tables, score new sentiment via `ai_query()` and `<FMAPI_ENDPOINT>`, redeploy the App.

> Deploy to dev and run the job once. Walk me through how I'd deploy to prod when I'm ready.

---

### Demo + Wrap (20 min, 3:40-4:00)

- 1 min per attendee: share App URL, show one Genie answer, show one Recommended Action
- Workshop Slack channel for ongoing questions
- Optional office hours follow-up 1 week later

---

## Risk Register

| Risk | Likelihood | Mitigation |
|---|---|---|
| AI Gateway not granted to all attendees | High | Test 1 week before; have facilitator's account as backup |
| App deploy fails on first run (resources not registered) | High | Drill `apps update --json` → `apps deploy` order. The ai-dev-kit skill handles this; reference App in `dab/` shows the working pattern |
| SQL warehouse 500s after idle / cold-start | Medium | Reference App's `sql_utils.py` retries on `RequestError` / session expiry. Attendees who write their own backend should mirror that pattern |
| Synthetic data has bad joins / null columns | Low | Reference Genie/dashboard exercises the schema during T-1 week setup |
| FMAPI endpoint slow / over quota | Medium | Pre-warm; have a backup endpoint identified |
| Attendees skip pre-workshop setup | High | Send reminder 24h before; reserve 15 min at start for stragglers (cuts into Module 1) |
| DAB module overruns | Low | The starter at `dab/` is fully working; attendees customize, not build from scratch |
| Lakebase write-back fails (perm error / sequence grants) | Medium | The setup job grants `INSERT/SELECT` on tables AND `USAGE/SELECT` on the underlying SERIAL sequences (a `permission denied for sequence` gotcha hit us in dev). If an attendee's App can't write, they can fall back to read-only demo |
| Genie space not visible to App's SP | Medium | App's `/api/genie` discovers by title; if discovery fails (SP needs CAN_VIEW on the space), the setup job writes the space ID into the workspace config JSON, App reads it from there |
| SDK version drift in serverless notebook runtime | Low | The setup notebooks pin `databricks-sdk>=0.40` and fall back to raw REST (`/api/2.0/database/instances`, `/api/2.0/database/credentials`) when `w.database` isn't present |
| **First-time deploy fails with `SCHEMA_DOES_NOT_EXIST` or `TABLE_OR_VIEW_NOT_FOUND`** | High (if bootstrap skipped) | Run `scripts/bootstrap.py` *before* `bundle deploy`. The App's `uc_securable` bindings are validated at deploy time, so the 8 tables must exist (even empty) — bootstrap creates them, the setup job overwrites with data |
| Warehouse name lookup fails on `bundle deploy` | Medium | The bundle's `warehouse_id` is a `lookup` by name (`Serverless Starter Warehouse`); not every workspace has one. Always pass `--var warehouse_id=<id>`. Find one with `databricks warehouses list --profile <p>` |
| Facilitator isn't workspace admin (can't create Lakebase) | Medium | Two workarounds in `dab/README.md` § "Lakebase binding fallback": admin pre-creates the instance, or comment out `lakebase.yml` and provision manually |

---

## Per-Attendee Asset Naming Convention

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

## Companion Documents

- **Lab Companion Guide** (attendee-facing): [`docs/lab-companion-guide.md`](lab-companion-guide.md) · [Google Doc mirror](https://docs.google.com/document/d/1r4urTIP6c1veje6WIE7iLS0n-qxQXP551YLlrv1eaJ8/edit)
- **Workshop Prerequisites** (admin-facing): [Google Doc](https://docs.google.com/document/d/10SRD1IfHHkqajmbExR2iswtbH2jjy2jtblq6el_pA0M/edit)
- **Operational runbook** (deploy commands, gotchas, fallbacks): [`dab/README.md`](../dab/README.md) — the source of truth for ops. Google Docs are mirrors; if they diverge, the repo wins.
- **Repo:** https://github.com/jonathan-whiteley/ucode-vibe-workshop
