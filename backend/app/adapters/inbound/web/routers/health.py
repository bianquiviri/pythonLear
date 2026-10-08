"""Health / readiness endpoints for observability."""

from __future__ import annotations

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.adapters.out.db.session import get_engine

router = APIRouter(tags=["ops"])


@router.get("/health", summary="Liveness probe — is the process up?")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready", summary="Readiness probe — is the DB reachable?")
async def ready(response: Response) -> dict[str, str]:
    try:
        async with get_engine().connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unavailable", "database": "down"}
    return {"status": "ready", "database": "ok"}
