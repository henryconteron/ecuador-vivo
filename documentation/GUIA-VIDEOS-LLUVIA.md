# Cómo hacer tú mismo el último video de lluvia

Esta guía reproduce el diseño del video diario de 2024 que ya viste: fondo oscuro,
mapa de Ecuador continental, fecha, ciudades, colores, leyenda y fuentes.
El programa hace todo el montaje. No necesitas diseñar cada imagen ni usar IA.

Para ampliar el archivo, consulta [Descargar datos históricos, recientes y otras
variables para videos](GUIA-DATOS-PARA-VIDEOS.md). Incluye un descargador sin render
y una receta de exportación numérica de lluvia y temperatura desde Earth Engine.

## 1. Qué tienes listo

Carpeta del proyecto en tu computadora (el nombre local sigue siendo `fallas-ecuador`):

```text
C:\Users\JHONY CONTERON\OneDrive\Documentos\GitHub\fallas-ecuador
```

Dentro encontrarás:

- `production/monitor/render_daily_rain.py`: el programa que hizo el video.
- `production/monitor/requirements-daily-rain.txt`: las versiones de sus cuatro dependencias.
- `_local/climate-studio/2024-01-01-366days/`: el video completo, sus datos y su registro.

Verificado el 6 de octubre de 2026: esa carpeta contiene los **366 archivos diarios
de 2024**, aproximadamente **1,31 GiB** de datos comprimidos. El MP4 pesa unos 22 MB.
También hay pruebas de siete días de enero y junio.

El resultado anual tiene 1080 × 1920 píxeles, 30 fps y dura **9 minutos y 9 segundos**.
Cada día permanece 1,5 segundos: 366 × 1,5 = 549 segundos.
2024 es bisiesto, por eso contiene 366 días.

Estos archivos están excluidos de Git. Un commit o un push no los respalda:
conserva una copia de la carpeta de resultados si quieres preservarlos.

## 2. Abrir la terminal en el lugar correcto

1. Abre la carpeta del proyecto en el Explorador de archivos de Windows.
2. Haz clic derecho en un espacio vacío y selecciona **Abrir en Terminal**.
3. Usa una pestaña de **PowerShell**. Los comandos de esta guía son para PowerShell.
4. Pega lo siguiente y presiona Enter:

```powershell
Set-Location -LiteralPath 'C:\Users\JHONY CONTERON\OneDrive\Documentos\GitHub\fallas-ecuador'
python --version
```

La instalación usada para el video es Python 3.13.12. En esta computadora ya
funcionó; no necesitas reinstalar Python.

Comprueba que las dependencias siguen disponibles:

```powershell
python -c "import numpy, PIL, rasterio, imageio_ffmpeg; print('Todo listo para renderizar')"
```

Si aparece `Todo listo para renderizar`, continúa al paso 3.
Si aparece `ModuleNotFoundError`, instala las dependencias con:

```powershell
python -m pip install -r production/monitor/requirements-daily-rain.txt
```

Este paso necesita Internet y normalmente solo se hace una vez. Instala las
versiones usadas en el video revisado. No instala toda la aplicación del atlas.
Si Windows no encuentra `python`, prueba `py -3.13 --version`; si funciona,
usa `py -3.13` en lugar de `python` en los comandos siguientes.

## 3. Reproducir exactamente el año completo

Primero, si quieres conservar el MP4 anterior, cópialo desde el Explorador a otra
carpeta o duplícalo con otro nombre. Ejecutar otra vez el mismo periodo sobrescribe
su MP4, las dos imágenes de muestra y el registro de resultados.

Ejecuta:

```powershell
python production/monitor/render_daily_rain.py --start 2024-01-01 --days 366
```

Eso es todo. El programa reutiliza los archivos de 2024 presentes en esa carpeta,
genera el mapa de cada fecha y construye el video. La apariencia y el ritmo serán
los del último video mientras mantengas el programa sin cambios. No prometemos
un archivo idéntico byte a byte si cambian Python, las bibliotecas o las fuentes.

Verás mensajes como `Loading 2024-01-01`, `Loading 2024-01-02`, etc.
**Loading también aparece cuando usa un archivo local**: no significa que siempre
lo esté descargando de nuevo.

Mantén abierta la terminal y evita que la computadora se suspenda. Puedes usarla
para otras cosas, aunque el procesamiento puede ir más lento. La duración del
proceso depende del equipo y, cuando faltan archivos, de la conexión.

El proceso termina cuando imprime la ruta del MP4 y vuelve a aparecer el indicador
de PowerShell. Para abrir el resultado:

```powershell
Invoke-Item -LiteralPath '_local/climate-studio/2024-01-01-366days/ecuador-lluvia-diaria-preview.mp4'
```

No necesitas Google Earth Engine, una suscripción de edición ni créditos de IA
para esta ejecución. Utiliza tu computadora; si faltan datos, los descarga desde
el servidor público de CHIRPS.

## 4. Hacer otro periodo con la misma presentación

Solo hay dos opciones de fecha: `--start` y `--days`. La fecha inicial está incluida.
Se admite de 1 a 366 días por ejecución. No existe una opción `--year` o `--end`.

| Qué quieres generar | Fecha inicial | Días | Duración del video |
| --- | --- | --- | --- |
| Prueba de enero de 2024 | 2024-01-01 | 7 | 10,5 segundos |
| Enero de 2024 completo | 2024-01-01 | 31 | 46,5 segundos |
| Año 2024 completo | 2024-01-01 | 366 | 9 min 9 s |
| Año 2023 completo | 2023-01-01 | 365 | 9 min 7,5 s |

Ejemplo para otro año:

```powershell
python production/monitor/render_daily_rain.py --start 2023-01-01 --days 365
```

La salida estará en:

```text
_local/climate-studio/2023-01-01-365days/ecuador-lluvia-diaria-preview.mp4
```

El generador descarga las fechas que no encuentre en la carpeta de ese periodo.
Todavía no hemos verificado aquí una descarga completa de 2023.
Para fechas recientes, primero revisa que el servidor haya publicado todos los
días elegidos. No presentes un periodo parcial de 2026 como un año completo.

**Detalle importante de la caché:** se guarda por periodo, no en una carpeta
compartida. Pedir enero con `--days 31` crea otra carpeta y no reutiliza
automáticamente los archivos de la carpeta anual. Para ahorrar descargas puedes
copiar, sin mover, los `.tif.gz` de enero y `ecuador.geojson` desde la carpeta anual
a `_local/climate-studio/2024-01-01-31days/` antes de ejecutar. Conserva sus nombres.
También puedes recortar enero del MP4 anual si no necesitas que el contador diga 31.

## 5. Comprobar que salió completo

En la carpeta de cada periodo deben aparecer:

- `ecuador-lluvia-diaria-preview.mp4`: el video.
- `frame-AAAA-MM-DD.png`: imágenes del primer y último día.
- `receipt.json`: fechas, fuentes, huellas SHA-256 y método de representación.
- `chirps-v2.0.AAAA.MM.DD.tif.gz`: los datos diarios comprimidos.
- `ecuador.geojson`: los límites usados para recortar el mapa.

Para el anual de 2024 puedes comprobar lo siguiente:

```powershell
$rainResult = '_local/climate-studio/2024-01-01-366days'
$rainReceipt = Get-Content "$rainResult/receipt.json" -Raw | ConvertFrom-Json
$rainReceipt.frames.Count
$rainReceipt.frames[0].date
$rainReceipt.frames[-1].date
$rainActualHash = (Get-FileHash "$rainResult/ecuador-lluvia-diaria-preview.mp4" -Algorithm SHA256).Hash
$rainActualHash -eq $rainReceipt.video_sha256
```

Debe mostrar `366`, `2024-01-01`, `2024-12-31` y `True`.
Eso confirma el registro y que el video coincide con su huella guardada; no
sustituye la revisión visual. Reproduce el comienzo, una parte intermedia y el final.
El campo `missing_cells` cuenta celdas sin dato en el rectángulo de lectura,
incluido el océano; no equivale al número de días faltantes.

## 6. Qué hacer si se detiene

- **Error de Internet o timeout:** espera a recuperar la conexión y ejecuta el
  mismo comando. Los datos ya guardados se reutilizan. El MP4 se vuelve a construir
  desde el primer día; no continúa desde el fotograma donde se interrumpió.
- **HTTP 404:** comprueba la fecha y que exista el archivo en el servidor. Puede
  ser una fecha aún no publicada. No la sustituyas por cero lluvia.
- **Archivo gzip/TIFF corrupto:** identifica la última fecha del mensaje de error,
  mueve solo su `.tif.gz` a una carpeta de respaldo y repite. Se descargará otra vez.
- **PermissionError:** cierra el video si lo tienes abierto y vuelve a intentarlo.
- **Faltan las fuentes Segoe UI:** el diseño usa las fuentes de Windows
  `C:/Windows/Fonts/segoeui.ttf` y `segoeuib.ttf`; no es todavía un generador portátil
  listo para macOS o Linux.
- **Se cerró antes de terminar:** puede existir un MP4 parcial y un registro de
  una ejecución anterior. No lo consideres terminado por ver el archivo; espera
  a que la nueva ejecución finalice y comprueba su huella como en el paso 5.

## 7. Cómo mejorarlo sin rehacer todo

### Primero: adaptar el ritmo

Guarda el anual de 9:09 como copia principal para examinar fechas con calma.
Para redes, duplica el video en tu editor y prueba velocidad **6×**: durará
**91,5 segundos**. A **12×**, durará **45,75 segundos**. Usa cambio normal de velocidad,
sin generación de cuadros por flujo óptico: ese efecto inventaría transiciones
entre patrones de días diferentes. Revisa que las fechas sigan siendo legibles.

Si prefieres generar directamente una versión corta, haz antes una copia del
programa. Busca `for _ in range(45):` y cambia solo el `45`:

| Repeticiones por día, a 30 fps | Tiempo por día | Duración para 366 días |
| --- | --- | --- |
| 45, original | 1,5 s | 549 s |
| 15 | 0,5 s | 183 s |
| 5 | 0,167 s | 61 s |

Cada fecha sigue representada. Copia el MP4 anterior a otra carpeta antes de
renderizar porque el nombre de salida es el mismo. Vuelve a `45` para recuperar
el ritmo original. Estas variantes de ritmo son opcionales y no están aplicadas.

### Después: hacer que el lector entienda lo que ve

- Añade una introducción breve: «Así cambió la lluvia en Ecuador, día por día».
- Añade pausas o rótulos en fechas verificadas que quieras explicar.
- Para comparar años, conserva fuente, unidades, escala y encuadre. Una comparación
  lado a lado ayuda más que cambiar la paleta en cada video.
- Si agregas voz o música, conserva una versión limpia y revisa los derechos del audio.
- Publica junto al video las fuentes y el registro. Respalda los datos originales
  aparte; los archivos `.tif.gz` no son necesarios para reproducir el MP4.

### Nitidez y límites de los datos

La composición ya se genera en Full HD vertical. Exporta desde tu editor a
1080 × 1920, 30 fps, H.264 y calidad alta, y usa el MP4 original para subirlo a redes.
Evita encadenar varias recompresiones o usar una captura de pantalla del video.

Los colores proceden de una malla de 0,05°; el propio video indica ≈5,6 km.
El suavizado espacial mejora su apariencia, pero no añade mediciones. Aunque
exportaras a 4K, no aparecería detalle real de una calle o de un río pequeño.
Conserva las notas sobre resolución e interpolación.

El mapa muestra **acumulación diaria de precipitación en mm**, no lluvia instantánea,
probabilidad de lluvia, inundaciones ni observaciones de pluviómetros en las ciudades
rotuladas. Los puntos de ciudades sirven para orientarse. Un mapa por sí solo tampoco
demuestra que un cambio haya sido causado por El Niño, La Niña o una actividad humana.

Para personalizar textos sin cambiar datos, busca las frases exactas en el programa
con Ctrl+F, modifica solo lo que está entre comillas y prueba primero siete días.
Títulos más largos pueden salirse del cuadro. Cambiar fuente de datos, variable,
proyección o unidades requiere adaptar y revisar el procesamiento.

## 8. Qué falta para temperatura y los demás videos

Este programa solo procesa **lluvia CHIRPS v2 diaria**. No acepta como entrada
un video exportado de Earth Engine ni las imágenes de temperatura.

Existen recetas para temperatura, anomalías y climatologías en `scripts/`, pero
eso no confirma que sus datos estén descargados o que el montaje equivalente
esté terminado. Para llevarlas al mismo diseño hay que conectar su variable,
fechas y unidades, definir una leyenda adecuada y generar un registro de fuentes.
No basta con cambiar «lluvia» por «temperatura» en el título.

Puedes repetir de forma autónoma los videos de lluvia con esta guía; la adaptación
a otras variables es un trabajo distinto pendiente.

## Fuentes y archivos para consultar

- Datos diarios originales: https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/2024/
- Catálogo y descripción de CHIRPS: https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY
- Límite geográfico: URL exacta y revisión de geoBoundaries en `receipt.json`.
- Método y notas del proyecto: `documentation/video-clima-diario.md`.

No necesitas volver a pedirle a Codex que renderice cada periodo: una vez
disponibles Python y las dependencias, tú ejecutas el comando del paso 3 o 4.
