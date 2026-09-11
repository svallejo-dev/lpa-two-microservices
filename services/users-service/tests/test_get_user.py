"""Pruebas del caso de uso GetUser (el que consume el Servicio de Pedidos)."""

from __future__ import annotations

from uuid import uuid4

import pytest

from users_service.application.dtos import CreateUserCommand
from users_service.application.use_cases.create_user import CreateUser
from users_service.application.use_cases.get_user import GetUser
from users_service.domain.errors import UserNotFoundError

from .in_memory_user_repository import InMemoryUserRepository


async def test_devuelve_el_usuario_existente() -> None:
    repository = InMemoryUserRepository()
    created = await CreateUser(users=repository).execute(
        CreateUserCommand(name="Ana", email="ana@example.com")
    )

    assert await GetUser(users=repository).execute(created.id) == created


async def test_falla_si_el_usuario_no_existe() -> None:
    with pytest.raises(UserNotFoundError):
        await GetUser(users=InMemoryUserRepository()).execute(uuid4())
