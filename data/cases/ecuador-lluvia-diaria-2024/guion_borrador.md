# 365 días de lluvia sobre Ecuador

## Idea

Una animación diaria convierte un año completo de lluvia en una experiencia
visual. El espectador ve primero el patrón y después aprende a leerlo: el
color codifica milímetros acumulados por día; el relieve sombreado solo aporta
contexto espacial.

La edición visual usa remuestreo bilineal exclusivamente para que la transición
entre celdas no domine la pantalla. El video no tiene más resolución que IMERG.
Para el formato corto tipo GeoPanda, la comparación recomendada es la pieza
mensual climatológica 1991–2020, que tiene 12 cuadros y una escala fija.

## Guion de voz (borrador)

**[0–4 s · mapa oscuro, aparece la fecha]**

Esta es la lluvia que cayó sobre Ecuador durante un año. Bueno: la mejor
estimación satelital que tenemos para cada celda del mapa.

**[4–12 s · comienza el avance diario]**

Cada cambio de color es un día distinto. El azul representa poca lluvia; el
amarillo y el rojo, más agua acumulada. No estamos viendo una foto del clima:
estamos viendo una película de 366 días.

**[12–24 s · se ilumina la cordillera]**

Mira los Andes. La cordillera no fabrica agua, pero obliga al aire húmedo a
subir. Al subir, el aire se enfría y la humedad puede condensarse. Por eso un
mapa de lluvia también cuenta una historia de montañas, vientos y océano.

**[24–36 s · transición hacia la Amazonía]**

Ahora mira el Napo. Un día rojo no significa automáticamente una inundación:
para saberlo necesitamos el cauce, el suelo, la pendiente y cuánto tiempo dura
la lluvia. La imagen plantea una pregunta; no inventa una respuesta.

**[36–48 s · pausa, aparece una celda ampliada]**

Y aquí está la trampa visual. Cada píxel mide aproximadamente once kilómetros.
Puedes hacer zoom, pero no estás viendo una estación meteorológica en tu barrio.
Es una estimación de satélite para una celda grande.

**[48–60 s · leyenda y fórmula]**

La banda original de IMERG es una tasa en milímetros por hora. Para obtener
un acumulado diario sumamos los 48 intervalos de treinta minutos y multiplicamos
por media hora. En una línea: tasa por tiempo es acumulado.

**[60–72 s · cierre]**

La próxima vez que veas un río crecido, recuerda que el agua empezó mucho
antes de llegar al cauce. A veces, para entender un paisaje, hay que mirar la
lluvia como una película.

## Ficha técnica

- **Producto:** NASA/GPM IMERG V07, banda `precipitation`.
- **Periodo:** 1 de enero a 31 de diciembre de 2024 (año bisiesto, 366 días).
- **Resolución temporal:** 30 minutos, 48 imágenes por día.
- **Conversión:** `sum(mm/h) × 0,5 h = mm/día`.
- **Resolución nativa:** 0,1° (aprox. 11 km en Ecuador).
- **Contexto topográfico:** relieve sombreado de USGS/SRTMGL1_003.

## Límites que deben aparecer en la descripción

Esta animación muestra una estimación satelital de precipitación. No es una
medición puntual de pluviómetro, no calcula caudal ni extensión de inundación y
no permite atribuir por sí sola un cambio a minería u otra actividad humana.
El relieve sombreado es contexto visual, no una segunda variable codificada.

## Créditos

NASA GPM IMERG V07; NASA Earthdata; Google Earth Engine; USGS SRTM. Conservar
el recibo JSON exportado junto con el video y enlazar la documentación del
producto en la publicación.
