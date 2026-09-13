import type { Order } from "../../domain/order";
import type { OrderItemInput } from "../../domain/order";

export interface CreateOrderBody {
  user_id: string;
  items: Array<{ sku: string; quantity: number; unit_price: number }>;
}

export function toCreateOrderCommand(body: CreateOrderBody): {
  userId: string;
  items: OrderItemInput[];
} {
  return {
    userId: String(body?.user_id ?? ""),
    items: Array.isArray(body?.items)
      ? body.items.map((item) => ({
          sku: item?.sku,
          quantity: item?.quantity,
          unitPrice: item?.unit_price,
        }))
      : [],
  };
}

export function toOrderResponse(order: Order) {
  return {
    id: order.id,
    user_id: order.userId,
    status: order.status,
    total: order.total,
    items: order.items.map((item) => ({
      sku: item.sku,
      quantity: item.quantity,
      unit_price: item.unitPrice,
      subtotal: item.subtotal,
    })),
    created_at: order.createdAt.toISOString(),
  };
}
