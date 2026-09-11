# Cuadro comparativo: arquitectura monolítica vs. microservicios

**Asignatura:** Lenguaje de Programación Avanzado 2
**Actividad:** Investigación teórica — cuadro comparativo (mínimo 5 criterios)

La última columna no es decorativa: ancla cada criterio a un archivo concreto
de este repositorio, donde la diferencia puede verificarse ejecutando el código.

| # | Criterio | Arquitectura monolítica | Arquitectura de microservicios | Dónde se ve en este repositorio |
|---|---|---|---|---|
| 1 | **Unidad de despliegue** | Un solo artefacto. Cambiar una línea en el módulo de pedidos obliga a desplegar también usuarios, facturación y todo lo demás. | Cada servicio se despliega por separado y en su propio ritmo. | `make up-users` levanta Usuarios sin tocar Pedidos. Son dos imágenes Docker independientes, con dos `Dockerfile` distintos. |
| 2 | **Escalabilidad** | Se replica la aplicación completa, aunque el cuello de botella sea un solo módulo. Se paga por escalar código que no lo necesita. | Se replica solo el servicio saturado. El escalado sigue a la demanda real. | Cada servicio es una imagen con su propio proceso: replicar Pedidos (`--scale orders-service=3`, quitando antes el puerto fijo del host) no obliga a replicar Usuarios. |
| 3 | **Base de datos** | Una base compartida. La integridad referencial la garantiza el motor con claves foráneas y transacciones ACID. | Una base por servicio (*database per service*). Ningún servicio lee las tablas de otro. | `orders.user_id` **no tiene FOREIGN KEY** hacia `users` (`services/orders-service/db/schema.sql`): la tabla vive en otro contenedor, en otra red. |
| 4 | **Acoplamiento e integridad** | Acoplamiento en tiempo de compilación: llamada a función, con el compilador como red de seguridad. | Acoplamiento por contrato de red: la validación se sostiene llamando al otro servicio. | `CreateOrder` consulta el puerto `UserDirectory` antes de insertar (`services/orders-service/src/application/create-order.ts`). |
| 5 | **Stack tecnológico** | Uno solo para todo el sistema. Cambiar de lenguaje o de versión es una migración global. | Cada servicio elige el suyo según el problema que resuelve. | Usuarios en **Python 3.13 + FastAPI**; Pedidos en **TypeScript + Bun 1.4**. Conviven sin conocerse: solo comparten JSON sobre HTTP. |
| 6 | **Aislamiento de fallos** | Un fallo grave (fuga de memoria, excepción no controlada) derriba todo el proceso, incluidas las funciones sanas. | El fallo queda confinado al servicio afectado; el resto sigue operando, quizá degradado. | `make demo-fallo`: con Usuarios apagado, `POST /orders` responde **503**, pero `GET /orders` sigue devolviendo **200**. |
| 7 | **Organización de los equipos** (Ley de Conway) | Muchos equipos sobre un mismo código: conflictos de integración y una cola única de release. | Cada equipo es dueño de su servicio, de su base y de su despliegue. | Los dos servicios no comparten ni una línea de código: `services/users-service` y `services/orders-service` son mundos separados. |
| 8 | **Complejidad operativa** | Baja. Un proceso, un log, un despliegue; se depura con un depurador local. | Alta. Red, descubrimiento de servicios, trazas distribuidas, versionado de APIs, orquestación. | Para correr esto hacen falta **4 contenedores, 3 redes y 2 volúmenes** (`compose.yaml`) donde un monolito usaría 1 proceso y 1 base. Ese es el precio. |
| 9 | **Consistencia transaccional** | `BEGIN … COMMIT` abarca toda la operación de negocio, aunque toque varios módulos. | No hay transacción distribuida. Hay consistencia eventual, *sagas* y compensaciones. | Si Usuarios se cayera justo después de validar y antes de insertar, no habría *rollback* automático entre servicios: por eso `CreateOrder` valida **antes** de persistir. |
| 10 | **Estrategia de pruebas** | Las pruebas de integración son baratas: todo está en el mismo proceso. | Las unitarias siguen siendo baratas, pero probar la integración real exige levantar varios servicios o sustituirlos por dobles. | `make test`: 37 pruebas en milisegundos usando dobles (`tests/doubles.ts`, `tests/in_memory_user_repository.py`). Probar el sistema completo requiere `make up`. |

---

## Lectura del cuadro

Las diez filas se reducen a un solo intercambio:

> Los microservicios **cambian complejidad interna por complejidad operativa**.

Un monolito concentra la dificultad dentro del código: a medida que crece, los
módulos se enredan y nadie se atreve a tocar el núcleo. Los microservicios
extraen esa dificultad del código y la depositan en la infraestructura: el
código de cada servicio queda pequeño y comprensible, pero aparecen problemas
que antes no existían —latencia, fallos parciales, versionado de contratos,
consistencia eventual.

El cambio conviene cuando la complejidad organizativa ya supera a la técnica:
cuando el cuello de botella no es escribir el código, sino coordinar a la gente
que lo escribe. Por eso es una arquitectura que rinde en empresas grandes y
suele castigar a los equipos pequeños, que pagan el costo operativo sin tener
el problema de coordinación que lo justifica.

Este repositorio hace visible ese precio: para dos servicios que en un monolito
serían dos módulos y una llamada a función, aquí hacen falta cuatro contenedores,
tres redes, dos esquemas de base de datos, un adaptador HTTP con timeout y
reintento, y una política explícita de qué hacer cuando el otro servicio no
responde.
