# LCE Workshop: Operator Command Center: Facilitator Plan

**Workshop:** Build an AI-powered Operator Command Center using vibe coding agents (UCode + Claude Code / Codex) routed through Databricks AI Gateway.
**Audience:** LCE engineers and analysts (8-15 attendees recommended).
**Duration:** 3 hours, 1:00-4:00 PM ET.
**End state:** Each attendee has their own deployed Databricks App ("Operator Command Center") that surfaces a Genie space, an AI/BI dashboard, and FMAPI-driven recommendations across three operational pillars: **Labor, Sales & Inventory, Sentiment**. Everything is packaged as a DAB with a multi-task Job and a dev/prod CI-CD path.

### Quick Links

- **ucode:** [github.com/databricks/ucode](https://github.com/databricks/ucode)
- **ai-dev-kit:** [github.com/databricks-solutions/ai-dev-kit](https://github.com/databricks-solutions/ai-dev-kit/tree/main)
- **Workspace:** [adb-30827331698809.9.azuredatabricks.net](https://adb-30827331698809.9.azuredatabricks.net) (lce-analytics-dev-adb)
- **Catalog.schema:** `ioc_sandbox.vibe_workshop`

---

## Agenda (1:00 - 4:00 PM ET)

| Time | Module | Duration | Outcome |
|---|---|---|---|
| 12:30-1:00 | Pre-workshop setup (async) | 30 min | `ucode` installed, IDE configured, ai-dev-kit skills pulled |
| 1:00-1:10 | Welcome + finished-app demo | 10 min | Attendees see what they'll build; environment table reviewed |
| 1:10-1:20 | Module 1: Explore the data | 10 min | Each attendee has schema summary for all 4 tables |
| 1:20-1:40 | Module 2: Scaffold the App shell | 20 min | Empty AppKit app deployed and visible in browser |
| 1:40-2:00 | Module 3: Build the Genie space | 20 min | Genie space answers natural-language questions over the 3 pillars |
| 2:00-2:20 | Module 4: Build the AI/BI dashboard | 20 min | Dashboard with 3 tiles, one per pillar |
| 2:20-2:30 | Break | 10 min | |
| 2:30-3:10 | Module 5: Integrate + AI insights + LCE branding | 40 min | App embeds Genie + dashboard, FMAPI "Recommended Actions" panel, LCE colors/logo |
| 3:10-3:40 | Module 6: DAB + multi-task Job + CI-CD | 30 min | Bundle deployed to dev target; multi-task job runs end-to-end |
| 3:40-3:55 | Demo round-robin | 15 min | Each attendee shows their App URL |
| 3:55-4:00 | Wrap + take-home | 5 min | Slack channel, post-workshop office hours |

---

## Pre-Workshop Checklist (Facilitator)

### T-2 weeks: confirm with LCE workspace admin

- [ ] **AI Gateway enabled** with attendee group access to `databricks-claude-sonnet-4-6` (or chosen endpoint)
- [ ] **Databricks Apps enabled** in the workspace
- [ ] **Foundation Model API** endpoint accessible to attendees (`databricks-meta-llama-3-3-70b-instruct` or similar via `ai_query()`)
- [ ] Attendee group has: Databricks SQL entitlement, workspace access, cluster create or serverless jobs entitlement
- [ ] LCE branding assets received: logo URL, primary brand color hex

### T-1 week: data + schemas

- [ ] Generate synthetic data using `/databricks-synthetic-data-gen` skill. **4 tables total** under `ioc_sandbox.vibe_workshop.*` (see schema below)
- [ ] Create catalog `ioc_sandbox` and schema `ioc_sandbox.vibe_workshop`; grant `USE CATALOG`, `USE SCHEMA`, `SELECT` to attendee group
- [ ] Create per-attendee sandbox schemas: `ioc_sandbox.<initials>_sandbox` with full DDL on schema + `CREATE` privs
- [ ] Pre-create or document the SQL warehouse (Pro or Serverless) and grant `CAN USE` to attendees
- [ ] Build a **reference solution App** (yours) ahead of time so attendees can see the finished product in the demo

### T-3 days: confirm tooling

- [ ] Confirm ai-dev-kit GitHub URL with attendees and verify the skills load via `ucode` / agent
- [ ] Build a **starter DAB skeleton** at `<STARTER_DAB_REPO_URL>` so Module 6 doesn't have to write a DAB from scratch
- [ ] Send the **Lab Companion Guide** (separate doc) to attendees with the pre-workshop setup steps and the environment table for them to fill in

### T-1 day: send attendees

- [ ] Workspace URL, catalog name, their sandbox schema name, warehouse name, AI Gateway model endpoint, FMAPI endpoint name
- [ ] LCE logo URL + brand color
- [ ] Pre-workshop setup instructions (Step 0 in the Lab Companion Guide)

---

## Synthetic Data Schema (5 tables: 3 facts + 2 dims)

The workshop runs on a small, dimensionally-modeled dataset so attendees spend their time on the *AI agent loop*, not on data wrangling. Shared dims (`dims_stores`, `dims_items`) join into multiple facts.

**Facts (3):**

- `ioc_sandbox.vibe_workshop.facts_labor_daily` (Labor): `date`, `store_id`, `role`, `headcount`, `total_hours`, `labor_cost`
- `ioc_sandbox.vibe_workshop.facts_sales_inventory_daily` (Sales & Inventory): `date`, `store_id`, `sku`, `units_sold`, `revenue`, `on_hand_eod`, `reorder_point`
- `ioc_sandbox.vibe_workshop.facts_customer_feedback` (Sentiment): `feedback_id`, `date`, `store_id`, `channel`, `rating`, `feedback_text`, `nps`

**Dims (2, shared across facts):**

- `ioc_sandbox.vibe_workshop.dims_stores`: `store_id`, `store_name`, `region`, `city`, `state`, `square_footage`
- `ioc_sandbox.vibe_workshop.dims_items`: `sku`, `item_name`, `category`, `retail_price`, `cost`

Generate **~365 days × 20 stores × ~50 SKUs** worth of rows. Plenty for Genie/Dashboard/FMAPI to chew on without being heavy.

---

## Pre-Workshop: Attendee Setup (30 min, async)

Send this to attendees 1-3 days before. The Lab Companion Guide has the same instructions.

1. Install `uv`: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Install `npm` if not already (`brew install node` on macOS)
3. Install `ucode`: `uv tool install git+https://github.com/databricks/ucode`
4. Open VSCode (or IDE of choice). Open a terminal.
5. Pick a coding agent: `ucode claude` (or `ucode codex`). On first launch, enter the workspace URL, complete OAuth.
6. Add Databricks MCP servers: `ucode configure mcp`. Pick **Databricks SQL** and **Managed Databricks MCPs**.
7. Pull the ai-dev-kit skills: prompt your agent to set up the skills from https://github.com/databricks-solutions/ai-dev-kit/tree/main.
8. Verify: ask the agent "List the tables in `ioc_sandbox.vibe_workshop`". If you see 5 tables (3 `facts_*`, 2 `dims_*`), you're ready.

If any of these fail, contact the facilitator in the workshop Slack channel **before** the workshop starts.

---

## Module-by-Module Plan

Prompts are intentionally terse. ai-dev-kit gives the agent the playbook for each step; we don't need to spell out flags or SQL. The facilitator's job is to **emphasize reading what the agent generates** before running it.

### Module 1: Explore the data (10 min, 1:10-1:20)

**Goal:** Ground the agent in the actual schema.

**Prompt:**

> Explore `ioc_sandbox.vibe_workshop`. Show me schemas, row counts, sample rows. Save a summary as `schema_summary.md`.

---

### Module 2: Scaffold the App shell (20 min, 1:20-1:40)

**Goal:** Get an empty App deployed and visible. **Do this before Genie/dashboard** so attendees hit permission errors with time to spare.

**Prompt:**

> Scaffold an AppKit app called `<initials>-operator-command-center` with 3 tabs (Labor, Sales & Inventory, Sentiment) and placeholder content. SP needs read on `ioc_sandbox.vibe_workshop`, full on my sandbox, `CAN_USE` on warehouse `<WAREHOUSE_NAME>`. Deploy it and open the URL.

**Critical:** Drill the `apps update --json` then `apps deploy` order. The ai-dev-kit skills handle this, but it's the #1 failure point if attendees try to shortcut.

---

### Module 3: Genie space (20 min, 1:40-2:00)

**Prompt:**

> Create a Genie space `<initials> Operator Command Center` over all tables in `ioc_sandbox.vibe_workshop`, warehouse `<WAREHOUSE_NAME>`. Add 6 sample questions (2 per pillar) and 4 metric definitions. Test it.

**Capture:** Genie space ID for Module 5.

---

### Module 4: AI/BI dashboard (20 min, 2:00-2:20)

**Prompt:**

> Create an AI/BI dashboard `<initials> Operator Insights`, warehouse `<WAREHOUSE_NAME>`. One tile per pillar, most insightful metric for each. Publish.

**Capture:** Dashboard ID for Module 5.

---

### Break (10 min, 2:20-2:30)

---

### Module 5: Integrate + AI insights + LCE branding (40 min, 2:30-3:10)

**Prompts:**

> Embed dashboard `<DASHBOARD_ID>` into the App, one tile per pillar tab.

> Add an "Ask Genie" tab embedding Genie space `<GENIE_SPACE_ID>`.

> Add a "Recommended Actions" sidebar that uses `ai_query()` against `<FMAPI_ENDPOINT>` to recommend top 3 actions for today, based on the 3-pillar KPIs. Store dropdown.

> Apply LCE branding: logo `<LCE_LOGO_URL>`, primary color `<LCE_PRIMARY_COLOR>`, title "Operator Command Center | LCE", dark navbar.

> Redeploy.

**If running long:** cut per-tab embed; put all 3 tiles on an "Overview" tab. Genie + Recommended Actions are the high-impact pieces.

---

### Module 6: DAB + multi-task Job + CI-CD (30 min, 3:10-3:40)

**Pre-built starter:** Provide a DAB skeleton at `<STARTER_DAB_REPO_URL>`. Attendees fork and customize.

**Prompts:**

> Clone `<STARTER_DAB_REPO_URL>`. Customize it to include my App, Genie space, dashboard.

> Add a 6am daily job with 3 tasks: refresh sandbox tables, score sentiment via `<FMAPI_ENDPOINT>`, redeploy the app.

> Two targets: dev and prod. Deploy to dev. Run the job once.

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
| App deploy fails on first run (resources not registered) | High | Trust the ai-dev-kit skill to do `apps update --json` before `apps deploy`; have a working example to share |
| Synthetic data has bad joins / null columns | Medium | Smoke test: ask Genie 3 questions and build 1 dashboard tile before the workshop |
| FMAPI endpoint slow / over quota | Medium | Pre-warm; have a backup endpoint identified |
| Attendees skip pre-workshop setup | High | Send reminder 24h before; reserve 15 min at start for stragglers (cuts into Module 1) |
| DAB module overruns | Medium | Provide a starter repo; cut prod-deploy step if time short |
| LCE branding assets late | Low | Use LCE primary color guess + placeholder logo; swap in real assets post-workshop |

---

## Per-Attendee Asset Naming Convention

All attendee-created assets include their initials to avoid collisions:

| Asset | Naming |
|---|---|
| Sandbox schema | `ioc_sandbox.<initials>_sandbox` |
| App name | `<initials>-operator-command-center` |
| Genie space | `<initials> Operator Command Center` |
| Dashboard | `<initials> Operator Insights` |
| DAB workspace path | `/Workspace/Users/<email>/.bundle/occ-<initials>/` |
| Job name | `occ-<initials>-daily-refresh` |
| Derived tables | `ioc_sandbox.<initials>_sandbox.<table_name>` |

---

## Companion Documents

- **Lab Companion Guide** (attendee-facing): https://docs.google.com/document/d/1r4urTIP6c1veje6WIE7iLS0n-qxQXP551YLlrv1eaJ8/edit
- **Workshop Prerequisites** (admin-facing): https://docs.google.com/document/d/10SRD1IfHHkqajmbExR2iswtbH2jjy2jtblq6el_pA0M/edit
