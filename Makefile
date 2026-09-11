# ===========================================================================
#  Taller LPA2 - Arquitectura de microservicios
#  Punto de entrada unico del monorepo.  Ejecuta `make` para ver la ayuda.
# ===========================================================================
SHELL := /bin/bash

# Docker Desktop en macOS no siempre queda en el PATH de la shell. Se exporta
# para los scripts de scripts/, y ademas se resuelve el binario a ruta absoluta
# porque GNU Make 3.81 (el que trae macOS) ejecuta los comandos simples sin
# pasar por la shell, con una copia del PATH tomada al arrancar.
export PATH := $(PATH):/Applications/Docker.app/Contents/Resources/bin
DOCKER      := $(shell command -v docker 2>/dev/null || echo /Applications/Docker.app/Contents/Resources/bin/docker)

COMPOSE     := $(DOCKER) compose
USERS_URL   := http://localhost:8001
ORDERS_URL  := http://localhost:8002

.DEFAULT_GOAL := help
.PHONY: help doctor up up-users up-orders up-orders-solo down stop clean restart \
        build ps logs logs-users logs-orders test test-users test-orders typecheck \
        demo demo-fallo psql-users psql-orders urls setup-local api-lint api-docs pdf pdf-evidencia

# --- Ayuda -----------------------------------------------------------------
help: ## Muestra esta ayuda
	@echo ""
	@echo "  Taller LPA2 - Microservicios (Usuarios: FastAPI  |  Pedidos: Bun)"
	@echo ""
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'
	@echo ""

# --- Requisitos ------------------------------------------------------------
doctor: ## Verifica que Docker y Compose esten disponibles
	@echo "==> Comprobando entorno"
	@command -v docker >/dev/null 2>&1 || { \
	  echo "  [X] No se encontro 'docker' en el PATH."; \
	  echo "      Abre Docker Desktop y agrega a tu ~/.zshrc:"; \
	  echo "      export PATH=\"\$$PATH:/Applications/Docker.app/Contents/Resources/bin\""; \
	  exit 1; }
	@echo "  [OK] $$(docker --version)"
	@$(COMPOSE) version >/dev/null 2>&1 || { echo "  [X] 'docker compose' no disponible"; exit 1; }
	@echo "  [OK] $$($(COMPOSE) version)"
	@$(DOCKER) info >/dev/null 2>&1 || { echo "  [X] El daemon de Docker no responde. Abre Docker Desktop."; exit 1; }
	@echo "  [OK] daemon activo"

.env:
	@cp .env.example .env && echo "==> .env creado a partir de .env.example"

# --- Levantar --------------------------------------------------------------
up: .env doctor ## Levanta AMBOS microservicios con sus bases de datos
	@$(COMPOSE) up -d --build
	@$(MAKE) --no-print-directory urls

up-users: .env ## Levanta SOLO el Servicio de Usuarios (+ su base de datos)
	@$(COMPOSE) up -d --build users-service
	@echo "==> Usuarios en $(USERS_URL)  (docs: $(USERS_URL)/docs)"

up-orders: .env ## Levanta el Servicio de Pedidos (arrastra a Usuarios, del que depende)
	@$(COMPOSE) up -d --build orders-service
	@echo "==> Pedidos en $(ORDERS_URL)"

up-orders-solo: .env ## Levanta Pedidos AISLADO, sin Usuarios (para demostrar el 503)
	@$(COMPOSE) up -d orders-db
	@$(COMPOSE) up -d --build --no-deps orders-service
	@-$(COMPOSE) stop users-service 2>/dev/null
	@echo "==> Pedidos AISLADO en $(ORDERS_URL). Crear un pedido ahora devuelve 503."

build: .env ## Construye las imagenes sin levantar nada
	@$(COMPOSE) build

# --- Apagar ----------------------------------------------------------------
stop: ## Detiene los contenedores sin borrarlos
	@$(COMPOSE) stop

down: ## Baja todos los contenedores (conserva los datos)
	@$(COMPOSE) down

clean: ## Baja todo y BORRA los volumenes de las bases de datos
	@$(COMPOSE) down -v --remove-orphans
	@echo "==> Entorno limpio (volumenes eliminados)"

restart: down up ## Reinicia el entorno completo

# --- Observar --------------------------------------------------------------
ps: ## Estado de los contenedores
	@$(COMPOSE) ps

logs: ## Logs de todo (Ctrl-C para salir)
	@$(COMPOSE) logs -f

logs-users: ## Logs del Servicio de Usuarios
	@$(COMPOSE) logs -f users-service

logs-orders: ## Logs del Servicio de Pedidos
	@$(COMPOSE) logs -f orders-service

urls: ## Muestra las URLs publicadas
	@echo ""
	@echo "  Usuarios (FastAPI) : $(USERS_URL)      docs: $(USERS_URL)/docs"
	@echo "  Pedidos  (Bun)     : $(ORDERS_URL)"
	@echo ""

# --- Pruebas ---------------------------------------------------------------
test: test-users test-orders ## Ejecuta las pruebas de los dos servicios

test-users: ## Pruebas de dominio y casos de uso de Usuarios (sin BD ni red)
	@echo "==> Pruebas: Servicio de Usuarios"
	@$(DOCKER) build --quiet --target dev -t lpa-users-tests ./services/users-service >/dev/null
	@$(DOCKER) run --rm lpa-users-tests pytest -q

typecheck: ## Verifica los tipos de TypeScript del Servicio de Pedidos
	@$(DOCKER) run --rm -v "$$PWD/services/orders-service":/app -w /app oven/bun:1-alpine \
	  sh -c "bun install --silent >/dev/null 2>&1; bunx tsc --noEmit" && echo "  [OK] sin errores de tipos"

test-orders: ## Pruebas de dominio y casos de uso de Pedidos (sin BD ni red)
	@echo "==> Pruebas: Servicio de Pedidos"
	@$(DOCKER) build --quiet --target dev -t lpa-orders-tests ./services/orders-service >/dev/null
	@$(DOCKER) run --rm lpa-orders-tests bun test

# --- Contrato de la API (design first) -------------------------------------
api-lint: ## Valida el contrato openapi.yaml con Redocly CLI
	@echo "==> Validando el contrato del Servicio de Pedidos"
	@$(DOCKER) run --rm -v "$$PWD/services/orders-service":/spec -w /spec node:22-alpine \
	  npx --yes @redocly/cli@latest lint openapi.yaml 2>&1 | grep -vE "npm notice|^$$"

api-docs: ## Muestra donde consultar el contrato y abre la comparativa
	@echo ""
	@echo "  Contrato (escrito a mano, design first):"
	@echo "    $(ORDERS_URL)/openapi.yaml     fuente de verdad, versionada en git"
	@echo "    $(ORDERS_URL)/openapi.json     lo que consumen los renderizadores"
	@echo ""
	@echo "  Un mismo contrato, cinco renderizadores:"
	@echo "    $(ORDERS_URL)/docs             <- comparativa"
	@echo "    $(ORDERS_URL)/docs/scalar      $(ORDERS_URL)/docs/redoc"
	@echo "    $(ORDERS_URL)/docs/rapidoc     $(ORDERS_URL)/docs/elements"
	@echo "    $(ORDERS_URL)/docs/swagger"
	@echo ""
	@echo "  Servicio de Usuarios (generado por FastAPI, code first):"
	@echo "    $(USERS_URL)/docs              $(USERS_URL)/openapi.json"
	@echo ""
	@-open $(ORDERS_URL)/docs 2>/dev/null || true

# --- Entregable en PDF -----------------------------------------------------
pdf: ## Genera el PDF de entrega desde los documentos de docs/
	@echo "==> 1/3 Renderizando los diagramas Mermaid"
	@mkdir -p entrega/assets
	@python3 -c "import pathlib,re; t=pathlib.Path('docs/03-arquitectura.md').read_text(); \
	  [pathlib.Path(f'entrega/assets/d{i}.mmd').write_text(b) \
	   for i,b in enumerate(re.findall(r'\x60\x60\x60mermaid\n(.*?)\x60\x60\x60', t, re.S), 1)]"
	@for f in entrega/assets/d*.mmd; do \
	  $(DOCKER) run --rm -u 0 -v "$$PWD/entrega/assets":/data minlag/mermaid-cli \
	    -i /data/$$(basename $$f) -o /data/$$(basename $$f .mmd).png -w 1600 -s 2 -b white >/dev/null 2>&1; \
	done
	@echo "==> 2/3 Componiendo el HTML desde docs/"
	@$(DOCKER) run --rm -v "$$PWD":/w -w /w python:3.13-slim sh -c \
	  "pip install --quiet markdown 2>/dev/null && python3 scripts/build-pdf.py /w/entrega/assets /w/entrega/entrega.html"
	@echo "==> 3/3 Generando el PDF con WeasyPrint"
	@$(DOCKER) run --rm -v "$$PWD":/w -w /w ghcr.io/weasyprint/weasyprint \
	  /w/entrega/entrega.html /w/entrega/Taller-Microservicios-LPA2.pdf 2>/dev/null
	@echo "  [OK] entrega/Taller-Microservicios-LPA2.pdf"

pdf-evidencia: ## Recaptura las salidas reales que el PDF incluye como evidencia (requiere `make up`)
	@mkdir -p entrega/assets
	@$(COMPOSE) ps --format 'table {{.Service}}\t{{.Status}}'            > entrega/assets/ev-ps.txt
	@$(MAKE) --no-print-directory test 2>&1 \
	  | grep -E "==>|^\.+ *\[100%\]|^ [0-9]+ (pass|fail)"              > entrega/assets/ev-test.txt
	@./scripts/demo.sh 2>&1       | sed $$'s/\033\[[0-9;]*m//g'         > entrega/assets/ev-demo.txt
	@./scripts/demo-fallo.sh 2>&1 | sed $$'s/\033\[[0-9;]*m//g'         > entrega/assets/ev-fallo.txt
	@echo "  [OK] evidencia recapturada en entrega/assets/"

# --- Demostraciones --------------------------------------------------------
demo: ## Recorre el flujo completo: crea usuario, crea pedido, consulta
	@./scripts/demo.sh

demo-fallo: ## Apaga Usuarios y muestra como Pedidos degrada a 503
	@./scripts/demo-fallo.sh

# --- Bases de datos --------------------------------------------------------
psql-users: ## Abre psql contra la base de Usuarios
	@$(COMPOSE) exec users-db psql -U $${USERS_DB_USER:-users_app} -d $${USERS_DB_NAME:-users_db}

psql-orders: ## Abre psql contra la base de Pedidos
	@$(COMPOSE) exec orders-db psql -U $${ORDERS_DB_USER:-orders_app} -d $${ORDERS_DB_NAME:-orders_db}

# --- Opcional --------------------------------------------------------------
setup-local: ## (Opcional) Instala Bun y Python en el host para editar con autocompletado
	@command -v brew >/dev/null || { echo "Se requiere Homebrew"; exit 1; }
	@brew install oven-sh/bun/bun python@3.13
	@echo "==> Listo. No es necesario para ejecutar el proyecto: todo corre en Docker."
