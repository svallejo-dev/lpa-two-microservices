/**
 * PUERTO de persistencia de pedidos.
 *
 * El dominio declara que necesita guardar pedidos; no decide con que motor.
 * La implementacion concreta (Postgres) vive en `infrastructure/`.
 */

import type { Order } from "./order";

export interface OrderRepository {
  add(order: Order): Promise<void>;
  get(orderId: string): Promise<Order | null>;
  list(options: { userId?: string; limit: number; offset: number }): Promise<Order[]>;
}
