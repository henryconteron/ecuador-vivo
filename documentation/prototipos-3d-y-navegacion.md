# Prototipos 3D y navegación · 2026-10-04

## Propósito y estado

Preparar y probar interacciones antes de incorporar cartografía de investigación. `modelos.html` es una versión de prueba explícita. No se ha creado un modelo geológico validado de Ecuador ni un servicio de predicción de terremotos. No se importaron, cambiaron de CRS ni publicaron archivos de ArticleMaps del usuario.

### Relieve

Malla de 37 × 37 puntos, fórmula sintética reproducible en `assets/js/terrain-model.js`, sin coordenadas geográficas, CRS o unidades físicas. Colores por altura, no por litología. Giro, inclinación, zoom, exageración vertical, malla y fila del perfil son controles de visualización. El perfil y la descarga conservan alturas originales. La línea de sección se superpone a la superficie para facilitar su lectura; no se usa para reconstruir subsuelo. No hay imagen generada por IA ni fotografía presentada como evidencia: es un objeto matemático de prueba.

### Nazca y Sudamérica

Geometría deliberadamente **conceptual**, no derivada de Slab2. Entrada simplificada en longitud −80,5°, constante a lo largo de la ventana; profundidad `0.3*d + 0.0007*d²`, donde `d=max(0,(longitud+80.5)*111)` km. Es una función inventada para probar una superficie descendente hacia el este; no describe geometría, velocidad ni espesor reales. No modela espesor continental, astenosfera, deformación, temperatura, fusión, ruptura ni evolución temporal. No ajustar la función para hacer coincidir sismos.

Los hipocentros sí proceden de la copia USGS ya preservada para [Andes Pulso](../andes-pulso.html): 2661 eventos, M ≥ 4, 1900–2025; ventana −83 a −74,5° y −5,5 a 2,5°, no frontera administrativa. Descargada el 2 de octubre de 2026. Se exige SHA-256 antes de mostrar registros. La escena filtra magnitud mínima, año final y profundidad máxima; omite profundidad ausente, negativa o superior a 700 km. No convierte desconocidos en 0 km. Registro original, fuente y precisiones disponibles: [manifiesto](../data/cases/memoria-sismica-1900-2025/manifest.json). Las profundidades son estimaciones; su calidad, fijación e incertidumbre varían por evento. No se representa aquí una elipse de incertidumbre.

Conversión visual horizontal local: `x=(lon+78.75)*111*cos(−1.5°)`, `y=−(lat+1.5)*111`; profundidad `z=−depth`, todo dividido por 450 para dibujar. Es una aproximación plana de kilómetros por grado, no una reproyección GIS precisa. La exageración vertical es explícita, de 1 a 2. Los puntos se dibujan sobre una malla transparente; no hay oclusión física. No medir inclinaciones reales, distancias exactas ni atribuir mecanismo focal a partir de esta escena. Las profundidades numéricas de la ficha no cambian al exagerar la geometría. No hay eventos de 2026 ni consulta en vivo.

El selector permite revisar cada evento visible sin usar el ratón sobre el lienzo. Fecha UTC, magnitud/tipo, profundidad, coordenadas e ID llevan a la ficha USGS. Tamaño del punto es una ayuda visual, no energía ni área de ruptura. Colores: <70 km, 70–<300 km, ≥300 km. Seleccionar otro filtro elimina una selección que deja de ser visible.

### Para pasar del borrador a un modelo defendible

1. Relieve: elegir DEM con fuente/licencia, resolución, CRS horizontal y datum vertical; verificar NoData y límites, producir una malla ligera y conservar originales.
2. Formaciones: revisar CRS y georreferenciación de los archivos del usuario. Una capa de afloramientos no define por sí sola contactos en profundidad.
3. Subducción: integrar un recorte de [Slab2, Hayes (2018), DOI 10.5066/F7PV6JNV](https://www.usgs.gov/data/slab2-a-comprehensive-subduction-zone-geometry-model), con incertidumbre y cobertura. Sigue siendo un modelo publicado, no una medición directa de toda la placa. Artículo: [Hayes et al., 2018](https://doi.org/10.1126/science.aat4723).
4. Sismos: conservar consulta/fecha, revisar incertidumbres y selección temporal; mantener la distinción entre distribución de hipocentros e interfaz modelada.

## Navegación y aprendizaje

Inicio: accesos directos antes de la portada y portada más compacta. Visor: botones de panel Capas/Catálogo/Fuentes/Guía que no tocan interruptores ni el estado de capas; la selección de Tierra/Agua/etc. sigue operando por separado. Aprender: selector de capítulos que usa los enlaces internos y revela la historia correspondiente; tres síntesis introductorias con fuentes. No se afirma haber revisado exhaustivamente todo el material anterior.

Fuentes introductorias consultadas: [USGS, rocas](https://pubs.usgs.gov/gip/collect1/collectgip.html), [USGS, cuencas](https://www.usgs.gov/water-science-school/science/watersheds-and-drainage-basins), [USGS, modelos 3D](https://pubs.usgs.gov/of/2001/of01-223/jachens.html), [IG-EPN, sismos](https://www.igepn.edu.ec/publicaciones-para-la-comunidad/comunidad-espanol/tripticos/16479-triptico-sismos-generalidades/file). Síntesis propias, sin copiar imágenes ni sustituir las fuentes locales de cada historia.

## Prueba del usuario

- Inicio: entrar directamente al visor, 3D, cartoteca, laboratorio y Aprender.
- Visor: cambiar sistema, panel y combinación; comprobar que ninguna capa cambia solo por abrir Fuentes o Guía.
- Aprender: elegir un capítulo de otra historia, cambiar ES/EN y usar Atrás; revisar fuentes y ejercicios.
- 3D: alternar escenas, girar con ratón/tacto o controles, filtrar sismos hasta cero resultados, seleccionar una ficha y restablecer. Comprobar que la profundidad de la ficha permanece igual con exageración ×2.
- Relieve: cambiar perfil, descargar JSON y confirmar marca sintética y alturas originales.
- Informar página, idioma, dispositivo, pasos y resultado esperado/observado. No hace falta cargar aún datos personales o inéditos para probar estos controles.
