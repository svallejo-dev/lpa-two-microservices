#!/bin/sh
set -e
PDF="${1:-/in/Taller-Microservicios-LPA2.pdf}"
apk add --no-cache poppler-utils >/dev/null 2>&1
echo "  Paginas: $(pdfinfo "$PDF" | awk '/^Pages:/{print $2}')"
pdfinfo -f 1 -l 9999 "$PDF" | awk '/^Page +[0-9]+ +size:/{print $4" x "$6}' | sort | uniq -c \
  | awk '{printf "  Tamano: %s x %s pt (%s pag.)\n", $2, $4, $1}'
pdffonts "$PDF" | awk 'NR>2 {sub(/^[A-Z][A-Z][A-Z][A-Z][A-Z][A-Z]\+/, "", $1); print $1}' \
  | sort -u | sed 's/^/  Fuente: /'
