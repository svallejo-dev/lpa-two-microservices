/**
 * Dobles de prueba de los dos puertos del servicio.
 *
 * `FakeUserDirectory` es el que hace valioso todo el diseno: permite probar
 * "que pasa cuando el Servicio de Usuarios se cae" sin levantar Docker, sin
 * red y en milisegundos. Con un `fetch` incrustado dentro del caso de uso,
 * ese escenario solo se podria probar apagando contenedores a mano.
 */

import { UserDirectoryUnavailableError } from "../src/domain/errors";
import type { Order } from "../src/domain/order";
import type { OrderRepository } from "../src/domain/order-repository";
import type { KnownUser, UserDirectory } from "../src/domain/user-directory";

export class InMemoryOrderRepository implements OrderRepository {
  readonly saved: Order[] = [];

  async add(order: Order): Promise<void> {
    this.saved.push(order);
  }

  async get(orderId: string): Promise<Order | null> {
    return this.saved.find((order) => order.id === orderId) ?? null;
  }

  async list(options: { userId?: string; limit: number; offset: number }): Promise<Order[]> {
    return this.saved
      .filter((order) => !options.userId || order.userId === options.userId)
      .slice(options.offset, options.offset + options.limit);
  }
}

/** El usuario existe. */
export class FakeUserDirectory implements UserDirectory {
  calls = 0;

  constructor(private readonly user: KnownUser) {}

  async findById(userId: string): Promise<KnownUser | null> {
    this.calls++;
    return userId === this.user.id ? this.user : null;
  }
}

/** El Servicio de Usuarios responde, y responde que el usuario no existe. */
export class EmptyUserDirectory implements UserDirectory {
  async findById(): Promise<KnownUser | null> {
    return null;
  }
}

/** El Servicio de Usuarios esta caido: no se puede saber nada. */
export class BrokenUserDirectory implements UserDirectory {
  async findById(): Promise<KnownUser | null> {
    throw new UserDirectoryUnavailableError("connection refused");
  }
}
