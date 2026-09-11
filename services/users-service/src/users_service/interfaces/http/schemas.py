"""DTOs de la frontera HTTP.

Nota deliberada: `email` es un `str` y NO un `EmailStr` de Pydantic. La regla
"un correo debe tener formato valido" es una regla de NEGOCIO y vive en
`domain/entities.py`. Si la delegaramos al framework, cambiar de FastAPI a otro
servidor nos haria perder una invariante del dominio.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from ...domain.entities import User


class CreateUserRequest(BaseModel):
    name: str = Field(..., description="Nombre del usuario", examples=["Sebastian Vallejo"])
    email: str = Field(..., description="Correo unico", examples=["sebastian@example.com"])


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    created_at: datetime

    @classmethod
    def from_entity(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at,
        )


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Codigo estable, apto para programar contra el")
    message: str = Field(..., description="Mensaje legible para una persona")
