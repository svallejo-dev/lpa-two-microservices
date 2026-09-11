"""Adaptador de `UserRepository` sobre PostgreSQL.

Este es el UNICO archivo del servicio que sabe SQL. Si mañana la persistencia
cambiara a Mongo o a un archivo, solo se reemplaza esta clase: el dominio y los
casos de uso no se enteran.
"""

from __future__ import annotations

from uuid import UUID

import asyncpg

from ..domain.entities import User

_COLUMNS = "id, name, email, created_at"


def _to_entity(row: asyncpg.Record) -> User:
    return User.rehydrate(
        id=row["id"],
        name=row["name"],
        email=row["email"],
        created_at=row["created_at"],
    )


class PostgresUserRepository:
    """Implementa el puerto `domain.repositories.UserRepository`."""

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def add(self, user: User) -> None:
        await self._pool.execute(
            "INSERT INTO users (id, name, email, created_at) VALUES ($1, $2, $3, $4)",
            user.id,
            user.name,
            user.email,
            user.created_at,
        )

    async def get(self, user_id: UUID) -> User | None:
        row = await self._pool.fetchrow(
            f"SELECT {_COLUMNS} FROM users WHERE id = $1", user_id
        )
        return _to_entity(row) if row else None

    async def find_by_email(self, email: str) -> User | None:
        row = await self._pool.fetchrow(
            f"SELECT {_COLUMNS} FROM users WHERE email = $1", email
        )
        return _to_entity(row) if row else None

    async def list(self, limit: int, offset: int) -> list[User]:
        rows = await self._pool.fetch(
            f"SELECT {_COLUMNS} FROM users ORDER BY created_at DESC LIMIT $1 OFFSET $2",
            limit,
            offset,
        )
        return [_to_entity(row) for row in rows]
