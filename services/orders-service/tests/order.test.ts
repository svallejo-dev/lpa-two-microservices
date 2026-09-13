import { describe, expect, test } from "bun:test";

import {
  EmptyOrderError,
  InvalidPriceError,
  InvalidQuantityError,
  InvalidSkuError,
  InvalidUserIdError,
} from "../src/domain/errors";
import { Order } from "../src/domain/order";

const USER_ID = "6f1a3b2c-1111-4222-8333-444455556666";

describe("Order", () => {
  test("calcula el total sumando los subtotales de cada linea", () => {
    const order = Order.place(USER_ID, [
      { sku: "TECLADO", quantity: 2, unitPrice: 15_000 },
      { sku: "MOUSE", quantity: 3, unitPrice: 8_000 },
    ]);

    expect(order.total).toBe(2 * 15_000 + 3 * 8_000);
    expect(order.status).toBe("PENDIENTE");
    expect(order.items).toHaveLength(2);
  });

  test("ignora cualquier total que venga desde fuera", () => {
    const order = Order.place(USER_ID, [{ sku: "SSD", quantity: 1, unitPrice: 250_000 }]);
    expect(order.total).toBe(250_000);
  });

  test("rechaza un pedido sin lineas", () => {
    expect(() => Order.place(USER_ID, [])).toThrow(EmptyOrderError);
  });

  test("rechaza cantidades no positivas o fraccionarias", () => {
    expect(() => Order.place(USER_ID, [{ sku: "A", quantity: 0, unitPrice: 100 }]))
      .toThrow(InvalidQuantityError);
    expect(() => Order.place(USER_ID, [{ sku: "A", quantity: -1, unitPrice: 100 }]))
      .toThrow(InvalidQuantityError);
    expect(() => Order.place(USER_ID, [{ sku: "A", quantity: 1.5, unitPrice: 100 }]))
      .toThrow(InvalidQuantityError);
  });

  test("rechaza precios negativos o con decimales", () => {
    expect(() => Order.place(USER_ID, [{ sku: "A", quantity: 1, unitPrice: -5 }]))
      .toThrow(InvalidPriceError);
    expect(() => Order.place(USER_ID, [{ sku: "A", quantity: 1, unitPrice: 10.5 }]))
      .toThrow(InvalidPriceError);
  });

  test("rechaza un SKU vacio", () => {
    expect(() => Order.place(USER_ID, [{ sku: "   ", quantity: 1, unitPrice: 100 }]))
      .toThrow(InvalidSkuError);
  });

  test("rechaza un identificador de usuario que no es UUID", () => {
    expect(() => Order.place("no-soy-un-uuid", [{ sku: "A", quantity: 1, unitPrice: 1 }]))
      .toThrow(InvalidUserIdError);
  });

  test("asigna un identificador unico a cada pedido", () => {
    const items = [{ sku: "A", quantity: 1, unitPrice: 1 }];
    expect(Order.place(USER_ID, items).id).not.toBe(Order.place(USER_ID, items).id);
  });
});
