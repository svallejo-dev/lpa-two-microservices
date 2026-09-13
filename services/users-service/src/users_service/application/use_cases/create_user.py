"""Caso de uso: registrar un usuario."""

from __future__ import annotations

from dataclasses import dataclass

from ...domain.entities import User
from ...domain.errors import DuplicateEmailError
from ...domain.repositories import UserRepository
from ..dtos import CreateUserCommand


@dataclass(frozen=True, slots=True)
class CreateUser:
    users: UserRepository

    async def execute(self, command: CreateUserCommand) -> User:
        user = User.register(name=command.name, email=command.email)

        if await self.users.find_by_email(user.email) is not None:
            raise DuplicateEmailError(user.email)

        await self.users.add(user)
        return user
