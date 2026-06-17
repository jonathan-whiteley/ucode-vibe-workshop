# LCE Workshop: Operator Command Center: Lab Companion Guide

**You'll build:** "Command Center", a Databricks App that surfaces AI insights and analytics across **Labor, Inventory, and Guest Feedback** for store operations. Your app will embed a Genie space, an AI/BI dashboard, and an FMAPI-powered "Recommended Actions" panel, all packaged as a Databricks Asset Bundle with a multi-task Job.

**Duration:** 3 hours, 1:00-4:00 PM ET.

### Quick Links

- **Workshop repo:** [github.com/jonathan-whiteley/ucode-vibe-workshop](https://github.com/jonathan-whiteley/ucode-vibe-workshop)
- **ucode:** [github.com/databricks/ucode](https://github.com/databricks/ucode)
- **ai-dev-kit:** [github.com/databricks-solutions/ai-dev-kit](https://github.com/databricks-solutions/ai-dev-kit/tree/main)
- **Workspace:** [adb-30827331698809.9.azuredatabricks.net](https://adb-30827331698809.9.azuredatabricks.net) (lce-analytics-dev-adb)

---

## Agenda

| Time | Module | Outcome |
|---|---|---|
| 12:30-1:00 (pre) | Setup | `ucode` + IDE + ai-dev-kit ready |
| 1:00-1:10 | Welcome + demo | See finished app, get environment values |
| 1:10-1:20 | Module 1: Explore data | Agent knows your schema |
| 1:20-1:40 | Module 2: App shell | Empty Command Center deployed |
| 1:40-2:00 | Module 3: Genie space | Natural-language Q&A over 3 pillars |
| 2:00-2:20 | Module 4: AI/BI dashboard | Widgets per pillar |
| 2:20-2:30 | Break | |
| 2:30-3:10 | Module 5: Integrate + AI + branding | Genie + dashboard + AI recommendations + LCE colors |
| 3:10-3:40 | Module 6: DAB + Job + CI-CD | Bundle deployed, job running |
| 3:40-4:00 | Demo round + wrap | Share your App URL |

---

## Your Workshop Environment

Fill these in from the facilitator's pre-workshop email. Keep this table handy: you'll paste these values into prompts all afternoon.

| Item | Your value |
|---|---|
| Your initials (lowercase, e.g. `jjw`) | `<INITIALS>` |
| Workspace URL | `https://adb-30827331698809.9.azuredatabricks.net` (lce-analytics-dev-adb) |
| Shared data catalog.schema | `ioc_sandbox.vibe_workshop` |
| Shared Lakebase instance | `command-center-lakebase` |
| SQL warehouse name | `<WAREHOUSE_NAME>` |
| AI Gateway model endpoint | `<MODEL_ENDPOINT>` |
| FMAPI endpoint | `<FMAPI_ENDPOINT>` (e.g. `databricks-meta-llama-3-3-70b-instruct`) |
| LCE branding folder (in repo) | `branding/lce/` |
| **Captured during workshop:** | |
| Your Genie space ID | `<GENIE_SPACE_ID>` |
| Your dashboard ID | `<DASHBOARD_ID>` |
| Your App URL | `<APP_URL>` |

---

## How to Use the Prompts in This Guide

The prompts are intentionally short. Your coding agent has the **ai-dev-kit** skills loaded ([github.com/databricks-solutions/ai-dev-kit](https://github.com/databricks-solutions/ai-dev-kit/tree/main)): it knows how to build apps, Genie spaces, dashboards, and DABs on Databricks. You don't need to spell out every flag or SQL detail. Tell the agent *what* you want; let the skills figure out the *how*.

If the agent asks clarifying questions, answer them. If it proposes something you don't like, redirect it. **Always read what it generates before running it.**

---

## Step 0: Pre-Workshop Setup (30 min, do this before 1pm)

If any of these fail, ping the facilitator in the workshop Slack channel **before** the workshop starts.

### Pre-workshop checklist

- [ ] `uv` installed: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [ ] `npm` installed: `brew install node` (macOS) or see nodejs.org
- [ ] `ucode` installed: `uv tool install git+https://github.com/databricks/ucode`
- [ ] Launched a coding agent: `ucode claude` (or `ucode codex`) and completed OAuth with the workspace URL
- [ ] `ucode status` shows the workspace and AI Gateway model endpoint
- [ ] MCP servers added: `ucode configure mcp` (pick **Databricks SQL** and **Managed Databricks MCPs**)
- [ ] ai-dev-kit skills loaded: prompt the agent to set them up from https://github.com/databricks-solutions/ai-dev-kit/tree/main
- [ ] Smoke test passed: agent can list 8 tables in `ioc_sandbox.vibe_workshop` (3 `dims_*`, 5 `facts_*`)

---

## Module 1: Explore the Data (10 min)

**Goal:** Ground the agent in the actual schema before building anything.

> Explore `ioc_sandbox.vibe_workshop`. Show me schemas, row counts, and sample rows for all 8 tables. Save a summary as `schema_summary.md`.

Read the summary. Make sure the agent has it open in context for the rest of the workshop.

---

## Module 2: Scaffold the App Shell (20 min)

**Goal:** Get an empty Command Center deployed and visible. Doing this before Genie/dashboard means deployment issues surface early.

> Scaffold an AppKit app called `<INITIALS>-command-center` with 3 tabs (Labor, Inventory, Guest Feedback) and placeholder content. The app's service principal needs SELECT on the 8 tables in `ioc_sandbox.vibe_workshop` and `CAN_USE` on warehouse `<WAREHOUSE_NAME>`. Deploy and open the URL.

Paste the URL into your environment table as `<APP_URL>`.

**Reference if you get stuck:** there's a fully-wired reference App in the workshop repo at `dab/src/app/`. The patterns in `lib/` (config, deps, sql_utils) and `routers/` are good cribs when wiring your own SQL + Lakebase + Genie integration.

### If it breaks

- **"Permission denied" at runtime on UC tables:** the App's SP didn't get its resources. ai-dev-kit's pattern is `databricks apps update <name> --json '{"resources":[...]}' --no-compute` **first**, then `databricks bundle deploy` (or `apps deploy`). Skipping the `apps update` step is the #1 failure mode — the resource block in `app.yaml` alone isn't enough on first deploy. The reference App's `dab/resources/app.yml` shows the working bindings (warehouse `CAN_USE` + 8 tables `SELECT` + Lakebase).
- **"SCHEMA_DOES_NOT_EXIST" or "TABLE_OR_VIEW_NOT_FOUND" at deploy:** the App resource block references tables that don't exist yet. You're using a shared schema (`ioc_sandbox.vibe_workshop`) so this shouldn't bite you — but if you build derived tables in your own sandbox and bind to them, create the tables first.
- **Blank page or stale UI after redeploy:** `databricks apps logs <INITIALS>-command-center` for backend errors. If logs look healthy, **hard-refresh the browser** (Cmd+Shift+R / Ctrl+Shift+R) — App static files are aggressively cached.

---

## Module 3: Genie Space (20 min)

**Goal:** Build a Genie space over all three pillars.

> Create a Genie space called `<INITIALS> Command Center` over all tables in `ioc_sandbox.vibe_workshop`. Use warehouse `<WAREHOUSE_NAME>`. Add 6 sample questions (2 per pillar: Labor / Inventory / Guest Feedback) and 4 metric definitions (labor % of sales, days of cover, sell-through rate, net sentiment score). Test it with one question per pillar.

If the answers are off, ask your agent to refine the instructions.

**Capture:** Genie space ID → `<GENIE_SPACE_ID>`.

---

## Module 4: AI/BI Dashboard (20 min)

**Goal:** A Lakeview dashboard with widgets per pillar.

> Create an AI/BI dashboard called `<INITIALS> Operator Insights` on warehouse `<WAREHOUSE_NAME>`. Add: (1) labor % of sales last 30 days as a line chart, (2) sales by daypart today vs forecast as a grouped bar, (3) stock health by category (at par / below par) as a stacked bar, (4) sentiment timeline last 30 days. Publish it.

**Capture:** Dashboard ID → `<DASHBOARD_ID>`.

---

## Break (10 min)

Stretch. Refill coffee. Make sure your App URL still loads.

---

## Module 5: Integrate + AI Insights + LCE Branding (40 min)

**Goal:** Wire Genie + dashboard into the App, add a "Recommended Actions" FMAPI panel, apply LCE branding.

> Embed dashboard `<DASHBOARD_ID>` into the App (one tile per pillar tab).

> Add an "Ask Genie" tab that embeds Genie space `<GENIE_SPACE_ID>`.

> Add a "Recommended Actions" sidebar visible on every tab. Use `ai_query()` with endpoint `<FMAPI_ENDPOINT>` to recommend the top 3 actions an operator should take this week, based on today's KPIs across the 3 pillars. Let users pick a store from a dropdown.

(The reference App in `dab/src/app/routers/` shows how to wire SQL warehouse reads, Lakebase writes, and Genie discovery. Borrow patterns liberally.)

> Apply LCE branding from `branding/lce/` in the workshop repo: logo at `branding/lce/logo.svg`, primary color `#FF671B`. Dark navbar. Page title "Command Center | LCE".

> Redeploy the app.

### If running low on time

Cut the dashboard-per-tab embed and put all the tiles on a single "Overview" tab. Genie + Recommended Actions are the higher-impact pieces.

---

## Module 6: DAB + Multi-Task Job + CI-CD (30 min)

**Goal:** Package everything as a Databricks Asset Bundle with a daily multi-task Job and dev/prod targets.

The workshop repo already contains a working DAB at `dab/`. You'll fork or copy it and customize.

> Clone https://github.com/jonathan-whiteley/ucode-vibe-workshop. Open `dab/`. Customize `databricks.yml` and the resource files to point at my App `<INITIALS>-command-center`, my Genie space `<GENIE_SPACE_ID>`, and my dashboard `<DASHBOARD_ID>` instead of the reference copies.

> Add a daily job at 6am ET with 3 tasks: (1) refresh derived tables in my sandbox, (2) score new sentiment via `ai_query()` and `<FMAPI_ENDPOINT>`, (3) redeploy the app.

> Deploy to dev: `databricks bundle deploy --target dev`. Then run the job once. Walk me through how I'd deploy to prod when I'm ready.

---

## Demo Round (15 min, 3:40-3:55)

Each attendee gets 1 minute:

1. Share your App URL
2. Show one Genie question that worked
3. Show one "Recommended Action" the FMAPI generated

---

## Wrap (5 min, 3:55-4:00)

- Workshop Slack channel: `<SLACK_CHANNEL>` for ongoing questions
- Optional office hours 1 week after
- Your App, DAB, and ucode setup are yours: keep iterating

---

## Vibe Coding Tips

- **Read every diff.** Agents move fast and are sometimes confidently wrong. Catch SQL that drops tables, code that hardcodes credentials, prompts that bypass auth.
- **Be specific about constraints when it matters** ("use the Databricks SQL connector, not pyodbc"); otherwise let the skills decide.
- **Iterate in small chunks.** One feature at a time is easier to review and debug.
- **When stuck, ask the agent to explain its own code.** Often surfaces the bug.

---

## Reference Links

- [Workshop repo](https://github.com/jonathan-whiteley/ucode-vibe-workshop)
- [databricks/ucode](https://github.com/databricks/ucode)
- [databricks-solutions/ai-dev-kit](https://github.com/databricks-solutions/ai-dev-kit/tree/main)
- [AI Gateway overview](https://docs.databricks.com/aws/en/ai-gateway/overview-beta)
- [Genie setup](https://docs.databricks.com/aws/en/genie/set-up)
- [Databricks Apps overview](https://docs.databricks.com/aws/en/dev-tools/databricks-apps)
- [Foundation Model APIs](https://docs.databricks.com/aws/en/machine-learning/foundation-models)
- [Databricks Asset Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles)
- [AI/BI Dashboards](https://docs.databricks.com/aws/en/dashboards)
