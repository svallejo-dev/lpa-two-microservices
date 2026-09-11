"""Conexion a Postgres.

`asyncpg` no acepta el esquema 'postgresql+driver://' ni parametros de
SQLAlchemy: normalizamos la URL antes de usarla.
"""

from __future__ import annotations

import asyncpg

from .config import Settings


def _normalize_dsn(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


async def create_pool(settings: Settings) -> asyncpg.Pool:
    return await asyncpg.create_pool(
        dsn=_normalize_dsn(settings.database_url),
        min_size=settings.db_pool_min_size,
        max_size=settings.db_pool_max_size,
        command_timeout=10,
    )


async def ping(pool: asyncpg.Pool) -> bool:
    """Comprobacion de disponibilidad usada por /health/ready."""
    try:
        async with pool.acquire() as connection:
            await connection.execute("SELECT 1")
        return True
    except Exception:
        return False
