/** Caso de uso: consultar un pedido por id. */

import { OrderNotFoundError } from "../domain/errors";
import type { Order } from "../domain/order";
import type { OrderRepository } from "../domain/order-repository";

export class GetOrder {
  constructor(private readonly orders: OrderRepository) {}

  async execute(orderId: string): Promise<Order> {
    const order = await this.orders.get(orderId);
    if (order === null) {
      throw new OrderNotFoundError(orderId);
    }
    return order;
  }
}
