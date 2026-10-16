param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
Remove-Item Env:ECUADOR_VIVO_DEVELOPMENT_RELOAD -ErrorAction SilentlyContinue
$studioRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$studioEnv = Join-Path $studioRoot '_local/video-studio/.venv'
$studioPython = Join-Path $studioEnv 'Scripts/python.exe'
$studioLog = Join-Path $studioRoot '_local/video-studio/server.log'
$studioErrors = Join-Path $studioRoot '_local/video-studio/server-errors.log'
$studioUrl = 'http://127.0.0.1:8534'
try {
    $studioResponse = Invoke-WebRequest "$studioUrl/_stcore/health" -TimeoutSec 2 -UseBasicParsing
    if ($studioResponse.StatusCode -eq 200) { if (!$NoBrowser) { Start-Process $studioUrl }; exit 0 }
} catch { }
try {
    if (!(Test-Path -LiteralPath $studioPython)) {
        & python -m venv $studioEnv
        if ($LASTEXITCODE -ne 0) { throw 'No se pudo preparar Python para el editor.' }
        & $studioPython -m pip install -r (Join-Path $PSScriptRoot 'requirements.txt')
        if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar las dependencias. Revisa la conexion.' }
    }
    $studioProcess = Start-Process -FilePath $studioPython -ArgumentList @('-X','utf8','-B','-m','streamlit','run','studio_server.py','--server.port','8534','--server.address','127.0.0.1','--server.headless','true','--server.fileWatcherType','none','--server.runOnSave','false','--browser.gatherUsageStats','false') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput $studioLog -RedirectStandardError $studioErrors -PassThru
    $studioDeadline = [Diagnostics.Stopwatch]::StartNew()
    while ($studioDeadline.Elapsed.TotalSeconds -lt 60) {
        try {
            $studioResponse = Invoke-WebRequest "$studioUrl/_stcore/health" -TimeoutSec 2 -UseBasicParsing
            if ($studioResponse.StatusCode -eq 200) { if (!$NoBrowser) { Start-Process $studioUrl }; exit 0 }
        } catch { }
        if ($studioProcess.HasExited) { break }
    }
    throw "No se pudo abrir el editor. Revisa $studioErrors"
} catch {
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show($_.Exception.Message, 'Ecuador Vivo - Editor de video') | Out-Null
    exit 1
}
