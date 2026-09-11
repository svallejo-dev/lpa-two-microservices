/** Traduccion entre JSON y el dominio, en la frontera HTTP. */

import type { Order } from "../../domain/order";
import type { OrderItemInput } from "../../domain/order";

export interface CreateOrderBody {
  user_id: string;
  items: Array<{ sku: string; quantity: number; unit_price: number }>;
}

/**
 * Pasa el JSON crudo a la forma que entiende el dominio.
 *
 * No valida nada: validar es trabajo del dominio. Aqui solo se renombran
 * campos (snake_case en el JSON publico, camelCase adentro) para que el
 * contrato de la API pueda evolucionar sin arrastrar al dominio.
 */
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
