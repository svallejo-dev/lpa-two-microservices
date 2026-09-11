"""Pruebas del caso de uso CreateUser, con repositorio en memoria."""

from __future__ import annotations

import pytest

from users_service.application.dtos import CreateUserCommand
from users_service.application.use_cases.create_user import CreateUser
from users_service.domain.errors import DuplicateEmailError, InvalidEmailError

from .in_memory_user_repository import InMemoryUserRepository


async def test_crea_y_persiste_el_usuario() -> None:
    repository = InMemoryUserRepository()
    use_case = CreateUser(users=repository)

    user = await use_case.execute(CreateUserCommand(name="Ana", email="ana@example.com"))

    assert await repository.get(user.id) == user


async def test_rechaza_un_correo_repetido() -> None:
    repository = InMemoryUserRepository()
    use_case = CreateUser(users=repository)
    await use_case.execute(CreateUserCommand(name="Ana", email="ana@example.com"))

    with pytest.raises(DuplicateEmailError):
        await use_case.execute(CreateUserCommand(name="Otra Ana", email="ana@example.com"))


async def test_la_unicidad_ignora_mayusculas() -> None:
    repository = InMemoryUserRepository()
    use_case = CreateUser(users=repository)
    await use_case.execute(CreateUserCommand(name="Ana", email="ana@example.com"))

    with pytest.raises(DuplicateEmailError):
        await use_case.execute(CreateUserCommand(name="Ana", email="ANA@EXAMPLE.COM"))


async def test_no_persiste_nada_si_el_correo_es_invalido() -> None:
    repository = InMemoryUserRepository()
    use_case = CreateUser(users=repository)

    with pytest.raises(InvalidEmailError):
        await use_case.execute(CreateUserCommand(name="Ana", email="roto"))

    assert await repository.list(limit=10, offset=0) == []
