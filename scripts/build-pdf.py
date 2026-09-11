#!/usr/bin/env python3
"""
Genera el PDF de entrega del taller a partir de los documentos del repositorio.

El PDF NO se escribe a mano: se compone desde `docs/*.md`, de modo que el
entregable y el repositorio no puedan contradecirse. Se ejecuta con `make pdf`.

Cadena: Markdown -> HTML (python-markdown) -> PDF (WeasyPrint, que soporta
CSS Paged Media de verdad: numeracion de paginas, encabezados corridos y
control de saltos).
"""

import pathlib
import re
import sys

import markdown

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"
ASSETS = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "entrega" / "assets"

REPO_URL = "https://github.com/svallejo-dev/lpa-two-microservices"

# --- Datos de la portada (normas APA 7, formato de trabajo de estudiante) ---
TITULO = "Arquitectura Orientada a Microservicios"
ESTUDIANTE = "Sebastián Vallejo"
PROGRAMA = "Ingeniería de Sistemas Mod. Virtual"
UNIVERSIDAD = "Uniremington"
MATERIA = "Lenguaje de Programación Avanzado 2"
DOCENTE = "Nixon Duarte Acosta"
ANIO = "2026"

# Marcador que el estudiante reemplaza cuando publique la sustentación.
VIDEO_URL = ""


def a_html(texto: str) -> str:
    return markdown.markdown(
        texto,
        extensions=["tables", "fenced_code", "attr_list", "sane_lists"],
    )


def cuerpo_markdown(ruta: pathlib.Path, desde: str) -> str:
    """Devuelve el contenido de un documento a partir de un encabezado dado."""
    texto = ruta.read_text(encoding="utf-8")
    indice = texto.index(desde)
    return texto[indice:]


def diagramas_a_imagenes(texto: str) -> str:
    """Sustituye cada bloque ```mermaid por la imagen ya renderizada."""
    contador = {"n": 0}

    def reemplazo(_match: re.Match) -> str:
        contador["n"] += 1
        return (
            f'<img class="diagrama" src="{ASSETS}/d{contador["n"]}.png" '
            f'alt="Diagrama {contador["n"]}">'
        )

    return re.sub(r"```mermaid\n.*?```", reemplazo, texto, flags=re.S)


def bloque_evidencia(nombre: str, titulo: str) -> str:
    ruta = ASSETS / nombre
    contenido = ruta.read_text(encoding="utf-8").rstrip() if ruta.exists() else "(sin datos)"
    return (
        f'<figure class="terminal"><figcaption>{titulo}</figcaption>'
        f"<pre>{contenido}</pre></figure>"
    )


CSS = """
@page {
  size: A4;
  margin: 20mm 18mm 20mm 18mm;
  @top-left  { content: string(seccion); font: 7.5pt "DejaVu Sans"; color: #8a8f98; }
  @top-right { content: counter(page); font: 9pt "Liberation Serif", serif; color: #4b5563; }
}

/* Portada segun APA 7: margenes de una pulgada, numero de pagina arriba a la
   derecha y nada mas en el encabezado. */
@page portada {
  margin: 2.54cm;
  @top-left { content: none }
  @top-right { content: counter(page); font: 12pt "Liberation Serif", serif; color: #000; }
}

html { font-size: 10pt; }
body { font-family: "Liberation Serif", "Times New Roman", serif; color: #1a1d21;
       line-height: 1.55; text-align: justify; hyphens: auto; }

h1, h2, h3, h4 { font-family: "DejaVu Sans", sans-serif; color: #14312a;
                 text-align: left; hyphens: none; }
h1 { font-size: 15pt; margin: 0 0 .2em; string-set: seccion content(); }
h2 { font-size: 11.5pt; margin: 1.5em 0 .5em; }
h3 { font-size: 10pt; margin: 1.2em 0 .4em; }
p  { margin: 0 0 .65em; }
a  { color: #14312a; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: .82em;
       background: #eef0f2; padding: .08em .3em; border-radius: 2px; }
strong { color: #0d211c; }

/* --- Portada (APA 7) --------------------------------------------------- */
/* Todo centrado y a doble espacio, en Times New Roman de 12 pt. El titulo va
   en negrita a unas tres lineas por debajo del margen superior; el resto de
   los datos, sin negrita, en el orden que fija la norma: autor, afiliacion,
   asignatura, docente y fecha. */
.portada { page: portada; page-break-after: always;
           font-family: "Liberation Serif", "Times New Roman", serif;
           font-size: 12pt; line-height: 2; text-align: center;
           hyphens: none; color: #000; padding-top: 2.54cm; }
.portada p { margin: 0; text-align: center; }
.portada .titulo { font-weight: bold; }
.portada .vacio { height: 24pt; }

/* --- Indice ------------------------------------------------------------ */
.indice { page-break-after: always; }
.indice ol { font-family: "DejaVu Sans", sans-serif; font-size: 10.5pt;
             list-style: none; padding: 0; counter-reset: sec; }
.indice li { counter-increment: sec; padding: 2.4mm 0;
             border-bottom: .5pt dotted #d7dade; }
.indice li::before { content: counter(sec) ". "; color: #14312a; font-weight: bold; }
.indice li span { color: #6b7280; font-size: 8.5pt; display: block;
                  margin-left: 5.5mm; font-family: "Liberation Serif", serif; }

/* --- Secciones --------------------------------------------------------- */
section { page-break-before: always; }
section.continua { page-break-before: auto; }
.rotulo { font-family: "DejaVu Sans", sans-serif; font-size: 7.5pt;
          letter-spacing: .12em; text-transform: uppercase; color: #8a8f98;
          margin-bottom: 1mm; }

/* --- Tablas ------------------------------------------------------------ */
table { width: 100%; border-collapse: collapse; margin: .8em 0 1em;
        font-size: 8.2pt; text-align: left; hyphens: none; }
thead { display: table-header-group; }
th { background: #14312a; color: #fff; font-family: "DejaVu Sans", sans-serif;
     font-size: 7.4pt; text-transform: uppercase; letter-spacing: .04em;
     padding: 2mm 1.8mm; vertical-align: bottom; }
td { padding: 1.8mm; border-bottom: .5pt solid #dfe2e6; vertical-align: top;
     text-align: left; }
tr { page-break-inside: avoid; }
tbody tr:nth-child(even) { background: #f6f7f8; }
table code { font-size: .78em; background: #e4e7ea; }

/* El cuadro comparativo tiene 5 columnas: necesita mas aire. */
.comparativo table { font-size: 7.4pt; }
.comparativo td, .comparativo th { padding: 1.5mm 1.3mm; }
.comparativo td:first-child { text-align: center; color: #8a8f98; }

/* --- Diagramas --------------------------------------------------------- */
.diagrama { display: block; max-width: 100%; margin: 4mm auto 2mm;
            page-break-inside: avoid; }
.diagrama + p em { display: block; text-align: center; }

/* --- Bloques de codigo y terminal --------------------------------------- */
pre { font-family: "DejaVu Sans Mono", monospace; font-size: 7.4pt;
      line-height: 1.4; background: #f6f7f8; border: .5pt solid #dfe2e6;
      border-left: 2.5pt solid #14312a; padding: 2.5mm 3mm; margin: .5em 0 1em;
      white-space: pre-wrap; word-wrap: break-word; text-align: left;
      page-break-inside: avoid; }
pre code { background: none; padding: 0; font-size: 1em; }

.terminal { margin: .6em 0 1.1em; page-break-inside: avoid; }
.terminal figcaption { font-family: "DejaVu Sans", sans-serif; font-size: 7.6pt;
                       color: #6b7280; margin-bottom: 1mm; }
.terminal pre { background: #12151a; color: #dfe3e8; border: none;
                border-left: 2.5pt solid #2d6a4f; }

/* --- Avisos ------------------------------------------------------------ */
.nota { background: #f0f6f3; border-left: 2.5pt solid #2d6a4f;
        padding: 3mm 4mm; margin: 1em 0; font-size: 9.2pt; }
.nota p:last-child { margin-bottom: 0; }
.pendiente { background: #fff8e6; border: .5pt dashed #b4881f;
             border-left: 2.5pt solid #b4881f; padding: 4mm 5mm; margin: 1em 0; }
.enlace { font-family: "DejaVu Sans Mono", monospace; font-size: 9.5pt;
          word-break: break-all; }
blockquote { margin: 1em 0; padding-left: 4mm; border-left: 2pt solid #cfd4d9;
             color: #3f4650; font-style: italic; }
ul, ol { margin: 0 0 .7em; padding-left: 5mm; }
li { margin-bottom: .25em; }
hr { border: none; border-top: .5pt solid #dfe2e6; margin: 1.2em 0; }
"""


# --- Seccion 1: cuadro comparativo ----------------------------------------
cuadro = a_html(cuerpo_markdown(DOCS / "01-cuadro-comparativo.md", "| # | Criterio"))

# --- Seccion 2: ensayo -----------------------------------------------------
ensayo_md = cuerpo_markdown(DOCS / "02-ensayo-microservicios.md", "Cuando Amazon")
ensayo_md = ensayo_md.replace("### Referencias", "## Referencias")
ensayo = a_html(ensayo_md)

# --- Seccion 3: diagramas --------------------------------------------------
arq_md = (DOCS / "03-arquitectura.md").read_text(encoding="utf-8")
inicio = arq_md.index("## 1. Diagrama de contenedores")
fin = arq_md.index("## 4. Decisiones de diseño")
arq_md = arq_md[inicio:fin]
# El bloque de comprobacion por consola sobra en un PDF.
arq_md = re.sub(r"Se puede comprobar con el sistema levantado:\n\n```bash.*?```\n", "", arq_md, flags=re.S)
arq_md = re.sub(r"```bash\n\$ make test.*?```\n", "", arq_md, flags=re.S)
arquitectura = diagramas_a_imagenes(arq_md)
arquitectura = a_html(arquitectura)

# --- Seccion 4: evidencia del codigo --------------------------------------
evidencia = f"""
<p class="rotulo">Entregable 3</p>
<h1>Evidencia del código</h1>

<p>El código completo, con su historial de commits, está publicado en un
repositorio público de GitHub:</p>

<div class="nota">
  <p class="enlace"><strong>{REPO_URL}</strong></p>
  <p>Se levanta con tres comandos, y el único requisito es Docker:
  <code>make doctor</code>, <code>make up</code>, <code>make demo</code>.</p>
</div>

<h2>Qué contiene</h2>

<table>
<thead><tr><th style="width:34%">Ruta</th><th>Contenido</th></tr></thead>
<tbody>
<tr><td><code>services/users-service/</code></td><td>Servicio de Usuarios — Python 3.13 + FastAPI + PostgreSQL</td></tr>
<tr><td><code>services/orders-service/</code></td><td>Servicio de Pedidos — TypeScript + Bun 1.4 + PostgreSQL</td></tr>
<tr><td><code>services/orders-service/openapi.yaml</code></td><td>Contrato OpenAPI 3.1 escrito a mano (<em>API Design First</em>)</td></tr>
<tr><td><code>compose.yaml</code></td><td>Cinco contenedores, tres redes, dos volúmenes</td></tr>
<tr><td><code>Makefile</code></td><td>Punto de entrada único: levantar, probar, demostrar</td></tr>
<tr><td><code>docs/</code></td><td>Cuadro comparativo, ensayo, arquitectura y contrato</td></tr>
<tr><td><code>scripts/</code></td><td><code>demo.sh</code> y <code>demo-fallo.sh</code> para la sustentación</td></tr>
</tbody></table>

<h2>Ambos servicios comparten el mismo diseño interno</h2>

<p>Las cuatro capas son idénticas en los dos microservicios, aunque uno esté
escrito en Python y el otro en TypeScript. El contraste entre ellos es de
tecnología, no de arquitectura:</p>

<pre><code>src/&lt;servicio&gt;/
├── domain/           entidades, invariantes y PUERTOS (cero dependencias externas)
├── application/      casos de uso; orquestan el dominio a través de los puertos
├── infrastructure/   ADAPTADORES: PostgreSQL, cliente HTTP, configuración
└── interfaces/http/  rutas, DTOs y traducción de errores de dominio a HTTP</code></pre>

<h2>El punto de comunicación entre los dos servicios</h2>

<p>Este es el caso de uso donde un microservicio necesita algo que otro posee.
Depende del <em>puerto</em> <code>UserDirectory</code>, no de <code>fetch</code>
ni de una URL: por eso puede probarse sin red.</p>

<pre><code>async execute(command: CreateOrderCommand): Promise&lt;Order&gt; {{
  // 1. Validación LOCAL primero. Si el pedido está mal formado, se rechaza
  //    sin gastar una llamada de red al otro servicio.
  const order = Order.place(command.userId, command.items);

  // 2. Validación REMOTA. Como las bases de datos están separadas, no existe
  //    una foreign key que garantice que el usuario existe: hay que
  //    preguntarlo. Si el directorio no responde, este `await` lanza
  //    UserDirectoryUnavailableError y el pedido NO se persiste.
  const user = await this.users.findById(order.userId);
  if (user === null) {{
    throw new UnknownUserError(order.userId);
  }}

  // 3. Persistencia. Solo se llega aquí con un usuario confirmado.
  await this.orders.add(order);
  return order;
}}</code></pre>

<h2>Evidencia de ejecución</h2>

<p>Las siguientes salidas se capturaron del sistema en funcionamiento, no
están transcritas a mano.</p>

{bloque_evidencia("ev-ps.txt", "make up — cinco contenedores, todos saludables")}

{bloque_evidencia("ev-test.txt", "make test — 37 pruebas de dominio, casos de uso y contrato, sin base de datos ni red")}

{bloque_evidencia("ev-demo.txt", "make demo — flujo completo entre los dos microservicios")}

{bloque_evidencia("ev-fallo.txt", "make demo-fallo — comportamiento con el Servicio de Usuarios caído")}
"""

# --- Seccion 5: video ------------------------------------------------------
if VIDEO_URL:
    bloque_video = (
        f'<div class="nota"><p class="enlace"><strong>{VIDEO_URL}</strong></p></div>'
    )
else:
    bloque_video = """
<div class="pendiente">
  <p><strong>Enlace del video de sustentación</strong></p>
  <p class="enlace" style="color:#8a8f98">
    ______________________________________________________________
  </p>
  <p style="font-size:8.5pt;color:#6b7280;margin-top:3mm">
    Para fijarlo de forma definitiva, escriba la URL en la constante
    <code>VIDEO_URL</code> de <code>scripts/build-pdf.py</code> y vuelva a
    ejecutar <code>make pdf</code>.
  </p>
</div>"""

video = f"""
<p class="rotulo">Entregable 5</p>
<h1>Video de sustentación</h1>

<p>La sustentación recorre el sistema en funcionamiento siguiendo el mismo
guion de <code>make demo</code> y <code>make demo-fallo</code>: creación de un
usuario, creación de un pedido con la validación entre servicios, los errores
de negocio, y el comportamiento del sistema cuando el Servicio de Usuarios se
cae.</p>

{bloque_video}
"""


# --- Ensamblado ------------------------------------------------------------
HTML = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<title>Taller de microservicios — {MATERIA}</title>
<style>{CSS}</style></head><body>

<div class="portada">
  <p class="titulo">{TITULO}</p>
  <p class="vacio">&nbsp;</p>
  <p>{ESTUDIANTE}</p>
  <p>{PROGRAMA}, {UNIVERSIDAD}</p>
  <p>{MATERIA}</p>
  <p>{DOCENTE}</p>
  <p>{ANIO}</p>
</div>

<div class="indice">
  <p class="rotulo">Contenido</p>
  <h1>Índice</h1>
  <ol>
    <li>Cuadro comparativo: monolito frente a microservicios
        <span>Diez criterios, cada uno anclado a un archivo verificable del repositorio</span></li>
    <li>Ensayo breve: por qué las grandes empresas adoptan microservicios
        <span>El argumento organizativo, su costo real y la contratendencia</span></li>
    <li>Diagrama de arquitectura
        <span>Contenedores, secuencia de la comunicación entre servicios y capas internas</span></li>
    <li>Evidencia del código
        <span>Repositorio público, estructura y salidas capturadas del sistema en ejecución</span></li>
    <li>Video de sustentación
        <span>Enlace a la grabación</span></li>
  </ol>
</div>

<section class="comparativo">
  <p class="rotulo">Entregable 1</p>
  <h1>Cuadro comparativo</h1>
  <p>Comparación entre la arquitectura monolítica y la orientada a
  microservicios. Se solicitaban cinco criterios como mínimo; se desarrollan
  diez. La última columna no es decorativa: ancla cada criterio a un archivo
  concreto del repositorio, donde la diferencia puede verificarse ejecutando
  el código.</p>
  {cuadro}
</section>

<section>
  <p class="rotulo">Entregable 2</p>
  <h1>Ensayo breve</h1>
  <h2 style="margin-top:.3em;color:#4b5563;font-size:11pt">¿Por qué las grandes
  empresas tecnológicas adoptan microservicios?</h2>
  {ensayo}
</section>

<section>
  <p class="rotulo">Entregable 4</p>
  <h1>Diagrama de arquitectura</h1>
  <p>Los diagramas están escritos en Mermaid dentro del repositorio, de modo
  que se versionan junto al código en lugar de vivir como imágenes sueltas.</p>
  {arquitectura}
</section>

<section>{evidencia}</section>

<section>{video}</section>

</body></html>"""

destino = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / "entrega" / "entrega.html"
destino.parent.mkdir(parents=True, exist_ok=True)
destino.write_text(HTML, encoding="utf-8")
print(f"HTML generado: {destino}  ({len(HTML):,} bytes)")
