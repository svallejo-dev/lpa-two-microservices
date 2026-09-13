export interface Config {
  port: number;
  databaseUrl: string;
  usersServiceUrl: string;
  userDirectoryTimeoutMs: number;
  userDirectoryRetries: number;
  docsEnabled: boolean;
  logLevel: string;
}

function env(name: string, fallback: string): string {
  const value = Bun.env[name];
  return value === undefined || value === "" ? fallback : value;
}

function envInt(name: string, fallback: number): number {
  const parsed = Number.parseInt(env(name, String(fallback)), 10);
  return Number.isFinite(parsed) ? parsed : fallback;
}

export function loadConfig(): Config {
  return {
    port: envInt("PORT", 8000),
    databaseUrl: env(
      "DATABASE_URL",
      "postgres://orders_app:orders_secret@localhost:5432/orders_db",
    ),
    usersServiceUrl: env("USERS_SERVICE_URL", "http://localhost:8001").replace(/\/+$/, ""),
    userDirectoryTimeoutMs: envInt("USER_DIRECTORY_TIMEOUT_MS", 2000),
    userDirectoryRetries: envInt("USER_DIRECTORY_RETRIES", 1),
    docsEnabled: env("DOCS_ENABLED", "true") !== "false",
    logLevel: env("LOG_LEVEL", "info"),
  };
}
