"""Errores de negocio del Servicio de Usuarios.

Capa de DOMINIO: estas excepciones no saben que existe HTTP ni SQL.
Traducirlas a codigos de estado es responsabilidad de `interfaces/http`.
"""


class DomainError(Exception):
    """Raiz de todos los errores de negocio."""


class EmptyNameError(DomainError):
    def __init__(self) -> None:
        super().__init__("El nombre del usuario no puede estar vacio.")


class NameTooLongError(DomainError):
    def __init__(self, max_length: int) -> None:
        super().__init__(f"El nombre del usuario supera los {max_length} caracteres.")
        self.max_length = max_length


class InvalidEmailError(DomainError):
    def __init__(self, email: str) -> None:
        super().__init__(f"El correo '{email}' no tiene un formato valido.")
        self.email = email


class DuplicateEmailError(DomainError):
    def __init__(self, email: str) -> None:
        super().__init__(f"Ya existe un usuario registrado con el correo '{email}'.")
        self.email = email


class UserNotFoundError(DomainError):
    def __init__(self, user_id: object) -> None:
        super().__init__(f"No existe un usuario con id '{user_id}'.")
        self.user_id = user_id
