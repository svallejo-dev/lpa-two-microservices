"""Caso de uso: registrar un usuario."""

from __future__ import annotations

from dataclasses import dataclass

from ...domain.entities import User
from ...domain.errors import DuplicateEmailError
from ...domain.repositories import UserRepository
from ..dtos import CreateUserCommand


@dataclass(frozen=True, slots=True)
class CreateUser:
    # Depende del PUERTO, nunca del adaptador de Postgres.
    users: UserRepository

    async def execute(self, command: CreateUserCommand) -> User:
        # 1. El dominio valida el formato y construye la entidad.
        user = User.register(name=command.name, email=command.email)

        # 2. La unicidad del correo es una regla que necesita consultar el
        #    repositorio, por eso vive aqui y no dentro de la entidad.
        if await self.users.find_by_email(user.email) is not None:
            raise DuplicateEmailError(user.email)

        await self.users.add(user)
        return user
