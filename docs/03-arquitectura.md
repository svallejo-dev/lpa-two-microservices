# Diseño de la arquitectura

**Asignatura:** Lenguaje de Programación Avanzado 2
**Actividad:** Actividad práctica — documentar el diseño mediante un diagrama

Los diagramas están escritos en Mermaid dentro del Markdown: se versionan junto
al código y GitHub los renderiza sin necesidad de adjuntar imágenes.

---

## 1. Diagrama de contenedores

Lo que realmente se ejecuta al lanzar `make up`: cinco contenedores repartidos
en tres redes.

```mermaid
graph TB
    Cliente["Cliente<br/>(curl / navegador / .http)"]

    subgraph services["red: services &nbsp;— &nbsp;único canal entre microservicios"]
        US["<b>users-service</b><br/>Python 3.13 + FastAPI<br/>host :8001 → :8000"]
        OS["<b>orders-service</b><br/>TypeScript + Bun 1.4<br/>host :8002 → :8000"]
    end

    subgraph usersdata["red: users-data (internal)"]
        UDB[("users-db<br/>PostgreSQL 17<br/>tabla: users")]
    end

    subgraph ordersdata["red: orders-data (internal)"]
        ODB[("orders-db<br/>PostgreSQL 17<br/>tablas: orders, order_items")]
    end

    Cliente -->|"HTTP :8001"| US
    Cliente -->|"HTTP :8002"| OS
    OS -->|"GET /users/{id}<br/><b>única dependencia</b>"| US
    US --> UDB
    OS --> ODB

    OS -.-x|"sin ruta de red"| UDB

    linkStyle 2 stroke:#c0392b,stroke-width:3px
    linkStyle 5 stroke:#c0392b,stroke-dasharray:4 4
```

La flecha punteada roja es el punto central del ejercicio: **no existe** y no
puede existir. `orders-service` no está conectado a la red `users-data`, así que
aunque alguien escribiera la cadena de conexión correcta, el paquete no
llegaría. La frontera entre microservicios es física, no una convención de
equipo.

Se puede comprobar con el sistema levantado:

```bash
docker compose exec orders-service sh -c \
  'bun --eval "const s=new Bun.SQL({url:\"postgres://users_app:users_secret@users-db:5432/users_db\"});
   try{await s\`SELECT 1 FROM users\`}catch(e){console.log(\"BLOQUEADO:\",e.message)}"'
# BLOQUEADO: Failed to connect
```

---

## 2. Diagrama de secuencia: `POST /orders`

El recorrido completo de la única operación donde un servicio necesita algo que
el otro posee. Incluye las tres ramas posibles.

```mermaid
sequenceDiagram
    autonumber
    actor C as Cliente
    participant OS as orders-service<br/>(Bun)
    participant CO as CreateOrder<br/>(caso de uso)
    participant UD as HttpUserDirectory<br/>(adaptador)
    participant US as users-service<br/>(FastAPI)
    participant ODB as orders-db

    C->>OS: POST /orders {user_id, items}
    OS->>CO: execute(comando)

    Note over CO: 1· Validación LOCAL primero:<br/>items no vacíos, cantidades y<br/>precios enteros, user_id es UUID.<br/>Si falla → 400 sin tocar la red.

    CO->>UD: findById(userId)
    UD->>US: GET /users/{id}<br/>timeout 2000 ms

    alt El usuario existe (200)
        US-->>UD: 200 {id, name, email}
        UD-->>CO: KnownUser
        Note over CO: 2· El dominio calcula el total.<br/>El cliente nunca lo envía.
        CO->>ODB: INSERT orders + order_items<br/>(una transacción)
        ODB-->>CO: ok
        CO-->>OS: Order
        OS-->>C: 201 Created + Location
    else El usuario NO existe (404)
        US-->>UD: 404
        UD-->>CO: null
        CO--xOS: UnknownUserError
        OS-->>C: 422 unknown_user
        Note over C,OS: Respuesta confirmada del negocio:<br/>el cliente debe corregir los datos.
    else No hay respuesta (timeout / 5xx / caído)
        US--xUD: ✗
        Note over UD: 1 reintento con espera corta,<br/>luego se rinde.
        UD--xCO: UserDirectoryUnavailableError
        CO--xOS: (nada se persiste)
        OS-->>C: 503 + Retry-After: 5
        Note over C,OS: Fallo de infraestructura:<br/>los datos del cliente estaban bien.
    end
```

### Por qué 422 y 503 no pueden ser el mismo error

Es la decisión de diseño más importante del servicio y está codificada en dos
excepciones distintas (`services/orders-service/src/domain/errors.ts`):

| Situación | Lo que sabemos | Error de dominio | HTTP | Qué debe hacer el cliente |
|---|---|---|---|---|
| Usuarios responde 404 | El usuario **no existe** | `UnknownUserError` | `422` | Corregir el `user_id` |
| Usuarios no responde | **No sabemos** si existe | `UserDirectoryUnavailableError` | `503` | Reintentar más tarde |

Colapsar ambos casos en un 400 haría que el sistema rechazara pedidos de
usuarios perfectamente válidos cada vez que la red tuviera un problema, y
culpara al cliente de un fallo propio.

---

## 3. Arquitectura limpia: la regla de dependencias

Ambos servicios tienen **exactamente el mismo diagrama de capas**, aunque uno
esté en Python y el otro en TypeScript. El contraste entre ellos es de stack,
no de arquitectura.

```mermaid
graph TB
    HTTP["HTTP / JSON<br/>(cliente)"]
    I["<b>interfaces/</b><br/>routers, DTOs, mapeo de errores"]
    A["<b>application/</b><br/>casos de uso"]
    D["<b>domain/</b><br/>entidades, invariantes, <i>puertos</i><br/>— no importa ninguna otra capa —"]
    F["<b>infrastructure/</b><br/>adaptadores concretos"]
    PG[("PostgreSQL")]
    REST["Otro microservicio<br/>(REST)"]

    HTTP --> I
    I --> A
    A --> D
    F -.->|"implementa los puertos<br/>(inversión de dependencias)"| D
    F --> PG
    F --> REST

    style D fill:#1b4332,color:#fff
    style A fill:#2d6a4f,color:#fff
    style I fill:#40916c,color:#fff
    style F fill:#74c69d
    linkStyle 3 stroke:#c0392b,stroke-width:2px
```

**La regla:** las flechas apuntan siempre hacia adentro. `domain/` no importa
nada de las otras capas; `infrastructure/` depende de `domain/` y nunca al
revés. Por eso `F` apunta hacia `D`, aunque el flujo de datos en tiempo de
ejecución vaya en sentido contrario: eso es la **inversión de dependencias**.

**Cómo se comprueba que la regla se cumple.** No hace falta creer en el
diagrama: si el dominio dependiera de Postgres o de `fetch`, sería imposible
ejecutar sus pruebas sin levantar infraestructura. `make test` corre 37 pruebas
—incluida "¿qué pasa si el otro servicio se cae?"— en milisegundos, sin base de
datos, sin red y sin Docker Compose.

```bash
$ make test
==> Pruebas: Servicio de Usuarios
................                                          [100%]   16 passed
==> Pruebas: Servicio de Pedidos
 21 pass · 0 fail · Ran 21 tests across 3 files. [13.00ms]
```

### Puertos y adaptadores

Un **puerto** es una interfaz declarada por el dominio; un **adaptador** es su
implementación concreta, elegida en el arranque. La última fila es la que hace
posible probar el fallo del otro servicio sin apagar nada.

| Servicio | Puerto (en `domain/`) | Adaptador de producción | Adaptador en pruebas |
|---|---|---|---|
| Usuarios | `UserRepository` | `PostgresUserRepository` | `InMemoryUserRepository` |
| Pedidos | `OrderRepository` | `PostgresOrderRepository` | `InMemoryOrderRepository` |
| Pedidos | `UserDirectory` | `HttpUserDirectory` → REST | `FakeUserDirectory`, `EmptyUserDirectory`, `BrokenUserDirectory` |

El *composition root* —el único punto donde se decide qué adaptador se usa— es
`interfaces/http/container.py` en Usuarios y `interfaces/http/container.ts` en
Pedidos. Cambiar de motor de persistencia es editar una línea en ese archivo.

---

## 4. Decisiones de diseño y sus motivos

| Decisión | Motivo |
|---|---|
| **Una base de datos por servicio** | Es lo que convierte a esto en microservicios y no en dos procesos sobre una base compartida. Si compartieran tablas, un cambio de esquema obligaría a desplegar los dos a la vez. |
| **Sin FOREIGN KEY en `orders.user_id`** | No puede haberla: la tabla `users` está en otro motor. La integridad se sostiene por protocolo, llamando al Servicio de Usuarios. |
| **Redes de Docker separadas** | Hace que el aislamiento sea verificable en lugar de confiar en la disciplina de quien escribe el código. |
| **Importes como enteros** | Sumar dinero en coma flotante acumula errores de redondeo. Los precios se manejan en la mínima unidad monetaria. |
| **El total lo calcula el dominio** | `Order.place()` no recibe un parámetro `total`: por construcción, el cliente no puede declarar cuánto cuesta su pedido. |
| **Timeout + 1 reintento** | Sin timeout, un servicio lento agota las conexiones del que lo llama y el fallo se propaga en cascada. Con demasiados reintentos, el que llama se convierte en un amplificador de carga contra un servicio que ya está sufriendo. |
| **Validar local antes que remoto** | Un pedido sin líneas se rechaza sin gastar una llamada de red. |
| **`/health` y `/health/ready` separados** | Liveness responde "el proceso vive"; readiness responde "puedo atender ahora", e informa cuál dependencia falló. |
| **Sin framework HTTP en Pedidos** | `Bun.serve` nativo basta y deja el servicio con cero dependencias de npm, lo que refuerza que la capa HTTP es reemplazable. |

---

## 5. Contrato de las APIs

### Servicio de Usuarios — `http://localhost:8001`

Documentación interactiva autogenerada: **http://localhost:8001/docs**

| Método | Ruta | Respuestas |
|---|---|---|
| `GET` | `/health` | `200` |
| `GET` | `/health/ready` | `200` · `503` si la base no responde |
| `POST` | `/users` | `201` · `400` datos inválidos · `409` correo duplicado |
| `GET` | `/users/{id}` | `200` · `404` — **consumido por Pedidos** |
| `GET` | `/users?limit=&offset=` | `200` |

### Servicio de Pedidos — `http://localhost:8002`

| Método | Ruta | Respuestas |
|---|---|---|
| `GET` | `/health` | `200` |
| `GET` | `/health/ready` | `200` · `503` con el detalle de qué dependencia falló |
| `POST` | `/orders` | `201` · `400` inválido · `422` usuario inexistente · `503` Usuarios no responde |
| `GET` | `/orders/{id}` | `200` · `404` |
| `GET` | `/orders?user_id=&limit=&offset=` | `200` |

Ambos servicios devuelven los errores con la misma forma:

```json
{ "error": "unknown_user", "message": "El usuario '…' no existe en el Servicio de Usuarios." }
```

El campo `error` es un código estable pensado para que un programa lo compare;
`message` es texto para una persona. Las peticiones de ejemplo, listas para
ejecutar, están en [`requests.http`](requests.http).

### El contrato, publicado

Ambos servicios publican su especificación OpenAPI 3.1, pero por caminos
opuestos a propósito:

| | Usuarios | Pedidos |
|---|---|---|
| Enfoque | **code first** — FastAPI genera el spec desde el código | **design first** — `openapi.yaml` escrito a mano |
| Contrato | `:8001/openapi.json` | `:8002/openapi.yaml` · `:8002/openapi.json` |
| Documentación | `:8001/docs` (Swagger UI) | `:8002/docs` (5 renderizadores) |

El contrato de Pedidos se valida con `make api-lint` y se vigila con nueve
pruebas en `tests/openapi.test.ts`, que fallan si el YAML y el código se
desvían. El detalle completo, junto con los estándares alternativos a OpenAPI,
está en [`04-api-design-first.md`](04-api-design-first.md).
