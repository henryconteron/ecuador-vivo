# Ecuador Vivo · web, propuesta de valor y oportunidades de audiencia

Fecha de consulta: 13 de octubre de 2026. Análisis, no autorización de publicación
ni implementación. No se modificaron aplicación, datos, proyectos o despliegue.

## Conclusión

El problema principal no es la falta de funciones. Hay más capacidad de producción
que historias terminadas y visibles en la web. La oportunidad es convertir Ecuador
Vivo en el lugar donde una persona entiende un cambio de su territorio, ve un video
y puede comprobarlo con el mismo mapa, cifras y fuentes. El SIG y Studio producen
esas historias; no deben convertirse en requisitos para consumirlas.

Recomendación de posicionamiento: ciencia del Ecuador que puedes explorar y
comprobar, desde tu provincia hasta el país. Andes Pulso identifica la serie de
videos; Ecuador Vivo es la marca principal. No competir con INAMHI o IG-EPN por
ser el aviso oficial más rápido ni presentar el atlas como predictor de riesgos.

## Alcance y límites de la revisión

Se revisaron contenido/estructura de 13 páginas públicas, catálogo de datos,
biblioteca, catálogos de casos, estilos y módulos representativos del visor;
arquitectura/documentación del proyecto, límites del panel privado y puente
Studio → paquete → importación editorial. Se contrastaron varios archivos con
GitHub Pages y se ejecutaron dos verificadores de solo lectura.

No se inspeccionó cada línea de todo el repositorio, ni se volvió a auditar cada
cálculo, ni se hicieron pruebas visuales en navegador: la preferencia guardada
sigue denegada. Las respuestas HTTP no equivalen a medir carga en un teléfono.
No se accedió a estadísticas privadas de redes, Search Console o Analytics.
Las propuestas de audiencia son hipótesis priorizadas, no pronósticos de viralidad.

## Qué se ofrece hoy

| Espacio | Valor existente | Carencia principal para el visitante |
|---|---|---|
| Inicio | Presentación ES/EN, imagen satelital real, entradas al atlas y evidencia | Pregunta general; no ofrece selección de provincia ni novedad editorial concreta |
| Explorar | Tierra/Agua/Cielo/Vida/Riesgo, capas, fechas, fuentes, explicación puntual y experiencias Napo | Muchos controles y vocabulario técnico; requiere una intención previa |
| Andes Pulso | Video sísmico, instantánea, mapa, CSV, método, límites y autoría | Catálogo de videos terminados todavía pequeño; novedades de Studio no publicadas |
| Datos | 16 registros: 4 archivos, 5 derivados/metadatos y 7 servicios externos | No todos son descargas completas; la distinción debe mantenerse clara |
| Biblioteca | 6 estudios seleccionados, pertinencia, citas y límites | Más útil al conectarla a una pregunta concreta que como listado de entrada |
| Aprender | Tres experiencias 3D, retos y cuaderno local; lecturas y rocas | Falta empaquetar recorridos breves para docentes y estudiantes |
| Ríos/Napo | Antes/después, RGB e índices, conteos de observaciones y procedencia | Muy buen caso distintivo, pero no representa cobertura nacional completa |
| Modelos/Cartoteca/Laboratorio | Superficies, geología local y herramientas experimentales | Demasiadas puertas secundarias para quien solo quiere entender una historia |
| SIG/Studio/Recursos | Producción, análisis, composición, voz/subtítulos y recursos | Su avance no implica actualización automática del sitio público |
| Panel privado | Edición local, importación de borradores y publicación explícita | Hace falta cerrar un flujo editorial pequeño y usarlo con regularidad |

Vida hoy se centra en cobertura, vegetación y anomalías térmicas: no equivale a
un atlas de especies. No anunciar distribución de fauna como función disponible.
El núcleo Napo es una fortaleza local, pero la portada nacional debe distinguir
entre datos nacionales y estudios regionales parciales.

## Hallazgos comprobados de publicación

- Inicio público: HTTP 200 y contenido idéntico a index.html local.
- Andes Pulso: HTTP 200, pero el HTML público difiere del local; público 26.872
  bytes frente a 29.901 locales. No todos los cambios locales están desplegados.
- Video sísmico público: HEAD 200, video/mp4, 9.694.184 bytes. No está todo roto.
- data/cases/studio-index.json: 404 público; local existe con cases vacío.
- assets/js/studio-evidence.js: 404 público. El puente nuevo no está desplegado;
  esto no demuestra que la versión anterior del sitio esté intentando cargarlo.
- El registro editorial existente tiene cinco casos data_ready, no cinco videos
  publicados. Incluye recibos y guiones; no confundir preparación con publicación.
- Catálogos de datos y estudios: HTTP 200 y coincidentes con la copia local.
- sitemap.xml y robots.txt: 404 en las rutas comprobadas. No se encontraron
  canonical, Open Graph o JSON-LD en las páginas públicas inspeccionadas.
  Carecer de robots.txt no impide por sí solo la indexación; no se ha demostrado
  que el sitio esté desindexado.
- No se encontró instrumentación habitual de analítica en los archivos públicos
  revisados. No se puede deducir audiencia, rebote o conversión a partir del código.
- README declara código MIT; LICENSE dice que el código no se ofrece actualmente
  con licencia abierta. Corregir esa contradicción documental; las licencias de
  datos y bibliotecas siguen siendo independientes.
- Las fuentes de portada se solicitan mediante Google Fonts. Hay PNG educativos
  individuales de más de 2–4 MiB: revisar carga diferida y variantes optimizadas,
  conservando originales científicos cuando correspondan. No es prueba de que
  todos se descarguen en Inicio ni de un problema de rendimiento medido.

Verificadores ejecutados: validate-js-imports.mjs aprobado; validate-catalog.mjs
aprobado con cuatro advertencias documentadas: citas de catálogo en 77 trazas,
145 sin escala cartográfica documentada, 18 nombres repetidos y tres ubicaciones
representativas regionales. No convertir estas advertencias en precisión aparente.

## Evidencia externa sobre el público

### Acceso y distribución

[INEC, TIC julio 2025](https://www.ecuadorencifras.gob.ec/tecnologias-de-la-informacion-y-comunicacion-tic/):
80,1 % de personas de cinco años y más había utilizado internet en los últimos
doce meses; 71,3 % de hogares tenía acceso. Son indicadores distintos. La
presentación desagrega acceso de hogares urbano 76,6 % y rural 58,7 %.
Esto respalda diseñar una entrada ligera y comprensible en móvil; no demuestra
preferencia por un tema ni implica que todos tengan buena conexión.

[DataReportal Digital 2026 Ecuador](https://datareportal.com/reports/digital-2026-ecuador)
usa principalmente datos de finales de 2025. Sus estimaciones publicitarias de
Facebook y YouTube justifican probar también esos canales, no limitarse a TikTok
e Instagram. No representan personas únicas ni usuarios activos comparables;
el propio informe advierte anomalías, especialmente en TikTok. No sumar audiencias.

### Intereses: señales, no una encuesta nacional propia

La consulta pública de [Google Trends Ecuador](https://trends.google.com/trending?geo=EC&hl=es)
mostró terremoto, variantes de temblor, lluvia e inundación entre tendencias de
las últimas 24 horas, junto con mucho fútbol y entretenimiento. Sirve como
señal puntual de preguntas que pueden activar interés, no como ranking anual,
ni como prueba de un evento ocurrido en Ecuador. No se verificó una serie
exportada de doce meses o cinco años para comparar esos temas.

[Google explica](https://support.google.com/trends/answer/4365533?hl=es) que
Trends utiliza muestras y normaliza el interés. Un índice relativo no equivale
a personas ni a un porcentaje de toda la población. Evitar titulares estadísticos
basados en una sola captura.

[Ipsos Ecuador, mayo 2024](https://www.ipsos.com/es-ec/la-sostenibilidad-como-desafio-colectivo)
publicó una señal de preocupación por el cambio climático. Es contexto histórico,
no una medición actual de 2026; el material consultado no permitió evaluar una
ficha muestral completa. No se usa para ordenar preferencias de toda la población.

No hay evidencia suficiente para afirmar que especies, volcanes o comparaciones
provinciales son las categorías más populares del país. Son apuestas compatibles
con el proyecto que deben comprobarse con contenido y medición propios.

## Referentes y oportunidad propia

Revisión de contenidos, navegación y documentación pública; no una auditoría
visual renderizada ni comparación de sus visitas.

| Referente | Qué resuelve | Qué conviene adaptar | Qué no conviene prometer |
|---|---|---|---|
| [INAMHI](https://servicios.inamhi.gob.ec/) | Pronóstico, estaciones, avisos y boletines | Entradas por necesidad y provincia; fecha y fuente visibles | Ser sustituto de avisos oficiales |
| [IG-EPN](https://www.igepn.edu.ec/) | Información sísmica/volcánica e informes | Autoridad de fuente y contexto de amenazas | Predicción, daños o riesgo de una casa desde un punto del mapa |
| [MapBiomas Ecuador](https://ecuador.mapbiomas.org/) | Cambios territoriales, productos, historia y métodos | Seleccionar territorio/periodo y explicar cambios | Tratar cualquier diferencia de color como deforestación validada |
| [MAAP](https://www.maapprogram.org/) | Historias territoriales con imágenes y evidencia | Una pregunta concreta, antes/después y síntesis | Atribuir minería o ilegalidad solo con nuestros índices |
| [BioWeb PUCE](https://bioweb.bio/aboutus.html) | Especies, fichas, mapas y multimedia | Nombre común, fotografía/sonido y mapa contextual | Registros como censo; usar medios sin revisar derechos |

La oportunidad no es afirmar que nadie une ciencia y mapas. Es integrar de forma
coherente un video corto propio, mapa sincronizado, métricas del mismo corte y
una explicación accesible de la evidencia. Los componentes ya existen parcialmente.
GeoLibre/QGIS/ArcGIS son referencias para autoría SIG, no el modelo de entrada
de una persona que llega desde Instagram y nunca ha trabajado con capas.

## Temas que probar, en orden

Prioridad editorial propuesta, no clasificación estadística de popularidad.

| Prioridad | Pregunta que engancha | Experiencia útil | Exigencia científica |
|---|---|---|---|
| 1 | ¿Cuándo y dónde llueve más en Ecuador? | Timelapse climatológico y selección provincial | Misma escala, periodo, cobertura y agregación explícitos |
| 1 | ¿Qué cambió en este río? | Arrastrar antes/después y ver las fechas originales | Nubes/NoData, geometría comparable y causas no inferidas |
| 1 | ¿Qué cuenta realmente un mapa de sismos? | Video breve, profundidad/magnitud y mapa de la instantánea | Completitud, tipos de magnitud y no predicción |
| 2 | ¿Qué tiene que ver el mar con nuestra lluvia? | Pacífico–Ecuador, anomalías y comparación de periodos | Baseline y observación/pronóstico separados; no causalidad automática |
| 2 | ¿Qué animales se han registrado en mi provincia? | Fichas, sonidos y registros cartográficos | Licencias, sesgo de muestreo y protección de ubicaciones sensibles |
| 3 | ¿De dónde viene el agua que usamos y la electricidad? | Cuenca, lluvia, embalse y generación | No convertir lluvia en caudal ni en pronóstico de apagones |
| 3 | ¿Cómo cambió mi ciudad o paisaje? | Extensión urbana/vegetación en años comparables | Productos y validación adecuados a la pregunta |

Para El Niño, [INOCAR/ERFEN](https://inocar.mil.ec/web/index.php/boletines/bac)
aporta contexto institucional; cada pieza deberá contrastar el boletín fechado,
región oceánica y periodo realmente usados, no reutilizar indefinidamente una
URL «actual». No se emite aquí diagnóstico del estado ENSO de hoy.

[MAAP #249](https://www.maapprogram.org/mining-ecuador-napo/), publicado el
24 de agosto de 2026, muestra que Napo tiene una agenda territorial vigente que
conecta con lo ya preparado en el proyecto. Sus conclusiones son de MAAP y
EcoCiencia; no se transfieren como hallazgos de nuestros índices ni se copian
sus imágenes sin revisar condiciones.

[BioWeb](https://bioweb.bio/portal/) permite buscar por provincia y localidad.
[CENACE](https://www.cenace.gob.ec/info-operativa/InformacionOperativa.htm)
ofrece información operativa eléctrica y advierte datos preliminares; integrar
esos temas exige otra ficha de fuente y no está implementado por esta revisión.

## Cómo debería sentirse la web

Primero una historia y un lugar; luego la explicación; después las herramientas.
Mantener ciencia visible sin convertir toda la página en un formulario o en una
lista de descargos. Resumen breve de límites junto al dato y método completo
a un clic. No esconderlos ni repetirlos como bloque dominante en cada sección.

Propuesta de organización, no diseño aprobado:

1. Cabecera simple: Explorar, Historias, Aprender, Datos. Biblioteca y laboratorio
   continúan accesibles dentro de esas rutas y en el pie; no borrar páginas.
2. Portada con una pregunta editorial, mapa real legible y dos acciones claras:
   explorar una provincia o ver la historia destacada.
3. Selección de lugar sin pedir ubicación GPS obligatoria: provincia/ciudad cuando
   los datos lo permitan. Diferenciar punto urbano y promedio territorial.
4. Una historia nueva y dos relacionadas, con portada, duración y fecha del dato.
   Una pregunta por pieza, no una portada con todas las herramientas encendidas.
5. Antes/después como interacción protagonista de las historias de territorio.
6. «En 30 segundos / explóralo / comprueba los datos» como profundidad progresiva.
7. Galápagos con presencia propia cuando exista cobertura; ausencia de datos no
   debe convertirse en cero ni recortarse de la promesa silenciosamente.
8. Un acceso educativo con una misión corta, explicación y ficha descargable;
   reutilizar los retos ya hechos, no desarrollar una plataforma escolar entera.

Tres territorios de marca evaluados: monitor de actualidad, atlas territorial
y aula interactiva. El monitor exige mantenimiento continuo y se solapa con
fuentes oficiales; el aula tiene buen nicho pero limita entrada general. Recomiendo
atlas narrativo como eje, con actualidad contextual y aprendizaje como recorridos.

La singularidad debe venir del contenido ecuatoriano y del uso del mapa, no de
añadir gradientes, paneles oscuros o 3D ornamental. La estética pública puede ser
editorial y el espacio de trabajo técnico más denso: coherencia de marca no exige
que un lector y un creador vean la misma interfaz.

## Plan acotado antes de más funciones

### Primero: cerrar lo que llega al público

- Elegir tres casos terminados; comprobar video, cifras, fuentes, cobertura y
  derechos; importar como borradores y publicar solo después de revisión explícita.
- Conciliar versión local/publicada y catálogo revisado; no mostrar data_ready
  como video terminado ni activar borradores privados automáticamente.
- Corregir mensajes de licencia contradictorios y estados de contenido.
- Crear una página estable por historia, no depender únicamente de fragmentos
  o de un catálogo que inyecta todo por JavaScript.

### Después: una portada con esas historias

- Reorganizar navegación y protagonismo de mapa/video, sin reescribir el visor.
- Probar selector territorial con datos realmente disponibles, empezando por
  cobertura nacional más el caso Napo; no crear 24 páginas vacías.
- Añadir miniaturas para compartir, canonical/idiomas y metadatos de cada video;
  sitemap y comprobación con Search Console cuando el propietario lo habilite.
  [Google recomienda páginas específicas y metadatos de video](https://developers.google.com/search/docs/appearance/video?hl=es).
  Esto ayuda al descubrimiento, pero no garantiza posicionamiento ni tráfico.
- Medir y optimizar carga móvil con mapa/3D/video bajo demanda, sin autoplay
  pesado. No migrar todo a otro framework antes de localizar cuellos de botella.

### Probar durante un ciclo editorial de cuatro semanas

Comparar piezas de clima, territorio y sismos con portada/pregunta y enlace a
la ficha correspondiente. Incluir Facebook Reels y YouTube Shorts en pruebas
además de Instagram y TikTok, adaptando cada publicación y sin prometer iguales
resultados entre plataformas. El sitio no debe obligar a salir de él para entender
el dato, pero tampoco duplicar toda la maquinaria de las redes.

Medir por canal: visitas que llegan, reproducción/avance de video, apertura del
mapa, selección de provincia, acceso a fuentes/descarga y retorno. Priorizar tasas
por visitas y retención comparable, no solo vistas brutas. No instalar seguimiento
ni recoger correos en este análisis. Definir privacidad y consentimiento antes.

Hacer sesiones exploratorias con 5–8 personas: visitante desde redes, docente,
estudiante y persona interesada en una provincia. No son una encuesta representativa.
Comprobar si entienden qué pueden hacer, encuentran su lugar y distinguen datos
observados de pronóstico/interpretación. Con poco tráfico, no declarar ganadores
estadísticos de una prueba A/B; usar señales descriptivas y comentarios.

Solo ampliar biodiversidad/energía/otras provincias cuando el flujo de publicación
y las primeras historias demuestren utilidad. Dejar para después otra app,
reconstrucción total del SIG, login obligatorio, chat IA general, alertas propias,
descargas masivas y un catálogo enorme de herramientas.

## Decisión recomendada

No empezar otra etapa de meses construyendo más herramientas. Usar lo existente
para entregar tres experiencias públicas completas y una portada que las haga
evidentes. La pregunta guía: «¿qué aprende o puede comprobar una persona en su
primera visita, y por qué volvería la semana siguiente?».
