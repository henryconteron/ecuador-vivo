# El pulso térmico de Ecuador

## Idea visual

Un mapa de calor que respira: azules y violetas para el aire frío, amarillos y
rojos para el aire cálido, con un pulso de brillo cada cambio mensual. La
cordillera queda visible como relieve, pero no se confunde con la variable.

## Guion breve

**[0–5 s]** El mismo país puede estar frío y caliente al mismo tiempo. No es
una contradicción: es Ecuador visto como un gradiente de altura, océano y aire.

**[5–18 s]** Este color representa temperatura del aire a dos metros sobre la
superficie. No es la temperatura de una roca ni la de una estación puntual.

**[18–32 s]** El mapa de calor se mueve día a día. En la costa, la Amazonía y
los Andes, la misma atmósfera encuentra superficies y alturas distintas.

**[32–46 s]** La escala está en grados Celsius. El relieve solo ayuda a leer el
mapa; la cifra viene de ERA5-Land, una reconstrucción física combinada con
observaciones.

**[46–58 s]** Y otra advertencia: una celda de unos once kilómetros es un
promedio. Hacer zoom no crea una estación meteorológica nueva.

**[58–68 s]** La temperatura no es solo un número: es la forma en que la
energía del planeta se reparte sobre el paisaje.

## Datos

- ECMWF/Copernicus ERA5-Land Daily Aggregated.
- Banda: `temperature_2m`, kelvin convertido a °C.
- Ventana 2026: enero–agosto, 243 imágenes.
- Resolución nativa: aproximadamente 11 km.
- El producto es reanálisis; no equivale a una medición puntual.
