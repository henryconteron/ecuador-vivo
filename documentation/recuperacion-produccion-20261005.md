# Recuperación del archivo de producción · 5 de octubre de 2026

Este documento registra cómo recuperar el material histórico de `monitor-sismos` después de su integración en Ecuador Vivo.

## Respaldo privado

- Carpeta: [Ecuador Vivo — respaldo de producción](https://drive.google.com/drive/folders/1Tw78ZkcWi4gN_ef-M72uDZ6NeN2Hyslh)
- Contenido comprobado por lectura posterior: 24 fragmentos y 2 manifiestos.
- Tamaño conjunto de los fragmentos: 2064572928 bytes.
- Visibilidad: privada; no se modificaron permisos de uso compartido.

Los archivos `MANIFEST.json` y `MANIFEST-with-chunks.json` describen los paquetes, el orden de los fragmentos, los tamaños y las sumas SHA-256 calculadas localmente antes de subirlos. Drive confirmó nombres y tamaños; su conexión no devolvió hashes remotos.

## Paquetes y huellas

| Paquete | Tamaño | SHA-256 |
|---|---:|---|
| `monitor-produccion-01-serie-sismica.tar` | 439040000 B | `dbf4de94daf98acde06f910290bcd1a56976db029458e19b8e45e077ba1cc33c` |
| `monitor-produccion-02-napo-ndwi-indices.tar` | 422188544 B | `fe8ef962ca9f7863cc9ebbd99256e0892d9f132e1693e88e398682ff2b968b7a` |
| `monitor-produccion-03-rios-metodos.tar` | 449701888 B | `977b50655da4962e5462f512714d99368e9b570fdee7cc8f65d8a38a6685a6c8` |
| `monitor-produccion-04-historias-y-reels.tar` | 327894016 B | `0d8175a860d43332f023bc4bd349d86010a61f57ea94091d24b5f2a3e3c59443` |
| `monitor-produccion-05-entornos-asr-reinstalables.tar` | 425748480 B | `89c125d3e4bc2f4b39f30c1e1f08315f40acc03bb32364a238815237c2bbbdb9` |

## Cómo reconstruir un paquete

1. Descarga todos los fragmentos que compartan el mismo nombre base.
2. Ordénalos por el sufijo `part001`, `part002`, etc.
3. Únelos en modo binario para recuperar el archivo `.tar`.
4. Calcula su SHA-256 y compáralo con la tabla anterior.
5. Abre o extrae el `.tar` solo cuando la huella coincida.

En PowerShell, desde la carpeta que contiene los fragmentos:

```powershell
$parts = Get-ChildItem 'monitor-produccion-01-serie-sismica.tar.part*' | Sort-Object Name
$output = [IO.File]::Create((Join-Path $PWD 'monitor-produccion-01-serie-sismica.tar'))
try {
  foreach ($part in $parts) {
    $input = [IO.File]::OpenRead($part.FullName)
    try { $input.CopyTo($output) } finally { $input.Dispose() }
  }
} finally { $output.Dispose() }
Get-FileHash '.\monitor-produccion-01-serie-sismica.tar' -Algorithm SHA256
```

## Qué no debe eliminarse

- El repositorio vigente de Ecuador Vivo, aunque la carpeta local todavía se llame `fallas-ecuador`.
- `_local/monitor-artifacts`, mientras sea el almacén activo de producción.
- `production/monitor/`, que contiene el código científico integrado.
- El video público final y sus datos de verificación en `assets/media/andes-pulso/` y `data/andes-pulso/`.

## Retirada manual pendiente

La automatización no recibió permiso del sistema para eliminar carpetas recursivamente. Tras cerrar aplicaciones que usen el proyecto, puede enviarse `C:\Users\JHONY CONTERON\monitor-sismos` a la Papelera. Antes, comprueba que su subcarpeta `artifacts` sea un enlace y que apunte a `_local/monitor-artifacts`; no borres directamente el destino consolidado.

Los paquetes temporales locales bajo `_local/migration-20261004/drive-backup` pueden eliminarse después de volver a confirmar que la carpeta privada de Drive contiene los 26 objetos. El clon temporal `_local/feed-geologico-retirement` también puede eliminarse: la transición ya está publicada y el repositorio remoto quedó archivado.
