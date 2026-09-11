import { describe, expect, test } from "bun:test";

import { CreateOrder } from "../src/application/create-order";
import {
  EmptyOrderError,
  UnknownUserError,
  UserDirectoryUnavailableError,
} from "../src/domain/errors";
import {
  BrokenUserDirectory,
  EmptyUserDirectory,
  FakeUserDirectory,
  InMemoryOrderRepository,
} from "./doubles";

const USER = {
  id: "6f1a3b2c-1111-4222-8333-444455556666",
  name: "Ana",
  email: "ana@example.com",
};
const ITEMS = [{ sku: "TECLADO", quantity: 2, unitPrice: 15_000 }];

describe("CreateOrder", () => {
  test("crea y persiste el pedido cuando el usuario existe", async () => {
    const orders = new InMemoryOrderRepository();
    const useCase = new CreateOrder(orders, new FakeUserDirectory(USER));

    const order = await useCase.execute({ userId: USER.id, items: ITEMS });

    expect(order.total).toBe(30_000);
    expect(orders.saved).toHaveLength(1);
    expect(await orders.get(order.id)).toBe(order);
  });

  test("rechaza el pedido si el usuario no existe, y no persiste nada", async () => {
    const orders = new InMemoryOrderRepository();
    const useCase = new CreateOrder(orders, new EmptyUserDirectory());

    await expect(useCase.execute({ userId: USER.id, items: ITEMS }))
      .rejects.toThrow(UnknownUserError);
    expect(orders.saved).toHaveLength(0);
  });

  test("si el Servicio de Usuarios esta caido, falla sin persistir el pedido", async () => {
    // La garantia importante: ante la duda, el sistema NO inventa datos. No
    // guarda un pedido "a ver si luego valida": se rechaza la operacion
    // completa y se le dice al cliente que reintente.
    const orders = new InMemoryOrderRepository();
    const useCase = new CreateOrder(orders, new BrokenUserDirectory());

    await expect(useCase.execute({ userId: USER.id, items: ITEMS }))
      .rejects.toThrow(UserDirectoryUnavailableError);
    expect(orders.saved).toHaveLength(0);
  });

  test("no llama al Servicio de Usuarios si el pedido ya es invalido", async () => {
    // Validacion local primero: se ahorra una llamada de red inutil.
    const directory = new FakeUserDirectory(USER);
    const useCase = new CreateOrder(new InMemoryOrderRepository(), directory);

    await expect(useCase.execute({ userId: USER.id, items: [] }))
      .rejects.toThrow(EmptyOrderError);
    expect(directory.calls).toBe(0);
  });
});
