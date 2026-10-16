param([ValidateSet('Plan','Apply','Verify')][string]$Stage='Plan')
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$record=Join-Path $repo '_local/maintenance/version-unica-20261015'
$planPath=Join-Path $record 'plan.json'
function Checked([string]$relative) {
    $p=[IO.Path]::GetFullPath((Join-Path $repo $relative))
    if (!$p.StartsWith($repo+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase) -or
        $relative -match '(^|[/\\])\.git([/\\]|$)' -or $p -eq $record) { throw "Unsafe target: $relative" }
    return $p
}
function Files([string]$p) {
    $item=Get-Item -LiteralPath $p -Force
    if($item.PSIsContainer){Get-ChildItem -LiteralPath $p -File -Recurse -Force}else{$item}
}
if($Stage -eq 'Plan') {
    if(Test-Path -LiteralPath $planPath){throw 'Plan already exists; do not overwrite the audit.'}
    $targets=[Collections.Generic.List[object]]::new()
    function Add([string]$relative,[string]$reason) {
        $p=Checked $relative
        if(Test-Path -LiteralPath $p){$targets.Add([pscustomobject]@{path=$relative;reason=$reason})}
    }
    Get-ChildItem (Join-Path $repo 'videos/expedicion-lote-20261013') -File -Filter 'respaldo-*.zip' |
        ForEach-Object { Add ([IO.Path]::GetRelativePath($repo,$_.FullName)) 'Guion/composición sustituido por la versión vigente' }
    foreach($name in @('reel_ecuador_1900_2025','reel_ecuador_1900_2025_v2','reel_ecuador_1900_2025_v3','reel_ecuador_1900_2025_v4','reel_ecuador_1900_2025_v5')) {
        Add "_local/monitor-artifacts/$name" 'Revisión sísmica sustituida por v6; originales y audio conservados en v6'
    }
    $master='videos/el-nino-no-es-una-fecha'
    Get-ChildItem (Join-Path $repo "$master/qa") -Directory | Where-Object Name -ne 'revision-serie' |
        ForEach-Object {Add ([IO.Path]::GetRelativePath($repo,$_.FullName)) 'Capturas de etapas reemplazadas; se conserva revisión final de la serie'}
    foreach($name in @('acercamiento-60s.png','acercamiento-87s.png','definicion-movimiento.png','walker-movement.png','guion-conectado-contact-sheet.jpg','definicion-keyframes.json')) {
        Add "$master/qa/$name" 'Prueba visual intermedia reemplazada'
    }
    # Keep the newest capture/check AND every artifact still linked by the review page
    # or current metadata. Never touch editor state, media, compositions or source seals.
    $textFiles=@(Get-ChildItem (Join-Path $repo 'videos') -File -Recurse -Force |
        Where-Object {$_.FullName -notmatch '[/\\]\.hyperframes[/\\]|[/\\]assets[/\\]' -and $_.Extension -in '.html','.json','.md'})
    $texts=($textFiles | ForEach-Object {Get-Content -LiteralPath $_.FullName -Raw}) -join "`n"
    foreach($project in Get-ChildItem (Join-Path $repo 'videos') -Directory) {
        foreach($kind in @('checks','snapshots')) {
            $folder=Join-Path $project.FullName ".hyperframes/artifacts/$kind"
            if(!(Test-Path -LiteralPath $folder)){continue}
            $sets=@(Get-ChildItem -LiteralPath $folder -Directory | Sort-Object LastWriteTimeUtc -Descending)
            foreach($set in ($sets | Select-Object -Skip 1)) {
                if(!$texts.Contains($set.Name)) {Add ([IO.Path]::GetRelativePath($repo,$set.FullName)) 'Artefacto de revisión anterior no enlazado; última revisión conservada'}
            }
        }
    }
    Add '_local/maintenance/consolidacion-20261015/archivos-retirados.zip' 'Respaldo de temporales y prototipos retirados, descartado por petición de conservar solo lo actual'
    $removed=@(foreach($target in $targets){foreach($f in Files (Checked $target.path)){
        [pscustomobject]@{path=[IO.Path]::GetRelativePath($repo,$f.FullName);bytes=$f.Length;sha256=(Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash;reason=$target.reason}
    }})
    $prefixes=@($targets | ForEach-Object {(Checked $_.path).TrimEnd('\')})
    $protected=@(foreach($root in @('videos','_local/video-studio/projects','_local/monitor-artifacts/reel_ecuador_1900_2025_v6')) {
        $p=Checked $root
        if(!(Test-Path -LiteralPath $p)){continue}
        foreach($f in Get-ChildItem -LiteralPath $p -File -Recurse -Force) {
            $remove=$false
            foreach($prefix in $prefixes){if($f.FullName -eq $prefix -or $f.FullName.StartsWith($prefix+'\',[StringComparison]::OrdinalIgnoreCase)){$remove=$true;break}}
            if(!$remove){[pscustomobject]@{path=[IO.Path]::GetRelativePath($repo,$f.FullName);bytes=$f.Length;sha256=(Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash}}
        }
    })
    New-Item -ItemType Directory -Path $record -Force | Out-Null
    [pscustomobject]@{created=(Get-Date).ToUniversalTime().ToString('o');targets=@($targets);files=$removed;protected=$protected} |
        ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $planPath -Encoding utf8
    [pscustomobject]@{targets=$targets.Count;files=$removed.Count;logicalMiB=[math]::Round(($removed|Measure-Object bytes -Sum).Sum/1MB,1);protected=$protected.Count} | ConvertTo-Json
    exit
}
$plan=Get-Content -LiteralPath $planPath -Raw | ConvertFrom-Json
if($Stage -eq 'Apply') {
    foreach($f in $plan.files){$p=Checked $f.path;if(!(Test-Path -LiteralPath $p) -or (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash -ne $f.sha256){throw "Changed target: $($f.path)"}}
    foreach($target in $plan.targets){$p=Checked $target.path;Remove-Item -LiteralPath $p -Recurse -Force}
    'Removed only the exact, hash-verified targets in plan.json.'
}
if($Stage -eq 'Verify') {
    $mutable=0
    foreach($f in $plan.protected){
        $p=Checked $f.path
        if(!(Test-Path -LiteralPath $p)){throw "Protected file missing: $($f.path)"}
        # The running Studio preview updates its internal state independently.
        # It is retained, but cannot be required to have a frozen content hash.
        if($f.path -match '[/\\]\.hyperframes[/\\]video-state\.json$'){$mutable++;continue}
        if((Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash -ne $f.sha256){throw "Protected file changed: $($f.path)"}
    }
    foreach($target in $plan.targets){if(Test-Path -LiteralPath (Checked $target.path)){throw "Target remains: $($target.path)"}}
    "Verified $($plan.protected.Count-$mutable) retained files unchanged; $mutable live editor states retained; $($plan.files.Count) superseded files removed."
}
