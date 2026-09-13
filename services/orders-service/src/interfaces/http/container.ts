import type { SQL } from "bun";

import { CreateOrder } from "../../application/create-order";
import { GetOrder } from "../../application/get-order";
import { ListOrders } from "../../application/list-orders";
import type { Config } from "../../infrastructure/config";
import { createPool } from "../../infrastructure/database";
import { HttpUserDirectory } from "../../infrastructure/http-user-directory";
import { PostgresOrderRepository } from "../../infrastructure/postgres-order-repository";

export interface Container {
  createOrder: CreateOrder;
  getOrder: GetOrder;
  listOrders: ListOrders;
  sql: SQL;
  userDirectory: HttpUserDirectory;
}

export function buildContainer(config: Config): Container {
  const sql = createPool(config.databaseUrl);

  const orders = new PostgresOrderRepository(sql);
  const userDirectory = new HttpUserDirectory(
    config.usersServiceUrl,
    config.userDirectoryTimeoutMs,
    config.userDirectoryRetries,
  );

  return {
    createOrder: new CreateOrder(orders, userDirectory),
    getOrder: new GetOrder(orders),
    listOrders: new ListOrders(orders),
    sql,
    userDirectory,
  };
}
