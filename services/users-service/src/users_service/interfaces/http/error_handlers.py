"""Traduccion de errores de dominio a codigos HTTP.

Esta tabla es la unica frontera donde el negocio se encuentra con el protocolo.
El dominio lanza `DuplicateEmailError`; que eso sea un 409 es una decision de
esta capa, no del negocio.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ...domain.errors import (
    DomainError,
    DuplicateEmailError,
    EmptyNameError,
    InvalidEmailError,
    NameTooLongError,
    UserNotFoundError,
)

_STATUS_BY_ERROR: dict[type[DomainError], tuple[int, str]] = {
    EmptyNameError: (400, "empty_name"),
    NameTooLongError: (400, "name_too_long"),
    InvalidEmailError: (400, "invalid_email"),
    DuplicateEmailError: (409, "duplicate_email"),
    UserNotFoundError: (404, "user_not_found"),
}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(_: Request, error: DomainError) -> JSONResponse:
        status, code = _STATUS_BY_ERROR.get(type(error), (400, "domain_error"))
        return JSONResponse(
            status_code=status,
            content={"error": code, "message": str(error)},
        )
