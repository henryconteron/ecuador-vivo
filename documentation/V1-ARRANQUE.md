# Arranque normal de Ecuador Vivo Studio

Desde la raíz del repositorio, con el entorno existente:

```powershell
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\production\video_studio\launch.ps1'
```

`Abrir editor de videos.vbs` llama a ese mismo lanzador. Abre `http://127.0.0.1:8526`.
Si el servidor ya responde, lo reutiliza. El lanzador elimina la variable de recarga
en su propio proceso y usa watcher `none` y `runOnSave=false` al iniciar otro servidor.
Para arrancar sin abrir el navegador: añadir `-NoBrowser`.
No depende de `tmp/`. El entorno es `_local/video-studio/.venv`.

Para que el 8526 existente cargue los cambios, primero verifica su identidad:

```powershell
$studioPid = (Get-NetTCPConnection -State Listen -LocalPort 8526).OwningProcess
Get-CimInstance Win32_Process -Filter "ProcessId=$studioPid" |
    Select-Object ProcessId,ParentProcessId,ExecutablePath,CommandLine
& '.\_local\video-studio\.venv\Scripts\python.exe' -c "import psutil; p=psutil.Process($studioPid); print(p.pid, p.cwd(), p.cmdline())"
```

Comprueba que la línea incluya `studio_server.py`, puerto 8526 y el Python del
repositorio, y que el cwd sea `production/video_studio`. Solo después:

```powershell
Stop-Process -Id $studioPid
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\production\video_studio\launch.ps1'
```

Los PIDs anteriores no son autorización para detener otro proceso: verifica de nuevo.
La medición se realiza separadamente en 8527 y nunca requiere tocar el 8526.
Para desarrollo, el arranque directo puede definir `ECUADOR_VIVO_DEVELOPMENT_RELOAD=1`;
el lanzador normal siempre la elimina. Los cambios de fuente requieren un reinicio
fuera de las ventanas de medición cuando se usa el modo normal.
