# API Design First: estándares y herramientas

**Asignatura:** Lenguaje de Programación Avanzado 2
**Complemento a la actividad práctica**

---

## 1. El principio

**API Design First** significa que el contrato de la API se acuerda **antes** de
escribir el código, y que ese contrato es la fuente de verdad. El código se
escribe para cumplirlo, no al revés.

El valor aparece cuando hay más de un equipo. En este taller, el Servicio de
Pedidos depende del Servicio de Usuarios. Sin contrato previo, quien programa
Pedidos tiene que esperar a que Usuarios exista para saber qué campos devuelve.
Con contrato previo, ambos equipos arrancan el mismo día: uno implementa y el
otro programa contra un **mock generado desde el contrato**.

> El contrato deja de ser documentación y pasa a ser una **dependencia de
> construcción**.

### Swagger no es OpenAPI

Se usan como sinónimos, pero no lo son:

- **OpenAPI Specification (OAS)** es el **estándar** — hoy en la versión 3.1,
  bajo la Linux Foundation.
- **Swagger** es la familia de **herramientas** de SmartBear construida
  alrededor de él: Swagger UI, Swagger Editor, Swagger Codegen.

En 2015 Swagger 2.0 se donó y pasó a llamarse OpenAPI 3.0; la marca Swagger
quedó solo para el tooling.

---

## 2. Otros estándares de contrato

OpenAPI no es el único, ni siquiera el más estricto.

| Estándar | Dominio | Qué lo distingue |
|---|---|---|
| **OpenAPI** | REST / HTTP | El de facto. Enorme ecosistema. Su debilidad: el contrato es *opcional*, se puede ignorar |
| **AsyncAPI** | Eventos: Kafka, RabbitMQ, MQTT, WebSockets | El hermano de OpenAPI para lo asíncrono. En microservicios reales buena parte del tráfico no es REST, y OpenAPI no lo describe |
| **Protobuf + gRPC** (`.proto`) | RPC binario entre servicios | **El design-first más estricto que existe**: no es opcional. Sin el `.proto` no hay código — el compilador genera cliente y servidor |
| **GraphQL SDL** | APIs de consulta | El esquema *es* la API, y es introspectable en tiempo de ejecución |
| **TypeSpec** (Microsoft) | Compila **a** OpenAPI, JSON Schema y Protobuf | Resuelve el dolor real: escribir YAML de OpenAPI a mano no compone. TypeSpec tiene tipos, herencia y namespaces. Azure describe con esto toda su superficie de API |
| **Smithy** (AWS) | IDL agnóstico del protocolo | Genera SDKs, servidores y OpenAPI. Es con lo que AWS construye sus propios SDKs |
| **JSON Schema** | Sistema de tipos | La base: OpenAPI 3.1 es por fin un superconjunto real de JSON Schema 2020-12 |
| **RAML**, **API Blueprint** | REST (históricos) | Competidores de OpenAPI, hoy prácticamente muertos. Hubo una guerra de estándares y OpenAPI la ganó |
| **WSDL / SOAP** | El antecesor | Design-first ya era la norma en los 2000. El principio no es nuevo; cambió el formato |

### Un enfoque distinto: contratos dirigidos por el consumidor

Todo lo anterior comparte un modelo: *un contrato central del que todos
derivan*. **Pact** propone otro: es el **consumidor** quien declara qué
necesita, y el proveedor se verifica contra esas expectativas en su CI. El
contrato deja de ser un documento y pasa a ser una **prueba que rompe el
build**.

Esto aplica directamente a este repositorio. El Servicio de Pedidos tiene
`FakeUserDirectory` en sus pruebas. Hoy ese doble **puede desviarse** del API
real de Usuarios: si mañana cambia el JSON de `GET /users/{id}`, las 12 pruebas
de Pedidos siguen en verde y el sistema real se rompe. Pact existe exactamente
para cerrar ese hueco.

---

## 3. Herramientas que hacen cumplir el diseño

Un estándar sin herramientas es un PDF que nadie lee. Estas son las piezas que
convierten el principio en algo real, ordenadas por el momento en que actúan:

| Momento | Herramienta | Qué hace |
|---|---|---|
| **Diseñar** | Stoplight Studio, Apicurio, SwaggerHub, Postman | Editores visuales del contrato |
| **Diseñar** | **TypeSpec** | Escribir el contrato en un lenguaje con tipos y compilarlo a OpenAPI |
| **Revisar** | **Spectral** (Stoplight), **Redocly CLI** | *Linters* de contratos: reglas de estilo que fallan en CI |
| **Paralelizar** | **Prism**, **Microcks**, WireMock | **Mock server desde el contrato.** El pago real del design-first: el consumidor programa antes de que el proveedor exista |
| **Implementar** | openapi-generator, **Kiota**, oazapfts, `openapi-typescript` | Generan clientes y tipos desde el contrato |
| **Verificar** | **Schemathesis**, Dredd | Prueban el servicio real contra su contrato, generando casos automáticamente |
| **Verificar** | **Pact** | Contratos dirigidos por el consumidor |
| **Evolucionar** | **oasdiff**, **Optic** | Detectan cambios incompatibles entre versiones del contrato |
| **Publicar** | Scalar, Redoc, RapiDoc, Elements, Swagger UI | Renderizan el contrato para humanos |

En este repositorio se usan tres: **Redocly CLI** para validar (`make api-lint`),
**cinco renderizadores** para publicar, y una **prueba de contrato propia**
(`tests/openapi.test.ts`) que hace de guardia contra la deriva.

---

## 4. Cinco renderizadores sobre el mismo contrato

Levante el sistema y abra **http://localhost:8002/docs**: hay una página que
permite saltar entre los cinco. **Todos leen el mismo `/openapi.json`.** Esa es
la demostración del principio — el contrato es el activo, la presentación es
intercambiable, y cambiar de renderizador no toca una línea del servicio.

| Renderizador | Autor | Probar peticiones | Fuerte en | Flojo en |
|---|---|---|---|---|
| **Scalar** | Scalar | **Sí**, cliente integrado | El más moderno; genera fragmentos de código en varios lenguajes | Bundle grande (~3,7 MB) |
| **Redoc** | Redocly | No (es de pago) | Documentación de referencia para leer; tipografía y navegación de esquemas | Sin consola de pruebas |
| **RapiDoc** | Comunidad | **Sí** | Un solo web component, configurable por atributos; el más liviano (~0,9 MB) | Menos pulido visualmente |
| **Stoplight Elements** | Stoplight | **Sí** | Tres paneles con consola; mismo ecosistema que Spectral | Pesado; requiere hoja de estilos aparte |
| **Swagger UI** | SmartBear | **Sí** | El más reconocido; es lo que FastAPI monta por defecto | Diseño anticuado; lento con contratos grandes |

Los cinco se verificaron renderizando el contrato en un navegador headless, no
solo respondiendo `200`.

**Recomendación para este taller:** Scalar para la sustentación (se ven bien
los ejemplos, muestra la insignia `OpenAPI 3.1.0`, genera el `curl` de cada
operación y permite ejecutarlas en vivo) y Redoc si lo que se quiere es
entregar documentación para leer.

---

## 5. Lo que se hizo en este repositorio

El repo ahora demuestra **los dos enfoques a la vez**, que es más interesante
que elegir uno:

| | Servicio de Usuarios | Servicio de Pedidos |
|---|---|---|
| **Enfoque** | **Code first** | **Design first** |
| Fuente de verdad | El código Python | `openapi.yaml`, escrito a mano |
| El spec… | lo *genera* FastAPI en `/openapi.json` | se *escribe primero*; el código lo cumple |
| Ventaja | Cero esfuerzo, imposible que se desvíe | Se puede acordar y mockear antes de existir |
| Desventaja | No se puede diseñar antes de programar | Puede pudrirse si nadie lo verifica |
| Cómo se mitiga | — | `tests/openapi.test.ts` falla si se desvía |

### El guardia contra la deriva

El riesgo real de un contrato escrito a mano es que envejezca. Por eso
`services/orders-service/tests/openapi.test.ts` compara el YAML con el código:

- Toda ruta del servidor está documentada, y el contrato no promete rutas que
  no existen.
- El `enum` de códigos de error del contrato cubre **todas** las excepciones de
  dominio (se leen por reflexión de `domain/errors.ts`).
- `POST /orders` documenta `201`, `400`, `422` y `503`, y el `503` declara la
  cabecera `Retry-After`.
- Ningún `$ref` apunta a un esquema inexistente.

Está verificado que **falla de verdad**: al agregar una ruta sin documentarla,
la prueba la señala por nombre.

```
(fail) cada operacion del codigo esta documentada en openapi.yaml
+ [ "POST /orders/{id}/cancelar" ]
```

### Gobierno del contrato

`services/orders-service/redocly.yaml` define qué reglas de estilo se exigen y
deja **por escrito cuáles se relajan y por qué**. Se ejecuta con `make api-lint`.

Dos decisiones que vale la pena mirar:

- **`security: []`** se declara explícitamente en el contrato. No es un parche
  del linter: es una afirmación real — esta API no exige autenticación, y
  decirlo es mejor que dejarlo ambiguo por omisión.
- **`operation-4xx-response` se apagó.** La regla exige un `4xx` en toda
  operación, pero `/health` y `GET /orders` no devuelven ninguno. Documentar un
  código que el servicio nunca produce haría que el contrato **mintiera**, que
  es peor que la falta.

---

## 6. Qué faltaría para cerrar el ciclo

Esto queda fuera del alcance del taller, pero es el siguiente paso natural y
vale la pena mencionarlo en la sustentación:

1. **Generar el cliente desde el contrato.** `HttpUserDirectory` tiene los
   tipos de la respuesta de Usuarios escritos a mano; podrían generarse con
   `openapi-typescript` desde el `/openapi.json` de Usuarios. El adaptador
   dejaría de poder desviarse del proveedor.
2. **Mock server con Prism o Microcks** sobre `openapi.yaml`, para desarrollar
   Pedidos sin levantar Usuarios.
3. **Schemathesis** contra el servicio corriendo: genera casos de prueba desde
   el contrato y encuentra respuestas que lo violan.
4. **RFC 9457 (*Problem Details for HTTP APIs*)** en lugar del actual
   `{error, message}`. Es el estándar para cuerpos de error, con los campos
   `type`, `title`, `status`, `detail` e `instance`.
5. **AsyncAPI**, si la comunicación entre servicios pasara de síncrona a
   eventos — que es el remedio habitual para el acoplamiento que produce el
   `503` de este taller.

---

### Referencias

- OpenAPI Initiative — *OpenAPI Specification v3.1.0*. spec.openapis.org
- AsyncAPI Initiative — *AsyncAPI Specification*. asyncapi.com
- Microsoft — *TypeSpec*. typespec.io
- AWS — *Smithy*. smithy.io
- Stoplight — *Spectral*, *Prism*, *Elements*. stoplight.io
- Pact Foundation — *Consumer-Driven Contract Testing*. pact.io
- IETF — *RFC 9457: Problem Details for HTTP APIs* (2023)
