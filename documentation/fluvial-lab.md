# Ríos bajo la lupa: comparación de métodos, no diagnóstico de minería

## Qué está aplicado

`rivers.html`, accesible desde Agua/Vida en el atlas, compara adquisiciones reales
del **11 julio 2019, 8 agosto 2024 y 29 julio 2026**. Cuatro ventanas editoriales:
Tena, Jatunyacu, Napo y Misahuallí. No son límites administrativos, una red completa
de ríos ni cobertura de toda Napo. Archidona no está incluida en estas ventanas.

El laboratorio es bilingüe, permite zoom y corte entre fechas, conserva la
selección y los umbrales en el enlace, e inspecciona valores numéricos desde
reflectancia float32, no desde los colores. Conserva los visores anuales previos:
son productos diferentes, no se mezclan sus fechas, máscaras ni resoluciones.

| Vista | Cálculo con reflectancia Sentinel-2 | Alcance |
|---|---|---|
| RGB | B4/B3/B2; 0–0,3; gamma 1,2 | Contexto óptico y reconocimiento visual |
| NDWI | (B3−B8)/(B3+B8) | Detector candidato, no agua confirmada |
| MNDWI | (B3−B11)/(B3+B11) | Detector candidato, no ganador local |
| AWEInsh | 4(B3−B11)−0,25B8−2,75B12 | Variante sin sombras; no normalizada |
| AWEIsh | B2+2,5B3−1,5(B8+B11)−0,25B12 | Variante para reducir confusión con sombras |
| Coincidencia | Número de los cuatro métodos que exceden su umbral | Coincidencia, no confianza ni exactitud |
| Transición | Acuerdo 4/4→0/4 o 0/4→4/4 | Pérdida/aparición candidata, no cauce seco confirmado |
| NDTI | (B4−B3)/(B4+B3) | Contraste rojo/verde solo en agua candidata |
| Reflectancia roja | B4, solo en agua candidata | Señal óptica; no mg/L ni NTU |
| NDVI / diferencia | (B8−B4)/(B8+B4); posterior−anterior | Verdor; no clase de bosque, minería o sedimento |

Los umbrales iniciales son **cero, exploratorios y no calibrados**. El usuario
puede variar cada uno: esto modifica el detector, no la imagen original. No se
usa consenso como verdad de campo: los cuatro métodos comparten bandas y errores.
No-agua por consenso no significa arena ni cauce seco. Los cambios se muestran
solo en soporte válido común a ambas fechas; los desacuerdos se conservan en ámbar.
No se generan hectáreas de minería, contaminación, erosión o sequía.

Para NDTI/B4, el gris sólido indica píxeles fuera del agua candidata; la trama
indica falta de soporte común. La selección de agua puede cambiar entre fechas:
no se calcula una diferencia cuantitativa de turbidez sobre esas máscaras distintas.
RGB y NDVI ayudan a revisar barras, pozas y vegetación, pero todavía **no hay
clasificación validada de sedimentos expuestos o excavaciones**.

## Procedencia y resolución

Configuración: `data/fluvial/config.json`; recibo: `data/fluvial/manifest.json`.
Fuentes públicas HTTPS COG de Earth Search / Element 84, colección legacy para
2019 y Sentinel-2 Collection 1 L2A para 2024/2026. Se fijan IDs, fecha/hora,
metadatos STAC, URL de cada banda, escala/offset, cuadrículas y hashes. Los SHA
detectan modificaciones; no son firmas del proveedor ni una validación temática.

Las fechas vienen de la selección previa por calidad local; no se optimizaron
por magnitud de cambio. No son una búsqueda exhaustiva de todas las escenas del
año ni garantizan igualdad de lluvia o caudal. 2019 no es una referencia prístina.
2026 es una escena fechada, **no el año completo ni una vista en vivo**.

Todos los métodos se calculan sobre seis bandas de reflectancia a **20 m,
EPSG:32717**. B2/B3/B4/B8 se agregan mediante media exacta de cuatro muestras
alineadas de 10 m antes de los cocientes. B11/B12 conservan sus 20 m nativos.
Se aplica una sola vez `DN × scale + offset` declarado por el activo STAC;
el constructor rechaza offsets legacy ambiguos ya aplicados. AWEInsh utiliza
**B12**, no repite B11 en su último término.

Máscara conservadora: SCL 4/5/6, seis reflectancias finitas no negativas y
denominadores positivos. SCL no proporciona etiquetas de validación. Esta QA
puede omitir agua real oscura o bajo sombra; todos los ceros/no observación se
distinguen. Una nube no es una observación de cauce seco.

Solo para visualizar se reproyecta a EPSG:3857 con vecino más cercano; el recibo
registra el espaciado web real, que no es exactamente el paso UTM. Banderas QA
binarias explícitas, NoData óptico −9999. Los paquetes son siete planos float32
little-endian comprimidos con gzip, unos **17,8 MB en total**; se cargan dos por
tramo, no toda la colección. Se verifican tamaño, SHA-256, dimensiones y QA antes
de mostrar cualquiera de las dos fechas. Un fallo retira ambas imágenes.

Escalas visuales fijas: cocientes −1/+1, AWEI −1/+1 **solo como intervalo
editorial**, B4 0/0,3 y diferencia NDVI −2/+2. AWEI no tiene rango matemático
−1/+1. Los valores fuera del intervalo saturan el color; el inspector conserva
el valor original. No usar la intensidad azul como cantidad de agua.

## Reproducir sin pago ni credenciales

Desde la raíz del repositorio, con Python y dependencias de `requirements-landcover.txt`:

```powershell
python scripts/build_fluvial_lab.py
pnpm run check:fluvial
python -m unittest discover -s tests -p test_fluvial_science.py
```

El constructor descarga las bandas públicas fijadas y recorta solo las cuatro
ventanas. El trabajo pesado y cachés quedan en `data/raw/fluvial/`, fuera de Git.
No activa facturación ni tareas de Earth Engine. Sí requiere red y espacio local.
`npm run check:fluvial` es equivalente donde npm está disponible.

En esta construcción se utilizó opcionalmente `--reuse` con los GeoTIFF nativos
verificados del video anterior para cinco bandas. No se utilizaron JPEG, PNG ni
imágenes generadas. B12 se descargó de cada adquisición original. La reutilización
se declara con hashes del recibo/crop padre y verificación de cuadrícula,
calibración y bandas. En esos cinco casos `raw_array_sha256` describe el recorte
padre, **no** el nuevo recorte regional. La ejecución sin `--reuse` es autónoma
y obtiene las seis bandas; reconstruir cambia los hashes de procedencia, no
debería cambiar los valores en soporte válido compartido.

## Clasificación multibanda y evaluación: preparada, todavía sin referencias

`scripts/evaluate_fluvial_methods.py` implementa una línea base de **mínima
distancia espectral euclídea**, con prototipos de agua poco profunda, agua
profunda, sedimento y vegetación. Usa seis bandas, ejemplos manuales y puntos:
es una adaptación para evaluación local, **no reproducción exacta** de Cavallo
et al. ni un modelo entrenado automáticamente para Napo.

Calibra umbrales exclusivamente con entrenamiento y los congela para evaluar
el conjunto separado. Reporta precisión, recuperación, F1, IoU y matriz de
confusión multiclase; no oculta omisiones de agua tras la exactitud global de
un paisaje dominado por bosque. No publica un ganador automáticamente.
Las métricas son condicionales a puntos con observaciones útiles. También
reporta cuántas referencias de cada clase se pierden por QA y sus identificadores:
no elimina silenciosamente agua real bajo sombras para aparentar más exactitud.
Si una clase queda sin referencias útiles, detiene la comparación completa.

### Lo que puedes aportar tú

1. Conseguir observaciones independientes: fotos de campo, dron o imágenes de
   mayor resolución, con fecha y ubicación. Para comparar agua poco profunda,
   no etiquetar solamente mirando el NDWI o SCL. La referencia debe ser de la
   misma fecha, idealmente simultánea: el evaluador exige una diferencia de
   como máximo 24 horas y reporta la diferencia. Eso no garantiza equivalencia
   hidrológica: hay que revisar lluvia y nivel del río igualmente.
2. En QGIS, abrir los TIFF nativos de `data/raw/fluvial/`. Crear una capa de
   puntos GeoJSON en EPSG:4326 y marcar puntos representativos **a partir de
   esas referencias externas**, evitando bordes con píxeles mixtos.
3. Completar los campos de `data/fluvial/reference-template.geojson`:
   `sample_id` único, `group_id` espacial, `region`, `date` de Sentinel-2,
   `class` (las cuatro clases anteriores), `role` (`train` o `test`),
   `independent_reference=true`, `reference_type` (`field`, `drone` o
   `high-resolution-image`), `evidence_uri` HTTPS, `reference_acquired_at`
   ISO con zona horaria y `observer`. No inventar referencias ni coordenadas.
4. Reservar áreas independientes para `test` antes de ajustar métodos.
   Separación mínima de 200 m entre entrenamiento y prueba, grupos distintos
   y ningún píxel repetido, incluso cuando las ventanas se solapan. Ambas
   particiones necesitan las cuatro clases. Ese mínimo no asegura que una
   muestra pequeña sea representativa: ampliar sitios y condiciones.
5. Guardar el archivo fuera de datos públicos hasta revisar consentimiento,
   permisos y representatividad; ejecutar:

```powershell
python scripts/evaluate_fluvial_methods.py --references data/raw/fluvial/references.geojson
```

El informe queda local. La plantilla está vacía deliberadamente: no son
observaciones y no permite declarar validación sin datos.

## Qué falta para estudiar desecación y causas

- Una serie de **muchas adquisiciones por tramo**, distribuida por estaciones;
  las tres escenas actuales son una comparación puntual, no prueba de tendencia.
- Validar agua/arena/vegetación, especialmente agua turbia o poco profunda,
  pozas, sombras y cauces estrechos; evaluación espacial y entre fechas.
- Frecuencia de presencia = observaciones de agua / observaciones útiles,
  nunca / todas las fechas. `presence_frequency` ya maneja esos huecos;
  todavía no se publica frecuencia de estas tres escenas como indicador de sequía.
- Duración del periodo seco requiere observaciones suficientes e intervalos de
  incertidumbre entre fechas; no se puede convertir un hueco de nubes en días secos.
- Revisar lluvia antecedente y niveles/caudales independientes. Los meses iguales
  no aseguran condiciones iguales. Sentinel-2 no mide flujo con estos índices.
- Turbidez/SSC: muestreo contemporáneo y calibración óptica local, corrección
  atmosférica adecuada al agua, control de píxeles mixtos y validación separada.
- Causas: evidencia de intervenciones, comparación antes/después y aguas arriba/
  abajo, controles y explicaciones naturales alternativas. No inferir mercurio,
  ilegalidad o responsabilidad desde un índice espectral.

## Bibliografía

- McFeeters (1996), NDWI. https://doi.org/10.1080/01431169608948714
- Xu (2006), MNDWI. https://doi.org/10.1080/01431160600589179
- Feyisa et al. (2014), AWEI. https://doi.org/10.1016/j.rse.2013.08.029
- Kirby et al. (2024), comparación Sentinel-2: no ganador universal.
  https://doi.org/10.1016/j.rsase.2024.101367
- Cavallo et al. (2025), *Estimating dry bed periods in non-perennial rivers
  using Sentinel-2 satellite data*. Dos tramos en Italia, no validación de Napo.
  https://doi.org/10.1016/j.jhydrol.2025.133416
- Lobo et al. (2018), sedimentos en ríos amazónicos y calibración de reflectancia.
  https://www.intechopen.com/chapters/62698
- *Water* (2025), tabla de índices NDTI rojo/verde; no calibración para Napo.
  https://www.mdpi.com/2073-4441/17/15/2195
- Dethier et al. (2023), minería aluvial y sedimentos en ríos tropicales.
  https://www.nature.com/articles/s41586-023-06309-9
- Copernicus Sentinel-2: bandas y resolución (referencia técnica, no equivalencia
  entre radiometría GEE y COG). https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED
- Earth Search: acceso a COG y calibración. https://github.com/Element84/earth-search
