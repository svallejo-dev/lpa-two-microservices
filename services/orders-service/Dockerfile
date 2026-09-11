# ---------------------------------------------------------------------------
# Servicio de Pedidos - TypeScript sobre Bun
#
# Bun trae el cliente de PostgreSQL incorporado (`Bun.SQL`) y su propio
# ejecutor de pruebas, asi que el servicio corre con CERO dependencias de npm
# en produccion.
#
#   base    -> dependencias y codigo fuente
#   dev     -> base + pruebas (la usa `make test-orders`)
#   runtime -> imagen final
# ---------------------------------------------------------------------------
FROM oven/bun:1-alpine AS base

WORKDIR /app

# Se copian primero los manifiestos para aprovechar la cache de capas: solo se
# reinstala cuando cambian las dependencias, no cada vez que cambia el codigo.
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY tsconfig.json ./
COPY src ./src

# El contrato viaja DENTRO de la imagen: el servicio publica su propia
# especificacion en /openapi.yaml y /openapi.json.
COPY openapi.yaml ./

# --- Etapa de pruebas ------------------------------------------------------
FROM base AS dev
COPY tests ./tests
CMD ["bun", "test"]

# --- Etapa de ejecucion ----------------------------------------------------
FROM base AS runtime

# La imagen de Bun ya trae un usuario sin privilegios llamado `bun`.
USER bun

EXPOSE 8000
CMD ["bun", "run", "src/index.ts"]
