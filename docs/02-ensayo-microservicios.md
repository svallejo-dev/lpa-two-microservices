# ¿Por qué las grandes empresas tecnológicas adoptan microservicios?

**Asignatura:** Lenguaje de Programación Avanzado 2
**Actividad:** Investigación teórica — ensayo breve

---

Cuando Amazon, Netflix o Uber migraron sus sistemas hacia microservicios, no lo
hicieron porque la arquitectura fuera técnicamente superior. Lo hicieron porque
su monolito había dejado de ser un problema de software para convertirse en un
problema de organización. Entender esa distinción es lo que separa adoptar
microservicios por criterio de adoptarlos por moda.

**El primer motivo es organizativo, no técnico.** La Ley de Conway observa que
toda organización produce sistemas que replican su estructura de comunicación.
Su corolario es incómodo: si dos mil ingenieros trabajan sobre un único
artefacto desplegable, todos compiten por la misma cola de integración. El
código no se vuelve más lento de escribir, sino más lento de *coordinar*.
Amazon lo reconoció hacia 2002, cuando Jeff Bezos impuso que todos los equipos
expusieran sus datos únicamente a través de interfaces de servicio: los
"equipos de dos pizzas" obtuvieron fronteras técnicas que hacían imposible
saltarse las fronteras de responsabilidad. Un microservicio es, antes que un
patrón de diseño, un contrato de propiedad.

**El segundo motivo es la frecuencia de despliegue.** En un monolito la unidad
mínima de cambio es la aplicación completa: corregir una errata en el módulo de
notificaciones obliga a desplegar también el motor de pagos. Ese acoplamiento
empuja a desplegar poco y en grandes lotes, lo que hace cada despliegue más
peligroso y justifica desplegar aún menos: un círculo vicioso. Los
microservicios lo rompen reduciendo el radio de impacto de cada cambio. Netflix,
que hacia 2009 operaba un monolito Java, llegó a miles de despliegues diarios
porque cada servicio podía liberarse sin sincronizarse con los demás.

**El tercer motivo es económico.** En un monolito la escalabilidad es uniforme:
para absorber la carga de un módulo hay que replicar todo el proceso, pagando
cómputo por código que nadie ejecuta. El perfil de carga real casi nunca es
uniforme —en Uber, el emparejamiento de conductores y el procesamiento de pagos
no crecen al mismo ritmo ni en el mismo horario—, y separar los servicios
permite dimensionar cada uno según su demanda. A escala de miles de instancias,
eso deja de ser una optimización y se vuelve una partida presupuestaria.

**El cuarto motivo es la contención de fallos.** En un proceso único, una fuga
de memoria derriba también las funciones sanas. Al separar los servicios, el
fallo queda confinado y el sistema se degrada en lugar de caerse: si el catálogo
no responde, las recomendaciones se apagan pero el usuario sigue reproduciendo
contenido. La contención no es automática —exige timeouts, reintentos acotados y
cortacircuitos—, pero el monolito ni siquiera ofrece la posibilidad. El
ejercicio práctico de este taller lo muestra: con el Servicio de Usuarios
apagado, crear un pedido devuelve **503**, mientras que consultar los pedidos
existentes sigue devolviendo **200**.

**El quinto motivo es la libertad tecnológica.** Cada servicio elige el lenguaje
y el motor de datos adecuados a su problema, y migra de versión sin arrastrar al
resto. Aquí el Servicio de Usuarios corre en Python con FastAPI y el de Pedidos
en TypeScript sobre Bun, sin compartir una línea de código y sin que ninguno
sepa en qué está escrito el otro.

**Ahora bien, el precio es real y se paga por adelantado.** Lo que era una
llamada a función pasa a ser una llamada de red, con latencia y fallos
parciales. Se pierde la transacción ACID y hay que sustituirla por consistencia
eventual y compensaciones. Depurar deja de ser seguir una pila de llamadas y
pasa a exigir trazas distribuidas. Por eso el consejo dominante entre quienes
lideraron estas migraciones —Martin Fowler lo formuló como *monolith first*— es
empezar por un monolito bien modularizado y extraer servicios solo cuando el
dolor lo exija.

La evidencia más honesta de que no es una verdad universal la aportó la propia
industria: en 2023 el equipo de Prime Video de Amazon reunió su sistema
distribuido de monitoreo de audio y vídeo en un único servicio, reduciendo sus
costos de infraestructura alrededor de un 90 %. Para ese caso, el tráfico entre
componentes costaba más de lo que valía la separación.

La conclusión no es que los microservicios sean buenos o malos, sino que
resuelven un problema específico: **permitir que muchos equipos avancen en
paralelo sobre un sistema grande**. Las empresas que los adoptan con éxito
tenían antes ese problema. Adoptarlos sin tenerlo significa pagar toda la
complejidad operativa —redes, observabilidad, versionado de contratos,
consistencia eventual— a cambio de un beneficio que no se necesita.

---

### Referencias

- Conway, M. E. (1968). *How Do Committees Invent?* Datamation, 14(4), 28–31.
- Fowler, M. (2015). *MonolithFirst.* martinfowler.com
- Newman, S. (2021). *Building Microservices* (2.ª ed.). O'Reilly Media.
- Richardson, C. *Microservices Patterns: Database per Service.* microservices.io
- Mauro, T. (2015). *Adopting Microservices at Netflix: Lessons for Architectural Design.* NGINX Blog.
- Amazon Prime Video Tech Blog (2023). *Scaling up the Prime Video audio/video monitoring service and reducing costs by 90%.*
