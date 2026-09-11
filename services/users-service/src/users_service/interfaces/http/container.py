"""Composition root.

El unico lugar del servicio donde se eligen implementaciones concretas. Aqui
se decide que `UserRepository` sea Postgres; cambiar esa linea es todo lo que
hace falta para cambiar de motor de persistencia.
"""

from __future__ import annotations

from dataclasses import dataclass

import asyncpg

from ...application.use_cases.create_user import CreateUser
from ...application.use_cases.get_user import GetUser
from ...application.use_cases.list_users import ListUsers
from ...infrastructure.postgres_user_repository import PostgresUserRepository


@dataclass(frozen=True, slots=True)
class Container:
    create_user: CreateUser
    get_user: GetUser
    list_users: ListUsers


def build_container(pool: asyncpg.Pool) -> Container:
    repository = PostgresUserRepository(pool)
    return Container(
        create_user=CreateUser(users=repository),
        get_user=GetUser(users=repository),
        list_users=ListUsers(users=repository),
    )
