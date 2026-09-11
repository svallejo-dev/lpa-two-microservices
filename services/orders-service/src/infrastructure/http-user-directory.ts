/**
 * Adaptador REST del puerto `UserDirectory`.
 *
 * Aqui, y solo aqui, el Servicio de Pedidos sabe que el Servicio de Usuarios
 * existe, que habla HTTP y que vive en una URL concreta. Todo lo que un
 * monolito resolveria con una llamada a funcion aqui pasa por la red, y la red
 * introduce tres problemas que una llamada local no tiene: latencia, fallos
 * parciales y respuestas ambiguas. Este archivo los maneja.
 */

import { UserDirectoryUnavailableError } from "../domain/errors";
import type { KnownUser, UserDirectory } from "../domain/user-directory";

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export class HttpUserDirectory implements UserDirectory {
  constructor(
    private readonly baseUrl: string,
    private readonly timeoutMs: number,
    private readonly retries: number = 1,
  ) {}

  async findById(userId: string): Promise<KnownUser | null> {
    let lastReason = "sin intentos";

    for (let attempt = 0; attempt <= this.retries; attempt++) {
      try {
        const response = await fetch(`${this.baseUrl}/users/${userId}`, {
          headers: { accept: "application/json" },
          // Sin timeout, un Servicio de Usuarios lento dejaria peticiones de
          // Pedidos colgadas hasta agotar sus conexiones: asi es como el fallo
          // de un servicio se propaga en cascada al resto del sistema.
          signal: AbortSignal.timeout(this.timeoutMs),
        });

        if (response.ok) {
          const body = (await response.json()) as KnownUser;
          return { id: body.id, name: body.name, email: body.email };
        }

        // 404 es una RESPUESTA, no un fallo: el servicio contesto y nos dijo
        // con certeza que ese usuario no existe. Reintentar seria inutil.
        if (response.status === 404) {
          return null;
        }

        lastReason = `respuesta inesperada HTTP ${response.status}`;
      } catch (error) {
        // Timeout, DNS, conexion rechazada, servicio caido... En todos estos
        // casos NO sabemos si el usuario existe.
        lastReason = error instanceof Error ? error.message : String(error);
      }

      // Un unico reintento con espera corta: cubre el fallo transitorio (un
      // contenedor reiniciandose) sin convertir a Pedidos en un amplificador
      // de carga contra un servicio que ya esta sufriendo.
      if (attempt < this.retries) {
        await sleep(100 * (attempt + 1));
      }
    }

    throw new UserDirectoryUnavailableError(lastReason);
  }

  /** Alcance del Servicio de Usuarios, para /health/ready. */
  async isReachable(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        signal: AbortSignal.timeout(this.timeoutMs),
      });
      return response.ok;
    } catch {
      return false;
    }
  }
}
