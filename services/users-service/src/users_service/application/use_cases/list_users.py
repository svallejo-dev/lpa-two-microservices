"""Caso de uso: listar usuarios."""

from __future__ import annotations

from dataclasses import dataclass

from ...domain.entities import User
from ...domain.repositories import UserRepository

DEFAULT_LIMIT = 20
MAX_LIMIT = 100


@dataclass(frozen=True, slots=True)
class ListUsers:
    users: UserRepository

    async def execute(self, limit: int = DEFAULT_LIMIT, offset: int = 0) -> list[User]:
        safe_limit = max(1, min(limit, MAX_LIMIT))
        safe_offset = max(0, offset)
        return await self.users.list(limit=safe_limit, offset=safe_offset)
