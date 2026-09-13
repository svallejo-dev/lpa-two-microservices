import type { Order } from "./order";

export interface OrderRepository {
  add(order: Order): Promise<void>;
  get(orderId: string): Promise<Order | null>;
  list(options: { userId?: string; limit: number; offset: number }): Promise<Order[]>;
}
