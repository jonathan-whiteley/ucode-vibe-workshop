"""/api/genie — discover the reference Genie space by title.

If GENIE_SPACE_ID is set in the env, return it directly. Otherwise hit the
Databricks Genie REST API and search for a space whose title matches the
configured GENIE_TITLE (defaults to "Command Center reference"). Cached
in-process after the first successful lookup.
"""
from __future__ import annotations

import os
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from lib.config import get_settings
from lib.deps import workspace_client

router = APIRouter(prefix="/api/genie", tags=["genie"])


class GenieInfo(BaseModel):
    space_id: str
    title: str
    discovered: bool
    error: str | None = None


_cache: Optional[GenieInfo] = None


def _discover() -> GenieInfo:
    s = get_settings()
    title = os.getenv("GENIE_TITLE", "Command Center reference")
    if s.genie_space_id:
        return GenieInfo(space_id=s.genie_space_id, title=title, discovered=False)
    try:
        w = workspace_client()
        resp = w.api_client.do("GET", "/api/2.0/genie/spaces")
        for sp in (resp or {}).get("spaces", []):
            if sp.get("title") == title:
                return GenieInfo(space_id=sp.get("space_id", ""), title=title, discovered=True)
        return GenieInfo(space_id="", title=title, discovered=False, error="no matching space")
    except Exception as e:
        return GenieInfo(space_id="", title=title, discovered=False, error=f"{type(e).__name__}: {str(e)[:200]}")


@router.get("", response_model=GenieInfo)
def info() -> GenieInfo:
    global _cache
    if _cache and _cache.space_id:
        return _cache
    _cache = _discover()
    return _cache
