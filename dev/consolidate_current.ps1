#Requires -Version 7.2
param([ValidateSet('Prepare','Organize','Clean','Verify','Finish','Seal')][string]$Stage='Prepare')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..')).TrimEnd('\')
$taskReport=Join-Path $taskRoot '_local/maintenance/consolidacion-20261015'
$taskPlan=Join-Path $taskReport 'plan.json'
$taskProtection=Join-Path $taskReport 'protected.json'
$taskZip=Join-Path $taskReport 'archivos-retirados.zip'

function Confirm-WorkspacePath([string]$Path) {
    $resolved=[IO.Path]::GetFullPath($Path).TrimEnd('\')
    $gitDirectory=Join-Path $taskRoot '.git'
    if(-not $resolved.StartsWith($taskRoot+'\',[StringComparison]::OrdinalIgnoreCase) -or $resolved -eq $gitDirectory -or $resolved.StartsWith($gitDirectory+'\',[StringComparison]::OrdinalIgnoreCase)) { throw "Ruta fuera del alcance: $resolved" }
    $current=$resolved
    while($current -and $current -ne $taskRoot) {
        if(Test-Path -LiteralPath $current) {
            if((Get-Item -Force -LiteralPath $current).LinkTarget) {throw "Enlace no autorizado: $current"}
        }
        $current=[IO.Path]::GetDirectoryName($current)
    }
    return $resolved
}
function Get-RegularFiles([string]$Path) {
    $resolved=Confirm-WorkspacePath $Path
    if(-not (Test-Path -LiteralPath $resolved)){return}
    $item=Get-Item -Force -LiteralPath $resolved
    if(-not $item.PSIsContainer){return $item}
    $pending=[Collections.Generic.Stack[string]]::new();$pending.Push($resolved)
    while($pending.Count) {
        foreach($child in Get-ChildItem -Force -LiteralPath $pending.Pop()) {
            if($child.LinkTarget){throw "No recorrer enlaces: $($child.FullName)"}
            if($child.PSIsContainer){$pending.Push($child.FullName)}else{$child}
        }
    }
}
function Get-Record($File) {
    [pscustomobject]@{path=$File.FullName.Substring($taskRoot.Length+1).Replace('\','/');bytes=$File.Length;sha256=(Get-FileHash -LiteralPath $File.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}
}
function Confirm-NoWorkers {
    $workers=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(blender|ffmpeg)\.exe$' -or ($_.Name -match '^python(w)?\.exe$' -and $_.CommandLine -match 'studio_(blender_worker|worker|jobs|sig_analysis_jobs)\.py') })
    if($workers.Count){throw 'Hay un render o cálculo activo; no limpiar durante su ejecución.'}
    $prototype=@(Get-NetTCPConnection -State Listen -LocalPort 3018 -ErrorAction SilentlyContinue)
    if($prototype.Count){throw 'El prototipo Remotion sigue activo en 3018.'}
}
function Confirm-Archive($Rows) {
    $archive=[IO.Compression.ZipFile]::OpenRead($taskZip)
    try {
        foreach($row in $Rows) {
            $entry=$archive.GetEntry($row.path)
            if(-not $entry -or $entry.Length -ne $row.bytes){throw "Respaldo incompleto: $($row.path)"}
            $stream=$entry.Open()
            try{$hash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($stream)).ToLowerInvariant()}finally{$stream.Dispose()}
            if($hash -ne $row.sha256){throw "Hash ZIP distinto: $($row.path)"}
        }
    } finally {$archive.Dispose()}
}

if($Stage -eq 'Prepare') {
    Confirm-NoWorkers
    if(Test-Path -LiteralPath $taskPlan){throw 'El plan ya existe; no sobrescribir evidencia.'}
    New-Item -ItemType Directory -Path $taskReport -Force | Out-Null
    $targets=[Collections.Generic.List[object]]::new()
    foreach($item in Get-ChildItem -Force -LiteralPath (Join-Path $taskRoot 'tmp')) {
        $targets.Add([pscustomobject]@{path=Confirm-WorkspacePath $item.FullName;action='archive_remove';reason='Pruebas y revisiones temporales anteriores'})
    }
    foreach($relative in @('_local/qa','_local/performance-20261013','_local/resource-development-20261012','_local/ev-science-map/src','_local/ev-science-map/package.json','_local/ev-science-map/package-lock.json','_local/ev-science-map/preview.log','_local/ev-science-map/preview-errors.log','dev/archive_old_studio_projects.ps1','dev/cleanup_expedicion_superseded.ps1','dev/remove_verified_monitor_drafts.ps1','dev/remove_verified_qa_profiles.ps1')) {
        $path=Join-Path $taskRoot $relative
        if(Test-Path -LiteralPath $path){$targets.Add([pscustomobject]@{path=Confirm-WorkspacePath $path;action='archive_remove';reason='Prototipo o mantenimiento anterior, sin uso en la aplicación'})}
    }
    foreach($item in Get-ChildItem -File -LiteralPath (Join-Path $taskRoot '_local')) {
        if($item.Extension -in @('.png','.jpg','.jpeg')){$targets.Add([pscustomobject]@{path=Confirm-WorkspacePath $item.FullName;action='archive_remove';reason='Captura suelta de revisión'})}
    }
    $targets.Add([pscustomobject]@{path=Confirm-WorkspacePath (Join-Path $taskRoot '_local/ev-science-map/node_modules');action='regenerate_remove';reason='Dependencias y caché del prototipo Remotion retirado'})
    $archiveRows=[Collections.Generic.List[object]]::new()
    foreach($target in $targets) {
        if($target.action -eq 'archive_remove'){foreach($file in Get-RegularFiles $target.path){$archiveRows.Add((Get-Record $file))}}
    }
    # Keep the pre-clean build for recovery while replacing every active variant
    # with the single canonical bundle. These paths are not deletion targets.
    foreach($relative in @('production/video_studio/ecuador-vivo-sig-map/ecuador_vivo_sig_map/frontend/build','production/video_studio/ecuador-vivo-sig-map/ecuador_vivo_sig_map/__init__.py','production/video_studio/ecuador-vivo-sig-map/ecuador_vivo_sig_map/frontend/vite.config.ts')) {
        foreach($file in Get-RegularFiles (Join-Path $taskRoot $relative)){$archiveRows.Add((Get-Record $file))}
    }
    # Data, authored videos, all saved projects and shared assets stay exactly as
    # they are. Runtime installations and generated QA are outside this guard.
    $protected=[Collections.Generic.List[object]]::new()
    foreach($relative in @('assets','data','videos','output','_local/climate-studio','_local/monitor-artifacts','_local/video-studio/projects','_local/video-studio/media','_local/video-studio/geography','_local/video-studio/downloads','_local/video-studio/cache','_local/video-studio/jobs','_local/video-studio/social-pilots-20261011','_local/video-studio/resource-3d','_local/site-admin')) {
        foreach($file in Get-RegularFiles (Join-Path $taskRoot $relative)){$protected.Add((Get-Record $file))}
    }
    # A saved project must never depend on a target being retired.
    foreach($file in Get-RegularFiles (Join-Path $taskRoot '_local/video-studio/projects')) {
        $text=Get-Content -Raw -LiteralPath $file.FullName
        $text=$text.Replace('\\','/').Replace('\','/')
        foreach($target in $targets) {
            $relative=$target.path.Substring($taskRoot.Length+1).Replace('\','/')
            if($text.Contains($relative)){throw "Proyecto guardado depende de $relative"}
        }
    }
    $protected | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $taskProtection -Encoding utf8
    $plan=[ordered]@{workspace=$taskRoot;created_utc=[DateTime]::UtcNow.ToString('o');targets=@($targets);archive_files=@($archiveRows);protected_files=$protected.Count}
    $plan | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $taskPlan -Encoding utf8
    $archive=[IO.Compression.ZipFile]::Open($taskZip,[IO.Compression.ZipArchiveMode]::Create)
    try {
        foreach($row in $archiveRows){[IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive,(Join-Path $taskRoot $row.path),$row.path,[IO.Compression.CompressionLevel]::Fastest)|Out-Null}
    }finally{$archive.Dispose()}
    Confirm-Archive $archiveRows
    [pscustomobject]@{stage=$Stage;targets=$targets.Count;archived_files=$archiveRows.Count;protected_files=$protected.Count;archive_bytes=(Get-Item -LiteralPath $taskZip).Length;report=$taskReport}|ConvertTo-Json
    exit
}

$plan=Get-Content -Raw -LiteralPath $taskPlan | ConvertFrom-Json
if($plan.workspace -ne $taskRoot){throw 'El plan corresponde a otro workspace.'}
if($Stage -eq 'Organize') {
    $externalRoot='C:\Users\JHONY CONTERON\Documents\Codex\2026-10-05\continua-implementa-todo-lo-que-puedas'
    $moves=@(
        @('_local/ev-science-map/python-deps','_local/scientific-inputs/enso/python-deps'),
        @('_local/ev-science-map/public','_local/scientific-inputs/enso/reference-data'),
        @((Join-Path $externalRoot 'reference-audit-20261015'),'_local/maintenance/revisiones-20261015/referencias-sig'),
        @((Join-Path $externalRoot 'output/design-styles-20261013'),'_local/maintenance/revisiones-20261015/diseno'),
        @((Join-Path $externalRoot 'video-origin-review'),'_local/maintenance/revisiones-20261015/video-origen'),
        @((Join-Path $externalRoot 'analisis-piloto-tiktok-instagram.md'),'_local/maintenance/revisiones-20261015/notas/analisis-piloto-tiktok-instagram.md'),
        @((Join-Path $externalRoot 'editor-interfaz.png'),'_local/maintenance/revisiones-20261015/notas/editor-interfaz.png'),
        @((Join-Path $externalRoot 'editor-ordenado.jpg'),'_local/maintenance/revisiones-20261015/notas/editor-ordenado.jpg')
    )
    $journal=[Collections.Generic.List[object]]::new()
    foreach($move in $moves) {
        $source=if([IO.Path]::IsPathRooted($move[0])){[IO.Path]::GetFullPath($move[0])}else{Confirm-WorkspacePath (Join-Path $taskRoot $move[0])}
        $destination=Confirm-WorkspacePath (Join-Path $taskRoot $move[1])
        if(-not (Test-Path -LiteralPath $source)){continue}
        if(-not $source.StartsWith($taskRoot+'\',[StringComparison]::OrdinalIgnoreCase) -and -not $source.StartsWith($externalRoot+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Origen externo no autorizado.'}
        if(Test-Path -LiteralPath $destination){throw "No sobrescribir destino: $destination"}
        $item=Get-Item -Force -LiteralPath $source
        $children=if($item.PSIsContainer){@(Get-ChildItem -Recurse -Force -LiteralPath $source)}else{@($item)}
        if($item.LinkTarget -or @($children|Where-Object LinkTarget).Count){throw 'No mover árboles con enlaces.'}
        $proof=@($children|Where-Object {-not $_.PSIsContainer}|ForEach-Object {[pscustomobject]@{suffix=if($item.PSIsContainer){$_.FullName.Substring($source.Length+1)}else{''};sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash}})
        New-Item -ItemType Directory -Force -Path ([IO.Path]::GetDirectoryName($destination))|Out-Null
        Move-Item -LiteralPath $source -Destination $destination
        foreach($entry in $proof) {
            $path=if($entry.suffix){Join-Path $destination $entry.suffix}else{$destination}
            if((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ne $entry.sha256){throw "Cambio durante el traslado: $path"}
        }
        $journal.Add([pscustomobject]@{source=$source;destination=$destination;files=$proof.Count;verified=$true})
        $journal|ConvertTo-Json -Depth 4|Set-Content -LiteralPath (Join-Path $taskReport 'moves.json') -Encoding utf8
    }
    $journal|ConvertTo-Json -Depth 4
    exit
}
if($Stage -eq 'Clean') {
    Confirm-NoWorkers
    Confirm-Archive $plan.archive_files
    $known=@{}
    foreach($row in $plan.archive_files){$known[[IO.Path]::GetFullPath((Join-Path $taskRoot $row.path))]=$row}
    foreach($target in $plan.targets) {
        $path=Confirm-WorkspacePath $target.path
        if($target.action -eq 'archive_remove') {
            foreach($file in Get-RegularFiles $path) {
                $row=$known[$file.FullName]
                if(-not $row -or (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant() -ne $row.sha256){throw "Archivo nuevo o modificado sin respaldo: $($file.FullName)"}
            }
        } elseif($target.action -ne 'regenerate_remove' -or $path -ne (Join-Path $taskRoot '_local/ev-science-map/node_modules')) {throw 'Acción no autorizada en el plan.'}
    }
    foreach($target in $plan.targets) {
        $path=Confirm-WorkspacePath $target.path
        if(Test-Path -LiteralPath $path){Remove-Item -LiteralPath $path -Recurse -Force}
    }
    $plan.targets | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $taskReport 'removed.json') -Encoding utf8
    [pscustomobject]@{stage=$Stage;removed_targets=$plan.targets.Count;recovery=$taskZip}|ConvertTo-Json
    exit
}

if($Stage -eq 'Finish') {
    $cacheRows=[Collections.Generic.List[object]]::new()
    $inventory=Import-Csv -LiteralPath (Join-Path $taskReport 'antes/directories.csv')
    foreach($row in $inventory) {
        if($row.path -notmatch '^(production|scripts|dev|tests)\\(?:.*\\)?__pycache__$' -or $row.path -match '(^|\\)(node_modules|\.venv|\.git)(\\|$)'){continue}
        $path=Confirm-WorkspacePath (Join-Path $taskRoot $row.path)
        if(Test-Path -LiteralPath $path) {
            if((Get-Item -Force -LiteralPath $path).Name -ne '__pycache__'){throw 'No es una caché Python.'}
            $cacheRows.Add([pscustomobject]@{path=$row.path;bytes=[long]$row.bytes;recovery='Regenerable por Python'})
            Remove-Item -LiteralPath $path -Recurse -Force
        }
    }
    foreach($relative in @('tmp','_local/ev-science-map')) {
        $path=Confirm-WorkspacePath (Join-Path $taskRoot $relative)
        if((Test-Path -LiteralPath $path) -and @(Get-ChildItem -Force -LiteralPath $path).Count -eq 0){Remove-Item -LiteralPath $path}
    }
    $cacheRows|ConvertTo-Json -Depth 3|Set-Content -LiteralPath (Join-Path $taskReport 'regenerable-caches.json') -Encoding utf8
    [pscustomobject]@{stage=$Stage;removed_python_caches=$cacheRows.Count}|ConvertTo-Json
    exit
}
if($Stage -eq 'Seal') {
    $files=[Collections.Generic.List[object]]::new()
    Push-Location $taskRoot
    try {
        $names=@(& git -c core.quotepath=false ls-files --cached --others --exclude-standard)
        foreach($name in $names) {
            $path=Confirm-WorkspacePath (Join-Path $taskRoot $name)
            if(Test-Path -LiteralPath $path -PathType Leaf){$files.Add((Get-Record (Get-Item -LiteralPath $path)))}
        }
    }finally{Pop-Location}
    $files|ConvertTo-Json -Depth 3|Set-Content -LiteralPath (Join-Path $taskReport 'current-source-manifest.json') -Encoding utf8
    [pscustomobject]@{stage=$Stage;source_files=$files.Count;manifest=(Join-Path $taskReport 'current-source-manifest.json')}|ConvertTo-Json
    exit
}
$protected=Get-Content -Raw -LiteralPath $taskProtection | ConvertFrom-Json
foreach($row in $protected) {
    $path=Confirm-WorkspacePath (Join-Path $taskRoot $row.path)
    if(-not (Test-Path -LiteralPath $path) -or (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $row.sha256){throw "Cambió un archivo protegido: $($row.path)"}
}
[pscustomobject]@{stage=$Stage;verified_files=$protected.Count;status='Todos los proyectos, datos, medios y videos protegidos conservan su SHA-256'} | ConvertTo-Json | Tee-Object -FilePath (Join-Path $taskReport 'verification.json')
