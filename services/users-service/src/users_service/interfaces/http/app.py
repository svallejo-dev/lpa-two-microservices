"""Ensamblado de la aplicacion FastAPI.

Orden de arranque: se abre el pool de Postgres, se construye el contenedor de
casos de uso con ese pool y se guarda en `app.state`. Los routers solo leen de
ahi, de modo que nunca instancian un adaptador por su cuenta.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from ...infrastructure.config import get_settings
from ...infrastructure.database import create_pool
from .container import build_container
from .error_handlers import register_error_handlers
from .routers import health, users

logger = logging.getLogger("users-service")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level.upper())

    pool = await create_pool(settings)
    app.state.pool = pool
    app.state.container = build_container(pool)
    logger.info("Servicio de Usuarios listo")
    try:
        yield
    finally:
        await pool.close()
        logger.info("Pool de Postgres cerrado")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Servicio de Usuarios",
        version="1.0.0",
        description=(
            "Microservicio propietario de los datos de usuarios. "
            "Taller de Lenguaje de Programacion Avanzado 2."
        ),
        lifespan=lifespan,
    )
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(users.router)
    return app


app = create_app()
