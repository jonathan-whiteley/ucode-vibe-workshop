"""/api/inventory — stock-health + watched-items for the Inventory module."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from lib.config import get_settings
from lib.sql_utils import fetch_all, fetch_one

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


class StockHealth(BaseModel):
    total_skus: int
    at_par: int
    below_par: int
    pct_at_par: float


class CategoryFill(BaseModel):
    category: str
    sku_count: int
    below_par: int
    pct_at_par: float


class WatchedItem(BaseModel):
    sku: str
    item_name: str
    category: str
    on_hand_eod: int
    reorder_point: int
    days_of_cover: float | None
    vendor_name: str | None = None
    lead_time_days: int | None = None


@router.get("/health", response_model=StockHealth)
def health() -> StockHealth:
    s = get_settings()
    cat, sch = s.catalog, s.schema_name
    row = fetch_one(
        f"""
        WITH latest AS (
          SELECT * FROM {cat}.{sch}.facts_sales_inventory_daily
          WHERE date = (SELECT MAX(date) FROM {cat}.{sch}.facts_sales_inventory_daily)
        )
        SELECT
          COUNT(*) AS total_skus,
          SUM(CASE WHEN on_hand_eod >= reorder_point THEN 1 ELSE 0 END) AS at_par,
          SUM(CASE WHEN on_hand_eod < reorder_point THEN 1 ELSE 0 END) AS below_par
        FROM latest
        """,
    ) or {}
    total = int(row.get("total_skus") or 0)
    at_par = int(row.get("at_par") or 0)
    return StockHealth(
        total_skus=total,
        at_par=at_par,
        below_par=int(row.get("below_par") or 0),
        pct_at_par=round(at_par / total * 100, 1) if total > 0 else 0.0,
    )


@router.get("/by-category", response_model=list[CategoryFill])
def by_category() -> list[CategoryFill]:
    s = get_settings()
    cat, sch = s.catalog, s.schema_name
    rows = fetch_all(
        f"""
        WITH latest AS (
          SELECT * FROM {cat}.{sch}.facts_sales_inventory_daily
          WHERE date = (SELECT MAX(date) FROM {cat}.{sch}.facts_sales_inventory_daily)
        )
        SELECT i.category,
               COUNT(*) AS sku_count,
               SUM(CASE WHEN l.on_hand_eod < l.reorder_point THEN 1 ELSE 0 END) AS below_par,
               SUM(CASE WHEN l.on_hand_eod >= l.reorder_point THEN 1 ELSE 0 END) AS at_par
        FROM latest l
        JOIN {cat}.{sch}.dims_items i USING (sku)
        GROUP BY i.category
        ORDER BY i.category
        """,
    )
    out = []
    for r in rows:
        total = int(r["sku_count"])
        at_par = int(r["at_par"] or 0)
        out.append(
            CategoryFill(
                category=r["category"],
                sku_count=total,
                below_par=int(r["below_par"] or 0),
                pct_at_par=round(at_par / total * 100, 1) if total > 0 else 0.0,
            )
        )
    return out


@router.get("/watched", response_model=list[WatchedItem])
def watched(limit: int = 6) -> list[WatchedItem]:
    s = get_settings()
    cat, sch = s.catalog, s.schema_name
    rows = fetch_all(
        f"""
        WITH latest AS (
          SELECT * FROM {cat}.{sch}.facts_sales_inventory_daily
          WHERE date = (SELECT MAX(date) FROM {cat}.{sch}.facts_sales_inventory_daily)
        ),
        usage AS (
          SELECT sku, store_id, AVG(units_sold) AS avg_daily_units
          FROM {cat}.{sch}.facts_sales_inventory_daily
          WHERE date >= date_sub((SELECT MAX(date) FROM {cat}.{sch}.facts_sales_inventory_daily), 7)
          GROUP BY sku, store_id
        ),
        po_vendor AS (
          SELECT sku, vendor_name, lead_time_days,
                 row_number() OVER (PARTITION BY sku ORDER BY created_at DESC) AS rn
          FROM {cat}.{sch}.facts_purchase_orders
        )
        SELECT l.sku, i.item_name, i.category,
               l.on_hand_eod, l.reorder_point,
               CASE WHEN u.avg_daily_units > 0 THEN ROUND(l.on_hand_eod / u.avg_daily_units, 1) END AS days_of_cover,
               pv.vendor_name, pv.lead_time_days
        FROM latest l
        JOIN {cat}.{sch}.dims_items i USING (sku)
        LEFT JOIN usage u ON u.sku = l.sku AND u.store_id = l.store_id
        LEFT JOIN po_vendor pv ON pv.sku = l.sku AND pv.rn = 1
        WHERE l.on_hand_eod < l.reorder_point
        ORDER BY days_of_cover ASC NULLS LAST
        LIMIT {limit}
        """,
    )
    return [WatchedItem(**r) for r in rows]
