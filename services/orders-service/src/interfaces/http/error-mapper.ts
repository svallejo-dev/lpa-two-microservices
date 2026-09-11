/**
 * Traduccion de errores de dominio a codigos HTTP.
 *
 * La fila importante es la ultima: `user_directory_unavailable` -> 503.
 * Un 4xx le diria al cliente "corrige tus datos" cuando sus datos estaban
 * bien; el 503 le dice la verdad: "el problema es nuestro, reintenta".
 */

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
  // 422: la peticion esta bien formada, pero se refiere a un usuario que no
  // existe. Es un problema de datos del cliente, no de sintaxis.
  [UnknownUserError, 422],
  // 503: no es culpa del cliente. Se acompana de Retry-After.
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
