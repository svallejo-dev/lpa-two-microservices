"""Configuracion leida del entorno.

Toda la configuracion entra por variables de entorno (12-factor): la misma
imagen sirve para local, pruebas y produccion cambiando solo el entorno.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    database_url: str = "postgres://users_app:users_secret@localhost:5432/users_db"
    log_level: str = "info"

    db_pool_min_size: int = 1
    db_pool_max_size: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()
