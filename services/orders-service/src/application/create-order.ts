import type { OrderItemInput } from "../domain/order";
import { Order } from "../domain/order";
import type { OrderRepository } from "../domain/order-repository";
import type { UserDirectory } from "../domain/user-directory";
import { UnknownUserError } from "../domain/errors";

export interface CreateOrderCommand {
  userId: string;
  items: readonly OrderItemInput[];
}

export class CreateOrder {
  constructor(
    private readonly orders: OrderRepository,
    private readonly users: UserDirectory,
  ) {}

  async execute(command: CreateOrderCommand): Promise<Order> {
    const order = Order.place(command.userId, command.items);

    const user = await this.users.findById(order.userId);
    if (user === null) {
      throw new UnknownUserError(order.userId);
    }

    await this.orders.add(order);
    return order;
  }
}
