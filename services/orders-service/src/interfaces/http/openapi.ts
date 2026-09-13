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
