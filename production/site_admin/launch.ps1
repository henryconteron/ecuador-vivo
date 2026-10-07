param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$studioPython = Join-Path $repoRoot '_local/video-studio/.venv/Scripts/python.exe'
$adminPython = (Get-Command python -ErrorAction SilentlyContinue).Source
$python = if (Test-Path -LiteralPath $studioPython) { $studioPython } else { $adminPython }
$port = 8511
$url = "http://127.0.0.1:$port"
$logRoot = Join-Path $repoRoot '_local/site-admin'
$stdoutLog = Join-Path $logRoot 'server.log'
$stderrLog = Join-Path $logRoot 'server-errors.log'
$adminScript = Join-Path $PSScriptRoot 'app.py'
$oldScript = Join-Path $repoRoot 'production/climate_explorer/app.py'
if (!$python) { throw 'No se encontró Python. Abre primero el Editor de videos para preparar su entorno local.' }
try {
    # A healthy Streamlit on this port can still be the obsolete climate app.
    $listeners = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    foreach ($listener in $listeners) {
        $owner = Get-CimInstance Win32_Process -Filter "ProcessId=$($listener.OwningProcess)"
        if ($owner.CommandLine -and $owner.CommandLine.Contains($oldScript.Replace('/', '\'))) {
            Get-CimInstance Win32_Process | Where-Object {
                $_.Name -match '^python' -and $_.CommandLine -and $_.CommandLine.Contains($oldScript.Replace('/', '\'))
            } | ForEach-Object { Stop-Process -Id $_.ProcessId -ErrorAction SilentlyContinue }
            Start-Sleep -Milliseconds 500
        } elseif ($owner.CommandLine -and !$owner.CommandLine.Contains($adminScript.Replace('/', '\'))) {
            throw "El puerto $port pertenece a otra aplicación. Ciérrala o cambia el puerto del panel; no se detuvo ese proceso."
        }
    }
} catch {
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show($_.Exception.Message, 'Ecuador Vivo - Panel personal') | Out-Null
    exit 1
}
try {
    $response = Invoke-WebRequest "$url/_stcore/health" -TimeoutSec 2 -UseBasicParsing
    if ($response.StatusCode -eq 200) { if (!$NoBrowser) { Start-Process $url }; exit 0 }
} catch { }
New-Item -ItemType Directory -Force -Path $logRoot | Out-Null
$process = Start-Process -FilePath $python -ArgumentList @(
    '-m','streamlit','run',('"' + $adminScript + '"'),
    '--server.address','127.0.0.1','--server.port',"$port",'--server.headless','true',
    '--browser.gatherUsageStats','false'
) -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog -PassThru
for ($attempt = 0; $attempt -lt 50; $attempt++) {
    Start-Sleep -Milliseconds 500
    try {
        $response = Invoke-WebRequest "$url/_stcore/health" -TimeoutSec 2 -UseBasicParsing
        if ($response.StatusCode -eq 200) { if (!$NoBrowser) { Start-Process $url }; exit 0 }
    } catch { }
    if ($process.HasExited) { break }
}
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.MessageBox]::Show("No se pudo abrir el panel personal. Revisa $stderrLog", 'Ecuador Vivo - Panel personal') | Out-Null
exit 1
