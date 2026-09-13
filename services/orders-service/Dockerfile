FROM oven/bun:1-alpine AS base

WORKDIR /app

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY tsconfig.json ./
COPY src ./src

COPY openapi.yaml ./

FROM base AS dev
COPY tests ./tests
CMD ["bun", "test"]

FROM base AS runtime

USER bun

EXPOSE 8000
CMD ["bun", "run", "src/index.ts"]
