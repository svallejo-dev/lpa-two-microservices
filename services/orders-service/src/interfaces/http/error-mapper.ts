import {
  DomainError,
  EmptyOrderError,
  InvalidPriceError,
  InvalidQuantityError,
  InvalidSkuError,
  InvalidUserIdError,
  OrderNotFoundError,
  UnknownUserError,
  UserDirectoryUnavailableError,
} from "../../domain/errors";

const STATUS_BY_ERROR = new Map<Function, number>([
  [EmptyOrderError, 400],
  [InvalidQuantityError, 400],
  [InvalidPriceError, 400],
  [InvalidSkuError, 400],
  [InvalidUserIdError, 400],
  [OrderNotFoundError, 404],
  [UnknownUserError, 422],
  [UserDirectoryUnavailableError, 503],
]);

export function jsonResponse(body: unknown, status: number, headers: Record<string, string> = {}): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", ...headers },
  });
}

export function toErrorResponse(error: unknown): Response {
  if (error instanceof DomainError) {
    const status = STATUS_BY_ERROR.get(error.constructor) ?? 400;
    const headers: Record<string, string> = status === 503 ? { "retry-after": "5" } : {};
    return jsonResponse({ error: error.code, message: error.message }, status, headers);
  }

  if (error instanceof SyntaxError) {
    return jsonResponse(
      { error: "invalid_json", message: "El cuerpo de la peticion no es JSON valido." },
      400,
    );
  }

  console.error("Error no controlado:", error);
  return jsonResponse(
    { error: "internal_error", message: "Error interno del servicio." },
    500,
  );
}
