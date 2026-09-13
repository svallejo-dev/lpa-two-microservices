import type { SQL } from "bun";

import type { OrderStatus } from "../domain/order";
import { Order, OrderItem } from "../domain/order";
import type { OrderRepository } from "../domain/order-repository";

interface OrderRow {
  id: string;
  user_id: string;
  total: string | number | bigint;
  status: string;
  created_at: Date | string;
  items: Array<{ sku: string; quantity: number; unit_price: string | number | bigint }>;
}

function toNumber(value: string | number | bigint): number {
  return typeof value === "number" ? value : Number(value);
}

function toEntity(row: OrderRow): Order {
  const items = (row.items ?? []).map((item) =>
    OrderItem.rehydrate(item.sku, Number(item.quantity), toNumber(item.unit_price)),
  );

  return Order.rehydrate(
    row.id,
    row.user_id,
    items,
    toNumber(row.total),
    row.status as OrderStatus,
    new Date(row.created_at),
  );
}

const SELECT_ORDERS = `
  SELECT o.id,
         o.user_id,
         o.total,
         o.status,
         o.created_at,
         COALESCE(
           json_agg(
             json_build_object(
               'sku', i.sku,
               'quantity', i.quantity,
               'unit_price', i.unit_price
             ) ORDER BY i.position
           ) FILTER (WHERE i.order_id IS NOT NULL),
           '[]'::json
         ) AS items
  FROM orders o
  LEFT JOIN order_items i ON i.order_id = o.id
`;

export class PostgresOrderRepository implements OrderRepository {
  constructor(private readonly sql: SQL) {}

  async add(order: Order): Promise<void> {
    await this.sql.begin(async (tx: SQL) => {
      await tx`
        INSERT INTO orders (id, user_id, total, status, created_at)
        VALUES (${order.id}, ${order.userId}, ${order.total}, ${order.status}, ${order.createdAt})
      `;

      for (const [position, item] of order.items.entries()) {
        await tx`
          INSERT INTO order_items (order_id, position, sku, quantity, unit_price)
          VALUES (${order.id}, ${position}, ${item.sku}, ${item.quantity}, ${item.unitPrice})
        `;
      }
    });
  }

  async get(orderId: string): Promise<Order | null> {
    const rows = (await this.sql.unsafe(
      `${SELECT_ORDERS} WHERE o.id = $1 GROUP BY o.id`,
      [orderId],
    )) as OrderRow[];

    return rows.length > 0 ? toEntity(rows[0]!) : null;
  }

  async list(options: { userId?: string; limit: number; offset: number }): Promise<Order[]> {
    const filter = options.userId ? "WHERE o.user_id = $3" : "";
    const params: unknown[] = [options.limit, options.offset];
    if (options.userId) params.push(options.userId);

    const rows = (await this.sql.unsafe(
      `${SELECT_ORDERS} ${filter}
       GROUP BY o.id
       ORDER BY o.created_at DESC
       LIMIT $1 OFFSET $2`,
      params,
    )) as OrderRow[];

    return rows.map(toEntity);
  }
}
