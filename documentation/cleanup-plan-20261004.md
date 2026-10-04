# Inventario y plan de limpieza · 4 de octubre de 2026

**Auditoría de solo lectura. Este documento no ejecutó borrados, movimientos ni renombres.**

## Decisión segura

La consolidación puede ahorrar espacio, pero **una carpeta con “v2”, “v6” o “tmp” no es necesariamente un borrador desechable**. Hay fuentes científicas, voces originales y trabajos vigentes dentro de ellas.

- **9 MP4 candidatos de alta confianza: 44.2 MiB**. Son montajes anteriores del reel nacional y el intermediario sin audio de v6. Se enumeran con ruta absoluta, tamaño y SHA-256 en el JSON. Se retiran únicamente tras verificar el maestro v6, su voz original, datos, subtítulos y generador.
- **ASR opcional: 403.1 MiB**. Runtime y modelo de transcripción reinstalables; eliminarlos impide recalcular alineaciones hasta reponerlos, pero no afecta los videos/locuciones originales ni los tiempos ya guardados.
- **Cachés Python: 1.4 MiB**, regenerables.
- **187 grupos idénticos por SHA-256: 419.4 MiB de copias adicionales**. No es ahorro inmediato: incluye rutas en uso y copias de la migración simultánea. No sumar categorías sin descontar solapamientos.

El ahorro indicado es tamaño lógico, no espacio de disco garantizado. No se realizó una nueva decodificación audiovisual completa: se verificaron tamaños, hashes, manifiestos y dependencias de código.

## Maestros y trabajos que sí deben conservarse

| Trabajo | Estado comprobado | Acción |
| --- | --- | --- |
| Reel nacional 1900–2025 v6 | MP4 final, voz original, SRT, CSV y snapshot USGS; relación exacta con los enlaces sociales no confirmada independientemente | Conservar paquete verificable. |
| Río Doce v9 | Último montaje local, proyecto pausado; no publicado | Conservar maestro, fuente USGS, voces, código y evidencia ecuatoriana v6. |
| Profundidad / placas y fallas | Último montaje 3D v5; guiones posteriores v10 y v11 sin montaje equivalente | Conservar animaciones y todos los textos/locuciones únicos; no tratarlos como un video publicado antiguo. |
| Tena / Napo | Última maqueta v5 sin voz definitiva | Conservar datos, fuentes, guion, código y maqueta. |
| Nororiente 1987 | Guion y fuentes; no video producido | Conservar. |
| Fotogrametría Porotoyacu | 89.5 MiB de manuscritos, perfiles, rasters, figuras y procesos | Preservar íntegro; no publicar automáticamente en GitHub. |
| Conceptos Ecuador Vivo | Tres diseños aceptados y sus prompts | Conservar. |

### Huellas de maestros

- `C:/Users/JHONY CONTERON/monitor-sismos/artifacts/reel_ecuador_1900_2025_v6/andes_pulso_reel_1900_2025.mp4`
  9694184 bytes · SHA-256 `e55995c04220dbff72331d6a651a9e4b4a6526a057c97a74a87271d10880a3e7`

- `C:/Users/JHONY CONTERON/monitor-sismos/artifacts/rios_doce_v9/rio_doce_desde_el_espacio_v9.mp4`
  30384863 bytes · SHA-256 `50c9ee77fe693f953eaba0d9fb136c5dae3658eb482f07e86b6146ad722eef7b`

- `C:/Users/JHONY CONTERON/monitor-sismos/artifacts/serie_memoria_sismica/00_profundidad_danos/v5/ondas_profundidad_3d_voz_provisional_v5.mp4`
  64603142 bytes · SHA-256 `50e04fb52e0a805c90bb247d256e43b270acd477c79f071a69568e93c7cf0ede`

- `C:/Users/JHONY CONTERON/monitor-sismos/artifacts/serie_memoria_sismica/01_napo/napo_1900_2026_fallas_3d_maqueta_sin_voz_v5.mp4`
  5200723 bytes · SHA-256 `5d270750615d5fc561e98490b0e40cb245e507a1624c9ddb275ac808f96a839c`

## Dependencias que impiden borrar las carpetas anteriores

1. **Río Doce v9 → evidencia de ríos v6.** El renderizador lee el manifiesto, RGB/MNDWI de 2019/2024/2026, datos de umbral y máscaras desde `artifacts/rios_historia_v6`.
2. **Río Doce v9 → voces y utilidades v8.** Las locuciones ya copiadas deben conservarse; la preparación todavía busca coincidencias en la carpeta v8 y el código importa el módulo anterior.
3. **Verificación v9 → MP4 antiguos v6 y v8.** `sources_manifest.json`, `verify_river_satellite_story.py` y una prueba abren ambos archivos mediante rutas absolutas. Antes de retirarlos, separar la procedencia histórica del render de las entradas científicas obligatorias; guardar sus hashes como antecedentes retirados. No eliminar controles de datos reales.
4. **Serie sísmica → catálogo nacional v6 y animaciones v5.** Los episodios siguientes usan la instantánea original; las pruebas v7 también abren audio v6 y video 3D v5.
5. **Atlas → respaldo de ríos en tmp.** `tmp/rivers-next/original-bundle` está documentado como recuperación previa a promoción. No borrar todo `tmp`.
6. **Porotoyacu → scripts y manuscritos locales.** El nombre `output` no convierte estos trabajos en caché.

## Retiro de borradores del video nacional

Retirar solo estos archivos (nunca sus carpetas completas), después de verificar la copia consolidada:

- `C:/Users/JHONY CONTERON/monitor-sismos/artifacts/reel_ecuador_1900_2025/andes_pulso_reel_1900_2025.mp4` — 2.2 MiB
- `C:/Users/JHONY CONTERON/monitor-sismos/artifacts/reel_ecuador_1900_2025_v2/andes_pulso_reel_1900_2025.mp4` — 3.1 MiB
- `C:/Users/JHONY CONTERON/monitor-sismos/artifacts/reel_ecuador_1900_2025_v3/andes_pulso_reel_1900_2025.mp4` — 6.0 MiB
- `C:/Users/JHONY CONTERON/monitor-sismos/artifacts/reel_ecuador_1900_2025_v3/visual_sin_audio.mp4` — 4.1 MiB
- `C:/Users/JHONY CONTERON/monitor-sismos/artifacts/reel_ecuador_1900_2025_v4/andes_pulso_reel_1900_2025.mp4` — 6.7 MiB
- `C:/Users/JHONY CONTERON/monitor-sismos/artifacts/reel_ecuador_1900_2025_v4/visual_sin_audio.mp4` — 4.2 MiB
- `C:/Users/JHONY CONTERON/monitor-sismos/artifacts/reel_ecuador_1900_2025_v5/andes_pulso_reel_1900_2025.mp4` — 6.8 MiB
- `C:/Users/JHONY CONTERON/monitor-sismos/artifacts/reel_ecuador_1900_2025_v5/visual_sin_audio.mp4` — 4.3 MiB
- `C:/Users/JHONY CONTERON/monitor-sismos/artifacts/reel_ecuador_1900_2025_v6/visual_sin_audio.mp4` — 6.7 MiB

Las voces únicas, guiones, licencias, fuentes y metadatos que compartan esas carpetas deben preservarse o comprobarse contra una copia idéntica antes de limpiar otra cosa. Un render antiguo no es fuente del render v6; su eliminación no justifica eliminar sus archivos vecinos.

## Organización sugerida

- `data/cases/<id>/`: versión exacta de los datos publicados, método, licencia y citas.
- `assets/media/andes-pulso/<id>/`: MP4 final y portada seleccionada.
- `production/andes-pulso/scripts/`: preparación, render y pruebas, con rutas portables.
- `production/andes-pulso/masters/`: originales de voz, edición y maestros locales.
- `production/andes-pulso/en-curso/`: Río Doce, profundidad/fallas, Napo y Nororiente.
- `production/fotogrametria/porotoyacu/`: trabajo científico distinto conservado, local y no público por defecto.
- `documentation/migration/`: mapa de rutas anteriores/nuevas, hashes y registro real de eliminaciones.
- `.cache/`: entornos/modelos reinstalables, nunca datos científicos.

## Verificación antes de retirar monitor-sismos

1. Copiar también los archivos ignorados y no versionados; los artefactos no están protegidos por Git.
2. Comparar origen y destino por tamaño y SHA-256. Conservar manifiesto previo y nuevo.
3. Resolver rutas absolutas y dependencias entre versiones sin modificar los datos congelados.
4. Ejecutar pruebas usando solo la carpeta consolidada. No considerar éxito una prueba que todavía lee el proyecto viejo.
5. Confirmar todos los trabajos únicos y audios originales en destino.
6. Retirar únicamente la lista verificada y generar un registro de lo eliminado, cuánto ocupa y cómo se recupera.

**Recuperación:** un MP4 borrador eliminado permanentemente puede regenerarse desde los insumos, pero no se promete recuperar exactamente el mismo binario sin papelera o respaldo. Para originales científicos y voz única, la condición es una copia verificada, no solo “se puede volver a descargar”.

Detalle procesable completo: [cleanup-plan-20261004.json](cleanup-plan-20261004.json).

