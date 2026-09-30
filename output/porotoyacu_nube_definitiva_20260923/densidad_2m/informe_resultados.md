# Resultados de validacion de la nube de Porotoyacu

- Archivo: `NUBE_COMPLETA_FINAL_TERRENO_MICRORELIEVE_DEPURADO_UTM18S.laz`
- CRS: EPSG:32718
- Puntos totales: 13,619,241
- Puntos Ground (clase 2): 2,810,862
- Puntos no Ground: 10,808,379
- Retencion Ground: 20.6389%
- Exclusion para el DTM: 79.3611%
- Tamano de celda: 2 m
- Area de soporte por celdas ocupadas: 0.377096 km2
- Densidad total sobre esa misma area: 36.1161 puntos/m2
- Densidad Ground sobre esa misma area: 7.4540 puntos/m2
- Celdas de la huella con al menos un punto Ground: 47.1275%

## Percentiles de densidad local sobre celdas de la huella total

| Conjunto | P25 | P50 | P75 | P95 | P99 |
|---|---:|---:|---:|---:|---:|
| All | 21.500 | 30.500 | 44.250 | 75.250 | 105.000 |
| Ground | 0.000 | 0.000 | 18.750 | 23.500 | 30.500 |

## Advertencias

- Ninguna.

## Texto base para Results (revisar antes de incorporar)

The classified SfM point cloud contained 13,619,241 points, of which 2,810,862 (20.64%) were retained as Ground for DTM generation. Using a common 2 x 2 m grid and the all-point support as the reference footprint, mean density decreased from 36.12 to 7.45 points/m2 after classification. Direct Ground observations occurred in 47.13% of occupied cells; the remaining cells therefore lacked direct terrain support at this analysis scale.

Nota: `no Ground` significa excluido de la entrada del DTM; no implica necesariamente que cada punto haya sido vegetacion.
