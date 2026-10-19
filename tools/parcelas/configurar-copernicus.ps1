# Ejecutar interactivamente. Nunca pasar secretos por argumentos o historial.
[CmdletBinding()]
param([switch]$SoloComprobar)
$ErrorActionPreference = 'Stop'
$credentialRoot = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'EcuadorVivo\credenciales'
$credentialFile = Join-Path $credentialRoot 'copernicus-piloto.dpapi.json'
$tokenEndpoint = 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token'
$clientSecret = $null
$tokenResult = $null
$tokenBody = $null
try {
    if ($SoloComprobar) {
        $stored = Get-Content -LiteralPath $credentialFile -Raw | ConvertFrom-Json
        if ($stored.version -ne 1 -or [DateTimeOffset]::Parse($stored.expires_utc) -le [DateTimeOffset]::UtcNow) {
            throw 'Credencial vencida o formato no admitido.'
        }
        $clientId = $stored.client_id
        $clientSecret = ConvertTo-SecureString $stored.secret_dpapi
    } else {
        if (Test-Path -LiteralPath $credentialFile) {
            throw 'Ya existe una credencial local. No se sobrescribe automáticamente.'
        }
        Write-Host 'Pega los valores del modal de Copernicus; el secreto no se mostrará.'
        $clientId = Read-Host 'Client ID'
        $clientSecret = Read-Host 'Client secret' -AsSecureString
    }
    if ($clientId -notmatch '^[a-zA-Z0-9_-]{8,160}$' -or $clientSecret.Length -lt 8) {
        throw 'Credencial incompleta o formato no admitido.'
    }
    # El texto claro existe únicamente en memoria durante el intercambio HTTPS.
    $tokenBody = @{
        grant_type = 'client_credentials'
        client_id = $clientId
        client_secret = [System.Net.NetworkCredential]::new('', $clientSecret).Password
    }
    $tokenResult = Invoke-RestMethod -Method Post -Uri $tokenEndpoint -Body $tokenBody -TimeoutSec 30
    if (-not $tokenResult.access_token -or $tokenResult.expires_in -le 0) {
        throw 'Respuesta de autenticación no válida.'
    }
    if (-not $SoloComprobar) {
        New-Item -ItemType Directory -Path $credentialRoot -Force | Out-Null
        $record = [ordered]@{
            version = 1
            client_id = $clientId
            secret_dpapi = ConvertFrom-SecureString $clientSecret
            expires_utc = '2026-10-26T23:59:59Z'
        }
        # DPAPI sin clave: ligado al usuario Windows actual, fuera del repositorio y OneDrive.
        $record | ConvertTo-Json | Out-File -LiteralPath $credentialFile -Encoding utf8 -NoClobber
        Write-Host 'Credencial cifrada guardada en el perfil local de Windows.'
    }
    Write-Host 'Conexión OAuth verificada. No se solicitaron imágenes ni se guardó el token.'
} catch {
    # No imprimir la excepción HTTP: podría incorporar datos de la solicitud.
    Write-Host 'No se completó la configuración. Revisa ID, secreto, vencimiento o conexión; no pegues el secreto en el chat.'
    exit 1
} finally {
    if ($tokenBody) { $tokenBody.Clear() }
    $tokenResult = $null
    if ($clientSecret) { $clientSecret.Dispose() }
}
