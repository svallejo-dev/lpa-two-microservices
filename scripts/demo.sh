#!/usr/bin/env bash
set -euo pipefail

USERS="${USERS_URL:-http://localhost:8001}"
ORDERS="${ORDERS_URL:-http://localhost:8002}"

bold() { printf '\n\033[1m%s\033[0m\n' "$1"; }
note() { printf '   \033[2m%s\033[0m\n' "$1"; }

call() {
  local method="$1" url="$2" body="${3:-}"
  printf '   \033[36m%s %s\033[0m\n' "$method" "$url"
  if [ -n "$body" ]; then
    curl -s -w '\n   [HTTP %{http_code}]\n' -X "$method" "$url" \
      -H 'content-type: application/json' -d "$body" | sed 's/^/   /'
  else
    curl -s -w '\n   [HTTP %{http_code}]\n' -X "$method" "$url" | sed 's/^/   /'
  fi
}

bold "0. Estado de las dos dependencias del Servicio de Pedidos"
call GET "$ORDERS/health/ready"

bold "1. Crear un usuario en el Servicio de Usuarios (Python + FastAPI)"
EMAIL="demo-$(date +%s)@example.com"
USER_JSON=$(curl -s -X POST "$USERS/users" -H 'content-type: application/json' \
  -d "{\"name\":\"Estudiante LPA2\",\"email\":\"$EMAIL\"}")
echo "$USER_JSON" | sed 's/^/   /'
USER_ID=$(echo "$USER_JSON" | sed -n 's/.*"id":"\([^"]*\)".*/\1/p')
note "id del usuario: $USER_ID"

bold "2. Crear un pedido en el Servicio de Pedidos (TypeScript + Bun)"
note "Pedidos NO tiene la tabla de usuarios: consulta a Usuarios por HTTP antes de insertar."
call POST "$ORDERS/orders" \
  "{\"user_id\":\"$USER_ID\",\"items\":[{\"sku\":\"TECLADO\",\"quantity\":2,\"unit_price\":15000},{\"sku\":\"MOUSE\",\"quantity\":3,\"unit_price\":8000}]}"
note "El total (54000) lo calculo el dominio; el cliente nunca lo envio."

bold "3. Consultar los pedidos de ese usuario"
call GET "$ORDERS/orders?user_id=$USER_ID"

bold "4. Intentar un pedido para un usuario que no existe"
note "Usuarios responde 404 -> Pedidos lo traduce a 422: los datos del cliente estan mal."
call POST "$ORDERS/orders" \
  '{"user_id":"00000000-0000-0000-0000-000000000000","items":[{"sku":"SSD","quantity":1,"unit_price":250000}]}'

bold "5. Intentar un pedido invalido (sin lineas)"
note "Se rechaza en el dominio, sin gastar una llamada de red al otro servicio."
call POST "$ORDERS/orders" "{\"user_id\":\"$USER_ID\",\"items\":[]}"

bold "Listo."
note "Para ver que ocurre cuando el Servicio de Usuarios se cae:  make demo-fallo"
