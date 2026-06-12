# Data Audit: Homebase Design vs. Workshop Schema

The `app/reference-prototype/Homebase.html` design is the Operator Command Center prototype. This doc maps every chart and insight in the design to the workshop's UC schema and flags what's been cut to stay in a 3-hour workshop.

**Reference design:** `app/reference-prototype/Homebase.html`
**Workshop schema:** `ioc_sandbox.vibe_workshop` (currently materialized in `jdub_demo.vibe_workshop` for dev)
**3 pillars in scope:** Labor, Inventory, Guest Feedback
**Tables (3 dims + 5 facts):** `dims_stores`, `dims_items`, `dims_employees`, `facts_sales_daypart`, `facts_labor_daypart`, `facts_sales_inventory_daily`, `facts_purchase_orders`, `facts_customer_feedback`. See `data/README.md` for column-level details.

---

## Verdict by module

### Today (home brief + KPIs)

| UI element | Backing data | Verdict |
|---|---|---|
| Sales yesterday + sparkline | `facts_sales_daypart` rolled up to daily | OK |
| Forecast today + confidence | `facts_sales_daypart.forecast_revenue` (confidence hardcoded or derived from forecast/actual ratio) | OK |
| Labor cost % | `facts_labor_daypart.labor_cost` ÷ `facts_sales_daypart.revenue` rolled to day | OK |
| Guest score (★ / NPS) | `facts_customer_feedback.rating` + `nps` aggregated | OK |
| Guests count | `facts_sales_daypart.traffic` rolled to day | OK |
| "Genie · your daily brief" prose | `ai_query()` against any FMAPI endpoint at render time | OK |
| 3 module cards (Labor / Inventory / Feedback) | Outstanding counts derived from modules below | OK |

### Labor

| UI element | Backing data | Verdict |
|---|---|---|
| Day-part planner hero (predicted sales, recommended labor, labor %) | `facts_sales_daypart` + `facts_labor_daypart` rolled to tomorrow | OK |
| 4 day-part cards (Breakfast / Lunch / Dinner / Late) | `facts_sales_daypart` (forecast_revenue + traffic) + `facts_labor_daypart` (forecast_headcount, forecast_labor_cost) by role | OK |
| Role mix per daypart (5 cooks, 4 cashiers, etc.) | `facts_labor_daypart.headcount` grouped by `role` | OK |
| Team-member roster (who is scheduled) | `dims_employees` | OK |
| Recent days table (forecast → actual) | `facts_sales_daypart` and `facts_labor_daypart` 7-day rollup; "approved" column from Lakebase write log | OK |
| Forecast confidence chip | Not in schema. Hardcode 90% or derive from forecast/actual deviation. | Tiny gap, low impact |
| **Timecard approvals** | — | **Cut** (per decision) |
| **Compliance flags** ("Missed meal break") | — | **Cut** with timecards |

### Inventory

| UI element | Backing data | Verdict |
|---|---|---|
| Stock health donut (X of Y SKUs at par) | `facts_sales_inventory_daily.on_hand_eod` vs `reorder_point`, latest snapshot | OK |
| Stock value trend (8 weeks) | `SUM(on_hand_eod × dims_items.cost)` per week | OK |
| Days of cover per SKU | `on_hand_eod ÷ avg(units_sold)` rolling | OK |
| Vendor lead-time marker | `facts_purchase_orders.lead_time_days` joined by SKU | OK |
| Fill rate by category | `facts_sales_inventory_daily` JOIN `dims_items` | OK |
| Staged reorder POs (vendor, ETA, line items, status) | `facts_purchase_orders` (pre-staged, flattened) | OK |
| "Release order" write-back | Shared Lakebase `purchase_orders_released` | Needs Lakebase provisioned |

### Guest Feedback

| UI element | Backing data | Verdict |
|---|---|---|
| Review list with rating, channel, time | `facts_customer_feedback` | OK |
| Themes 4-tile rollup ("Pickup wait times", "Friendly staff", etc.) | SQL `GROUP BY theme` on `facts_customer_feedback` | OK |
| 30-day sentiment timeline (stacked area) | SQL `GROUP BY date, sentiment_label` on `facts_customer_feedback` | OK |
| AI-drafted reply per review | `facts_customer_feedback.ai_drafted_reply` (pre-staged) | OK |
| "Reply sent" write-back | Shared Lakebase `review_replies` | Needs Lakebase provisioned |

### Genie slide-over

| UI element | Backing data | Verdict |
|---|---|---|
| Natural-language Q&A panel | Genie space over all 8 tables, joined on `store_id` / `sku` / `daypart` | OK |
| Citations to "governed table" | Genie API returns this | OK |

---

## What was cut from the design

| Design element | Why |
|---|---|
| **Timecard approvals** | Drops a UI feature that needed shift-level data. We capture roles in `dims_employees`; we don't model individual shifts. |
| **Compliance flags** | Lived inside the timecard approval list; gone with it. |
| **Day-part planner inline overrides** ("Bump lunch +12%" → live recompute) | Keep the visual cards but make them **read-only** to stay in time. The override math is fun but adds ~30 min/attendee. |
| **"Why the change?" approval modal** | One-tap approve instead. |
| **Tweaks panel** (brand accent picker, AI brief style) | Out of scope for the workshop. |
| **Equipment + Loyalty modules** | Out of 3-pillar scope. |

## Per-attendee complexity reduction

| Risk | Mitigation |
|---|---|
| Per-attendee Lakebase provisioning | **Pre-provision 1 shared Lakebase** `vibe-workshop-lakebase` with 4 tables (`timecards_approved`, `purchase_orders_released`, `review_replies`, `schedules_approved`). Attendees' Apps' SPs get `INSERT, SELECT` on these. |
| Per-attendee FMAPI endpoint setup | Use a managed Databricks foundation model (`databricks-meta-llama-3-3-70b-instruct` or similar); confirm attendee group has query access |
| Per-attendee data generation | Already pre-generated in `ioc_sandbox.vibe_workshop`; attendees only read |

---

## What to pre-provision (facilitator, T-1 week)

1. **Shared Lakebase instance** `vibe-workshop-lakebase`:
   ```sql
   CREATE TABLE purchase_orders_released (
     event_id UUID PRIMARY KEY,
     po_id TEXT, store_id TEXT, total_amount NUMERIC,
     released_by TEXT, released_at TIMESTAMP
   );
   CREATE TABLE review_replies (
     event_id UUID PRIMARY KEY,
     feedback_id TEXT, store_id TEXT, reply_text TEXT,
     replied_by TEXT, replied_at TIMESTAMP
   );
   CREATE TABLE schedules_approved (
     event_id UUID PRIMARY KEY,
     date DATE, store_id TEXT, total_hours NUMERIC,
     approved_by TEXT, approved_at TIMESTAMP
   );
   ```
   Grant the attendee group `INSERT, SELECT` on all 3 tables.

2. **FMAPI endpoint** accessible to the attendee group (used by the Today daily brief and any optional `ai_query()` enrichments).

3. **LCE branding** (optional, opt-in only) — `branding/lce/` ships logo + favicon + CSS-token overrides. Don't apply by default.

---

## Implementation status

- [x] Design files in `app/reference-prototype/`
- [x] Prototype renders locally: `cd app/reference-prototype && python3 -m http.server 8765` → http://localhost:8765/Homebase.html
- [x] 8-table schema implemented in `data/ddl.sql` + `data/generate_data.py`
- [x] Data materialized in `jdub_demo.vibe_workshop`
- [x] LCE branding assets in `branding/lce/` (opt-in only, not wired into prototype)
- [ ] Real AppKit build wired to workshop data (this is what attendees produce in Modules 2-5)
- [ ] Shared `vibe-workshop-lakebase` provisioned

The prototype is the design source of truth. The real AppKit build is what gets constructed during the workshop via ucode + ai-dev-kit.
