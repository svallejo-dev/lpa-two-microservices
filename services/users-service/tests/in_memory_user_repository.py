"""Doble de prueba del puerto `UserRepository`.

Que este archivo pueda existir es la demostracion practica de la arquitectura
limpia: los casos de uso se prueban completos, con su logica real, sin levantar
Postgres ni Docker. Si `CreateUser` importara asyncpg, esto seria imposible.
"""

from __future__ import annotations

from uuid import UUID

from users_service.domain.entities import User


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}

    async def add(self, user: User) -> None:
        self._users[user.id] = user

    async def get(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)

    async def find_by_email(self, email: str) -> User | None:
        return next(
            (u for u in self._users.values() if u.email == email.strip().lower()),
            None,
        )

    async def list(self, limit: int, offset: int) -> list[User]:
        ordered = sorted(self._users.values(), key=lambda u: u.created_at, reverse=True)
        return ordered[offset : offset + limit]
