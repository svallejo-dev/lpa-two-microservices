import { SQL } from "bun";

export function createPool(databaseUrl: string): SQL {
  return new SQL({ url: databaseUrl, max: 10 });
}

export async function ping(sql: SQL): Promise<boolean> {
  try {
    await sql`SELECT 1`;
    return true;
  } catch {
    return false;
  }
}
