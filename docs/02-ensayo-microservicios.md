# ¿Por qué las grandes empresas tecnológicas adoptan microservicios?

**Asignatura:** Lenguaje de Programación Avanzado 2
**Actividad:** Investigación teórica — ensayo breve (una página)

El texto entre los marcadores `ensayo:inicio` y `ensayo:fin` es el que
`scripts/build-pdf.py` inserta en el documento de entrega. Está ajustado para
ocupar una sola página en formato APA 7 (Times New Roman de 12 puntos, doble
espacio, márgenes de una pulgada), y usa citas en el texto con autor y año.

---

<!-- ensayo:inicio -->

Las grandes empresas tecnológicas no adoptan microservicios porque sean técnicamente superiores, sino porque su sistema monolítico dejó de ser un problema de software para convertirse en uno de organización. Conway (1968) observó que los sistemas reproducen la estructura de comunicación de quienes los diseñan: cuando miles de ingenieros comparten un único artefacto desplegable, el código no se vuelve más lento de escribir, sino de coordinar. Amazon enfrentó ese problema hacia 2002, cuando exigió que todos sus equipos se comunicaran únicamente mediante interfaces de servicio (Yegge, 2011).

El segundo motivo es la frecuencia de despliegue. En un monolito, corregir un módulo obliga a desplegar la aplicación completa, lo que empuja a publicar poco y en lotes riesgosos; al reducir el alcance de cada cambio, Netflix pudo migrar su plataforma a un conjunto de servicios que evolucionan de manera independiente (Mauro, 2015). A ello se suman el escalado selectivo, que evita replicar componentes que no están bajo carga; el aislamiento de fallos, que permite degradar una función sin detener el sistema, y la libertad de elegir la tecnología adecuada para cada servicio (Newman, 2021).

Sin embargo, el costo es real. Una llamada a función se convierte en una llamada de red, con latencia y fallos parciales, y la transacción ACID cede su lugar a la consistencia eventual. Por ello, Fowler (2015) recomienda comenzar con un monolito bien modularizado y extraer servicios solo cuando el problema lo exija. El propio equipo de Prime Video reunió en una sola aplicación un servicio de monitoreo que había construido de forma distribuida, y con ello redujo sus costos de infraestructura en más de un 90 % (Kolny, 2023).

En conclusión, los microservicios resuelven un problema específico: permitir que muchos equipos avancen en paralelo sobre un sistema de gran tamaño. Las empresas que los adoptan con éxito ya enfrentaban ese problema; adoptarlos sin tenerlo implica asumir toda su complejidad operativa sin obtener el beneficio que la justifica.

<!-- ensayo:fin -->

---

## Referencias

Conway, M. E. (1968). How do committees invent? *Datamation, 14*(4), 28–31.

Fowler, M. (2015, 3 de junio). MonolithFirst. *Martin Fowler*. https://martinfowler.com/bliki/MonolithFirst.html

Kolny, M. (2023, 22 de marzo). Scaling up the Prime Video audio/video monitoring service and reducing costs by 90%. *Prime Video Tech*. https://web.archive.org/web/20230323220106/https://www.primevideotech.com/video-streaming/scaling-up-the-prime-video-audio-video-monitoring-service-and-reducing-costs-by-90

Mauro, T. (2015, 19 de febrero). Adopting microservices at Netflix: Lessons for architectural design. *NGINX Blog*. https://web.archive.org/web/20160114045720/https://www.nginx.com/blog/microservices-at-netflix-architectural-best-practices/

Newman, S. (2021). *Building microservices: Designing fine-grained systems* (2.ª ed.). O'Reilly Media.

Yegge, S. (2011, 12 de octubre). *Stevey's Google platforms rant*. GitHub Gist. https://gist.github.com/chitchcock/1281611
