/**
 * Punto de entrada del Servicio de Pedidos.
 *
 * Arranque: leer configuracion -> construir adaptadores -> inyectarlos en los
 * casos de uso -> exponerlos por HTTP.
 */

import { loadConfig } from "./infrastructure/config";
import { buildContainer } from "./interfaces/http/container";
import { createServer } from "./interfaces/http/server";

const config = loadConfig();
const container = buildContainer(config);
const server = createServer(container, config);

console.log(
  `[orders-service] escuchando en http://localhost:${server.port} ` +
    `| Servicio de Usuarios: ${config.usersServiceUrl} ` +
    `(timeout ${config.userDirectoryTimeoutMs} ms, ${config.userDirectoryRetries} reintento/s)`,
);

// Cierre ordenado: deja de aceptar peticiones y suelta el pool de Postgres.
for (const signal of ["SIGINT", "SIGTERM"] as const) {
  process.on(signal, async () => {
    console.log(`[orders-service] ${signal} recibido, cerrando...`);
    await server.stop(true);
    await container.sql.close();
    process.exit(0);
  });
}
