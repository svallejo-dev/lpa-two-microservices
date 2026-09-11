/**
 * Errores de negocio del Servicio de Pedidos.
 *
 * Capa de DOMINIO: no conocen HTTP ni SQL. Cada uno lleva un `code` estable
 * que `interfaces/http/error-mapper.ts` traduce a un codigo de estado.
 */

export abstract class DomainError extends Error {
  abstract readonly code: string;

  constructor(message: string) {
    super(message);
    this.name = new.target.name;
  }
}

/** Un pedido sin lineas no es un pedido. */
export class EmptyOrderError extends DomainError {
  readonly code = "empty_order";
  constructor() {
    super("Un pedido debe tener al menos una linea.");
  }
}

export class InvalidQuantityError extends DomainError {
  readonly code = "invalid_quantity";
  constructor(readonly sku: string, readonly quantity: unknown) {
    super(`La cantidad de '${sku}' debe ser un entero mayor que cero (recibido: ${quantity}).`);
  }
}

export class InvalidPriceError extends DomainError {
  readonly code = "invalid_price";
  constructor(readonly sku: string, readonly unitPrice: unknown) {
    super(
      `El precio unitario de '${sku}' debe ser un entero no negativo en la ` +
        `minima unidad monetaria (recibido: ${unitPrice}).`,
    );
  }
}

export class InvalidSkuError extends DomainError {
  readonly code = "invalid_sku";
  constructor() {
    super("Cada linea del pedido debe indicar un SKU no vacio.");
  }
}

export class InvalidUserIdError extends DomainError {
  readonly code = "invalid_user_id";
  constructor(readonly userId: string) {
    super(`El identificador de usuario '${userId}' no es un UUID valido.`);
  }
}

export class OrderNotFoundError extends DomainError {
  readonly code = "order_not_found";
  constructor(readonly orderId: string) {
    super(`No existe un pedido con id '${orderId}'.`);
  }
}

/**
 * El usuario NO existe. Es una respuesta confirmada del Servicio de Usuarios:
 * sabemos con certeza que ese usuario no esta registrado.
 */
export class UnknownUserError extends DomainError {
  readonly code = "unknown_user";
  constructor(readonly userId: string) {
    super(`El usuario '${userId}' no existe en el Servicio de Usuarios.`);
  }
}

/**
 * NO SABEMOS si el usuario existe: el Servicio de Usuarios no respondio.
 *
 * Distinguir este caso del anterior es la decision de diseno mas importante
 * del servicio. "No existe" es una respuesta del negocio (el cliente debe
 * corregir los datos); "no pude preguntar" es un fallo de infraestructura (el
 * cliente debe reintentar mas tarde). Confundirlos llevaria a rechazar pedidos
 * de usuarios perfectamente validos cada vez que la red falla.
 */
export class UserDirectoryUnavailableError extends DomainError {
  readonly code = "user_directory_unavailable";
  constructor(readonly reason: string) {
    super(
      "No se pudo verificar el usuario porque el Servicio de Usuarios no " +
        `respondio (${reason}). El pedido no fue creado; reintente mas tarde.`,
    );
  }
}
