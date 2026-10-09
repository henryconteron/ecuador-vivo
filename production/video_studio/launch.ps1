$ErrorActionPreference = 'Stop'
$studioRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$studioEnv = Join-Path $studioRoot '_local/video-studio/.venv'
$studioPython = Join-Path $studioEnv 'Scripts/python.exe'
$studioLog = Join-Path $studioRoot '_local/video-studio/server.log'
$studioErrors = Join-Path $studioRoot '_local/video-studio/server-errors.log'
$studioUrl = 'http://127.0.0.1:8510'
try {
    $studioResponse = Invoke-WebRequest "$studioUrl/_stcore/health" -TimeoutSec 2 -UseBasicParsing
    if ($studioResponse.StatusCode -eq 200) { Start-Process $studioUrl; exit 0 }
} catch { }
try {
    if (!(Test-Path -LiteralPath $studioPython)) {
        & python -m venv $studioEnv
        if ($LASTEXITCODE -ne 0) { throw 'No se pudo preparar Python para el editor.' }
        & $studioPython -m pip install -r (Join-Path $PSScriptRoot 'requirements.txt')
        if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar las dependencias. Revisa la conexion.' }
    }
    $studioProcess = Start-Process -FilePath $studioPython -ArgumentList @('-m','streamlit','run','studio_server.py') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput $studioLog -RedirectStandardError $studioErrors -PassThru
    for ($studioAttempt = 0; $studioAttempt -lt 60; $studioAttempt++) {
        Start-Sleep -Milliseconds 500
        try {
            $studioResponse = Invoke-WebRequest "$studioUrl/_stcore/health" -TimeoutSec 2 -UseBasicParsing
            if ($studioResponse.StatusCode -eq 200) { Start-Process $studioUrl; exit 0 }
        } catch { }
        if ($studioProcess.HasExited) { break }
    }
    throw "No se pudo abrir el editor. Revisa $studioErrors"
} catch {
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show($_.Exception.Message, 'Ecuador Vivo - Editor de video') | Out-Null
    exit 1
}
