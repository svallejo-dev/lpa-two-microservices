# Taller: Arquitectura orientada a microservicios

**Lenguaje de Programación Avanzado 2** · Monorepo con dos microservicios
políglotas que se comunican por una API REST.

| | Servicio de Usuarios | Servicio de Pedidos |
|---|---|---|
| **Stack** | Python 3.13 + FastAPI | TypeScript + Bun 1.4 |
| **Base de datos** | PostgreSQL 17 (privada) | PostgreSQL 17 (privada) |
| **Puerto** | `8001` | `8002` |
| **Rol** | Es dueño de los usuarios | Consume a Usuarios para validar los pedidos |

Los dos servicios **no comparten una sola línea de código**, ni base de datos,
ni lenguaje. Lo único que comparten es un contrato HTTP.

---

## Arranque rápido

Requisito único: **Docker Desktop** corriendo. No hace falta instalar Python,
Bun ni PostgreSQL: todo —incluidas las pruebas— se ejecuta en contenedores.

```bash
make doctor    # comprueba que Docker responde
make up        # levanta los 4 contenedores
make demo      # recorre el flujo completo y lo explica paso a paso
```

> **Si `make doctor` no encuentra Docker:** el binario de Docker Desktop vive en
> `/Applications/Docker.app/Contents/Resources/bin`. El `Makefile` ya lo
> resuelve por su cuenta; para usarlo también en la terminal, agregue esa ruta
> al `PATH` en su `~/.zshrc`.

Verifique que funciona:

```bash
curl localhost:8001/docs            # documentación interactiva de Usuarios
curl localhost:8002/health/ready    # estado de las dependencias de Pedidos
```

---

## Comandos

`make` sin argumentos muestra esta lista.

### Levantar y bajar

| Comando | Qué hace |
|---|---|
| `make up` | Levanta **ambos** microservicios con sus bases de datos |
| `make up-users` | Levanta **solo** Usuarios + su base |
| `make up-orders` | Levanta Pedidos (arrastra a Usuarios, del que depende) |
| `make up-orders-solo` | Levanta Pedidos **aislado**, sin Usuarios — para ver el `503` |
| `make down` | Baja todo, conservando los datos |
| `make clean` | Baja todo y **borra** los volúmenes de las bases |

### Demostrar

| Comando | Qué hace |
|---|---|
| `make demo` | Crea un usuario, crea un pedido, consulta, y muestra los errores `422` y `400` |
| `make demo-fallo` | Apaga Usuarios y muestra cómo Pedidos degrada a `503` y se recupera solo |

### Contrato de la API

| Comando | Qué hace |
|---|---|
| `make api-docs` | Abre la comparativa de renderizadores y lista las URLs del contrato |
| `make api-lint` | Valida `openapi.yaml` con Redocly CLI y las reglas de `redocly.yaml` |

### Verificar y observar

| Comando | Qué hace |
|---|---|
| `make test` | 37 pruebas de dominio, casos de uso y contrato, **sin base de datos ni red** |
| `make typecheck` | Verifica los tipos de TypeScript |
| `make ps` · `make logs` | Estado y registros |
| `make psql-users` · `make psql-orders` | Consola de PostgreSQL de cada servicio |

---

## Endpoints

### Usuarios — `http://localhost:8001` ([docs interactivas](http://localhost:8001/docs))

| Método | Ruta | Respuestas |
|---|---|---|
| `POST` | `/users` | `201` · `400` inválido · `409` correo duplicado |
| `GET` | `/users/{id}` | `200` · `404` — **el endpoint que consume Pedidos** |
| `GET` | `/users` | `200` |
| `GET` | `/health` · `/health/ready` | `200` · `503` |

### Pedidos — `http://localhost:8002`

| Método | Ruta | Respuestas |
|---|---|---|
| `POST` | `/orders` | `201` · `400` inválido · `422` usuario inexistente · `503` Usuarios caído |
| `GET` | `/orders/{id}` | `200` · `404` |
| `GET` | `/orders?user_id=` | `200` |
| `GET` | `/health` · `/health/ready` | `200` · `503` |

Peticiones listas para ejecutar desde VS Code o JetBrains:
[`docs/requests.http`](docs/requests.http).

---

## El contrato: API Design First

Los dos servicios publican su especificación OpenAPI, pero **por caminos
opuestos a propósito** — el repositorio demuestra los dos enfoques a la vez:

| | Usuarios | Pedidos |
|---|---|---|
| **Enfoque** | **Code first** | **Design first** |
| Fuente de verdad | el código Python | [`openapi.yaml`](services/orders-service/openapi.yaml), escrito a mano |
| El spec… | lo *genera* FastAPI | se *escribe primero*; el código lo cumple |
| Riesgo | no se puede diseñar antes de programar | que se pudra |
| Mitigación | — | [`tests/openapi.test.ts`](services/orders-service/tests/openapi.test.ts) falla si se desvía |

### Un contrato, cinco renderizadores

```bash
make api-docs      # abre http://localhost:8002/docs
```

Esa página deja saltar entre **Scalar, Redoc, RapiDoc, Stoplight Elements y
Swagger UI**. Los cinco leen el mismo `/openapi.json`: el contrato es el activo
y la presentación es intercambiable. Cambiar de renderizador no toca una línea
del servicio.

| Ruta | Qué es |
|---|---|
| `:8002/openapi.yaml` | La fuente de verdad, tal como se versiona en git |
| `:8002/openapi.json` | Lo mismo en JSON, que es lo que consumen las herramientas |
| `:8002/docs` | Comparativa de los cinco renderizadores |
| `:8001/docs` | Swagger UI de Usuarios, generado por FastAPI |

### El guardia contra la deriva

Un contrato escrito a mano envejece si nadie lo vigila, y una documentación que
miente es peor que no tenerla. Nueve pruebas comparan el YAML con el código:
cobertura de rutas en ambos sentidos, que el `enum` de errores cubra todas las
excepciones de dominio, y que `POST /orders` siga documentando `201/400/422/503`
con su `Retry-After`.

Está comprobado que **fallan de verdad**: al agregar una ruta sin documentarla,
la prueba la señala por nombre.

```
(fail) cada operacion del codigo esta documentada en openapi.yaml
+ [ "POST /orders/{id}/cancelar" ]
```

Más detalle, y el panorama de estándares alternativos (AsyncAPI, gRPC/Protobuf,
TypeSpec, Smithy, Pact): [`docs/04-api-design-first.md`](docs/04-api-design-first.md).

---

## Qué demuestra este proyecto

**1. Comunicación entre servicios.** Crear un pedido obliga a Pedidos a
preguntarle a Usuarios si el usuario existe, porque no tiene esa tabla:

```bash
curl -X POST localhost:8002/orders -H 'content-type: application/json' \
  -d '{"user_id":"<id>","items":[{"sku":"TECLADO","quantity":2,"unit_price":15000}]}'
# 201 {"total": 30000, ...}   <- el total lo calculó el dominio, no el cliente
```

**2. Una base de datos por servicio, impuesta por la red.** Las dos bases están
en redes de Docker separadas. `orders-service` **no tiene ruta** hacia
`users-db`: aunque tuviera las credenciales, el paquete no llegaría.

```bash
make psql-orders    # \dt  ->  orders, order_items.  Ninguna tabla users.
```

**3. Fallos parciales y degradación controlada.** `make demo-fallo` apaga
Usuarios y muestra el comportamiento completo:

| | Resultado |
|---|---|
| `POST /orders` | `503` + `Retry-After`, en ~4 s, **sin guardar nada** |
| `GET /orders` | `200` — las lecturas no dependen del otro servicio |
| `GET /health/ready` | `503 degraded`, indicando cuál dependencia falló |
| Al restaurar Usuarios | vuelve a `201` sin reiniciar nada |

La distinción clave: **`422`** significa "el usuario no existe" (respuesta
confirmada, corrija los datos); **`503`** significa "no pude preguntar"
(problema nuestro, reintente). Confundirlos haría que el sistema rechazara
pedidos válidos cada vez que la red falla.

**4. Arquitectura limpia, verificable.** `make test` ejecuta 37 pruebas
—incluida *"¿qué pasa si el otro microservicio se cae?"*— en milisegundos, sin
base de datos, sin red y sin Docker Compose. Eso solo es posible porque los
casos de uso dependen de interfaces y no de `asyncpg` ni de `fetch`.

---

## Estructura

```
.
├── Makefile                  # punto de entrada único
├── compose.yaml              # 4 contenedores, 3 redes, 2 volúmenes
├── docs/
│   ├── 01-cuadro-comparativo.md    # monolito vs. microservicios (10 criterios)
│   ├── 02-ensayo-microservicios.md # ensayo: por qué las grandes empresas los adoptan
│   ├── 03-arquitectura.md          # diagramas Mermaid + decisiones de diseño
│   ├── 04-api-design-first.md      # estándares y herramientas de contrato
│   └── requests.http               # peticiones de ejemplo
├── entrega/                  # PDF de entrega (make pdf)
├── scripts/                  # demo.sh y demo-fallo.sh
└── services/
    ├── users-service/        # Python + FastAPI  (spec generado)
    └── orders-service/       # TypeScript + Bun
        ├── openapi.yaml      # CONTRATO escrito a mano: la fuente de verdad
        └── redocly.yaml      # reglas de gobierno del contrato
```

Ambos servicios usan **el mismo layout de capas**, para que el contraste entre
ellos sea de stack y no de arquitectura:

```
src/<servicio>/
├── domain/           # entidades, invariantes y PUERTOS. Cero dependencias externas.
├── application/      # casos de uso. Orquestan el dominio a través de los puertos.
├── infrastructure/   # ADAPTADORES: Postgres, cliente HTTP, configuración.
└── interfaces/http/  # routers, DTOs y traducción de errores de dominio a HTTP.
```

**La regla de dependencias:** las flechas apuntan siempre hacia `domain/`.
`infrastructure/` depende del dominio; el dominio no depende de nadie.

---

## Entregables del taller

El documento final está en
**[`entrega/Taller-Microservicios-LPA2.pdf`](entrega/Taller-Microservicios-LPA2.pdf)**,
en formato **APA 7**, y se regenera con `make pdf`. El cuadro comparativo, el
ensayo, los diagramas, el fragmento de código y las salidas de ejecución se
toman del propio repositorio; antes de generar el PDF se verifica que tablas,
figuras, citas y referencias estén numeradas y correspondidas según APA.

| Actividad solicitada | Archivo |
|---|---|
| Cuadro comparativo (mín. 5 criterios) | [`docs/01-cuadro-comparativo.md`](docs/01-cuadro-comparativo.md) — 10 criterios |
| Ensayo breve (1 página) | [`docs/02-ensayo-microservicios.md`](docs/02-ensayo-microservicios.md) |
| Dos servicios sencillos | [`services/users-service`](services/users-service) · [`services/orders-service`](services/orders-service) |
| Comunicación vía API REST | `POST /orders` → `GET /users/{id}` · ver `make demo` |
| Diagrama de arquitectura | [`docs/03-arquitectura.md`](docs/03-arquitectura.md) — 3 diagramas Mermaid |
| *(complemento)* API Design First | [`docs/04-api-design-first.md`](docs/04-api-design-first.md) · contrato en [`openapi.yaml`](services/orders-service/openapi.yaml) |
