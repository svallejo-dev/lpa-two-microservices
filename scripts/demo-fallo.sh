#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Demuestra la desventaja mas citada de los microservicios: un servicio depende
# de otro, y ese otro se puede caer.
#
# Lo que se quiere mostrar no es que falle, sino COMO falla: rapido, con un
# codigo de estado honesto y sin dejar datos inconsistentes.
# ---------------------------------------------------------------------------
set -euo pipefail

cd "$(dirname "$0")/.."
export PATH="$PATH:/Applications/Docker.app/Contents/Resources/bin"

USERS="${USERS_URL:-http://localhost:8001}"
ORDERS="${ORDERS_URL:-http://localhost:8002}"

bold() { printf '\n\033[1m%s\033[0m\n' "$1"; }
note() { printf '   \033[2m%s\033[0m\n' "$1"; }

bold "0. Preparacion: un usuario que SI existe"
EMAIL="fallo-$(date +%s)@example.com"
USER_ID=$(curl -s -X POST "$USERS/users" -H 'content-type: application/json' \
  -d "{\"name\":\"Usuario Valido\",\"email\":\"$EMAIL\"}" \
  | sed -n 's/.*"id":"\([^"]*\)".*/\1/p')
note "id: $USER_ID  (este usuario es real, el pedido deberia poder crearse)"

bold "1. Apagando el Servicio de Usuarios..."
docker compose stop users-service >/dev/null 2>&1
note "Servicio de Usuarios DETENIDO."

bold "2. Intentando crear un pedido de ese mismo usuario valido"
START=$(date +%s)
curl -s -i -X POST "$ORDERS/orders" -H 'content-type: application/json' \
  -d "{\"user_id\":\"$USER_ID\",\"items\":[{\"sku\":\"SSD\",\"quantity\":1,\"unit_price\":250000}]}" \
  | grep -iE '^(HTTP/|retry-after:|\{)' | sed 's/^/   /'
note "Tardo $(( $(date +%s) - START )) s: el timeout acota la espera en lugar de colgar la peticion."
note "503, no 400: el problema no son los datos del cliente. Y el pedido NO se guardo."

bold "3. Lo que SIGUE funcionando mientras Usuarios esta caido"
printf '   GET /orders  -> [HTTP %s]\n' "$(curl -s -o /dev/null -w '%{http_code}' "$ORDERS/orders")"
note "Las lecturas de pedidos no dependen de Usuarios: el fallo esta acotado, no tumba el servicio entero."

bold "4. Diagnostico automatico"
curl -s "$ORDERS/health/ready" | sed 's/^/   /'; echo
note "La sonda dice exactamente cual de las dos dependencias fallo."

bold "5. Restaurando el Servicio de Usuarios..."
docker compose start users-service >/dev/null 2>&1
for _ in $(seq 1 20); do
  [ "$(curl -s -o /dev/null -w '%{http_code}' "$USERS/health" || true)" = "200" ] && break
  sleep 1
done
note "Servicio de Usuarios ARRIBA."

bold "6. El mismo pedido, ahora sin cambiar nada en el cliente"
curl -s -w '\n   [HTTP %{http_code}]\n' -X POST "$ORDERS/orders" -H 'content-type: application/json' \
  -d "{\"user_id\":\"$USER_ID\",\"items\":[{\"sku\":\"SSD\",\"quantity\":1,\"unit_price\":250000}]}" \
  | sed 's/^/   /'
note "Recuperacion automatica: no hubo que reiniciar Pedidos ni limpiar datos a medias."
