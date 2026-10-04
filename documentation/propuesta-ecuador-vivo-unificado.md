# Ecuador Vivo: propuesta de integración y archivo verificable

**Fecha de evaluación:** 4 de octubre de 2026, Ecuador.
**Estado:** propuesta para discutir; no se ha iniciado la integración ni retirado ningún proyecto.
**Alcance acordado:** pausar el video; evaluar Ecuador Vivo, monitor-sismos y Feed Geológico; reunir mapa, datos, casos, videos y bibliografía de Ecuador en un solo proyecto.

## 1. Qué debe ser Ecuador Vivo

**Un archivo abierto para explorar y entender los fenómenos del Ecuador, con casos que permitan comprobar los datos detrás de las explicaciones.**

La unidad central sería el **caso documentado**. Una persona llega desde un video, abre su ficha, ve las observaciones utilizadas y puede descargar los datos o reproducir el resultado. Otra persona llega buscando datos y descubre qué casos, mapas y publicaciones los utilizan.

Andes Pulso sería la colección de casos audiovisuales de Ecuador Vivo. El monitor sísmico pasaría a ser una herramienta dentro de Explorar. La biblioteca seleccionaría estudios sobre Ecuador pertinentes a los temas publicados; no conservaría el enfoque de novedades geológicas globales.

El objetivo es unir la explicación accesible con la posibilidad de comprobarla. Una comprobación informática confirma aspectos como integridad, filtros y cálculos; no equivale por sí misma a validación de campo o revisión científica por pares.

## 2. Evaluación de los tres proyectos

| Proyecto | Lo que ya aporta | Lo que limita su integración actual |
|---|---|---|
| Ecuador Vivo / fallas-ecuador | Atlas bilingüe, capas territoriales, fallas GEM, sismicidad USGS, lluvia, temperatura, nubes, inundación, cuencas, estaciones y comparaciones satelitales de Napo. Manifiestos, fuentes, licencias y pruebas. | La experiencia gira alrededor del mapa y acumula laboratorios. Los datos tienen documentación técnica, pero falta un catálogo público que conecte versiones, usos y casos. Parte del laboratorio fluvial sigue local. |
| monitor-sismos / Andes Pulso | Consultas sísmicas, catálogo histórico, perfiles y visualizaciones, herramientas educativas, guiones, datos congelados, producción y comprobación de videos. | Aplicación Streamlit y producción audiovisual mezcladas; abundan carpetas por versión y dependencias entre ellas. Solo 9 archivos están registrados en Git; no hay remoto configurado en este clon. Mucho trabajo y todos los artefactos requieren preservación explícita. |
| Feed Geológico / GeoPulso | Sitio público funcional, descubrimiento de bibliografía, filtros y un módulo práctico de observación de rocas. Automatización diaria operativa. | Selección global, sin relación estructurada con Ecuador ni con los casos. Actualmente 175 entradas automáticas, ninguna revisada, sin explicaciones editoriales o aplicaciones completadas. |

### Hallazgos que conviene resolver antes de migrar

- **Catálogos de fallas diferentes:** el atlas contiene 145 entidades y el monitor 182. Sus campos también difieren. No deben concatenarse ni sustituirse por conteo: hay que contrastar fuente, versión, cobertura y geometría, y conservar los subconjuntos reproducibles con su identidad.
- **La capa consultable no siempre es un archivo descargable:** algunas capas meteorológicas son servicios externos de visualización. Su ficha debe declarar si ofrece datos numéricos, una imagen, metadatos o acceso al proveedor. Una captura coloreada no reproduce una medición.
- **Feed con problemas observables:** 167 abstracts tienen exactamente 650 caracteres porque el script los corta; la interfaz los llama «abstract original». Deberían identificarse como extractos. Hay una entrada con fecha 2029-05-06, posterior a la fecha de evaluación, que necesita revisión. Ninguna entrada menciona literalmente Ecuador en el título o abstract disponible; esta búsqueda textual no demuestra por sí sola que ninguna tenga relación con el país.
- **El actualizador puede borrar el trabajo editorial:** reemplaza el registro completo por la respuesta nueva, incluidos estado, explicación y aplicación. Además, conserva como máximo 180 entradas. Eso resulta inadecuado para una bibliografía permanente de casos.
- **La automatización puede aparentar actualización correcta aunque fallen las consultas:** captura errores por tema y escribe una fecha nueva de actualización. El futuro catálogo necesita distinguir intento, éxito y cambios reales.
- **El histórico audiovisual depende de versiones anteriores:** por ejemplo, la pieza de ríos v9 lee evidencia v6, que a su vez verifica antecedentes. Borrar carpetas antiguas sin resolver estas relaciones rompería la reproducción.
- **La identificación pública necesita simplificarse:** Ecuador Vivo como marca principal; Andes Pulso como colección; Biblioteca de Ecuador como sección. Tres nombres principales independientes dificultan entender que los recursos pertenecen a la misma iniciativa.

### Comprobaciones realizadas

Se revisaron código, documentación, manifiestos, estado de Git, archivos locales, repositorio público del feed y respuestas de sus páginas publicadas. La validación completa de JavaScript/datos del atlas pasó, conservando cuatro advertencias científicas documentadas: citas a nivel de catálogo, escalas ausentes, nombres repetidos y puntos geomorfológicos representativos. Pasaron 20 pruebas existentes del núcleo sísmico, histórico y educativo del monitor.

No se ejecutaron nuevamente todos los procesos de descarga/renderizado ni se validaron en campo los resultados. La evaluación de interfaz se apoya en estructura y contenido; no constituye una prueba exhaustiva de navegación en todos los dispositivos.

## 3. Tres propuestas posibles

| Propuesta | Resultado | Coste y valoración |
|---|---|---|
| A. Portal que enlaza los tres sitios | Una portada común con accesos al atlas, monitor y feed existentes. | Rápida, pero conserva datos y experiencias separadas. No cumple suficientemente el objetivo de verificación integrada. |
| **B. Archivo de casos + catálogo de datos + visor** | Una ficha estable por caso, un catálogo común y herramientas que consumen las mismas versiones de datos. | **Recomendada.** Aprovecha lo construido, permite crecer por casos y ofrece una diferencia concreta: seguir el camino del video a la evidencia. |
| C. Plataforma completa de usuarios y servicios en tiempo real | Cuentas, contribuciones, trabajos en servidor, panel editorial y almacenamiento gestionado. | Mayor mantenimiento, infraestructura y posibles costes. No hace falta para ofrecer consultas, descargas y casos reproducibles en esta etapa. |

La propuesta B puede empezar con páginas estáticas y generación de contenidos a partir de fichas estructuradas. El Python actual sigue sirviendo para preparar y comprobar datos. La aplicación Streamlit puede conservarse temporalmente como laboratorio mientras se incorporan sus funciones útiles al visor común. GitHub Pages no ejecutará la aplicación Python del monitor: mover sus archivos al repositorio no integra automáticamente su funcionamiento.

## 4. Navegación propuesta

| Apartado | Qué puede hacer la persona |
|---|---|
| **Explorar Ecuador** | Entrar por lugar o fenómeno; abrir mapa, observaciones recientes y comparaciones. |
| **Datos** | Buscar conjuntos por territorio, tema, fecha y resolución; verlos, descargarlos y citarlos. |
| **Andes Pulso** | Ver los casos y videos; abrir la evidencia exacta de cada pieza. |
| **Biblioteca de Ecuador** | Encontrar estudios pertinentes y saber con qué caso, capa o conjunto de datos se relacionan. |
| **Aprender** | Comprender conceptos y practicar procedimientos con datos de los casos. |

Fuentes, metodología, autoría, correcciones y contribuciones tendrían accesos permanentes secundarios. Tierra, Agua, Cielo, Vida y Riesgo se conservarían como filtros temáticos dentro de Explorar y Datos. Así se evita convertir cada tema y cada herramienta en otra pestaña principal.

La portada presentaría una pregunta o caso destacado, su evidencia visual y tres entradas directas: explorar un lugar, ver un caso y encontrar datos. Las imágenes principales deberían proceder de observaciones reales o figuras documentadas. El mapa completo permanecería a un acceso de distancia, con apertura directa desde los casos.

Napo —especialmente Tena y Archidona— sería el territorio con mayor profundidad inicial. El sitio debe mostrar con claridad las zonas sin cobertura y distinguir Ecuador continental, Galápagos y ventanas regionales que incluyen países vecinos.

## 5. La ficha de verificación de cada video

Cada episodio tendría una dirección estable, por ejemplo `andes-pulso/memoria-sismica-1900-2025/`. Un enlace o QR en la publicación llevaría a esa página. El video, los datos y sus relaciones estarían allí visibles para el público.

```text
CASO: MEMORIA SÍSMICA 1900–2025
Pregunta · territorio · periodo · autor · versión

[Video]          [Abrir el mapa de este video]
                [Descargar los datos utilizados]

Ver los datos | Cómo se hizo | Qué podemos concluir | Fuentes

Tabla y mapa interactivos de la versión utilizada
CSV / GeoJSON · descripción de columnas · licencia · cita

Momento del video → afirmación o gráfico → datos → cálculo → fuente
Correcciones y versiones anteriores
```

La ficha mínima contendría:

1. **Video y texto:** reproducción o enlace al video publicado, transcripción y subtítulos. Los enlaces sociales no serían la única forma de conservar el episodio; se preservaría también su archivo maestro.
2. **Observaciones utilizadas:** tabla, mapa e imágenes con fechas, unidades, cobertura y valores ausentes visibles. El usuario debe poder comprobar contenido sin instalar herramientas.
3. **Descargas reales:** datos de entrada redistribuibles, derivados utilizados y diccionario de variables. Si un dato debe obtenerse del proveedor, acceso y procedimiento explícitos; no un botón que prometa una descarga inexistente.
4. **Método:** fuente, fecha de recuperación, filtros, transformaciones, parámetros y programa empleado. Una explicación legible y una receta reproducible para quien quiera ejecutarla.
5. **Vínculo entre resultado y evidencia:** las principales cifras, afirmaciones y gráficos del video identifican qué datos o documento los sustentan. Las afirmaciones conceptuales remiten a su bibliografía; los esquemas se identifican como tales.
6. **Alcance y revisión:** qué se observó, qué se calculó, qué se interpretó, limitaciones y revisiones realizadas. «Comprobaciones técnicas aprobadas» y «revisado científicamente» tendrían significados distintos.
7. **Versiones y correcciones:** fecha, cambios y acceso a la versión que vio la audiencia. Una corrección posterior no sobrescribe silenciosamente la evidencia histórica.

### Ejemplo con material que ya existe

El paquete local `reel_ecuador_1900_2025_v6` conserva un CSV, un GeoJSON USGS, consulta original, guion, comprobaciones y video. Su manifiesto registra **2661 eventos**, magnitud publicada ≥4, periodo 1900–2025 y descarga del 2 de octubre de 2026. Es una **ventana regional rectangular**, incluye áreas vecinas y excluye Galápagos; no se debe llamar «todos los sismos de Ecuador».

Ese conjunto podría alimentar la ficha del episodio sin repetir la investigación. Antes de asociarlo definitivamente con las publicaciones sociales hay que comprobar que el archivo y edición publicados son exactamente los mismos: no basta con reconocer el tema.

Los enlaces facilitados por el autor se han identificado para esa conciliación:

- Instagram: https://www.instagram.com/reel/DeAUmHNTp7R/
- TikTok: https://www.tiktok.com/@elgeocientifico/video/7692168484624780564

La lectura automática de esas plataformas fue bloqueada; no se afirma haber reproducido ambos videos ni confirmado su correspondencia exacta con el archivo local.

El laboratorio en vivo usaría otra entrada: **«Consultar datos actuales»**. El botón **«Datos usados en este video»** abriría siempre la versión conservada. Si el proveedor revisa posteriormente una magnitud, esa revisión puede documentarse sin cambiar lo que sustentaba el episodio original.

## 6. Biblioteca centrada en Ecuador

La biblioteca recogería estudios **sobre el territorio o fenómenos de Ecuador y relacionados con lo que presenta el sitio**. No basta con una afiliación ecuatoriana de un autor ni con que aparezca Ecuador en una referencia bibliográfica.

Los temas iniciales serían fallas y sismicidad; geomorfología y movimientos en masa; ríos y cuencas; clima y precipitación; cobertura del suelo y teledetección. Se daría prioridad editorial a Napo, Tena y Archidona. Otras áreas entrarían cuando hubiera contenido y datos que las justifiquen.

Cada registro conservaría DOI o identificador estable, autores, tipo de documento, área estudiada, periodo, tema, fuente, disponibilidad de datos, estado de revisión y enlaces a los casos/capas correspondientes. Una explicación revisada indicaría qué aporta y qué límites tiene. Cuando solo se disponga de un extracto, se rotularía como extracto.

La búsqueda automática propondría candidatos. Una revisión comprobaría el ámbito geográfico y la pertinencia temática antes de incorporarlos a la colección principal. La búsqueda incluiría nombres de cuencas, localidades, volcanes y sistemas de fallas; no dependería únicamente de la palabra «Ecuador». Tampoco limitaría la bibliografía a los últimos 120 días: los estudios anteriores esenciales deben permanecer.

Se mantendrían separados los metadatos recuperados y la interpretación editorial para que una actualización automática no borre revisiones o notas. Un artículo ligado a un caso no desaparecería por un límite de 180 registros.

Las referencias internacionales de métodos pueden seguir citadas dentro de las explicaciones. Un ejemplo comparativo como el Doce se identificaría por su país y su función didáctica; no se incorporaría al feed como investigación sobre Ecuador.

## 7. Un proyecto con almacenamiento organizado

Una sola base de proyecto puede reunir web, catálogo, herramientas científicas y producción audiovisual. Los archivos de gran tamaño necesitan un tratamiento distinto al código para que el repositorio siga siendo manejable.

| Tipo | Ubicación propuesta |
|---|---|
| Código, textos, fichas, metadatos y datos pequeños | Repositorio principal de Ecuador Vivo, con control de versiones. |
| Capas comunes y conjuntos de datos publicados | Una versión canónica por conjunto; cada caso referencia esa versión, sin volver a copiarla. |
| Paquetes científicos voluminosos | Descargas de versiones o depósito científico, con ficha pública, procedencia y comprobación de integridad. |
| Videos finales | Catálogo del episodio y reproducción/enlaces; maestro conservado y separado de renders intermedios. |
| Datos de trabajo, voces y renders | Área local de producción excluida del sitio público y respaldada. Cachés y resultados regenerables identificados. |

Las fichas de datos compartirían campos de cobertura, escala/resolución, sistema de coordenadas, unidades, fechas, versión, licencia, productor, transformaciones, calidad, usos y descarga. Un DOI de proyecto o software no reemplaza la cita al conjunto original. Se distinguirían datos de terceros, derivados del proyecto y observaciones propias.

Para conjuntos científicos terminados se puede valorar Zenodo y su DOI. No es necesario depositar cada borrador. Los recursos consultables solo a través de servicios externos conservarían su enlace, parámetros y límites de acceso; no se prometería custodia del archivo completo.

### Espacio medido

Mediciones de tamaño lógico de archivos; no equivalen necesariamente a ocupación física liberable en OneDrive.

| Área | Tamaño aproximado |
|---|---:|
| Carpeta completa de Ecuador Vivo | 2,30 GiB |
| De ella, directorio `.git` | 1,46 GiB |
| Archivos registrados de la versión de trabajo del atlas | 163,1 MiB |
| Carpeta completa de monitor-sismos | 2,43 GiB |
| De ella, producción `artifacts` | 1,96 GiB |
| Entorno Python del monitor | 475,3 MiB |
| Los 38 MP4 encontrados en producción | 454,4 MiB |

En `data`/`assets` del atlas y `artifacts` del monitor, excluyendo runtimes y archivos ≤64 KiB, se comprobaron **185 grupos de contenido idéntico**, con **405,6 MiB en copias adicionales**. Incluyen datos reutilizados entre versiones. Esto señala una oportunidad de organización; no autoriza borrarlos porque hay dependencias de rutas y verificadores.

Git calcula aproximadamente 176,7 MiB para los objetos alcanzables desde las referencias del atlas, frente a 1,46 GiB del directorio completo. La diferencia merece una revisión posterior de historial, reflogs y objetos; no se promete recuperar toda esa cantidad ni se propone ahora reescribir el historial.

Feed Geológico es pequeño: la API de GitHub informa un tamaño de 137 KiB para el repositorio remoto. Eliminarlo no resolvería el consumo de espacio local. Mantener una transición ligera con enlaces a Ecuador Vivo sería útil para quienes ya conocen su dirección.

## 8. Integración por etapas, después de discutir la propuesta

1. **Inventario y preservación.** Guardar los cambios locales, identificar datos únicos, archivos maestros y derechos por recurso, y mapear dependencias entre versiones. Conservar un inventario con hashes y respaldo recuperable.
2. **Un caso completo como piloto.** El episodio sísmico ya publicado, una vez conciliado con la edición local. Video, mapa exacto, tabla, CSV/GeoJSON, método, fuentes y correcciones en una misma ficha.
3. **Catálogo común y navegación.** Incorporar las fichas de datos y las cinco entradas propuestas; conservar enlaces del atlas ya difundidos en el CV y en publicaciones.
4. **Integrar las funciones del monitor.** Reutilizar el núcleo de cálculo y construir su presentación dentro del proyecto común. Separar consulta actual y archivo histórico. Migrar las funciones avanzadas solo cuando su lectura y utilidad estén claras.
5. **Biblioteca de Ecuador.** Ajustar búsqueda, curación geográfica, preservación de metadatos y relación con casos. Conservar el módulo de rocas como recurso de Aprender, sin expandir una academia completa durante esta integración.
6. **Producción audiovisual común.** Cada episodio futuro declara sus conjuntos de entrada y genera una ficha junto con el video, guion y subtítulos. Publicar un video también supone publicar o enlazar su evidencia correspondiente.
7. **Retirada comprobada.** Probar que se puede abrir el sitio, consultar el caso y regenerar un resultado usando la ubicación nueva. Resolver rutas antiguas y comprobar el respaldo antes de retirar carpetas. Los repositorios públicos antiguos pueden quedar archivados o como transición; su eliminación definitiva se decide aparte.

### Condición de aceptación del piloto

Una persona que llega desde Instagram o TikTok puede encontrar la edición correcta, abrir sus mismos datos sin registro, reproducir el mapa, descargar el conjunto, conocer los filtros y rastrear una cifra relevante hasta su fuente. Un cambio posterior en el monitor o en el feed no altera esa ficha histórica.

## 9. Referencias de infraestructura y evidencia de esta evaluación

- Atlas y documentación: https://github.com/henryconteron/fallas-ecuador
- Feed inspeccionado: https://github.com/henryconteron/feed-geologico/tree/5dfee0655f21cf13bcdff61d8f8d043c95154771
- Actualizador: https://github.com/henryconteron/feed-geologico/blob/5dfee0655f21cf13bcdff61d8f8d043c95154771/scripts/update_feed.py
- Curso publicado: https://henryconteron.github.io/feed-geologico/cursos/observacion-rocas.html
- GitHub Pages: sitio publicado máximo 1 GB y repositorio fuente recomendado por debajo de 1 GB. https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- GitHub: tratamiento de archivos grandes y distribución mediante releases. https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github
- Zenodo: DOI para registros publicados. https://help.zenodo.org/docs/deposit/describe-records/reserve-doi/

**Decisión recomendada:** propuesta B, usando el caso audiovisual publicado como primera prueba de la integración. El valor diferencial se comprobará al poder recorrer una explicación hasta sus datos y volver de esos datos a todas las piezas que los utilizan.
