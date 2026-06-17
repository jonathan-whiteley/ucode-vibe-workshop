# LCE Workshop: Operator Command Center: Lab Companion Guide

**You'll build:** "Command Center", a Databricks App that surfaces AI insights and analytics across **Labor, Inventory, and Guest Feedback** for store operations. Your app will embed a Genie space, an AI/BI dashboard, and an FMAPI-powered "Recommended Actions" panel, all packaged as a Databricks Asset Bundle with a multi-task Job.

**Duration:** 3 hours, 1:00-4:00 PM ET.

### Quick Links

- **Workshop repo:** [github.com/jonathan-whiteley/ucode-vibe-workshop](https://github.com/jonathan-whiteley/ucode-vibe-workshop)
- **ucode:** [github.com/databricks/ucode](https://github.com/databricks/ucode)
- **ai-dev-kit:** [github.com/databricks-solutions/ai-dev-kit](https://github.com/databricks-solutions/ai-dev-kit/tree/main)
- **Workspace:** [adb-30827331698809.9.azuredatabricks.net](https://adb-30827331698809.9.azuredatabricks.net) (lce-analytics-dev-adb)

---

## 📅 Agenda

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

## 🌐 Your Workshop Environment

Most values are pre-filled below. The only one you set is **your initials**. Keep this table handy: you'll paste these values into prompts all afternoon.

| Item | Your value |
|---|---|
| Your initials (lowercase, e.g. `jjw`) | `<INITIALS>` ← **you fill this in** |
| Workspace URL | `https://adb-30827331698809.9.azuredatabricks.net` (lce-analytics-dev-adb) |
| Shared data catalog.schema | `ioc_sandbox.vibe_workshop` |
| Shared Lakebase instance | `command-center-lakebase` |
| SQL warehouse name | `serverless` |
| AI Gateway model endpoint (for `ucode codex`) | `databricks-gpt-oss-120b` |
| FMAPI endpoint (for `ai_query()`) | `databricks-gpt-oss-120b` (same as above) |
| LCE branding folder (in repo) | `branding/lce/` |
| **Captured during workshop:** | |
| Your Genie space ID | `<GENIE_SPACE_ID>` |
| Your dashboard ID | `<DASHBOARD_ID>` |
| Your App URL | `<APP_URL>` |

---

## 🧭 How to use this guide

Every prompt below is in a **code block** — hit the copy button, paste into your coding agent. **You only fill in `<INITIALS>` once**, in the **⭐ Session setup** prompt at the start of the day-of section. Every prompt after that says "my app", "my Genie space", etc. — your agent already knows the values from the setup prompt.

Prompts are short on purpose. Your agent has **ai-dev-kit** skills loaded — it knows how to build apps, Genie spaces, dashboards, and DABs on Databricks. Tell it *what*; the skills know *how*. **Always read what it generates before running it.**

---

## 📋 All prompts in one place

Skip ahead to the section that matches what you're doing. Each prompt has the full context inline in its module below — these are the same prompts, listed here for quick paste.

### 🎓 Prereqs prompts (run these before the workshop)

**Shell setup** (copy into your terminal):

```bash
# 1) Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2) Install node (macOS via Homebrew; non-mac: https://nodejs.org)
brew install node

# 3) Install ucode and launch a coding agent (OAuth into the workspace when prompted)
uv tool install git+https://github.com/databricks/ucode
ucode claude
```

**Inside the agent**, paste these one at a time:

```text
Set up the ai-dev-kit skills from https://github.com/databricks-solutions/ai-dev-kit/tree/main.
```

```text
Configure my MCP servers. Add Databricks SQL and the Managed Databricks MCPs.
```

```text
Smoke test: list the tables in ioc_sandbox.vibe_workshop. I should see 8 (3 dims_* and 5 facts_*).
```

If the smoke test returns 8 tables, you're ready. If anything above fails, ping the facilitator in the workshop Teams channel **before** the workshop starts.

### 🚀 Day-of prompts (run these in the workshop, in order)

#### ⭐ Session setup (paste this FIRST — fills in all your values once)

Substitute `<INITIALS>` once, paste, hit enter. Your agent will use these values for every prompt below — no more find-and-replace.

```text
I'm running the LCE ucode workshop. Set up session context using
these values and remember them throughout this conversation:

  My initials:  <INITIALS>   (← replace with yours, e.g. jjw)
  Workspace:    adb-30827331698809.9.azuredatabricks.net
  Catalog:      ioc_sandbox.vibe_workshop
  Warehouse:    serverless
  Model endpt:  databricks-gpt-oss-120b
                  (use for BOTH ai_query() AND the AI Gateway route)
  Lakebase:     command-center-lakebase

The resources I'll build today (use exactly these names):
  - my app:         <initials>-command-center
  - my Genie space: "<initials> Command Center"
  - my dashboard:   "<initials> Operator Insights"
  - my DAB job:     <initials>-command-center-refresh

Capture and remember as the workshop progresses:
  - my Genie space ID (after Module 3)
  - my dashboard ID  (after Module 4)
  - my app URL       (after Module 2)

Reference build to crib patterns from (especially dab/src/app/ for
SQL warehouse + Lakebase + Genie wiring):
  https://github.com/jonathan-whiteley/ucode-vibe-workshop

Confirm you've got it, then wait for my first module prompt.
```

Now paste each module's prompt in order; the agent already knows your initials and your resource names.

**Module 1 — Explore the data:**

```text
Module 1. Explore my workshop catalog. Show me schemas, row counts,
and sample rows for all 8 tables. Save a summary as schema_summary.md.
```

**Module 2 — App shell:**

```text
Module 2. Scaffold my AppKit app with 3 tabs (Labor, Inventory,
Guest Feedback) and placeholder content.

The app's service principal needs SELECT on the 8 workshop tables
and CAN_USE on the warehouse.

Deploy with `apps update --json` first to register the resources,
then `apps deploy`. Print the URL.
```

**Module 3 — Genie space:**

```text
Module 3. Create my Genie space over all 8 workshop tables.

Add 6 sample questions (2 per pillar: Labor / Inventory / Guest
Feedback) and 4 metric definitions (labor % of sales, days of
cover, sell-through rate, net sentiment score).

Test it with one question per pillar, then capture and remember
the space ID.
```

**Module 4 — AI/BI dashboard:**

```text
Module 4. Create my AI/BI dashboard with 4 widgets:
  (1) labor % of sales last 30 days as a line chart
  (2) sales by daypart today vs forecast as a grouped bar
  (3) stock health by category (at par / below par) as a stacked bar
  (4) sentiment timeline last 30 days

Publish it, then capture and remember the dashboard ID.
```

**Module 5 — Integrate + AI + branding** (paste one at a time):

```text
Embed my dashboard into my app, one tile per pillar tab.
```

```text
Add an "Ask Genie" tab to my app that embeds my Genie space.
```

```text
Add a "Recommended Actions" sidebar visible on every tab. Use
ai_query() with the model endpoint to recommend the top 3 actions
an operator should take this week, based on today's KPIs across
Labor / Inventory / Guest Feedback.

Let users pick a store from a dropdown.
```

```text
Apply LCE branding from branding/lce/ in the workshop repo:
  - logo at branding/lce/logo.svg
  - primary color #FF671B
  - dark navbar
  - page title "Command Center | LCE"

Redeploy my app.
```

**Module 6 — DAB + Job + CI-CD** (paste one at a time):

```text
Clone the workshop repo. Open dab/. Customize databricks.yml and
the resource files to point at MY app, MY Genie space, and MY
dashboard instead of the reference copies.
```

```text
Add a daily job at 6am ET with 3 tasks:
  (1) refresh derived tables in my sandbox
  (2) score new sentiment via ai_query() and the model endpoint
  (3) redeploy my app
```

```text
Deploy the bundle to the dev target and run the job once. Then walk
me through what I'd change to deploy to prod when I'm ready.
```

---

## 🎓 Step 0: Pre-Workshop Setup (30 min, do this before 1pm)

The prompts in "Prereqs prompts" above match this checklist. Tick each box as you go. If any step fails, ping the facilitator in the workshop Teams channel **before** the workshop starts.

- [ ] `uv` installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- [ ] `npm` installed (`brew install node` on macOS, or see nodejs.org)
- [ ] `ucode` installed (`uv tool install git+https://github.com/databricks/ucode`)
- [ ] Coding agent launched + OAuthed to the workspace (`ucode claude` or `ucode codex`)
- [ ] `ucode status` shows the workspace + AI Gateway model endpoint
- [ ] MCP servers added: Databricks SQL + Managed Databricks MCPs
- [ ] ai-dev-kit skills loaded
- [ ] Smoke test passed: agent lists 8 tables in `ioc_sandbox.vibe_workshop` (3 `dims_*`, 5 `facts_*`)

---

## 🔍 Module 1: Explore the Data (10 min)

**Goal:** Ground the agent in the actual schema before building anything.

> 💡 Make sure you've already pasted the **⭐ Session setup** prompt from the "All prompts" section. Every prompt below assumes the agent knows your initials, warehouse, catalog, etc.

```text
Module 1. Explore my workshop catalog. Show me schemas, row counts,
and sample rows for all 8 tables. Save a summary as schema_summary.md.
```

Read the summary. Make sure the agent has it open in context for the rest of the workshop.

---

## 🏗️ Module 2: Scaffold the App Shell (20 min)

**Goal:** Get an empty Command Center deployed and visible. Doing this before Genie/dashboard means deployment issues surface early.

```text
Module 2. Scaffold my AppKit app with 3 tabs (Labor, Inventory,
Guest Feedback) and placeholder content.

The app's service principal needs SELECT on the 8 workshop tables
and CAN_USE on the warehouse.

Deploy with `apps update --json` first to register the resources,
then `apps deploy`. Print the URL.
```

Paste the URL into your environment table as `<APP_URL>`.

**Reference if you get stuck:** there's a fully-wired reference App in the workshop repo at `dab/src/app/`. The patterns in `lib/` (config, deps, sql_utils) and `routers/` are good cribs when wiring your own SQL + Lakebase + Genie integration.

### If it breaks

- **"Permission denied" at runtime on UC tables:** the App's SP didn't get its resources. ai-dev-kit's pattern is `databricks apps update <name> --json '{"resources":[...]}' --no-compute` **first**, then `databricks bundle deploy` (or `apps deploy`). Skipping the `apps update` step is the #1 failure mode — the resource block in `app.yaml` alone isn't enough on first deploy. The reference App's `dab/resources/app.yml` shows the working bindings (warehouse `CAN_USE` + 8 tables `SELECT` + Lakebase).
- **"SCHEMA_DOES_NOT_EXIST" or "TABLE_OR_VIEW_NOT_FOUND" at deploy:** the App resource block references tables that don't exist yet. You're using a shared schema (`ioc_sandbox.vibe_workshop`) so this shouldn't bite you — but if you build derived tables in your own sandbox and bind to them, create the tables first.
- **Blank page or stale UI after redeploy:** ask the agent to run `databricks apps logs` on your app for backend errors. If logs look healthy, **hard-refresh the browser** (Cmd+Shift+R / Ctrl+Shift+R) — App static files are aggressively cached.

---

## 🧞 Module 3: Genie Space (20 min)

**Goal:** Build a Genie space over all three pillars.

```text
Module 3. Create my Genie space over all 8 workshop tables.

Add 6 sample questions (2 per pillar: Labor / Inventory / Guest
Feedback) and 4 metric definitions (labor % of sales, days of
cover, sell-through rate, net sentiment score).

Test it with one question per pillar, then capture and remember
the space ID.
```

If the answers are off, ask your agent to refine the instructions.

**Capture:** Your Genie space ID (the agent should remember it for later modules).

---

## 📊 Module 4: AI/BI Dashboard (20 min)

**Goal:** A Lakeview dashboard with widgets per pillar.

```text
Module 4. Create my AI/BI dashboard with 4 widgets:
  (1) labor % of sales last 30 days as a line chart
  (2) sales by daypart today vs forecast as a grouped bar
  (3) stock health by category (at par / below par) as a stacked bar
  (4) sentiment timeline last 30 days

Publish it, then capture and remember the dashboard ID.
```

**Capture:** Your dashboard ID (the agent should remember it for Module 5).

---

## ☕ Break (10 min)

Stretch. Refill coffee. Make sure your App URL still loads.

---

## 🔗 Module 5: Integrate + AI Insights + LCE Branding (40 min)

**Goal:** Wire Genie + dashboard into the App, add a "Recommended Actions" FMAPI panel, apply LCE branding. Paste these one at a time.

```text
Embed my dashboard into my app, one tile per pillar tab.
```

```text
Add an "Ask Genie" tab to my app that embeds my Genie space.
```

```text
Add a "Recommended Actions" sidebar visible on every tab. Use
ai_query() with the model endpoint to recommend the top 3 actions
an operator should take this week, based on today's KPIs across
Labor / Inventory / Guest Feedback.

Let users pick a store from a dropdown.
```

(The reference App in `dab/src/app/routers/` shows how to wire SQL warehouse reads, Lakebase writes, and Genie discovery. Borrow patterns liberally.)

```text
Apply LCE branding from branding/lce/ in the workshop repo:
  - logo at branding/lce/logo.svg
  - primary color #FF671B
  - dark navbar
  - page title "Command Center | LCE"

Redeploy my app.
```

### If running low on time

Cut the dashboard-per-tab embed and put all the tiles on a single "Overview" tab. Genie + Recommended Actions are the higher-impact pieces.

---

## 📦 Module 6: DAB + Multi-Task Job + CI-CD (30 min)

**Goal:** Package everything as a Databricks Asset Bundle with a daily multi-task Job and dev/prod targets.

The workshop repo already contains a working DAB at `dab/`. You'll fork or copy it and customize. Paste these one at a time.

```text
Clone the workshop repo. Open dab/. Customize databricks.yml and
the resource files to point at MY app, MY Genie space, and MY
dashboard instead of the reference copies.
```

```text
Add a daily job at 6am ET with 3 tasks:
  (1) refresh derived tables in my sandbox
  (2) score new sentiment via ai_query() and the model endpoint
  (3) redeploy my app
```

```text
Deploy the bundle to the dev target and run the job once. Then walk
me through what I'd change to deploy to prod when I'm ready.
```

---

## 🎤 Demo Round (15 min, 3:40-3:55)

Each attendee gets 1 minute:

1. Share your App URL
2. Show one Genie question that worked
3. Show one "Recommended Action" the FMAPI generated

---

## 🎁 Wrap (5 min, 3:55-4:00)

- Workshop Teams channel: `<TEAMS_CHANNEL>` for ongoing questions
- Optional office hours 1 week after
- Your App, DAB, and ucode setup are yours: keep iterating

---

## 💡 Vibe Coding Tips

- **Read every diff.** Agents move fast and are sometimes confidently wrong. Catch SQL that drops tables, code that hardcodes credentials, prompts that bypass auth.
- **Be specific about constraints when it matters** ("use the Databricks SQL connector, not pyodbc"); otherwise let the skills decide.
- **Iterate in small chunks.** One feature at a time is easier to review and debug.
- **When stuck, ask the agent to explain its own code.** Often surfaces the bug.

---

## 🔖 Reference Links

- [Workshop repo](https://github.com/jonathan-whiteley/ucode-vibe-workshop)
- [databricks/ucode](https://github.com/databricks/ucode)
- [databricks-solutions/ai-dev-kit](https://github.com/databricks-solutions/ai-dev-kit/tree/main)
- [AI Gateway overview](https://docs.databricks.com/aws/en/ai-gateway/overview-beta)
- [Genie setup](https://docs.databricks.com/aws/en/genie/set-up)
- [Databricks Apps overview](https://docs.databricks.com/aws/en/dev-tools/databricks-apps)
- [Foundation Model APIs](https://docs.databricks.com/aws/en/machine-learning/foundation-models)
- [Databricks Asset Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles)
- [AI/BI Dashboards](https://docs.databricks.com/aws/en/dashboards)
