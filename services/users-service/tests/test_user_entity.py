"""Pruebas de las invariantes de la entidad User."""

from __future__ import annotations

import pytest

from users_service.domain.entities import MAX_NAME_LENGTH, User
from users_service.domain.errors import (
    EmptyNameError,
    InvalidEmailError,
    NameTooLongError,
)


def test_registra_un_usuario_valido() -> None:
    user = User.register(name="Sebastian Vallejo", email="Sebastian@Example.com")

    assert user.name == "Sebastian Vallejo"
    # El dominio normaliza el correo a minusculas: esa es la invariante en la
    # que confia el esquema de la base de datos.
    assert user.email == "sebastian@example.com"
    assert user.id is not None


def test_recorta_espacios_alrededor_del_nombre() -> None:
    assert User.register(name="  Ana  ", email="ana@example.com").name == "Ana"


def test_rechaza_nombre_vacio() -> None:
    with pytest.raises(EmptyNameError):
        User.register(name="   ", email="ana@example.com")


def test_rechaza_nombre_demasiado_largo() -> None:
    with pytest.raises(NameTooLongError):
        User.register(name="a" * (MAX_NAME_LENGTH + 1), email="ana@example.com")


@pytest.mark.parametrize(
    "email",
    ["sin-arroba", "sin@dominio", "@example.com", "ana@ejemplo", "con espacio@a.com"],
)
def test_rechaza_correos_invalidos(email: str) -> None:
    with pytest.raises(InvalidEmailError):
        User.register(name="Ana", email=email)


def test_el_usuario_es_inmutable() -> None:
    user = User.register(name="Ana", email="ana@example.com")
    with pytest.raises(Exception):
        user.name = "Otro"  # type: ignore[misc]
