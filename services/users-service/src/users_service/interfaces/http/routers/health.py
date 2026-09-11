"""Sondas de salud.

Se distinguen dos preguntas distintas, que en microservicios NO son la misma:
  - /health       -> "el proceso esta vivo" (liveness)
  - /health/ready -> "puede atender trafico ahora" (readiness: incluye la BD)
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ....infrastructure.database import ping

router = APIRouter(tags=["salud"])

SERVICE_NAME = "users-service"


@router.get("/health", summary="Liveness")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}


@router.get("/health/ready", summary="Readiness")
async def ready(request: Request) -> JSONResponse:
    database_ok = await ping(request.app.state.pool)
    payload = {
        "status": "ready" if database_ok else "degraded",
        "service": SERVICE_NAME,
        "dependencies": {"database": "ok" if database_ok else "unreachable"},
    }
    return JSONResponse(status_code=200 if database_ok else 503, content=payload)
