"""Entidades del dominio de Usuarios."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from .errors import EmptyNameError, InvalidEmailError, NameTooLongError

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

MAX_NAME_LENGTH = 120


@dataclass(frozen=True, slots=True)
class User:
    """Un usuario registrado.

    Es inmutable y solo puede construirse por sus fabricas, de modo que un
    `User` que existe en memoria es, por definicion, un usuario valido.
    """

    id: UUID
    name: str
    email: str
    created_at: datetime

    @staticmethod
    def register(name: str, email: str) -> "User":
        """Crea un usuario nuevo aplicando las invariantes del negocio."""
        normalized_name = name.strip()
        if not normalized_name:
            raise EmptyNameError()
        if len(normalized_name) > MAX_NAME_LENGTH:
            raise NameTooLongError(MAX_NAME_LENGTH)

        normalized_email = email.strip().lower()
        if not _EMAIL_PATTERN.match(normalized_email):
            raise InvalidEmailError(email)

        return User(
            id=uuid4(),
            name=normalized_name,
            email=normalized_email,
            created_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def rehydrate(id: UUID, name: str, email: str, created_at: datetime) -> "User":
        """Reconstruye un usuario ya persistido.

        No revalida: lo que esta en la base de datos ya paso por `register`.
        La usa exclusivamente la capa de infraestructura.
        """
        return User(id=id, name=name, email=email, created_at=created_at)
