const SPEC_URL = "/openapi.json";

function htmlResponse(html: string): Response {
  return new Response(html, {
    headers: { "content-type": "text/html; charset=utf-8" },
  });
}

const NAV = `
<nav class="lpa-nav">
  <a href="/docs">&larr; comparar</a>
  <a href="/docs/scalar">Scalar</a>
  <a href="/docs/redoc">Redoc</a>
  <a href="/docs/rapidoc">RapiDoc</a>
  <a href="/docs/elements">Elements</a>
  <a href="/docs/swagger">Swagger UI</a>
  <a href="/openapi.yaml">openapi.yaml</a>
</nav>
<style>
  .lpa-nav{position:fixed;top:0;left:0;right:0;z-index:9999;display:flex;gap:.75rem;
    align-items:center;padding:.45rem .9rem;background:#111827;font:600 12px/1
    ui-sans-serif,system-ui,sans-serif}
  .lpa-nav a{color:#d1d5db;text-decoration:none;padding:.3rem .5rem;border-radius:4px}
  .lpa-nav a:hover{background:#374151;color:#fff}
  body{margin-top:34px!important}
</style>`;

export const scalarPage = () =>
  htmlResponse(`<!doctype html><html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pedidos · Scalar</title></head><body>
${NAV}
<script id="api-reference" data-url="${SPEC_URL}"></script>
<script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
</body></html>`);

export const redocPage = () =>
  htmlResponse(`<!doctype html><html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pedidos · Redoc</title></head><body>
${NAV}
<redoc spec-url="${SPEC_URL}"></redoc>
<script src="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js"></script>
</body></html>`);

export const rapidocPage = () =>
  htmlResponse(`<!doctype html><html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pedidos · RapiDoc</title>
<script type="module" src="https://cdn.jsdelivr.net/npm/rapidoc/dist/rapidoc-min.js"></script>
</head><body>
${NAV}
<rapi-doc spec-url="${SPEC_URL}" theme="light" render-style="read"
  show-header="false" allow-spec-url-load="false" allow-spec-file-load="false"
  primary-color="#2d6a4f" style="height:calc(100vh - 34px)"></rapi-doc>
</body></html>`);

export const elementsPage = () =>
  htmlResponse(`<!doctype html><html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pedidos · Stoplight Elements</title>
<script src="https://cdn.jsdelivr.net/npm/@stoplight/elements/web-components.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@stoplight/elements/styles.min.css">
</head><body>
${NAV}
<elements-api apiDescriptionUrl="${SPEC_URL}" router="hash" layout="sidebar"></elements-api>
</body></html>`);

export const swaggerPage = () =>
  htmlResponse(`<!doctype html><html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pedidos · Swagger UI</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui.css">
</head><body>
${NAV}
<div id="swagger"></div>
<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui-bundle.js"></script>
<script>
  SwaggerUIBundle({ url: "${SPEC_URL}", dom_id: "#swagger", deepLinking: true });
</script>
</body></html>`);

const RENDERERS = [
  {
    slug: "scalar",
    name: "Scalar",
    tag: "recomendado",
    blurb:
      "Referencia moderna con cliente HTTP integrado. Permite ejecutar las peticiones desde la propia pagina y genera fragmentos de codigo en varios lenguajes.",
  },
  {
    slug: "redoc",
    name: "Redoc",
    tag: "para leer",
    blurb:
      "Tres paneles, tipografia cuidada y navegacion por esquemas. Pensado para documentacion de referencia publicada, no para experimentar. No trae 'try it' en la version libre.",
  },
  {
    slug: "rapidoc",
    name: "RapiDoc",
    tag: "ligero",
    blurb:
      "Un unico web component configurable por atributos. El mas facil de incrustar dentro de otra pagina y el mas liviano de los cinco.",
  },
  {
    slug: "elements",
    name: "Stoplight Elements",
    tag: "con consola",
    blurb:
      "Web component de tres paneles con consola de pruebas. Del mismo ecosistema que Spectral, el linter de contratos.",
  },
  {
    slug: "swagger",
    name: "Swagger UI",
    tag: "el clasico",
    blurb:
      "La referencia historica: es lo que FastAPI monta por defecto en el Servicio de Usuarios. Universalmente reconocido, aunque su diseño muestra la edad.",
  },
];

export const docsIndexPage = () =>
  htmlResponse(`<!doctype html><html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Contrato del Servicio de Pedidos</title>
<style>
  :root{color-scheme:light dark}
  *{box-sizing:border-box}
  body{margin:0;padding:2.5rem 1.25rem 4rem;background:#f6f7f9;color:#111827;
    font:15px/1.6 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
  main{max-width:60rem;margin:0 auto}
  h1{font-size:1.7rem;margin:0 0 .35rem}
  .sub{color:#6b7280;margin:0 0 2rem}
  .callout{background:#fff;border-left:4px solid #2d6a4f;border-radius:6px;
    padding:1rem 1.15rem;margin:0 0 2rem;box-shadow:0 1px 2px rgba(0,0,0,.06)}
  .callout p{margin:0 0 .6rem}.callout p:last-child{margin:0}
  code{background:#e5e7eb;padding:.12em .4em;border-radius:4px;font-size:.88em}
  h2{font-size:1.05rem;margin:2.2rem 0 .9rem;text-transform:uppercase;
    letter-spacing:.06em;color:#6b7280}
  .grid{display:grid;gap:.9rem;grid-template-columns:repeat(auto-fit,minmax(16rem,1fr))}
  .card{display:block;background:#fff;border:1px solid #e5e7eb;border-radius:8px;
    padding:1.1rem;text-decoration:none;color:inherit;transition:.15s}
  .card:hover{border-color:#2d6a4f;transform:translateY(-2px);
    box-shadow:0 4px 14px rgba(0,0,0,.08)}
  .card h3{margin:0 0 .1rem;font-size:1.05rem}
  .tag{display:inline-block;background:#d1fae5;color:#065f46;border-radius:999px;
    padding:.1rem .55rem;font-size:.7rem;font-weight:700;text-transform:uppercase;
    letter-spacing:.04em;margin-bottom:.5rem}
  .card p{margin:0;color:#4b5563;font-size:.87rem;line-height:1.5}
  .files a{display:inline-block;margin-right:.9rem;color:#2d6a4f;font-weight:600}
  footer{margin-top:2.5rem;padding-top:1.2rem;border-top:1px solid #e5e7eb;
    color:#6b7280;font-size:.85rem}
  @media(prefers-color-scheme:dark){
    body{background:#0f1115;color:#e5e7eb}
    .callout,.card{background:#1a1d24;border-color:#2b303b}
    .card p{color:#9ca3af} code{background:#2b303b}
    footer{border-color:#2b303b}
  }
</style></head><body><main>

<h1>Contrato del Servicio de Pedidos</h1>
<p class="sub">OpenAPI 3.1 &middot; Taller de microservicios &middot; Lenguaje de Programaci&oacute;n Avanzado 2</p>

<div class="callout">
  <p><strong>Este contrato est&aacute; escrito a mano.</strong> No lo genera ning&uacute;n
  framework a partir del c&oacute;digo: vive en <code>openapi.yaml</code>, se versiona en git
  y el c&oacute;digo debe cumplirlo. La prueba <code>tests/openapi.test.ts</code> falla si
  ambos se desv&iacute;an.</p>
  <p>Es el contraste deliberado con el <strong>Servicio de Usuarios</strong>, donde FastAPI
  <em>genera</em> el spec desde el c&oacute;digo: ah&iacute; el c&oacute;digo manda y el contrato es un
  subproducto (<em>code first</em>). Aqu&iacute; manda el contrato (<em>design first</em>).</p>
</div>

<h2>Un mismo contrato, cinco renderizadores</h2>
<p style="margin:-.4rem 0 1.2rem;color:#6b7280">
  Las cinco p&aacute;ginas leen el mismo <code>/openapi.json</code>. Ninguna sabe nada del
  c&oacute;digo del servicio: esa independencia es justamente lo que hace valioso tener
  un contrato.
</p>

<div class="grid">
  ${RENDERERS.map(
    (r) => `<a class="card" href="/docs/${r.slug}">
    <span class="tag">${r.tag}</span>
    <h3>${r.name}</h3>
    <p>${r.blurb}</p>
  </a>`,
  ).join("\n  ")}
</div>

<h2>El contrato en crudo</h2>
<p class="files">
  <a href="/openapi.yaml">openapi.yaml</a>
  <a href="/openapi.json">openapi.json</a>
</p>
<p style="color:#6b7280;font-size:.87rem;margin-top:.4rem">
  El YAML es la fuente de verdad que se edita y se versiona; el JSON es la misma
  informaci&oacute;n en el formato que consumen los renderizadores y los generadores de
  clientes.
</p>

<footer>
  Servicio de Usuarios (FastAPI, <em>code first</em>):
  <a href="http://localhost:8001/docs" style="color:#2d6a4f">localhost:8001/docs</a>
  &middot; validaci&oacute;n del contrato: <code>make api-lint</code>
</footer>

</main></body></html>`);
