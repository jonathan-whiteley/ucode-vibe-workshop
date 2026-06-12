// Live wiring banner: fetches /api/wiring on load and shows a small pill at
// the bottom-right with table counts + Genie space status. Confirms the
// published App is connected to the workshop tables, FMAPI endpoint, and
// Lakebase instance — not running on the mock data baked into the prototype.

(function () {
  function fmt(n) {
    if (n == null) return "0";
    if (n >= 1000000) return (n / 1000000).toFixed(1) + "M";
    if (n >= 1000) return (n / 1000).toFixed(1) + "k";
    return String(n);
  }

  function render(status) {
    var el = document.createElement("div");
    el.id = "wiring-banner";
    var connected = status && status.connected;
    var hasGenie = status && status.genie_space_id;
    var bg = connected ? "#0E538B" : "#BD2B26";
    el.style.cssText = [
      "position:fixed",
      "bottom:14px",
      "left:14px",
      "z-index:10000",
      "padding:10px 14px",
      "border-radius:8px",
      "background:" + bg,
      "color:#fff",
      "font-family:'DM Sans',ui-sans-serif,system-ui,sans-serif",
      "font-size:12px",
      "line-height:1.45",
      "box-shadow:0 4px 12px rgba(11,32,38,0.18)",
      "max-width:380px",
    ].join(";");

    if (!status) {
      el.textContent = "Wiring check failed: no response";
      document.body.appendChild(el);
      return;
    }

    if (!connected) {
      el.innerHTML =
        '<div style="font-weight:600;margin-bottom:4px">Wiring: disconnected</div>' +
        '<div style="opacity:0.85">' +
        (status.error || "no data in workshop tables") +
        "</div>";
      document.body.appendChild(el);
      return;
    }

    var tc = status.table_counts || {};
    var rowsTotal =
      (tc.facts_sales_daypart || 0) +
      (tc.facts_labor_daypart || 0) +
      (tc.facts_sales_inventory_daily || 0) +
      (tc.facts_purchase_orders || 0) +
      (tc.facts_customer_feedback || 0);

    var lines = [
      "<div style=\"font-weight:600;margin-bottom:4px\">Live: " +
        status.catalog +
        "." +
        status.schema_name +
        "</div>",
      "<div>" +
        fmt(tc.dims_stores) +
        " stores · " +
        fmt(tc.dims_items) +
        " items · " +
        fmt(tc.dims_employees) +
        " employees</div>",
      "<div>" +
        fmt(rowsTotal) +
        " fact rows · anchor " +
        (status.anchor_date || "?") +
        "</div>",
      "<div style=\"margin-top:4px;font-family:'DM Mono',ui-monospace,monospace;font-size:11px;opacity:0.85\">" +
        (hasGenie
          ? "Genie: " + status.genie_space_id.slice(0, 12) + "…"
          : "Genie: not yet wired") +
        "</div>",
    ];
    el.innerHTML = lines.join("");
    document.body.appendChild(el);
  }

  function load() {
    fetch("/api/wiring", { credentials: "include" })
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(render)
      .catch(function (err) {
        render({ connected: false, error: String(err) });
      });
  }

  if (document.readyState === "complete" || document.readyState === "interactive") {
    setTimeout(load, 0);
  } else {
    document.addEventListener("DOMContentLoaded", load);
  }
})();
