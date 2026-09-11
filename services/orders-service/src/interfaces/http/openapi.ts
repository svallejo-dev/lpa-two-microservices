/**
 * Publicacion del contrato.
 *
 * El spec se lee UNA vez del archivo `openapi.yaml` escrito a mano y se
 * expone en dos representaciones del mismo documento:
 *
 *   GET /openapi.yaml  -> el archivo tal cual, como se versiona en git
 *   GET /openapi.json  -> el mismo contenido en JSON, que es lo que consumen
 *                         los renderizadores y los generadores de clientes
 *
 * Bun trae analizador de YAML incorporado (`Bun.YAML`), asi que esto no
 * agrega ninguna dependencia.
 */

const SPEC_FILE = `${import.meta.dir}/../../../openapi.yaml`;

export const specYaml: string = await Bun.file(SPEC_FILE).text();
export const specDocument = Bun.YAML.parse(specYaml) as {
  info: { title: string; version: string };
  paths: Record<string, Record<string, unknown>>;
};

const specJson: string = JSON.stringify(specDocument, null, 2);

export function yamlResponse(): Response {
  return new Response(specYaml, {
    headers: {
      "content-type": "application/yaml; charset=utf-8",
      // Permite que un renderizador servido desde otro origen lea el contrato.
      "access-control-allow-origin": "*",
    },
  });
}

export function jsonSpecResponse(): Response {
  return new Response(specJson, {
    headers: {
      "content-type": "application/json; charset=utf-8",
      "access-control-allow-origin": "*",
    },
  });
}
