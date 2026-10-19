[CmdletBinding()]
param([Parameter(Mandatory)][ValidateSet('2020-12-23','2021-01-04','2025-03-08','2025-03-20')][string]$Fecha)
$ErrorActionPreference = 'Stop'
$pilotRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$outputFolder = Join-Path $pilotRoot ('_local/parcelas/piloto-352/api-rtc-' + $Fecha.Replace('-',''))
if ($Fecha -eq '2025-03-20') { $outputFolder += '-trazable' }
$outputFile = Join-Path $outputFolder 'response.tar'
$credentialFile = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'EcuadorVivo/credenciales/copernicus-piloto.dpapi.json'
$secret = $null; $tokenBody = $null; $token = $null; $client = $null; $response = $null
try {
    if (Test-Path -LiteralPath $outputFile) { throw 'Output already exists' }
    # Rebuild the payload from reviewed code, never execute a user-provided endpoint/evalscript.
    $python = Join-Path $pilotRoot '_local/video-studio/.venv/Scripts/python.exe'
    Push-Location $pilotRoot
    try { & $python -m tools.parcelas.process_api prepare $Fecha; if ($LASTEXITCODE) { throw 'Preparation failed' } }
    finally { Pop-Location }
    $stored = Get-Content -LiteralPath $credentialFile -Raw | ConvertFrom-Json
    if ($stored.version -ne 1 -or [DateTimeOffset]::Parse($stored.expires_utc) -le [DateTimeOffset]::UtcNow) { throw 'Expired' }
    $secret = ConvertTo-SecureString $stored.secret_dpapi
    $tokenBody = @{grant_type='client_credentials'; client_id=$stored.client_id; client_secret=[Net.NetworkCredential]::new('', $secret).Password}
    $token = Invoke-RestMethod -Method Post -Uri 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token' -Body $tokenBody -TimeoutSec 30
    if (-not $token.access_token) { throw 'Authentication failed' }
    Add-Type -AssemblyName System.Net.Http
    $handler = [Net.Http.HttpClientHandler]::new(); $handler.AllowAutoRedirect = $false
    $client = [Net.Http.HttpClient]::new($handler)
    $client.Timeout = [TimeSpan]::FromSeconds(120)
    $client.MaxResponseContentBufferSize = 5000000
    $client.DefaultRequestHeaders.Authorization = [Net.Http.Headers.AuthenticationHeaderValue]::new('Bearer', $token.access_token)
    $client.DefaultRequestHeaders.Accept.ParseAdd('application/x-tar')
    $body = [Net.Http.StringContent]::new((Get-Content -LiteralPath (Join-Path $outputFolder 'request.json') -Raw), [Text.Encoding]::UTF8, 'application/json')
    $response = $client.PostAsync('https://sh.dataspace.copernicus.eu/process/v1', $body).GetAwaiter().GetResult()
    if (-not $response.IsSuccessStatusCode) {
        Write-Host ('Process API rechazó la solicitud. HTTP ' + [int]$response.StatusCode + '; sin reintentos automáticos.')
        throw 'Remote failure'
    }
    $bytes = $response.Content.ReadAsByteArrayAsync().GetAwaiter().GetResult()
    if ($response.Content.Headers.ContentType.MediaType -notin @('application/x-tar','application/tar')) { throw 'Unexpected media type' }
    $stream = [IO.File]::Open($outputFile, [IO.FileMode]::CreateNew)
    try { $stream.Write($bytes,0,$bytes.Length) } finally { $stream.Dispose() }
    Write-Host ('Recorte guardado: ' + $bytes.Length + ' bytes. Token no persistido.')
} catch {
    Write-Host 'Descarga no completada. No se muestran credenciales ni respuestas HTTP sensibles.'
    exit 1
} finally {
    if ($tokenBody) { $tokenBody.Clear() }
    $token = $null
    if ($secret) { $secret.Dispose() }
    if ($response) { $response.Dispose() }
    if ($client) { $client.Dispose() }
}
