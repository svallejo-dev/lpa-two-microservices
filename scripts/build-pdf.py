#!/usr/bin/env python3
"""
Genera el documento de entrega del taller en formato APA 7 (trabajo de estudiante).

    python3 scripts/build-pdf.py [ruta/salida.html]

`make pdf` ejecuta la cadena completa: renderiza los diagramas, prepara las
fuentes, llama a este script y convierte el HTML en PDF con WeasyPrint.

Procedencia del contenido
-------------------------
- Tabla 1 y su interpretacion: docs/01-cuadro-comparativo.md
- Ensayo: docs/02-ensayo-microservicios.md (entre ensayo:inicio y ensayo:fin)
- Figuras 1 a 3: bloques Mermaid de docs/03-arquitectura.md
- Figura 4: metodo execute() de services/orders-service/src/application/create-order.ts
- Figuras 5 a 8: salidas reales capturadas en entrega/assets/ev-*.txt
Los textos que enlazan las secciones, los titulos y notas de tablas y figuras y
la lista de referencias se redactan aqui, porque pertenecen al documento APA.

Normas APA 7 aplicadas
----------------------
- Papel carta, margenes de 1 in y numero de pagina arriba a la derecha desde la
  portada. Sin encabezado corrido: no se exige en trabajos de estudiante.
- Times New Roman de 12 pt a doble espacio, alineado a la izquierda sin
  justificar ni dividir palabras, con sangria de 0.5 in en la primera linea.
- Portada de estudiante: titulo en negrita a tres lineas del margen superior,
  linea en blanco, autor, afiliacion, asignatura, docente y fecha.
- El texto empieza en la pagina 2 repitiendo el titulo, sin rotulo "Introduccion".
- Encabezados sin numerar: nivel 1 centrado en negrita, nivel 2 a la izquierda
  en negrita, en mayusculas de titulo. Cada nivel 1 empieza pagina, por
  solicitud expresa para esta entrega.
- Tablas y figuras numeradas por orden de primera mencion, con numero en
  negrita, titulo en cursiva y nota que empieza con "Nota." en cursiva. Tablas
  solo con filetes horizontales; la Tabla 1, por su anchura, en pagina horizontal.
- Referencias en pagina propia, en orden alfabetico y con sangria francesa.

Antes de escribir el HTML, `verificar()` comprueba que tablas y figuras esten
numeradas en orden y citadas en el texto antes de aparecer, y que cada cita
tenga su referencia y viceversa. Si algo falla, la generacion se detiene.
"""

import html
import pathlib
import re
import sys

import markdown

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"
ENTREGA = RAIZ / "entrega"
ASSETS = ENTREGA / "assets"
FUENTES = ENTREGA / ".fuentes"

REPO_URL = "https://github.com/svallejo-dev/lpa-two-microservices"

VIDEO_URL = "https://youtu.be/t6DTXp7V4aU"

TITULO = "Arquitectura Orientada a Microservicios"
ESTUDIANTE = "Sebastián Vallejo"
AFILIACION = "Ingeniería de Sistemas Mod. Virtual, Uniremington"
ASIGNATURA = "Lenguaje de Programación Avanzado 2"
DOCENTE = "Nixon Duarte Acosta"
FECHA = "2026"

REFERENCIAS = [
    ("Conway", "1968",
     "Conway, M. E. (1968). How do committees invent? <em>Datamation, 14</em>(4), 28–31."),
    ("Fowler", "2015",
     "Fowler, M. (2015, 3 de junio). MonolithFirst. <em>Martin Fowler</em>. "
     "{url:https://martinfowler.com/bliki/MonolithFirst.html}"),
    ("Kolny", "2023",
     "Kolny, M. (2023, 22 de marzo). Scaling up the Prime Video audio/video monitoring "
     "service and reducing costs by 90%. <em>Prime Video Tech</em>. "
     "{url:https://web.archive.org/web/20230323220106/https://www.primevideotech.com/"
     "video-streaming/scaling-up-the-prime-video-audio-video-monitoring-service-and-"
     "reducing-costs-by-90}"),
    ("Martin", "2017",
     "Martin, R. C. (2017). <em>Clean architecture: A craftsman’s guide to software "
     "structure and design</em>. Prentice Hall."),
    ("Mauro", "2015",
     "Mauro, T. (2015, 19 de febrero). Adopting microservices at Netflix: Lessons for "
     "architectural design. <em>NGINX Blog</em>. "
     "{url:https://web.archive.org/web/20160114045720/https://www.nginx.com/blog/"
     "microservices-at-netflix-architectural-best-practices/}"),
    ("Newman", "2021",
     "Newman, S. (2021). <em>Building microservices: Designing fine-grained systems</em> "
     "(2.ª ed.). O’Reilly Media."),
    ("Yegge", "2011",
     "Yegge, S. (2011, 12 de octubre). <em>Stevey’s Google platforms rant</em>. GitHub Gist. "
     "{url:https://gist.github.com/chitchcock/1281611}"),
]


def url(direccion: str, en_texto: bool = False) -> str:
    clase = "url-texto" if en_texto else "url"
    return f'<a class="{clase}" href="{direccion}">{direccion}</a>'


def con_urls(texto: str) -> str:
    return re.sub(r"\{url:([^}]+)\}", lambda m: url(m.group(1)), texto)


def inline(md: str) -> str:
    """Markdown en linea a HTML. APA no usa negrita para enfatizar: se elimina."""
    salida = markdown.markdown(" ".join(md.split()))
    salida = re.sub(r"^<p>(.*)</p>$", r"\1", salida, flags=re.S)
    return salida.replace("<strong>", "").replace("</strong>", "")


def celda(md: str) -> str:
    """Contenido de celda: permite partir rutas largas despues de cada barra."""
    return re.sub(r"<code>(.*?)</code>",
                  lambda m: "<code>" + m.group(1).replace("/", "/​") + "</code>",
                  inline(md))


def parrafo(contenido: str, sangria: bool = True) -> str:
    return f"<p>{contenido}</p>" if sangria else f'<p class="sin-sangria">{contenido}</p>'


def tabla(numero, titulo, encabezados, filas, nota, anchos=None, clase="", centradas=()):
    columnas = ""
    if anchos:
        columnas = "<colgroup>" + "".join(f'<col style="width:{a}">' for a in anchos) + "</colgroup>"
    cabecera = "".join(f"<th>{h}</th>" for h in encabezados)
    cuerpo = "".join(
        "<tr>" + "".join(f'<td class="centro">{c}</td>' if i in centradas else f"<td>{c}</td>"
                         for i, c in enumerate(fila)) + "</tr>"
        for fila in filas)
    return (f'<div class="tabla {clase}">'
            f'<p class="etiqueta">Tabla {numero}</p>'
            f'<p class="titulo-objeto">{titulo}</p>'
            f"<table>{columnas}<thead><tr>{cabecera}</tr></thead><tbody>{cuerpo}</tbody></table>"
            f'<p class="nota"><em>Nota.</em> {nota}</p>'
            "</div>")


def figura(numero, titulo, contenido, nota, clase=""):
    return (f'<div class="figura {clase}">'
            f'<p class="etiqueta">Figura {numero}</p>'
            f'<p class="titulo-objeto">{titulo}</p>'
            f'<div class="contenido-figura">{contenido}</div>'
            f'<p class="nota"><em>Nota.</em> {nota}</p>'
            "</div>")


def salida_terminal(nombre: str) -> str:
    texto = (ASSETS / nombre).read_text(encoding="utf-8").strip("\n")
    return f'<pre class="codigo">{html.escape(texto)}</pre>'


def filas_cuadro():
    filas = []
    for linea in (DOCS / "01-cuadro-comparativo.md").read_text(encoding="utf-8").splitlines():
        if re.match(r"^\|\s*\d+\s*\|", linea):
            _, criterio, monolito, micro, repo = [c.strip() for c in linea.strip().strip("|").split("|")]
            filas.append([celda(criterio), celda(monolito), celda(micro), celda(repo)])
    assert len(filas) == 10, f"se esperaban 10 criterios y hay {len(filas)}"
    return filas


def interpretacion_cuadro():
    texto = (DOCS / "01-cuadro-comparativo.md").read_text(encoding="utf-8")
    bloque = texto.split("## Lectura del cuadro", 1)[1]
    parrafos = [re.sub(r"^>\s*", "", " ".join(l.strip() for l in b.splitlines()))
                for b in bloque.split("\n\n") if b.strip()]
    unidos = []
    for par in parrafos:
        if unidos and unidos[-1].endswith(":"):
            unidos[-1] += " " + par[0].lower() + par[1:]
        else:
            unidos.append(par)
    return [inline(p) for p in unidos]


def parrafos_ensayo():
    texto = (DOCS / "02-ensayo-microservicios.md").read_text(encoding="utf-8")
    cuerpo = texto.split("<!-- ensayo:inicio -->")[1].split("<!-- ensayo:fin -->")[0]
    return [inline(b) for b in cuerpo.split("\n\n") if b.strip()]


def metodo_execute():
    ruta = RAIZ / "services/orders-service/src/application/create-order.ts"
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    inicio = next(i for i, l in enumerate(lineas) if "async execute(" in l)
    fin = next(i for i in range(inicio, len(lineas)) if lineas[i] == "  }")
    return "\n".join(l[2:] for l in lineas[inicio:fin + 1])


def fuentes_css():
    """Usa Times New Roman y Courier New reales si `make pdf` pudo copiarlas."""
    variantes = [
        ("Times New Roman", "TimesNewRoman-Regular", "normal", "normal"),
        ("Times New Roman", "TimesNewRoman-Bold", "bold", "normal"),
        ("Times New Roman", "TimesNewRoman-Italic", "normal", "italic"),
        ("Times New Roman", "TimesNewRoman-BoldItalic", "bold", "italic"),
        ("Courier New", "CourierNew-Regular", "normal", "normal"),
        ("Courier New", "CourierNew-Bold", "bold", "normal"),
    ]
    return "\n".join(
        f'@font-face {{ font-family: "{fam}"; src: url(".fuentes/{arch}.ttf"); '
        f"font-weight: {peso}; font-style: {estilo}; }}"
        for fam, arch, peso, estilo in variantes if (FUENTES / f"{arch}.ttf").exists())


CSS = """
@page {
  size: letter;
  margin: 1in;
  @top-right {
    content: counter(page);
    font-family: "Times New Roman", "Liberation Serif", serif;
    font-size: 12pt;
    vertical-align: middle;
  }
}
@page horizontal { size: letter landscape; }

html { font-size: 12pt; }
body {
  margin: 0;
  font-family: "Times New Roman", "Liberation Serif", serif;
  font-size: 12pt;
  line-height: 2;
  color: #000;
  text-align: left;
  hyphens: manual;
  orphans: 2;
  widows: 2;
}
p { margin: 0; text-indent: 0.5in; }
p.sin-sangria { text-indent: 0; }
h1, h2 { font-size: 12pt; line-height: 2; margin: 0; font-weight: bold;
         break-after: avoid; page-break-after: avoid; }
h1 { text-align: center; }
h2 { text-align: left; }
.nueva-pagina { break-before: page; page-break-before: always; }
a { color: #000; text-decoration: none; }
.url { word-break: break-all; }
.url-texto { white-space: nowrap; }
code { font-family: "Courier New", "Liberation Mono", monospace; font-size: 11pt; }

.portada { padding-top: 72pt; break-after: page; page-break-after: always; }
.portada p { text-indent: 0; text-align: center; }
.portada .titulo { font-weight: bold; }

.etiqueta { text-indent: 0; font-weight: bold; break-after: avoid; page-break-after: avoid; }
.titulo-objeto { text-indent: 0; font-style: italic; break-after: avoid; page-break-after: avoid; }
.nota { text-indent: 0; }
.compacta, .figura { break-inside: avoid; page-break-inside: avoid; }

table { width: 100%; table-layout: fixed; border-collapse: collapse; font-size: 11pt; line-height: 1.2;
        margin: 3pt 0 6pt; }
thead { display: table-header-group; }
th { font-weight: normal; text-align: center; vertical-align: bottom; padding: 4pt 5pt;
     border-top: 1pt solid #000; border-bottom: 0.75pt solid #000; }
th:first-child { text-align: left; }
td { text-align: left; vertical-align: top; padding: 4pt 5pt; }
td.centro { text-align: center; }
.puertos td code { font-size: 8pt; }
tbody tr:last-child td { border-bottom: 1pt solid #000; }
tr { break-inside: avoid; page-break-inside: avoid; }
td code { font-size: 8.5pt; overflow-wrap: break-word; }
.horizontal { page: horizontal; }
.horizontal table { font-size: 10.5pt; }

.contenido-figura { margin: 3pt 0 6pt; text-align: center; }
.contenido-figura img { max-width: 100%; }
.media .contenido-figura img { max-height: 4.6in; }
.alta .contenido-figura img { max-height: 6.3in; }
.baja .contenido-figura img { max-height: 3.2in; }
pre.codigo { font-family: "Courier New", "Liberation Mono", monospace; font-size: 8.5pt;
             line-height: 1.2; text-align: left; white-space: pre-wrap; overflow-wrap: break-word; margin: 0;
             padding: 5pt 7pt; border: 0.5pt solid #808080; }

.espacio-enlace { display: inline-block; width: 5in; border-bottom: 0.75pt solid #000; }
.referencias p { text-indent: -0.5in; padding-left: 0.5in; }
"""


def portada():
    return ('<div class="portada">'
            f'<p class="titulo">{TITULO}</p><p>&nbsp;</p>'
            f"<p>{ESTUDIANTE}</p><p>{AFILIACION}</p><p>{ASIGNATURA}</p>"
            f"<p>{DOCENTE}</p><p>{FECHA}</p>"
            "</div>")


def introduccion():
    return "".join([
        f"<h1>{TITULO}</h1>",
        parrafo("El presente trabajo aborda los fundamentos de la arquitectura orientada a "
                "microservicios, sus diferencias frente a la arquitectura monolítica y su "
                "relevancia en la construcción de aplicaciones modernas. Su propósito es "
                "reconocer los principios básicos de este estilo arquitectónico, identificar sus "
                "ventajas, desventajas y escenarios de aplicación, y experimentar con un ejemplo "
                "práctico de comunicación entre servicios."),
        parrafo("Para la actividad práctica se construyeron dos microservicios independientes: un "
                "Servicio de Usuarios, desarrollado en Python 3.13 con FastAPI, y un Servicio de "
                "Pedidos, desarrollado en TypeScript sobre Bun 1.4. Cada servicio cuenta con su "
                "propia base de datos PostgreSQL, ambos se comunican mediante una API REST y el "
                "conjunto se ejecuta con Docker Compose."),
        parrafo("El documento se organiza en cinco secciones, cada una iniciada en una página "
                "nueva. La primera presenta el cuadro comparativo entre la arquitectura monolítica "
                "y la de microservicios. La segunda contiene el ensayo breve sobre las razones por "
                "las que las grandes empresas tecnológicas adoptan microservicios, que ocupa una "
                "única página. La tercera documenta el diseño mediante diagramas de arquitectura; "
                "la cuarta reúne la evidencia del código y de su ejecución, y la quinta incluye el "
                "enlace al video de sustentación. Al final se presenta la lista de referencias."),
    ])


def cuadro():
    return "".join([
        '<h1 class="nueva-pagina">Cuadro Comparativo</h1>',
        parrafo("La Tabla 1 compara la arquitectura monolítica y la arquitectura orientada a "
                "microservicios a partir de diez criterios, el doble del mínimo solicitado. Además "
                "de describir cada enfoque, la última columna vincula cada criterio con un archivo "
                "o comando del repositorio del ejercicio práctico, de modo que la diferencia pueda "
                "verificarse al ejecutar el código."),
        "<h2>Interpretación de la Comparación</h2>",
        *[parrafo(p) for p in interpretacion_cuadro()],
        '<div class="horizontal">',
        tabla(1, "Comparación Entre la Arquitectura Monolítica y la Arquitectura de Microservicios",
              ["Criterio", "Arquitectura monolítica", "Arquitectura de microservicios",
               "Evidencia en el repositorio"],
              filas_cuadro(),
              "La última columna remite a archivos y comandos del repositorio del ejercicio "
              "práctico. Elaboración propia con base en Newman (2021) y Fowler (2015).",
              anchos=["15%", "25%", "25%", "35%"]),
        "</div>",
    ])


def ensayo():
    return "".join([
        '<h1 class="nueva-pagina">Ensayo Breve: ¿Por Qué las Grandes Empresas Tecnológicas '
        "Adoptan Microservicios?</h1>",
        '<div class="ensayo">', *[parrafo(p) for p in parrafos_ensayo()], "</div>",
    ])


def diagrama():
    return "".join([
        '<h1 class="nueva-pagina">Diagrama de Arquitectura</h1>',
        parrafo("El diseño del ejercicio práctico se documenta mediante tres diagramas "
                "complementarios. La Figura 1 muestra los contenedores que se ejecutan y las redes "
                "que los conectan; la Figura 2 describe la secuencia de la única operación que "
                "requiere comunicación entre servicios, y la Figura 3 presenta la organización "
                "interna de cada servicio de acuerdo con los principios de la arquitectura limpia "
                "(Martin, 2017)."),
        "<h2>Diagrama de Contenedores</h2>",
        parrafo("El sistema se compone de cuatro contenedores distribuidos en tres redes de Docker. "
                "Cada microservicio accede únicamente a su propia base de datos, y la red compartida "
                "<code>services</code> es el único canal entre ambos, de modo que la comunicación "
                "ocurre exclusivamente por HTTP. Como se observa en la Figura 1, el Servicio de "
                "Pedidos no tiene ruta de red hacia la base de datos del Servicio de Usuarios: el "
                "aislamiento de los datos se impone en la infraestructura y no depende de la "
                "disciplina del código."),
        figura(1, "Contenedores, Redes y Dependencias del Sistema",
               '<img src="assets/d1.png" alt="Diagrama de contenedores del sistema">',
               "La línea continua roja representa la única dependencia entre microservicios, la "
               "consulta <code>GET /users/{id}</code>. La línea discontinua terminada en cruz "
               "representa una conexión inexistente: <code>orders-service</code> no pertenece a la "
               "red <code>users-data</code>.",
               clase="media"),
        "<h2>Diagrama de Secuencia de la Creación de un Pedido</h2>",
        parrafo("La Figura 2 detalla la operación <code>POST /orders</code>, en la que el Servicio "
                "de Pedidos consulta al Servicio de Usuarios antes de registrar un pedido. La "
                "secuencia contempla tres resultados posibles: el usuario existe, el usuario no "
                "existe o el Servicio de Usuarios no responde."),
        figura(2, "Secuencia de la Operación de Creación de un Pedido",
               '<img src="assets/d2.png" alt="Diagrama de secuencia de POST /orders">',
               "El Servicio de Pedidos valida localmente el pedido antes de consultar al Servicio de "
               "Usuarios, con un tiempo máximo de espera de 2 s y un único reintento. Si no obtiene "
               "respuesta, no persiste el pedido.",
               clase="alta"),
        parrafo("La distinción entre los dos últimos resultados constituye la decisión de diseño "
                "central del servicio y se resume en la Tabla 2. Cuando el Servicio de Usuarios "
                "responde con el código 404 existe certeza de que el usuario no está registrado; "
                "cuando no responde, no es posible saberlo. Tratar ambos casos como un mismo error "
                "provocaría que el sistema rechazara pedidos de usuarios válidos cada vez que la red "
                "fallara, atribuyendo al cliente un fallo propio."),
        tabla(2, "Tratamiento de las Respuestas del Servicio de Usuarios",
              ["Situación", "Conocimiento del sistema", "Error de dominio", "Código HTTP",
               "Acción del cliente"],
              [["El Servicio de Usuarios responde 404", "El usuario no existe",
                "<code>UnknownUserError</code>", "422", "Corregir el identificador del usuario"],
               ["El Servicio de Usuarios no responde", "Se desconoce si el usuario existe",
                "<code>UserDirectoryUnavailableError</code>", "503",
                "Reintentar la operación más tarde"]],
              "Los errores de dominio se definen en "
              "<code>services/orders-service/src/domain/errors.ts</code>.",
              anchos=["19%", "17%", "36%", "10%", "18%"], clase="compacta", centradas=(3,)),
        "<h2>Capas de la Arquitectura Limpia</h2>",
        parrafo("Ambos servicios comparten la misma organización interna en cuatro capas, aunque "
                "estén escritos en lenguajes distintos, como muestra la Figura 3. La regla de "
                "dependencias establece que estas apuntan siempre hacia el dominio: la capa de "
                "infraestructura implementa las interfaces que el dominio declara, y nunca a la "
                "inversa (Martin, 2017)."),
        figura(3, "Capas de la Arquitectura Limpia y Regla de Dependencias",
               '<img src="assets/d3.png" alt="Diagrama de capas de la arquitectura limpia">',
               "La flecha discontinua indica que la infraestructura implementa los puertos "
               "declarados por el dominio, es decir, la inversión de dependencias.",
               clase="baja"),
        parrafo("Un puerto es una interfaz declarada por el dominio, y un adaptador es su "
                "implementación concreta, que se elige al iniciar el servicio. La Tabla 3 relaciona "
                "los puertos de cada servicio con sus adaptadores. Disponer de adaptadores de prueba "
                "permite verificar el dominio y los casos de uso sin base de datos ni red, incluido "
                "el escenario en que el Servicio de Usuarios no está disponible."),
        tabla(3, "Puertos y Adaptadores de los Microservicios",
              ["Servicio", "Puerto", "Adaptador de producción", "Adaptadores de prueba"],
              [["Usuarios", "<code>UserRepository</code>", "<code>PostgresUserRepository</code>",
                "<code>InMemoryUserRepository</code>"],
               ["Pedidos", "<code>OrderRepository</code>", "<code>PostgresOrderRepository</code>",
                "<code>InMemoryOrderRepository</code>"],
               ["Pedidos", "<code>UserDirectory</code>", "<code>HttpUserDirectory</code>",
                "<code>FakeUserDirectory</code>, <code>EmptyUserDirectory</code>, "
                "<code>BrokenUserDirectory</code>"]],
              "Los adaptadores de prueba se encuentran en la carpeta <code>tests/</code> de cada "
              "servicio.",
              anchos=["12%", "19%", "27%", "42%"], clase="compacta puertos"),
    ])


def evidencia():
    contenido_repo = [
        ["`services/users-service/`", "Servicio de Usuarios: Python 3.13, FastAPI y PostgreSQL"],
        ["`services/orders-service/`", "Servicio de Pedidos: TypeScript, Bun 1.4 y PostgreSQL"],
        ["`services/orders-service/openapi.yaml`",
         "Contrato OpenAPI 3.1 del Servicio de Pedidos, redactado manualmente y verificado por pruebas"],
        ["`compose.yaml`", "Definición de los cuatro contenedores, las tres redes y los dos volúmenes"],
        ["`Makefile`", "Comandos para levantar, probar y demostrar el sistema"],
        ["`docs/`", "Cuadro comparativo, ensayo, arquitectura y contrato de la API"],
        ["`scripts/`", "Guiones de demostración y generador de este documento"],
        ["`entrega/`", "Este documento en formato PDF"],
    ]
    return "".join([
        '<h1 class="nueva-pagina">Evidencia del Código</h1>',
        parrafo("El código fuente completo del ejercicio práctico, junto con su historial de "
                "commits, está publicado en un repositorio público de GitHub disponible en "
                + url(REPO_URL, en_texto=True) + ". La Tabla 4 describe su contenido. El único requisito para "
                "ejecutarlo es Docker: los comandos <code>make up</code>, <code>make test</code> y "
                "<code>make demo</code> levantan el sistema, ejecutan las pruebas automatizadas y "
                "recorren el flujo completo, respectivamente."),
        tabla(4, "Contenido del Repositorio", ["Ruta", "Contenido"],
              [[celda(r), celda(c)] for r, c in contenido_repo],
              "Las rutas son relativas a la raíz del repositorio.",
              anchos=["40%", "60%"], clase="compacta"),
        "<h2>Comunicación Entre los Servicios</h2>",
        parrafo("La Figura 4 presenta el caso de uso <code>CreateOrder</code>, el único punto en el "
                "que un microservicio requiere información que pertenece al otro. El caso de uso "
                "depende de la interfaz <code>UserDirectory</code> y no de un cliente HTTP concreto, "
                "lo que permite probarlo sin red."),
        figura(4, "Caso de Uso de Creación de un Pedido",
               f'<pre class="codigo">{html.escape(metodo_execute())}</pre>',
               "Fragmento del archivo "
               "<code>services/orders-service/src/application/create-order.ts</code>. El método "
               "ejecuta tres pasos: valida el pedido localmente, de modo que uno mal formado se "
               "rechaza sin gastar una llamada de red; consulta al Servicio de Usuarios a través "
               "del puerto <code>UserDirectory</code>, que lanza una excepción si no obtiene "
               "respuesta; y solo entonces lo persiste."),
        "<h2>Resultados de la Ejecución</h2>",
        parrafo("Las salidas que se presentan a continuación se capturaron del sistema en "
                "funcionamiento. La Figura 5 muestra los cuatro contenedores en estado saludable y "
                "la Figura 6, el resultado de las pruebas automatizadas. La Figura 7 recorre el flujo "
                "completo entre ambos microservicios, y la Figura 8 muestra el comportamiento del "
                "sistema cuando el Servicio de Usuarios deja de responder."),
        figura(5, "Estado de los Contenedores en Ejecución", salida_terminal("ev-ps.txt"),
               "Salida del comando <code>docker compose ps</code>."),
        figura(6, "Resultado de las Pruebas Automatizadas", salida_terminal("ev-test.txt"),
               "Salida del comando <code>make test</code>. Cada punto de la segunda línea "
               "corresponde a una prueba superada del Servicio de Usuarios, 16 en total; el Servicio "
               "de Pedidos reporta 21 pruebas superadas. Ninguna prueba requiere base de datos ni red."),
        figura(7, "Flujo Completo Entre los Dos Microservicios", salida_terminal("ev-demo.txt"),
               "Salida del comando <code>make demo</code>. Se observan las respuestas 201 al crear el "
               "pedido, 422 ante un usuario inexistente y 400 ante un pedido sin líneas."),
        figura(8, "Comportamiento del Sistema con el Servicio de Usuarios Detenido",
               salida_terminal("ev-fallo.txt"),
               "Salida del comando <code>make demo-fallo</code>. La creación del pedido responde 503 "
               "sin persistir datos, la consulta de pedidos continúa respondiendo 200 y, al "
               "restaurar el Servicio de Usuarios, la misma operación vuelve a responder 201."),
    ])


def video():
    enlace = url(VIDEO_URL, en_texto=True) if VIDEO_URL else '<span class="espacio-enlace">&nbsp;</span>'
    return "".join([
        '<h1 class="nueva-pagina">Video de Sustentación</h1>',
        parrafo("La sustentación recorre el sistema en funcionamiento siguiendo el mismo guion de "
                "los comandos <code>make demo</code> y <code>make demo-fallo</code>: la creación de "
                "un usuario, la creación de un pedido con la validación entre servicios, los errores "
                "de negocio y el comportamiento del sistema cuando el Servicio de Usuarios deja de "
                "responder. La grabación está disponible en el siguiente enlace:"),
        parrafo(enlace, sangria=False),
    ])


def referencias():
    return ('<h1 class="nueva-pagina">Referencias</h1><div class="referencias">'
            + "".join(f"<p>{con_urls(r)}</p>" for _, _, r in REFERENCIAS) + "</div>")


def verificar(documento: str) -> list:
    problemas = []
    etiqueta = re.compile(r'<p class="etiqueta">[^<]*</p>')

    for tipo in ("Tabla", "Figura"):
        encontradas = [(m.start(), int(m.group(1)))
                       for m in re.finditer(rf'<p class="etiqueta">{tipo} (\d+)</p>', documento)]
        numeros = [n for _, n in encontradas]
        if numeros != list(range(1, len(numeros) + 1)):
            problemas.append(f"{tipo}s numeradas fuera de orden: {numeros}")
        for posicion, n in encontradas:
            texto_previo = etiqueta.sub(" ", documento[:posicion])
            if not re.search(rf"\b{tipo} {n}\b", texto_previo):
                problemas.append(f"{tipo} {n} aparece sin mencionarse antes en el texto")

    cuerpo = re.sub(r"<[^>]+>", " ", documento.split('<div class="referencias">')[0])
    citadas = (set(re.findall(r"\(([A-ZÁÉÍÓÚ][a-záéíóúñ]+), (\d{4})\)", cuerpo))
               | set(re.findall(r"\b([A-ZÁÉÍÓÚ][a-záéíóúñ]+) \((\d{4})\)", cuerpo)))
    listadas = {(apellido, anio) for apellido, anio, _ in REFERENCIAS}
    problemas += [f"cita sin referencia: {a} ({y})" for a, y in sorted(citadas - listadas)]
    problemas += [f"referencia sin cita: {a} ({y})" for a, y in sorted(listadas - citadas)]

    orden = [apellido for apellido, _, _ in REFERENCIAS]
    if orden != sorted(orden):
        problemas.append(f"referencias fuera de orden alfabetico: {orden}")
    return problemas


def main():
    salida = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ENTREGA / "entrega.html"
    documento = (
        '<!doctype html><html lang="es"><head><meta charset="utf-8">'
        f"<title>{TITULO}</title><style>{fuentes_css()}\n{CSS}</style></head><body>"
        + portada() + introduccion() + cuadro() + ensayo() + diagrama()
        + evidencia() + video() + referencias()
        + "</body></html>"
    )

    problemas = verificar(documento)
    if problemas:
        print("La verificacion APA encontro problemas:", *problemas, sep="\n  - ")
        sys.exit(1)

    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(documento, encoding="utf-8")
    palabras = sum(len(re.sub(r"<[^>]+>", " ", p).split()) for p in parrafos_ensayo())
    fuentes = "Times New Roman" if fuentes_css() else "Liberation Serif (sustituto metrico)"
    print(f"HTML generado: {salida}")
    print(f"  Verificacion APA: tablas, figuras, citas y referencias en orden")
    print(f"  Ensayo: {palabras} palabras | Fuente: {fuentes}")


if __name__ == "__main__":
    main()
