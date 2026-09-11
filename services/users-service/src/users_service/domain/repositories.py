"""Puertos (interfaces) que el dominio necesita del mundo exterior.

El dominio DECLARA que necesita guardar y recuperar usuarios, pero no decide
con que tecnologia. La implementacion concreta vive en `infrastructure/` y se
inyecta en el arranque. Esto es la inversion de dependencias que sostiene toda
la arquitectura limpia.
"""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from .entities import User


class UserRepository(Protocol):
    async def add(self, user: User) -> None:
        """Persiste un usuario nuevo."""
        ...

    async def get(self, user_id: UUID) -> User | None:
        """Devuelve el usuario o `None` si no existe."""
        ...

    async def find_by_email(self, email: str) -> User | None:
        """Busca por correo, normalizado a minusculas."""
        ...

    async def list(self, limit: int, offset: int) -> list[User]:
        """Listado paginado, mas recientes primero."""
        ...
