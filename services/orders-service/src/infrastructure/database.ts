/**
 * Conexion a Postgres usando el cliente SQL nativo de Bun (`Bun.SQL`).
 *
 * No hace falta ninguna dependencia de npm: Bun trae el driver incorporado.
 */

import { SQL } from "bun";

export function createPool(databaseUrl: string): SQL {
  return new SQL({ url: databaseUrl, max: 10 });
}

/** Comprobacion usada por /health/ready. */
export async function ping(sql: SQL): Promise<boolean> {
  try {
    await sql`SELECT 1`;
    return true;
  } catch {
    return false;
  }
}
