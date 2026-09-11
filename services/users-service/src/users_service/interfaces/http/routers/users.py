"""Rutas HTTP de usuarios.

Los handlers son deliberadamente delgados: traducen JSON a un comando, invocan
el caso de uso y traducen la entidad de vuelta a JSON. Ninguna regla de negocio
vive aqui.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from ....application.dtos import CreateUserCommand
from ....application.use_cases.list_users import DEFAULT_LIMIT, MAX_LIMIT
from ..container import Container
from ..dependencies import get_container
from ..schemas import CreateUserRequest, ErrorResponse, UserResponse

router = APIRouter(prefix="/users", tags=["usuarios"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    summary="Registrar un usuario",
    responses={
        400: {"model": ErrorResponse, "description": "Datos invalidos"},
        409: {"model": ErrorResponse, "description": "El correo ya existe"},
    },
)
async def create_user(
    payload: CreateUserRequest,
    container: Container = Depends(get_container),
) -> UserResponse:
    user = await container.create_user.execute(
        CreateUserCommand(name=payload.name, email=payload.email)
    )
    return UserResponse.from_entity(user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Consultar un usuario",
    description=(
        "Endpoint consumido por el Servicio de Pedidos para validar que el "
        "usuario de un pedido existe."
    ),
    responses={404: {"model": ErrorResponse, "description": "No existe"}},
)
async def get_user(
    user_id: UUID,
    container: Container = Depends(get_container),
) -> UserResponse:
    user = await container.get_user.execute(user_id)
    return UserResponse.from_entity(user)


@router.get(
    "",
    response_model=list[UserResponse],
    summary="Listar usuarios",
)
async def list_users(
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    offset: int = Query(0, ge=0),
    container: Container = Depends(get_container),
) -> list[UserResponse]:
    users = await container.list_users.execute(limit=limit, offset=offset)
    return [UserResponse.from_entity(user) for user in users]
