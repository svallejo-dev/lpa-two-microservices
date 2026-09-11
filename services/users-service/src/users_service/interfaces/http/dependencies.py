"""Acceso al contenedor desde los routers."""

from __future__ import annotations

from fastapi import Request

from .container import Container


def get_container(request: Request) -> Container:
    return request.app.state.container
