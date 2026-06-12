"""Operator Command Center reference app (facilitator copy).

Serves the Homebase prototype as a static FastAPI app. The prototype is
copied from `app/reference-prototype/` at deploy time so the bundle is
self-contained.

This is intentionally minimal. Attendees build their own App during the
workshop with FastAPI + AppKit components and wire to the workshop schema.
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

STATIC_DIR = Path(__file__).parent / "static"
DEFAULT_DOC = os.environ.get("DEFAULT_DOC", "Homebase.html")

app = FastAPI(title="Operator Command Center (reference)")


@app.get("/")
def root():
    return RedirectResponse(url=f"/{DEFAULT_DOC}")


@app.get("/healthz")
def healthz():
    return {"ok": True}


# Mount the prototype directory as static. `html=True` makes index.html
# resolve automatically; we redirect to Homebase.html explicitly above.
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
