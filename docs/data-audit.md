# Data Audit: Homebase Design vs. Workshop Schema

The `app/reference-prototype/Homebase.html` design is a polished Operator Command Center for a fictional QSR chain (Lakehouse Market). This doc maps every chart and insight in the design to the workshop's UC schema, calls out gaps, and flags what's too complex for a 3-hour workshop.

**Reference design:** `app/reference-prototype/Homebase.html`
**Workshop schema:** `ioc_sandbox.vibe_workshop` (currently materialized in `jdub_demo.vibe_workshop` for dev)
**3 pillars in scope:** Labor, Inventory, Guest Feedback

---

## Verdict by module

### Today (home brief + KPIs)

| UI element | Data needed | We have | Verdict |
|---|---|---|---|
| Sales yesterday + sparkline (12 pts) | Daily revenue trend last 12 days | `facts_sales_inventory_daily` | OK |
| Forecast today + confidence | Forecast for today | NOT in schema | **Gap.** Compute with `ai_forecast()` on `facts_sales_inventory_daily` at workshop time, or pre-stage in a derived table |
| Labor cost % | Daily labor cost / daily revenue | `facts_labor_daily` + `facts_sales_inventory_daily` | OK |
| Guest score (4.3★ / NPS) | Avg rating + NPS rollup | `facts_customer_feedback` | OK |
| Guests count | Daily guest count | NOT in schema | **Gap.** Either drop this KPI or add `daily_guest_count` (could synthesize as `units_sold` / avg basket) |
| "Genie · your daily brief" prose | LLM-generated summary | `ai_query()` against any FMAPI endpoint | OK |
| 3 module cards (Labor / Inventory / Feedback) | Outstanding counts per module | Derived from the modules below | OK |

### Labor

| UI element | Data needed | We have | Verdict |
|---|---|---|---|
| **Day-part planner hero** (Breakfast / Lunch / Dinner / Late) | Tomorrow's revenue forecast by daypart, recommended crew + cost | We have **daily-only** labor + sales, no daypart granularity | **Gap.** Add `facts_sales_daypart` OR scope Labor down to daily-grain (skip the planner UI's per-daypart cards) |
| Schedule vs. forecast bar chart (Mon-Sun) | Planned headcount vs. forecast demand by day | `facts_labor_daily` has `headcount`, but no "forecast" column | **Partial.** Either compute forecast at runtime via `ai_forecast()` or derive from rolling average |
| Timecards needing approval (shift-level) | Individual shifts with scheduled vs. actual times, overtime, compliance flags | NOT in schema (we have daily aggregates) | **Gap.** Add `dims_employees` + `facts_shifts` (recommended) — or scope down to "approve yesterday's total labor" |
| Recent days table (forecast → approved → actual) | Daily totals with forecast | Partial | **Partial** — same as above, needs forecast |

### Inventory

| UI element | Data needed | We have | Verdict |
|---|---|---|---|
| Stock health donut (X of Y SKUs at par) | Per-SKU on-hand vs. par/reorder for current day | `facts_sales_inventory_daily.on_hand_eod` + `reorder_point` | OK |
| Stock value trend (8 weeks) | Weekly on-hand × unit cost | `facts_sales_inventory_daily.on_hand_eod` × `dims_items.cost` | OK |
| Days of cover per SKU | On-hand ÷ avg daily usage | `facts_sales_inventory_daily.units_sold` rolling avg | OK |
| Vendor lead-time marker | Lead time per SKU/vendor | NOT in schema | **Gap.** Either add `dims_vendors` or hardcode a default 2-day lead time |
| Fill rate by category | % of par on hand, grouped by `dims_items.category` | `dims_items` + `facts_sales_inventory_daily` | OK |
| Staged reorder POs (multi-vendor, multi-line, ETA) | Pre-built PO records | NOT in schema | **Gap.** Either compute on the fly (any SKU where `on_hand < reorder_point` becomes a candidate line, grouped by category as a stand-in vendor), OR add `facts_purchase_orders` + `dims_vendors` |
| "Release order" write-back | Lakebase write | NEEDED | Pre-provision shared Lakebase with `purchase_orders` table |

### Guest Feedback

| UI element | Data needed | We have | Verdict |
|---|---|---|---|
| Review list with rating, channel, time | Per-feedback row | `facts_customer_feedback` | OK |
| Themes rollup ("Pickup wait times", "Friendly staff", etc.) | Topic clusters | NOT in schema | **Partial.** Either compute at workshop time with `ai_classify()` over `feedback_text`, or pre-stage 4-6 themes in a derived table |
| **Sentiment timeline (30-day stacked area: pos/neu/neg counts per day)** | Per-day sentiment counts | `facts_customer_feedback.rating` (1-2=neg, 3=neu, 4-5=pos) grouped by `date` | OK. Aggregate at query time, or pre-stage in a derived table. If we want true sentiment (not rating buckets), run `ai_classify` over `feedback_text` and stage the result |
| AI-drafted reply per review | Generated reply text | `ai_query()` against FMAPI at runtime | OK |
| "Reply sent" write-back | Lakebase write | NEEDED | Pre-provision shared Lakebase with `review_replies` table |

### Genie slide-over

| UI element | Data needed | We have | Verdict |
|---|---|---|---|
| Natural-language Q&A panel | Genie space over all workshop tables | All 5 + any derived tables | OK |
| Citations to "governed table" | Genie response metadata | Genie API returns this | OK |

---

## Schema gaps: recommended additions

Pick what you actually want in v1. The smaller the additions, the less wrangling time.

**Add 2 tables (recommended minimum to support the design as-built):**

1. **`dims_employees`** — needed for shift-level timecard approvals.
   - `employee_id`, `store_id`, `name`, `role` (cook/cashier/lead/manager), `hire_date`
2. **`facts_shifts`** — needed for shift-level timecard approvals.
   - `shift_id`, `employee_id`, `store_id`, `date`, `role`, `scheduled_start`, `scheduled_end`, `actual_start`, `actual_end`, `hours_worked`, `overtime_hours`, `has_issue` (bool), `issue_note`

**Add 1 more table if you want the day-part Labor Planner UI as-designed:**

3. **`facts_sales_daypart`** — daypart-level forecasts and actuals.
   - `date`, `store_id`, `daypart` (breakfast/lunch/dinner/late), `forecast_revenue`, `actual_revenue`, `forecast_traffic`, `actual_traffic`

**Optional (nice-to-have, can be computed instead):**

4. `dims_vendors` (`vendor_id`, `name`, `lead_time_days`, `cutoff_time`) — for inventory PO ETAs
5. `facts_purchase_orders` (`po_id`, `vendor_id`, `store_id`, `created_at`, `eta`, `status`) + `po_lines` — for the staged-reorder workflow
6. `facts_feedback_themes` (`theme`, `count_7d`, `direction`, `sentiment`) — if you don't want to run `ai_classify` live in the workshop

If you skip #4-#6, the corresponding UI gets computed at runtime via SQL or LLM calls. Slight latency hit; no schema bloat.

---

## What I'd cut or simplify to stay in 3 hours

| Design element | Recommendation | Why |
|---|---|---|
| **Lakebase writeback per attendee** | **Pre-provision 1 shared Lakebase instance** named `vibe-workshop-lakebase` with 4 tables: `timecards_approved`, `purchase_orders_released`, `review_replies`, `schedules_approved`. Grant the App's SP write access. | Setting up Lakebase per person is 30+ min/attendee and a hard blocker if any attendee hits a provisioning glitch |
| **Day-part planner inline overrides** (`Bump lunch +12%` → live recompute) | Keep the visual cards, but make them **read-only** (no inline override). Just show forecast + recommended crew. | The override math is fun but adds ~30 min of frontend code per attendee |
| **Multi-step approval flow** ("Why the change?" prompt before `Lakebase.schedules` write) | Skip the modal. One-tap approve. | Adds 15 min, low signal |
| **Equipment + Loyalty modules** | Already cut. Stay cut. | Out of scope for 3 pillars |
| **Hourly sales chart on Today** | Cut — KPI strip is enough for the Today screen | Saves a chart, saves a query |
| **Tweaks panel** (brand accent picker, AI brief style, etc.) | Cut. It's a fun-to-have, not core. | Saves ~15 min |

---

## What to pre-provision (facilitator T-1 week)

In addition to the existing prereqs:

1. **Shared Lakebase instance** `vibe-workshop-lakebase` with these tables:
   ```sql
   CREATE TABLE timecards_approved (
     approval_id UUID PRIMARY KEY,
     shift_id TEXT, store_id TEXT, approved_by TEXT,
     approved_at TIMESTAMP, notes TEXT
   );
   CREATE TABLE purchase_orders_released (
     po_id UUID PRIMARY KEY,
     vendor TEXT, store_id TEXT, total_amount NUMERIC,
     released_by TEXT, released_at TIMESTAMP
   );
   CREATE TABLE review_replies (
     reply_id UUID PRIMARY KEY,
     feedback_id TEXT, store_id TEXT, reply_text TEXT,
     replied_by TEXT, replied_at TIMESTAMP
   );
   CREATE TABLE schedules_approved (
     approval_id UUID PRIMARY KEY,
     date DATE, store_id TEXT, total_hours NUMERIC,
     approved_by TEXT, approved_at TIMESTAMP, reason TEXT
   );
   ```
   Grant the attendee group `INSERT, SELECT` on all 4 tables.

2. **FMAPI endpoint** confirmed accessible for `ai_query()`:
   - For "Recommended Actions" sidebar
   - For drafting review replies
   - For the Today daily brief

3. **(Optional) `ai_forecast()` accessibility** — DBSQL AI function. If the workshop wants forecasts vs. historical, this is the cleanest path.

4. **LCE logo + brand color** — the design uses Databricks brand by default; if LCE wants its own colors, swap the `--db-lava-600` token in `colors_and_type.css`.

---

## Implementation status

- [x] Design files copied to `app/reference-prototype/` (HTML/JSX/CSS/assets)
- [x] Prototype confirmed renders locally: `cd app/reference-prototype && python3 -m http.server 8765` → http://localhost:8765/Homebase.html
- [ ] Real AppKit build wired to workshop data (this is what attendees produce in Modules 2-5)
- [ ] Synthetic data extensions for `dims_employees`, `facts_shifts`, `facts_sales_daypart`
- [ ] Shared Lakebase provisioned

The prototype is the design source of truth. The real AppKit build is what gets constructed during the workshop via ucode + ai-dev-kit.
