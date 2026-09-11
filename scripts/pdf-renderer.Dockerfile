# ---------------------------------------------------------------------------
# Renderizador del PDF de entrega.
#
# La imagen oficial de WeasyPrint solo trae las fuentes DejaVu, y las normas
# APA piden Times New Roman. Liberation Serif es libre y METRICAMENTE IDENTICA
# a Times New Roman (mismos anchos de caracter), por lo que es el sustituto
# estandar donde no estan las fuentes de Microsoft: el documento sale con la
# misma medida de linea y el mismo aspecto.
#
# Las fuentes se toman de una etapa con Debian vigente y se copian: la imagen
# de WeasyPrint esta sobre Debian 11, cuyos repositorios ya caducaron y hacen
# fallar a `apt-get update`. Los archivos de fuente son datos, independientes
# de la arquitectura, asi que copiarlos entre etapas es seguro.
# ---------------------------------------------------------------------------
FROM debian:bookworm-slim AS fuentes

RUN apt-get update \
 && apt-get install -y --no-install-recommends fonts-liberation \
 && rm -rf /var/lib/apt/lists/*

FROM ghcr.io/weasyprint/weasyprint:latest

COPY --from=fuentes /usr/share/fonts/truetype/liberation /usr/share/fonts/truetype/liberation
RUN fc-cache -f
