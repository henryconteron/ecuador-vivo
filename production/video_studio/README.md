# Estudio local de video

Editor Streamlit para la plantilla cartográfica vertical de Ecuador Vivo. Inicio de usuario: doble clic en `Abrir editor de videos.vbs` en la raíz del repositorio.

La [guía de uso](../../documentation/GUIA-EDITOR-VIDEOS.md) explica datos, diseño, créditos, exportación y límites científicos.

Los tres tipos de video comparten **Datos → Maqueta → Montaje → Exportar**.
Maqueta muestra un único lienzo editable, sin una vista previa paralela. Eliminar
un elemento se guarda en el proyecto y se respeta al exportar; puede recuperarse.
Cada **OK** actualiza un borrador de trabajo, sin sobrescribir el proyecto original.
Los tiempos y formatos se editan únicamente en Montaje, y generar/guardar versiones
queda en Exportar. `workspace.py` comparte esa navegación y valida el diseño actual.

La sección **Obtener datos** conecta CHIRPS v3 y NASA POWER con el editor y
permite descargar series observadas por estación desde INAMHI. El detalle de
productos, fechas, créditos y limitaciones está en la
[guía de fuentes](../../documentation/video-studio-fuentes-de-datos.md). Los
portales IGM, IIGE, IG-EPN, INOCAR, IEDG y Datos Abiertos aparecen como
catálogo de descubrimiento; aún no se presentan como descargas automatizadas.

En **Editor → Tipo de video → Comparación climática** se comparan meses entre años y territorios,
presenta ENSO/Pacífico y exporta una maqueta social vertical con su MP4, CSV,
ranking provincial y recibo de trazabilidad. El comparador usa los mismos
descargadores y caché local que el editor; ya no tiene un lanzador independiente.

## Desarrollo

Python 3.13 probado en Windows. Instalar `requirements.txt` en un entorno virtual. Desde esta carpeta, ejecutar `python -m streamlit run app.py`; la configuración liga el servidor únicamente a 127.0.0.1:8510. El dibujado usa fuentes Segoe UI de Windows. No desplegar este editor como servicio público sin autenticación, aislamiento y revisión de seguridad.

Pruebas desde la raíz: `python -m unittest discover -s production/video_studio -p 'test_*.py' -v`, usando el entorno del editor. La prueba de lluvia usa la caché de 2024 o requiere red para descargar una fecha y los límites.

`model.py` valida proyectos; `data.py` importa y prepara matrices; `render.py` comparte el dibujado entre PNG y MP4; `maqueta.py` compone el mapa vertical e incluye un inset visible de Galápagos; `endcard.py` calcula y dibuja la tarjeta final de métricas; `jobs.py` ejecuta procesos independientes y registra procedencia; `app.py` implementa la interfaz. Todos los resultados y cachés viven en `_local/video-studio/`, excluido de Git. Los proyectos anteriores se migran sin perder sus ajustes.

## Cierre de métricas

En **Maqueta → Configuración de la plantilla → Cierre final** se puede activar
una tarjeta posterior al mapa y definir sus textos base. El lienzo edita sus
elementos; su duración se elige en **Montaje**. Las cifras se calculan con los mismos rásteres
que generan el video: fecha con mayor promedio espacial, periodo destacado,
promedio del periodo, máximo por píxel y ranking de provincias. Cada provincia
se calcula como una estadística zonal de píxeles válidos del ráster fuente
dentro de su polígono ADM1; en CRS geográficos se pondera aproximadamente por
área con cos(latitud), y en CRS proyectados se usa media de píxeles nativos.
No es el valor de la capital provincial ni un promedio de los colores del mapa.
En el encuadre nacional el ranking contiene las 24
provincias, incluida Galápagos. El promedio y los extremos que aparecen en la
tarjeta corresponden al Ecuador continental —el dominio del mapa principal—;
el `receipt.json` declara esa diferencia para no presentar una estadística
continental como si incluyera automáticamente las islas. El promedio principal
pondera cada fila por el coseno de su latitud; no confunde las celdas
geográficas con áreas idénticas.

La regla automática elige la operación según la física de la variable:
**Acumular** para cantidades por intervalo (CHIRPS: mm/día → mm del periodo)
y **Promediar** para variables intensivas (°C, NDWI, anomalías). El modo
manual no permite sumar una variable intensiva. Los valores negativos de
temperatura e índices siguen siendo datos válidos. Una dirección tampoco se
promedia aritméticamente: se debe importar como componentes u/v o como media
circular calculada previamente. Las capas categóricas no permiten este cierre
numérico porque sus códigos no se pueden promediar. El resumen queda en
`receipt.json` y la imagen independiente en `endcard.png`; así cada publicación
conserva una traza reproducible de lo que se mostró.
Galápagos se representa en el mapa
cuando el encuadre es Ecuador completo, incluso cuando el valor diario es 0
mm (0 es dato válido, no NoData). El inset conserva la proporción geográfica,
queda dentro del recorte social y no cubre el continente. Usa la misma paleta
y escala que el mapa principal. Su media y máximo diarios se calculan sobre
los píxeles originales válidos de CHIRPS en el encuadre insular, antes del
suavizado visual; los valores -9999 y el océano se excluyen. No se extrapola
lluvia a celdas sin datos: esas áreas quedan transparentes dentro del recuadro.
Un error al leer la escena interrumpe la generación con el error visible.
# Andes Pulso: preparar una ficha tras exportar

Cuando una exportación termina, la pestaña **Exportaciones** permite preparar
un borrador del caso directamente en este repositorio. La acción copia el MP4,
la portada, el resumen JSON, el ranking provincial CSV, las fuentes por fecha,
el recibo de trazabilidad y una nota metodológica. El registro se agrega a
`data/cases/registry.json` con estado `draft`; no hace commit ni publica el sitio.

Los GeoTIFF completos permanecen en el equipo: el sitio recibe las cifras
utilizadas y las referencias/huellas SHA-256 de los insumos, no una copia
potencialmente pesada de cada ráster. Revisa la ficha, sus límites y la cita
antes de cambiarla a `published` y hacer commit/push.

## Reglas de las métricas

- Lluvia en unidades por intervalo: suma temporal; el ranking provincial suma
  los promedios espaciales diarios válidos de cada polígono ADM1.
- Temperatura, rapidez del viento, humedad, porcentajes e índices: promedio
  temporal; la temperatura mantiene sus valores negativos cuando corresponda.
- Dirección del viento: el cierre numérico se bloquea hasta importar componentes
  u/v o una dirección ya resumida con media circular.
- El promedio nacional usa pesos aproximados de área (`cos(latitud)`) en la
  rejilla geográfica. Las medias provinciales del GeoTIFF también los usan en
  CRS geográficos; en CRS proyectados usan la media de píxeles nativos.
- Los extremos nacionales se calculan sobre píxeles fuente de las 23 provincias
  continentales, no sobre la rejilla de visualización remuestreada. El ranking
  sí incluye Galápagos como provincia 24.

El resumen, los títulos y etiquetas del cierre salen de los mismos valores que
se guardan en el recibo; `endcard_auto_text` se puede desactivar para editar el
texto manualmente.

## Mapas comparativos y CSV geográficos

El cuerpo audiovisual de la comparación es un mapa o dos mapas con escala común,
no una gráfica de líneas. Los rankings quedan en la tarjeta final. Los campos
mensuales se derivan de los rásteres diarios originales: una tabla de promedios
nacionales no basta para inventar una superficie.

**Editor → Tipo de video → CSV geográfico** admite puntos WGS84 y valores por
provincia. Permite elegir columnas, periodo, categorías, colores, créditos y
duración; genera MP4 y cierre calculado. Los registros de especies se cuentan
como registros, no como individuos o estimaciones de población. Compartir sus
coordenadas en Andes Pulso exige autorización explícita.

Instrucciones y límites: [Guía de mapas y CSV](../../documentation/GUIA-MAPAS-Y-CSV-VIDEOS.md).

## Formatos y montaje local

**Editor → Montaje → Formato y secuencia de tarjetas** ofrece 9:16, 16:9, 1:1, 4:5 y
4:3 en 1080p o 720p. Los mapas y métricas mantienen su proporción y encajan
completos: un formato horizontal añade márgenes, no redistribuye automáticamente
la maqueta vertical.

La secuencia permite imágenes, clips locales de hasta 100 MB, explicaciones,
pausas del último mapa y tarjetas de métricas. Cada tarjeta tiene orden y
duración; los clips tienen inicio, encuadre y audio opcional. No se repiten ni
aceleran clips para rellenar tiempo. Los ejemplos no entran en las estadísticas.
La exportación normaliza a 30 fps y conserva créditos, hashes y fotogramas en
`receipt.json → montage`. Los recursos permanecen en `_local/video-studio/media/`.

Respalda proyectos, insumos y medios juntos. La guía incluye el flujo completo:
[Formatos y montaje](../../documentation/GUIA-EDITOR-VIDEOS.md#elegir-formato-y-montar-una-historia).
