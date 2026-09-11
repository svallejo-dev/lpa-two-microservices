"""Caso de uso: consultar un usuario por id.

Este es el caso de uso que el Servicio de Pedidos termina invocando a traves
de la red cada vez que alguien crea un pedido.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from ...domain.entities import User
from ...domain.errors import UserNotFoundError
from ...domain.repositories import UserRepository


@dataclass(frozen=True, slots=True)
class GetUser:
    users: UserRepository

    async def execute(self, user_id: UUID) -> User:
        user = await self.users.get(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user
