# Una sola entrada para el expediente local aprobado. No publica ni certifica.
[CmdletBinding()]
param([switch]$SoloInforme,[switch]$CasoEcuador,[switch]$ParcelasCampo)
$ErrorActionPreference = 'Stop'
if ($CasoEcuador -and $ParcelasCampo) { throw 'Choose one case' }
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$workFolder = Join-Path $projectRoot '_local/parcelas/piloto-352/expediente'
$pilotModule='tools.parcelas.expediente'
if ($CasoEcuador) {
    $workFolder=Join-Path $projectRoot '_local/parcelas/ecuador-2435'
    $pilotModule='tools.parcelas.ecuador_case'
}
if ($ParcelasCampo) {
    $workFolder=Join-Path $projectRoot '_local/parcelas/parcelas-campo-ecuador/observaciones'
    $pilotModule='tools.parcelas.field_observations'
}
$python = Join-Path $projectRoot '_local/video-studio/.venv/Scripts/python.exe'
$secret=$null; $tokenBody=$null; $token=$null; $client=$null
function Invoke-PilotPython([string[]]$Arguments) {
    & $python -m $pilotModule @Arguments
    if ($LASTEXITCODE) { throw 'Pilot stage failed' }
}
Push-Location $projectRoot
try {
    if (-not $SoloInforme) {
        Invoke-PilotPython @('plan')
        $plan = Get-Content -LiteralPath (Join-Path $workFolder 'plan.json') -Raw | ConvertFrom-Json
        if ($ParcelasCampo) {
            if ($plan.case -ne 'RF05-RF06' -or $plan.observations.Count -gt 24) { throw 'Invalid field plan' }
        } elseif ($CasoEcuador) {
            if ($plan.case -ne '2435' -or $plan.observations.Count -gt 12) { throw 'Invalid Ecuador plan' }
        } elseif ($plan.version -ne 1 -or $plan.observations.Count -gt 28) { throw 'Invalid plan' }
        # Python valida cada fecha/ruta y reconstruye las solicitudes revisadas antes de autenticar.
        foreach ($row in $plan.observations) {
            if ($CasoEcuador -or $ParcelasCampo) { Invoke-PilotPython @('prepare','--key',$row.key) }
            else { Invoke-PilotPython @('prepare','--date',$row.date) }
        }
        $credentialFile = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'EcuadorVivo/credenciales/copernicus-piloto.dpapi.json'
        $stored = Get-Content -LiteralPath $credentialFile -Raw | ConvertFrom-Json
        if ($stored.version -ne 1 -or [DateTimeOffset]::Parse($stored.expires_utc) -le [DateTimeOffset]::UtcNow) { throw 'Credential expired' }
        $secret = ConvertTo-SecureString $stored.secret_dpapi
        $tokenBody = @{grant_type='client_credentials';client_id=$stored.client_id;client_secret=[Net.NetworkCredential]::new('',$secret).Password}
        $token = Invoke-RestMethod -Method Post -Uri 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token' -Body $tokenBody -TimeoutSec 30
        if (-not $token.access_token) { throw 'Authentication failed' }
        $expires = [DateTimeOffset]::UtcNow.AddSeconds([int]$token.expires_in-20)
        Add-Type -AssemblyName System.Net.Http
        $handler = [Net.Http.HttpClientHandler]::new(); $handler.AllowAutoRedirect=$false
        $client = [Net.Http.HttpClient]::new($handler)
        $client.Timeout=[TimeSpan]::FromSeconds(60)
        $client.MaxResponseContentBufferSize=5000000
        $client.DefaultRequestHeaders.Authorization=[Net.Http.Headers.AuthenticationHeaderValue]::new('Bearer',$token.access_token)
        $client.DefaultRequestHeaders.Accept.ParseAdd('application/x-tar')
        $totalBytes=0; $requests=0
        foreach ($row in $plan.observations) {
            $folder = Join-Path (Join-Path $projectRoot '_local/parcelas/piloto-352') $row.folder
            if ($CasoEcuador) {
                if ($row.key -notmatch '^(optical|radar)-(2020|2022)-\d{2}-\d{2}$' -or $row.folder -ne $row.key) { throw 'Unexpected Ecuador output key' }
                $folder=Join-Path $workFolder $row.key
            }
            if ($ParcelasCampo) {
                if ($row.key -notmatch '^RF0[56]-(optical|radar)-(2020|2025)-\d{2}-\d{2}$' -or $row.folder -ne $row.key) { throw 'Unexpected field output key' }
                $folder=Join-Path $workFolder $row.key
            }
            $target = Join-Path $folder 'response.tar'
            if (Test-Path -LiteralPath $target) { Write-Host ('Cache: '+$row.date); continue }
            if ([DateTimeOffset]::UtcNow -ge $expires -or $requests -ge 28 -or $totalBytes -ge 15000000) { throw 'Session or batch budget reached; safe to resume' }
            $body=[Net.Http.StringContent]::new((Get-Content -LiteralPath (Join-Path $folder 'request.json') -Raw),[Text.Encoding]::UTF8,'application/json')
            $response=$null
            try {
                $response=$client.PostAsync('https://sh.dataspace.copernicus.eu/process/v1',$body).GetAwaiter().GetResult()
                $requests++
                if (-not $response.IsSuccessStatusCode) { Write-Host ('HTTP '+[int]$response.StatusCode+'; sin reintentos.'); throw 'Remote error' }
                if ($response.Content.Headers.ContentType.MediaType -notin @('application/x-tar','application/tar')) { throw 'Unexpected media' }
                $bytes=$response.Content.ReadAsByteArrayAsync().GetAwaiter().GetResult()
                $stream=[IO.File]::Open($target,[IO.FileMode]::CreateNew)
                try { $stream.Write($bytes,0,$bytes.Length) } finally { $stream.Dispose() }
                $totalBytes+=$bytes.Length
                Write-Host ('Descargado '+$row.date+': '+$bytes.Length+' bytes')
            } finally { if ($response) { $response.Dispose() }; $body.Dispose() }
        }
        Write-Host ('Lote: '+$requests+' solicitudes, '+$totalBytes+' bytes nuevos; token no persistido.')
    }
    Invoke-PilotPython @('report')
    Invoke-PilotPython @('verify')
    Write-Host 'Expediente listo para revision humana; no es certificacion.'
} catch {
    Write-Host 'Proceso detenido de forma segura. Salidas conservadas; sin credenciales en registros. Consulta el estado del expediente.'
    exit 1
} finally {
    if ($tokenBody) { $tokenBody.Clear() }; $token=$null
    if ($secret) { $secret.Dispose() }; if ($client) { $client.Dispose() }
    Pop-Location
}
