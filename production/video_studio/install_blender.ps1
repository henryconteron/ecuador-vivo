param([switch]$KeepArchive)
$ErrorActionPreference = 'Stop'
$blenderVersion = '4.5.4'
$blenderName = "blender-$blenderVersion-windows-x64"
$blenderTools = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../_local/video-studio/tools'))
$blenderArchive = Join-Path $blenderTools "$blenderName.zip"
$blenderFolder = Join-Path $blenderTools $blenderName
$blenderExe = Join-Path $blenderFolder 'blender.exe'
$blenderUrl = "https://download.blender.org/release/Blender4.5/$blenderName.zip"
$blenderHashUrl = "https://download.blender.org/release/Blender4.5/blender-$blenderVersion.sha256"
New-Item -ItemType Directory -Path $blenderTools -Force | Out-Null
if (Test-Path -LiteralPath $blenderExe) {
    & $blenderExe --background --factory-startup --disable-autoexec --version
    if ($LASTEXITCODE -ne 0) { throw 'Blender está presente pero no pudo arrancar.' }
    Write-Output $blenderExe; exit 0
}
if (Test-Path -LiteralPath $blenderFolder) { throw 'Hay una instalación incompleta. No se sobrescribirá.' }
$blenderHashes = (Invoke-WebRequest $blenderHashUrl -TimeoutSec 30 -UseBasicParsing).Content
$blenderHashLine = @($blenderHashes -split "`n" | Where-Object { $_ -match ([regex]::Escape("$blenderName.zip")+'\s*$') })
if ($blenderHashLine.Count -ne 1 -or $blenderHashLine[0] -notmatch '^([a-fA-F0-9]{64})\s+') { throw 'No se pudo comprobar la huella oficial.' }
$blenderExpectedHash = $Matches[1].ToLowerInvariant()
if (!(Test-Path -LiteralPath $blenderArchive)) {
    Invoke-WebRequest $blenderUrl -OutFile $blenderArchive -TimeoutSec 900 -UseBasicParsing
}
if ((Get-FileHash -LiteralPath $blenderArchive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $blenderExpectedHash) { throw 'La descarga no coincide con el SHA-256 oficial. No se ejecutará.' }
Add-Type -AssemblyName System.IO.Compression.FileSystem
$blenderZip = [IO.Compression.ZipFile]::OpenRead($blenderArchive)
try {
    foreach ($blenderEntry in $blenderZip.Entries) {
        $blenderTarget = [IO.Path]::GetFullPath((Join-Path $blenderTools $blenderEntry.FullName))
        if (!$blenderTarget.StartsWith($blenderFolder+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase) -and $blenderTarget -ne $blenderFolder) { throw 'La descarga contiene una ruta no permitida.' }
    }
} finally { $blenderZip.Dispose() }
[IO.Compression.ZipFile]::ExtractToDirectory($blenderArchive,$blenderTools)
if (!(Test-Path -LiteralPath $blenderExe)) { throw 'La descarga no contiene Blender.' }
$blenderReport = [ordered]@{version=$blenderVersion;source=$blenderUrl;archive_sha256=$blenderExpectedHash;executable_sha256=(Get-FileHash -LiteralPath $blenderExe -Algorithm SHA256).Hash.ToLowerInvariant();installed_at=(Get-Date).ToString('o')}
$blenderReport | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $blenderFolder 'ecuador-vivo-install.json') -Encoding utf8
if (!$KeepArchive) {
    if ([IO.Path]::GetFullPath($blenderArchive) -ne (Join-Path $blenderTools "$blenderName.zip")) { throw 'No se retirará una ruta no verificada.' }
    Remove-Item -LiteralPath $blenderArchive
}
& $blenderExe --background --factory-startup --disable-autoexec --version
if ($LASTEXITCODE -ne 0) { throw 'Blender se verificó pero no pudo arrancar; revisa la instalación de Windows.' }
Write-Output $blenderExe
