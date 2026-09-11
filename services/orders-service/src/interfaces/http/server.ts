/**
 * Servidor HTTP con `Bun.serve` nativo, sin framework.
 *
 * Los handlers son delgados a proposito: leen el JSON, invocan un caso de uso
 * y serializan el resultado. Toda la logica esta en `application/` y
 * `domain/`, de modo que cambiar Bun por Express o Hono no tocaria una sola
 * regla de negocio.
 */

import { DEFAULT_LIMIT } from "../../application/list-orders";
import { ping } from "../../infrastructure/database";
import type { Config } from "../../infrastructure/config";
import type { Container } from "./container";
import type { CreateOrderBody } from "./dto";
import { toCreateOrderCommand, toOrderResponse } from "./dto";
import {
  docsIndexPage,
  elementsPage,
  rapidocPage,
  redocPage,
  scalarPage,
  swaggerPage,
} from "./docs-pages";
import { jsonResponse, toErrorResponse } from "./error-mapper";
import { jsonSpecResponse, yamlResponse } from "./openapi";

const SERVICE_NAME = "orders-service";

function intParam(url: URL, name: string, fallback: number): number {
  const raw = url.searchParams.get(name);
  if (raw === null) return fallback;
  const parsed = Number.parseInt(raw, 10);
  return Number.isFinite(parsed) ? parsed : fallback;
}

/**
 * Tabla de rutas del servicio.
 *
 * Se separa de `createServer` para que `tests/openapi.test.ts` pueda compararla
 * con las rutas declaradas en `openapi.yaml` sin necesidad de abrir un puerto
 * ni de conectarse a la base de datos.
 */
export function buildRoutes(container: Container) {
  return {
    // --- Salud --------------------------------------------------------
    "/health": {
      GET: () => jsonResponse({ status: "ok", service: SERVICE_NAME }, 200),
    },

    "/health/ready": {
      GET: async () => {
        // Readiness mira las dos dependencias: la base propia y el otro
        // microservicio. Reportarlas por separado permite saber de un
        // vistazo cual de las dos fallo.
        const [databaseOk, usersOk] = await Promise.all([
          ping(container.sql),
          container.userDirectory.isReachable(),
        ]);

        return jsonResponse(
          {
            status: databaseOk && usersOk ? "ready" : "degraded",
            service: SERVICE_NAME,
            dependencies: {
              database: databaseOk ? "ok" : "unreachable",
              users_service: usersOk ? "ok" : "unreachable",
            },
          },
          databaseOk && usersOk ? 200 : 503,
        );
      },
    },

    // --- Pedidos ------------------------------------------------------
    "/orders": {
      POST: async (request: Request) => {
        try {
          const body = (await request.json()) as CreateOrderBody;
          const order = await container.createOrder.execute(toCreateOrderCommand(body));
          return jsonResponse(toOrderResponse(order), 201, {
            location: `/orders/${order.id}`,
          });
        } catch (error) {
          return toErrorResponse(error);
        }
      },

      GET: async (request: Request) => {
        try {
          const url = new URL(request.url);
          const orders = await container.listOrders.execute({
            userId: url.searchParams.get("user_id") ?? undefined,
            limit: intParam(url, "limit", DEFAULT_LIMIT),
            offset: intParam(url, "offset", 0),
          });
          return jsonResponse(orders.map(toOrderResponse), 200);
        } catch (error) {
          return toErrorResponse(error);
        }
      },
    },

    "/orders/:id": {
      GET: async (request: Bun.BunRequest<"/orders/:id">) => {
        try {
          const order = await container.getOrder.execute(request.params.id);
          return jsonResponse(toOrderResponse(order), 200);
        } catch (error) {
          return toErrorResponse(error);
        }
      },
    },
  };
}

/**
 * Rutas que publican el CONTRATO y su documentacion.
 *
 * Se mantienen aparte de las rutas de negocio por dos motivos: no forman parte
 * del contrato (no aparecen en `openapi.yaml`, porque un contrato no se
 * describe a si mismo) y se desactivan en bloque con DOCS_ENABLED=false para
 * no exponer la documentacion en un entorno real.
 */
export function buildDocsRoutes() {
  return {
    "/openapi.yaml": { GET: () => yamlResponse() },
    "/openapi.json": { GET: () => jsonSpecResponse() },
    "/docs": { GET: () => docsIndexPage() },
    "/docs/scalar": { GET: () => scalarPage() },
    "/docs/redoc": { GET: () => redocPage() },
    "/docs/rapidoc": { GET: () => rapidocPage() },
    "/docs/elements": { GET: () => elementsPage() },
    "/docs/swagger": { GET: () => swaggerPage() },
  };
}

export function createServer(container: Container, config: Config) {
  const routes = config.docsEnabled
    ? { ...buildRoutes(container), ...buildDocsRoutes() }
    : buildRoutes(container);

  return Bun.serve({
    port: config.port,
    routes,

    fetch: () =>
      jsonResponse({ error: "not_found", message: "Ruta no encontrada." }, 404),
  });
}
