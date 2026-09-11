# ---------------------------------------------------------------------------
# Servicio de Usuarios - Python + FastAPI
#
# Tres etapas:
#   base    -> dependencias de ejecucion y codigo fuente
#   dev     -> base + dependencias de prueba (la usa `make test-users`)
#   runtime -> imagen final, sin pytest ni pruebas dentro
# ---------------------------------------------------------------------------
FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml ./
COPY src ./src

# --- Etapa de pruebas ------------------------------------------------------
FROM base AS dev
COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY tests ./tests
CMD ["pytest"]

# --- Etapa de ejecucion ----------------------------------------------------
FROM base AS runtime

# No ejecutar como root.
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "users_service.interfaces.http.app:app", "--host", "0.0.0.0", "--port", "8000"]
