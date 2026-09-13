import { describe, expect, test } from "bun:test";

import { DomainError } from "../src/domain/errors";
import * as errors from "../src/domain/errors";
import { specDocument } from "../src/interfaces/http/openapi";
import { buildDocsRoutes, buildRoutes } from "../src/interfaces/http/server";
import type { Container } from "../src/interfaces/http/container";

function toOpenApiPath(bunPath: string): string {
  return bunPath.replace(/:(\w+)/g, "{$1}");
}

function operacionesDelCodigo(rutas: Record<string, object>): string[] {
  return Object.entries(rutas)
    .flatMap(([ruta, metodos]) =>
      Object.keys(metodos).map((metodo) => `${metodo} ${toOpenApiPath(ruta)}`),
    )
    .sort();
}

function operacionesDelContrato(): string[] {
  return Object.entries(specDocument.paths)
    .flatMap(([ruta, metodos]) =>
      Object.keys(metodos).map((metodo) => `${metodo.toUpperCase()} ${ruta}`),
    )
    .sort();
}

const rutasDeNegocio = buildRoutes({} as Container);

describe("El contrato describe el servicio real", () => {
  test("cada operacion del codigo esta documentada en openapi.yaml", () => {
    const enElCodigo = operacionesDelCodigo(rutasDeNegocio);
    const enElContrato = operacionesDelContrato();

    const sinDocumentar = enElCodigo.filter((op) => !enElContrato.includes(op));
    expect(sinDocumentar).toEqual([]);
  });

  test("el contrato no promete operaciones que el codigo no implementa", () => {
    const enElCodigo = operacionesDelCodigo(rutasDeNegocio);
    const enElContrato = operacionesDelContrato();

    const inventadas = enElContrato.filter((op) => !enElCodigo.includes(op));
    expect(inventadas).toEqual([]);
  });

  test("las rutas de documentacion NO aparecen en el contrato", () => {
    const rutasDocs = Object.keys(buildDocsRoutes());
    const rutasContrato = Object.keys(specDocument.paths);

    for (const ruta of rutasDocs) {
      expect(rutasContrato).not.toContain(ruta);
    }
  });
});

describe("Los codigos de error coinciden con el dominio", () => {
  function codigosDelDominio(): string[] {
    const codigos: string[] = [];

    for (const exportado of Object.values(errors)) {
      if (typeof exportado !== "function") continue;
      if (!(exportado.prototype instanceof DomainError)) continue;

      const ClaseError = exportado as unknown as new (
        ...args: unknown[]
      ) => DomainError;
      codigos.push(new ClaseError("x", 1).code);
    }

    return codigos.sort();
  }

  test("el enum del contrato cubre todos los errores de dominio", () => {
    const enumDelContrato = (specDocument as any).components.schemas.Error
      .properties.error.enum as string[];

    const sinDocumentar = codigosDelDominio().filter(
      (codigo) => !enumDelContrato.includes(codigo),
    );
    expect(sinDocumentar).toEqual([]);
  });

  test("POST /orders documenta 201, 400, 422 y 503", () => {
    const respuestas = Object.keys(
      (specDocument as any).paths["/orders"].post.responses,
    );
    expect(respuestas).toEqual(expect.arrayContaining(["201", "400", "422", "503"]));
  });

  test("el 503 documenta la cabecera Retry-After", () => {
    const respuesta503 = (specDocument as any).paths["/orders"].post.responses["503"];
    expect(respuesta503.headers).toHaveProperty("Retry-After");
  });
});

describe("El contrato es utilizable", () => {
  test("declara OpenAPI 3.1 y una version de la API", () => {
    expect((specDocument as any).openapi).toStartWith("3.1");
    expect(specDocument.info.version).toMatch(/^\d+\.\d+\.\d+$/);
  });

  test("toda operacion tiene operationId, y son unicos", () => {
    const ids: string[] = [];
    for (const metodos of Object.values(specDocument.paths)) {
      for (const operacion of Object.values(metodos)) {
        const id = (operacion as { operationId?: string }).operationId;
        expect(id).toBeDefined();
        ids.push(id!);
      }
    }
    expect(new Set(ids).size).toBe(ids.length);
  });

  test("ninguna referencia $ref apunta a un esquema inexistente", () => {
    const definidos = Object.keys((specDocument as any).components.schemas);
    const usados = [
      ...JSON.stringify(specDocument).matchAll(
        /#\/components\/schemas\/(\w+)/g,
      ),
    ].map((coincidencia) => coincidencia[1]!);

    const rotas = [...new Set(usados)].filter((n) => !definidos.includes(n));
    expect(rotas).toEqual([]);
  });
});
