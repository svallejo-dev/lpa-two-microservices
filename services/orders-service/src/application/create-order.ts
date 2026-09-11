/**
 * Caso de uso: crear un pedido.
 *
 * Es el corazon del taller: el unico punto donde un microservicio necesita
 * algo que otro microservicio posee.
 */

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
    // 1. Validacion LOCAL primero. Si el pedido esta mal formado, se rechaza
    //    sin gastar una llamada de red al otro servicio.
    const order = Order.place(command.userId, command.items);

    // 2. Validacion REMOTA. Como las bases de datos estan separadas, no existe
    //    una foreign key que garantice que el usuario existe: hay que
    //    preguntarlo. Si el directorio no responde, este `await` lanza
    //    `UserDirectoryUnavailableError` y el pedido NO se persiste.
    const user = await this.users.findById(order.userId);
    if (user === null) {
      throw new UnknownUserError(order.userId);
    }

    // 3. Persistencia. Solo se llega aqui con un usuario confirmado.
    await this.orders.add(order);
    return order;
  }
}
