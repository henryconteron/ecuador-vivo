# Estudio local de video

Editor Streamlit para la plantilla cartográfica vertical de Ecuador Vivo. Inicio de usuario: doble clic en `Abrir editor de videos.vbs` en la raíz del repositorio.

La [guía de uso](../../documentation/GUIA-EDITOR-VIDEOS.md) explica datos, diseño, créditos, exportación y límites científicos.

## Desarrollo

Python 3.13 probado en Windows. Instalar `requirements.txt` en un entorno virtual. Desde esta carpeta, ejecutar `python -m streamlit run app.py`; la configuración liga el servidor únicamente a 127.0.0.1:8510. El dibujado usa fuentes Segoe UI de Windows. No desplegar este editor como servicio público sin autenticación, aislamiento y revisión de seguridad.

Pruebas desde la raíz: `python -m unittest discover -s production/video_studio -p 'test_*.py' -v`, usando el entorno del editor. La prueba de lluvia usa la caché de 2024 o requiere red para descargar una fecha y los límites.

`model.py` valida proyectos; `data.py` importa y prepara matrices; `render.py` comparte el dibujado entre PNG y MP4; `maqueta.py` compone el mapa vertical e incluye un inset visible de Galápagos; `endcard.py` calcula y dibuja la tarjeta final de métricas; `jobs.py` ejecuta procesos independientes y registra procedencia; `app.py` implementa la interfaz. Todos los resultados y cachés viven en `_local/video-studio/`, excluido de Git. Los proyectos anteriores se migran sin perder sus ajustes.

## Cierre de métricas

En `Cierre final` se puede activar una tarjeta posterior al mapa, editar sus
textos y elegir su duración. Las cifras se calculan con los mismos rásteres
que generan el video: fecha con mayor promedio espacial, mes destacado,
promedio del periodo, máximo por píxel y ranking de provincias. Cada provincia
se calcula como la media de los píxeles válidos del ráster fuente dentro de su
polígono ADM1; no es el valor de la capital provincial ni un promedio de los
colores del mapa. En el encuadre nacional aparecen las 24 provincias,
incluida Galápagos. El promedio nacional pondera cada fila por el coseno de su
latitud; no confunde las celdas geográficas con áreas idénticas.

Elige la operación temporal según la física de la variable: **Acumular** para
cantidades por intervalo (CHIRPS: mm/día → mm del periodo) y **Promediar**
para variables intensivas (°C, NDWI, anomalías). Los valores negativos de
temperatura e índices siguen siendo datos válidos. Las capas categóricas no
permiten este cierre numérico porque sus códigos no se pueden promediar. El
resumen queda en `receipt.json` y la imagen independiente en `endcard.png`;
así cada publicación conserva una traza reproducible de lo que se mostró.
Galápagos se representa en el mapa
cuando el encuadre es Ecuador completo, incluso cuando el valor diario es 0
mm (0 es dato válido, no NoData). El inset conserva la proporción geográfica,
queda dentro del recorte social y no cubre el continente. Usa la misma paleta
y escala que el mapa principal. Su media y máximo diarios se calculan sobre
los píxeles originales válidos de CHIRPS en el encuadre insular, antes del
suavizado visual; los valores -9999 y el océano se excluyen. No se extrapola
lluvia a celdas sin datos: esas áreas quedan transparentes dentro del recuadro.
Un error al leer la escena interrumpe la generación con el error visible.
