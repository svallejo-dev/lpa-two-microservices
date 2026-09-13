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

for (const signal of ["SIGINT", "SIGTERM"] as const) {
  process.on(signal, async () => {
    console.log(`[orders-service] ${signal} recibido, cerrando...`);
    await server.stop(true);
    await container.sql.close();
    process.exit(0);
  });
}
