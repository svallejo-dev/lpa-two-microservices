import {
  EmptyOrderError,
  InvalidPriceError,
  InvalidQuantityError,
  InvalidSkuError,
  InvalidUserIdError,
} from "./errors";

const UUID_PATTERN =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export type OrderStatus = "PENDIENTE" | "CONFIRMADO" | "CANCELADO";

export interface OrderItemInput {
  sku: string;
  quantity: number;
  unitPrice: number;
}

export class OrderItem {
  private constructor(
    readonly sku: string,
    readonly quantity: number,
    readonly unitPrice: number,
  ) {}

  static create(input: OrderItemInput): OrderItem {
    const sku = String(input.sku ?? "").trim();
    if (sku.length === 0) throw new InvalidSkuError();

    if (!Number.isInteger(input.quantity) || input.quantity <= 0) {
      throw new InvalidQuantityError(sku, input.quantity);
    }
    if (!Number.isInteger(input.unitPrice) || input.unitPrice < 0) {
      throw new InvalidPriceError(sku, input.unitPrice);
    }

    return new OrderItem(sku, input.quantity, input.unitPrice);
  }

  static rehydrate(sku: string, quantity: number, unitPrice: number): OrderItem {
    return new OrderItem(sku, quantity, unitPrice);
  }

  get subtotal(): number {
    return this.quantity * this.unitPrice;
  }
}

export class Order {
  private constructor(
    readonly id: string,
    readonly userId: string,
    readonly items: readonly OrderItem[],
    readonly total: number,
    readonly status: OrderStatus,
    readonly createdAt: Date,
  ) {}

  static place(userId: string, items: readonly OrderItemInput[]): Order {
    if (!UUID_PATTERN.test(String(userId ?? ""))) {
      throw new InvalidUserIdError(String(userId));
    }
    if (!Array.isArray(items) || items.length === 0) {
      throw new EmptyOrderError();
    }

    const orderItems = items.map((item) => OrderItem.create(item));
    const total = orderItems.reduce((sum, item) => sum + item.subtotal, 0);

    return new Order(
      crypto.randomUUID(),
      userId.toLowerCase(),
      orderItems,
      total,
      "PENDIENTE",
      new Date(),
    );
  }

  static rehydrate(
    id: string,
    userId: string,
    items: readonly OrderItem[],
    total: number,
    status: OrderStatus,
    createdAt: Date,
  ): Order {
    return new Order(id, userId, items, total, status, createdAt);
  }
}
