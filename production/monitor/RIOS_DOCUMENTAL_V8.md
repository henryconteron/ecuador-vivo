# ¿Qué le pasó al río? — montaje documental v8

Producción horizontal 1920 × 1080, animaciones a 30 fotogramas por segundo.
Carpeta: `artifacts/rios_documental_v8`. No modifica el atlas, la aplicación
ni las versiones anteriores. No incluye publicación ni contratación de servicios.

Primer montaje completo exportado: **11 min 36,9 s**, 35 tomas y 20 907
fotogramas. Archivo: `que_le_paso_al_rio_v8.mp4` (H.264 / AAC, 38 820 006 bytes).
SHA-256: `da834a76c9efa0cac71c56f166dd21d7158f1885adbe2b3a8328b51418dfaedb`.
Cuatro pruebas automatizadas aprobadas. Decodificación completa sin errores,
señal de audio hasta la última palabra de cada toma, límites de subtítulos y
capturas del archivo codificado comprobados en `verification.json`.
Revisadas visualmente las muestras de las 35 tomas y ampliaciones de la
comparación y del umbral. Esto no sustituye una escucha humana completa ni
la revisión científica final. El archivo v6 conserva su hash anterior.

## Dirección narrativa

Fortaleza de v7: voz de conversación, analogías antes de las fórmulas y una
pregunta comprensible. Debilidad: abrir con fotos de un río poco conocido hacía
depender demasiado el gancho del lugar. Mejora: un puente sobre el Colorado,
sin agua debajo, y el retorno del agua nueve días después. La recompensa no
es un culpable inventado: es descubrir la intervención documentada y aprender
a separar imágenes, mediciones e inferencias. Estrategia: público sin formación
previa, sin duración arbitraria y sin imitar una voz o copiar un guion ajeno.

Las habilidades de crítica creativa y narrativa visual influyeron en el cambio
de apertura y el regreso al Colorado al final. Secuencia: sorpresa real →
nivel y caudal → luz invisible → contraste → experimento con umbral → resolución
→ Ecuador → observaciones repetidas y causalidad → regreso a la pregunta.

Momentos clave: seco/agua, las piedras que no se mueven, el mapa que pierde
azul sin perder agua y el zoom que no puede resolver una medición mezclada.
Estética: fotografías a pantalla grande, mapas con geometría constante y
esquemas originales con movimiento explicativo. La animación no convierte
las fotografías en una película falsa ni finge trabajo de campo.

## Caso Colorado y atribución fotográfica

- **20 de marzo de 2014**, Colorado River at Southerly International Boundary,
  antes del pulso. [Página del USGS](https://www.usgs.gov/media/images/colorado-river-pulse-flow).
- **29 de marzo de 2014**, mismo lugar informado por el USGS, durante el pulso.
  [Página del USGS](https://www.usgs.gov/media/images/colorado-riverduring-pulse-flow).
- Ambas páginas indican **Public Domain**. Crédito: USGS / Communications and
  Publishing. No se inventa el nombre de un fotógrafo que esas fichas no dan.
  Se conservan los archivos originales de 4608 × 2592 y sus hashes.
- Los encuadres difieren: sirven para contraste visual, **no** para medir cambios
  de superficie mediante una superposición. No se registran ni deforman.
- Contexto: [USGS (2016), A River Ran Through It and Brought Life, At Least for a While](https://www.usgs.gov/news/featured-story/a-river-ran-through-it-and-brought-life-least-a-while).
  Pulso controlado de 2014 en el delta, dentro del acuerdo binacional Minute 319.
  No se afirma que todo el Colorado estuviera seco ni que se recuperara de
  forma permanente. El mecanismo animado es cualitativo, no la geometría real.

## Datos y límites del caso ecuatoriano

Jatunyacu: **11 JUL 2019 / 08 AGO 2024 / 29 JUL 2026**. Recortes de Sentinel-2
ya auditados en v4 y v6. Esta versión verifica los originales y copia solamente
las imágenes y arreglos que necesita. `sources_manifest.json` registra hashes,
fuentes, fechas, cuadrícula y transformaciones de presentación.

Cuadrícula común de 20 m; visualización por vecino más cercano sin inventar
detalle. B3 originalmente 10 m; B11 originalmente 20 m. Soporte común:
34 308 celdas. MNDWI = (B3 − B11) / (B3 + B11), con reflectancias corregidas
y metadatos de la versión anterior. Umbrales **>0 y >0,2** solo demostrativos:
947 y 681 celdas candidatas, respectivamente. No es un mapa de agua validado,
superficie seca medida, caudal, concentración ni prueba de una causa.
Durante el movimiento, el número del umbral se muestra redondeado a dos
decimales; el conteo usa el umbral subyacente, no ese rótulo redondeado.

La trama conserva los casos sin soporte válido; no es lecho seco. La paleta del
índice coincide con la de los archivos auditados. La barra de 1 km corresponde
a 50 celdas UTM de 20 m. Los cortes temporales son discretos; no se interpolan
estados del río. Nivel, morfología y desecación requieren observaciones y
referencias adicionales. No se identifica minería con un cambio de color.

## Bibliografía científica

- [USGS, How Streamflow is Measured](https://www.usgs.gov/water-science-school/science/how-streamflow-measured): caudal, sección y velocidad.
- [USGS, Geomorphology, Sediment, and Habitat](https://www.usgs.gov/centers/washington-water-science-center/science/science-topics/geomorphology-sediment-and-habitat): transporte, erosión y depósito.
- [Xu (2006)](https://doi.org/10.1080/01431160600589179): MNDWI; no validación local ecuatoriana.
- [Sentinel-2 SR, catálogo de bandas](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED): referencia instrumental. Los archivos utilizados proceden de Earth Search, no de una exportación nueva de GEE.
- [Cavallo et al. (2025)](https://doi.org/10.1016/j.jhydrol.2025.133416): seguimiento de lechos secos en Italia; resultados no trasladados a Napo.
- [Dethier et al. (2023)](https://doi.org/10.1038/s41586-023-06309-9): minería aluvial y sedimentos en ríos tropicales; no atribución causal en nuestro recorte.
- Procedencia completa: [NAPO_RIOS_METODOS_V4.md](NAPO_RIOS_METODOS_V4.md) y [RIOS_DIRECCION_V7.md](RIOS_DIRECCION_V7.md).

Contains modified Copernicus Sentinel data (2019, 2024, 2026).
Procesamiento, guion y divulgación: Henry Conteron / Ecuador Vivo.

## Voz, subtítulos y revisión

### Capítulos del montaje

```text
00:00 El puente sin agua
01:31 Nivel, lecho y caudal
02:52 Lo que registra el satélite
03:51 MNDWI: dos señales
04:52 El mapa que cambia sin sacar agua
06:09 El límite del zoom
06:50 Ecuador: 2019, 2024 y 2026
08:09 Cómo investigar la desecación
09:07 Qué prueba una causa
10:10 Volvamos al Colorado
11:15 Fuentes y créditos
```

Voz sintética **es-EC-LuisNeural**, no voz del autor ni de un divulgador imitado.
Acceso sin clave de pago mediante `edge-tts` 7.2.7, aislado en
`artifacts/river_voice_runtime`; no altera dependencias de la aplicación.
Se envía exclusivamente el texto original de la narración al servicio de voz.
No se introducen credenciales ni se adquiere un plan. Disponibilidad futura y
condiciones del servicio deben revisarse si se reutiliza o publica comercialmente.

Cada toma dispone de audio separado y tiempos de palabras del sintetizador;
subtítulos sincronizados a esos eventos, no por reparto proporcional de palabras.
Revisión humana final de pronunciación y subtítulos recomendada. El guion limpio
`GUION_PARA_GRABAR.md` permite sustituir la locución por una grabación personal.

Para regenerar desde `monitor-sismos`, usando el entorno de video:

1. `venv\Scripts\python.exe reel_rivers_documentary.py prepare`
2. `venv\Scripts\python.exe reel_rivers_documentary.py voices` (reutiliza caché)
3. `venv\Scripts\python.exe reel_rivers_documentary.py storyboard`
4. `venv\Scripts\python.exe -m unittest discover -s tests -p test_rivers_documentary.py`
5. `venv\Scripts\python.exe reel_rivers_documentary.py export`
6. `venv\Scripts\python.exe verify_rivers_documentary.py`

La generación no publica. El video necesita la revisión científica/editorial
final del autor antes de compartirse como pieza definitiva.
