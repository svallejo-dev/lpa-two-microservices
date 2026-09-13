export abstract class DomainError extends Error {
  abstract readonly code: string;

  constructor(message: string) {
    super(message);
    this.name = new.target.name;
  }
}

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

export class UnknownUserError extends DomainError {
  readonly code = "unknown_user";
  constructor(readonly userId: string) {
    super(`El usuario '${userId}' no existe en el Servicio de Usuarios.`);
  }
}

export class UserDirectoryUnavailableError extends DomainError {
  readonly code = "user_directory_unavailable";
  constructor(readonly reason: string) {
    super(
      "No se pudo verificar el usuario porque el Servicio de Usuarios no " +
        `respondio (${reason}). El pedido no fue creado; reintente mas tarde.`,
    );
  }
}
