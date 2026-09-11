"""Objetos de entrada de los casos de uso.

Son tipos planos: ni Pydantic ni nada del framework HTTP. Asi los casos de uso
pueden invocarse desde una prueba, una CLI o una cola de mensajes sin arrastrar
FastAPI.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CreateUserCommand:
    name: str
    email: str
