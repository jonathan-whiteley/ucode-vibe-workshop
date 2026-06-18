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

## 🧭 How to use this guide

Every prompt below is in a **code block** — hit the copy button, paste into your coding agent. **You only fill in `<INITIALS>` once**, in the **⭐ Session setup** prompt at the start of the day-of section. Every prompt after that says "my app", "my Genie space", etc. — your agent already knows the values from the setup prompt.

Prompts are short on purpose. Your agent has **ai-dev-kit** skills loaded — it knows how to build apps, Genie spaces, dashboards, and DABs on Databricks. Tell it *what*; the skills know *how*. **Always read what it generates before running it.**

---

## 📋 All prompts in one place

Skip ahead to the section that matches what you're doing. Each prompt has the full context inline in its module below — these are the same prompts, listed here for quick paste.

### 🎓 Prereqs prompts (run these before the workshop)

**Shell setup** — pick the block that matches your OS.

**macOS / Linux** (Terminal / iTerm / any Unix shell):

```bash
# 1) Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2) Install node (macOS via Homebrew; Linux: see nodejs.org)
brew install node

# 3) Install ucode and launch a coding agent (OAuth into the workspace when prompted)
uv tool install git+https://github.com/databricks/ucode
ucode claude
```

**Windows** (PowerShell — not Command Prompt). All steps are user-scope, no admin needed:

```powershell
# 1) Install uv (user scope, no admin)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Refresh PATH so the new uv is visible in this session
# (the installer adds it to your user PATH but PowerShell only reads PATH at startup)
$env:Path = [Environment]::GetEnvironmentVariable("Path", "User") + ";" + [Environment]::GetEnvironmentVariable("Path", "Machine")
uv --version   # should print a version

# 2) Install Scoop (user-scope package manager), then Node LTS via Scoop
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
scoop install nodejs-lts

# Refresh PATH again (Scoop and Node also updated user PATH)
$env:Path = [Environment]::GetEnvironmentVariable("Path", "User") + ";" + [Environment]::GetEnvironmentVariable("Path", "Machine")
node -v   # should print v20.x

# 3) Install ucode and launch a coding agent (OAuth into the workspace when prompted)
uv tool install git+https://github.com/databricks/ucode
ucode claude
```

> ⚠️ **Windows gotchas:**
> - `curl | sh` from the Unix block WON'T work in PowerShell. Use the `irm | iex` form above.
> - `winget install OpenJS.NodeJS.LTS` requires admin on most managed laptops — Scoop is user-scope and bypasses that.
> - **"uv is not recognized" / "node is not recognized"** right after install: the installer updated your user PATH, but the current PowerShell session was started before that. Run the `$env:Path = ...` refresh shown above, or just close and re-open PowerShell.

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

**Checklist — tick each box as you go.** If anything fails, ping the facilitator in the workshop Teams channel **before** the workshop starts.

- [ ] `uv` installed (mac/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh` · Windows PowerShell: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`)
- [ ] Node installed (macOS: `brew install node` · Windows: `irm get.scoop.sh | iex` then `scoop install nodejs-lts` · Linux: see nodejs.org)
- [ ] `ucode` installed (`uv tool install git+https://github.com/databricks/ucode`)
- [ ] Coding agent launched + OAuthed to the workspace (`ucode claude` or `ucode codex`)
- [ ] `ucode status` shows the workspace + AI Gateway model endpoint
- [ ] MCP servers added: Databricks SQL + Managed Databricks MCPs
- [ ] ai-dev-kit skills loaded
- [ ] Smoke test passed: agent lists 8 tables in `ioc_sandbox.vibe_workshop` (3 `dims_*`, 5 `facts_*`)

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
  Model endpt:  databricks-claude-sonnet-4-6
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

### 🔍 Module 1: Explore the data (1:10-1:20)

```text
Module 1. Explore my workshop catalog. Show me schemas, row counts,
and sample rows for all 8 tables. Save a summary as schema_summary.md.
```

### 🏗️ Module 2: App shell (1:20-1:40)

```text
Module 2. Scaffold my AppKit app with 3 tabs (Labor, Inventory,
Guest Feedback) and placeholder content.

The app's service principal needs SELECT on the 8 workshop tables
and CAN_USE on the warehouse.

Deploy with `apps update --json` first to register the resources,
then `apps deploy`. Print the URL.
```

> 💡 **If deploy fails with "Permission denied" on UC tables:** the `apps update --json` step is mandatory before `apps deploy` on first deploy — the resource block in `app.yaml` alone isn't enough. Reference: [`dab/resources/app.yml`](https://github.com/jonathan-whiteley/ucode-vibe-workshop/blob/main/dab/resources/app.yml). Hard-refresh (Cmd+Shift+R) if the UI looks stale after redeploy — App static files are aggressively cached.

### 🧞 Module 3: Genie space (1:40-2:00)

```text
Module 3. Create my Genie space over all 8 workshop tables.

Add 6 sample questions (2 per pillar: Labor / Inventory / Guest
Feedback) and 4 metric definitions (labor % of sales, days of
cover, sell-through rate, net sentiment score).

Test it with one question per pillar, then capture and remember
the space ID.
```

### 📊 Module 4: AI/BI dashboard (2:00-2:20)

```text
Module 4. Create my AI/BI dashboard with 4 widgets:
  (1) labor % of sales last 30 days as a line chart
  (2) sales by daypart today vs forecast as a grouped bar
  (3) stock health by category (at par / below par) as a stacked bar
  (4) sentiment timeline last 30 days

Publish it, then capture and remember the dashboard ID.
```

### ☕ Break (2:20-2:30)

### 🔗 Module 5: Integrate + AI + branding (2:30-3:10) — paste one at a time

```text
Embed my dashboard into my app, one tile per pillar tab.
```

```text
Add an "Ask Genie" chat panel to my app where users type questions in
natural language and get answers (with the SQL Genie generated) back
from my Genie space.

Wiring requirements — the reference build at
dab/src/app/routers/genie.py shows the exact working pattern; borrow
it. Common ways this breaks:

  1. Use OBO (on-behalf-of-user) auth, NOT the app's service principal.
     Genie spaces are user-permissioned, so SP calls 403 on
     start-conversation. The logged-in user's bearer token is in the
     X-Forwarded-Access-Token request header.

  2. In the app's resource block (dab/resources/app.yml), declare
     user_api_scopes:
       - genie
       - sql
       - dashboards.genie
     Without these the forwarded user token lacks the genie scope and
     start-conversation 403s with "Invalid scope, required scopes:
     genie". After adding scopes, redeploy + you'll re-consent on first
     open.

  3. Support multi-turn: first ask calls
     POST /api/2.0/genie/spaces/{space_id}/start-conversation;
     follow-up asks call
     POST /api/2.0/genie/spaces/{space_id}/conversations/{conv_id}/messages
     so Genie sees prior context. The backend should return
     conversation_id; the UI should thread it back on subsequent asks.
     Reset the conversation_id when the user closes the panel.

  4. Poll GET /messages/{msg_id} until status is COMPLETED (or up to
     ~45s), then extract the assistant text + first SQL query from the
     attachments array.
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

> 💡 **If running low on time:** drop the per-tab dashboard embed and put all 4 widgets on a single "Overview" tab. Genie + Recommended Actions are the higher-impact pieces.

### 📦 Module 6: DAB + Job + CI-CD (3:10-3:40) — paste one at a time

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

### 🎤 Demo round + wrap (3:40-4:00)

1 min per attendee: share your App URL, show one Genie question that worked, show one Recommended Action. Workshop Teams channel for ongoing questions; optional office hours 1 week after.

---

## 🌐 Workshop Environment (reference)

Pre-filled values used throughout the workshop. The **⭐ Session setup** prompt at the top already pastes these into your agent — this table is here in case you need to look one up manually.

| Item | Your value |
|---|---|
| Your initials (lowercase, e.g. `jjw`) | `<INITIALS>` ← **you fill this in** |
| Workspace URL | `https://adb-30827331698809.9.azuredatabricks.net` (lce-analytics-dev-adb) |
| Shared data catalog.schema | `ioc_sandbox.vibe_workshop` |
| Shared Lakebase instance | `command-center-lakebase` |
| SQL warehouse name | `serverless` |
| AI Gateway model endpoint (for `ucode codex`) | `databricks-claude-sonnet-4-6` |
| FMAPI endpoint (for `ai_query()`) | `databricks-claude-sonnet-4-6` (same as above) |
| LCE branding folder (in repo) | `branding/lce/` |
| **Captured during workshop:** | |
| Your Genie space ID | `<GENIE_SPACE_ID>` |
| Your dashboard ID | `<DASHBOARD_ID>` |
| Your App URL | `<APP_URL>` |

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
