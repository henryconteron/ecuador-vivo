# Imagen frente a interpretación: Tena–Archidona, 2024

Estado al 30 de septiembre de 2026: **exportación real procesada y validada**.
La revisión técnica comprueba bandas, proyección, máscaras y archivos; no certifica
la exactitud temática de MapBiomas ni sustituye el campo. No se usa imagen de IA.

## Fuentes y composición

- [Copernicus Sentinel-2 SR Harmonized](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED):
  bandas B4/B3/B2; reflectancia procesada, no fotografía sin correcciones.
- [Google Cloud Score+ V1](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_CLOUD_SCORE_PLUS_V1_S2_HARMONIZED):
  QA enlazado por `system:index`, umbral `cs_cdf ≥ 0.65`. No significa «65 % de certeza».
- [MapBiomas Ecuador V1.0](https://developers.google.com/earth-engine/datasets/catalog/projects_mapbiomas-public_assets_ecuador_lulc_v1):
  clasificación anual 2024; no mezclar su leyenda con otras versiones.

Ventana editorial `[-78.04, -1.12, -77.55, -0.72]` (oeste/sur/este/norte),
**no** límites cantonales, parcelas o toda la provincia de Napo.
Periodo `[2024-01-01, 2025-01-01)`: inicio inclusive, fin exclusive.
296 escenas candidatas y 296 enlazadas a QA; incluye teselas, no son 296 fechas
únicas ni 296 observaciones en cada píxel. El recibo conserva todos los IDs y fechas.

Se excluyen códigos SCL 0/1/3/8/9/10/11 (inválidos, sombras, nubes, cirros y nieve).
La mediana **por banda** puede combinar fechas diferentes. Se exige un mínimo de
**3 observaciones útiles** en B4 para mostrar RGB; la banda `clear_count` conserva
ese conteo de la banda de referencia tras aplicar QA. También se exige que las
tres bandas RGB finales sean válidas.
Estos filtros no garantizan ausencia total de nubes, sombras o errores automáticos.

## Resolución y máscara común

Entradas ópticas nominales de 10 m, **muestreadas a 30 m** en EPSG:32718 con vecino
más cercano: no es un promedio de nueve píxeles ni una imagen publicada de 10 m.
Reflectancia uint16 × 0.0001; NoData **65535**, no cero. Los píxeles oscuros válidos
se conservan. Para la web se usa la misma rejilla EPSG:3857 de **1821 × 1486** del
PNG MapBiomas. Reflectancia reproyectada con bilinear; máscaras con vecino más
cercano. No se interpola la clasificación ni sus colores.

Estiramiento fijo: reflectancia 0–0.3, gamma 1.2; WebP con pérdida, calidad 88.
Es para lectura visual, **no** para medir reflectancia o inferir detalle subpíxel.
Se reutiliza el PNG MapBiomas 2024 de la [comparación 2000/2024](napo-landcover.md),
ya limitado a observaciones comunes en ambos años. Ambas vistas reciben además
la máscara óptica útil de 2024. Los huecos son transparentes y se ven rayados;
no se rellenan con otro año o territorio. La leyenda indica clases presentes
en la ventana MapBiomas 2024 original, no necesariamente en cada mitad visible.

Resultados del ráster UTM de 30 m:

- 2.684.668 centros de píxel dentro de la ventana; 2.559.802 útiles (**95,3 %**).
- Observaciones útiles por píxel mostrado: mínimo **3**, mediana **17**, máximo **74**.
- En la rejilla de visualización: 2.572.296 píxeles con comparación sobre
  2.697.912 píxeles clasificados de la vista original (**95,3 %**).

Los conteos UTM y Mercator son diferentes. No mezclarlos, restarlos ni convertir
esos porcentajes en hectáreas, áreas cantonales o exactitud del clasificador.

## Reproducir

1. En un proyecto propio habilitado para Earth Engine, pega todo
   `scripts/export_napo_imagery_gee.js` en un **script nuevo** del Code Editor.
   Revisa elegibilidad y términos antes de registrarte. Este flujo no comercial
   exporta a Drive; no requiere activar servicios de pago.
2. Pulsa **Run** y espera la consulta asíncrona. Ejecuta en **Tasks**
   `napo_sentinel2_2024` y `napo_sentinel2_2024_receipt`, sin cambiar parámetros.
3. Descarga TIFF y GeoJSON de la misma ejecución desde `EcuadorVivo` a
   `data/raw/imagery/` (ignorada por Git). No publiques credenciales.
4. Con Python 3.12 o posterior, desde la raíz del repositorio:

```powershell
python -m pip install -r requirements-landcover.txt
python scripts/build_napo_imagery.py --input data/raw/imagery/napo_sentinel2_2024.tif --receipt data/raw/imagery/napo_sentinel2_2024_receipt.geojson
pnpm run check
python -m unittest discover -s tests
```

Necesitas primero el bundle MapBiomas `ready`. El procesador comprueba su SHA-256,
el recibo, los nombres de banda del TIFF, CRS, escala, fechas, calidad y extensión.
Se detiene ante diferencias; no sustituyas silenciosamente la fuente.
Un recibo declara procedencia y los SHA-256 detectan cambios: **no** son firmas
del proveedor ni certificación externa de autenticidad o exactitud en campo.

Publica las dos vistas pequeñas (aproximadamente **629 kB en conjunto**) y los JSON
de `data/imagery/`. El TIFF de trabajo de unos 21 MB queda fuera de Git.
El comparador publicado no necesita sesión Google, token o ID del proyecto personal.

## Interpretación y atribución

Coincidencias entre texturas y colores son pistas. Diferencias pueden venir de
píxeles mixtos, nubes residuales, fechas, métodos o errores de clase. Esta composición
no identifica causas, legalidad, minería, daños o deforestación por sí sola.
**No es validación independiente de MapBiomas**: para medir exactitud se necesitan
muestras de referencia independientes y un diseño de evaluación apropiado.

Contains modified Copernicus Sentinel data (2024). Modificaciones: filtro, mediana,
recorte, muestreo, reproyección y renderizado. Cloud Score+ © Google Earth Engine
(CC BY 4.0). MapBiomas Ecuador Publisher Catalog V1.0, mapa 2024 (CC BY 4.0).
Véase [LICENSE-DATA.md](../LICENSE-DATA.md).

Método Cloud Score+: Pasquarella, V. J., Brown, C. F., Czerwinski, W., & Rucklidge,
W. J. (2023). *Comprehensive Quality Assessment of Optical Satellite Imagery Using
Weakly Supervised Video Learning*, CVPR Workshops, 2125–2135.
[DOI:10.1109/CVPRW59228.2023.00206](https://doi.org/10.1109/CVPRW59228.2023.00206).

## English summary

A **real 2024 Sentinel-2 per-band median** is compared with MapBiomas Ecuador V1.0
over an editorial window around Tena and Archidona. 10 m optical bands were sampled
at 30 m, QA-filtered and reprojected onto the classification display grid. Both views
share a mask; missing comparisons are hatched, not filled. Scene provenance,
processing scripts and SHA-256 checks are included. Technical verification is
**not independent classification accuracy assessment**. This is educational context,
not a deforestation estimate, emergency alert or parcel map.
