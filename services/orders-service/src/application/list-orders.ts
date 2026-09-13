import type { Order } from "../domain/order";
import type { OrderRepository } from "../domain/order-repository";

export const DEFAULT_LIMIT = 20;
export const MAX_LIMIT = 100;

export interface ListOrdersQuery {
  userId?: string;
  limit?: number;
  offset?: number;
}

export class ListOrders {
  constructor(private readonly orders: OrderRepository) {}

  async execute(query: ListOrdersQuery = {}): Promise<Order[]> {
    const limit = Math.max(1, Math.min(query.limit ?? DEFAULT_LIMIT, MAX_LIMIT));
    const offset = Math.max(0, query.offset ?? 0);
    return this.orders.list({ userId: query.userId, limit, offset });
  }
}
