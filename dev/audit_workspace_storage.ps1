#Requires -Version 7.2
param(
    [Parameter(Mandatory=$true)][string]$Workspace,
    [Parameter(Mandatory=$true)][string]$ReportDirectory
)
$ErrorActionPreference = 'Stop'
$rootPath = (Resolve-Path -LiteralPath $Workspace).Path.TrimEnd('\')
$reportPath = [IO.Path]::GetFullPath($ReportDirectory)
$allowedReports = Join-Path $rootPath '_local\maintenance'
if (-not $reportPath.StartsWith($allowedReports + '\', [StringComparison]::OrdinalIgnoreCase)) {
    throw 'The report must stay inside the workspace maintenance directory.'
}
if (Test-Path -LiteralPath $reportPath) { throw 'Use a new report directory; existing evidence is never overwritten.' }
New-Item -ItemType Directory -Path $reportPath -Force | Out-Null
$files = [Collections.Generic.List[object]]::new()
$directories = @{}
$failures = [Collections.Generic.List[string]]::new()
$pending = [Collections.Generic.Stack[string]]::new()
$pending.Push($rootPath)
while ($pending.Count -gt 0) {
    $folder = $pending.Pop()
    $relativeFolder = $folder.Substring($rootPath.Length).TrimStart('\')
    if ($relativeFolder) { $directories[$relativeFolder] = @{ bytes = [long]0; files = 0 } }
    try { $entries = [IO.DirectoryInfo]::new($folder).GetFileSystemInfos() }
    catch { $failures.Add($folder + ': ' + $_.Exception.Message); continue }
    foreach ($entry in $entries) {
        if ($entry.Attributes -band [IO.FileAttributes]::Directory) {
            # OneDrive cloud directories also carry ReparsePoint. Only skip
            # actual junction/symlink targets, not ordinary cloud placeholders.
            if ($entry.LinkTarget) {
                $failures.Add('Link not traversed: ' + $entry.FullName)
            } else { $pending.Push($entry.FullName) }
        } else {
            $relative = $entry.FullName.Substring($rootPath.Length).TrimStart('\')
            $files.Add([pscustomobject]@{
                path = $relative; bytes = [long]$entry.Length
                modified_utc = $entry.LastWriteTimeUtc.ToString('o')
                attributes = [string]$entry.Attributes
            })
        }
    }
    if ($directories.Count % 5000 -eq 0) {
        Write-Host ('Metadata scanned: {0} directories / {1} files' -f $directories.Count,$files.Count)
    }
}
# Aggregate metadata only: this does not read/hydrate raster or media content.
foreach ($file in $files) {
    $parent = [IO.Path]::GetDirectoryName($file.path)
    while ($parent) {
        if ($directories.ContainsKey($parent)) {
            $directories[$parent].bytes += $file.bytes
            $directories[$parent].files += 1
        }
        $parent = [IO.Path]::GetDirectoryName($parent)
    }
}
$directoryRows = @($directories.GetEnumerator() | ForEach-Object {
    [pscustomobject]@{ path=$_.Key; bytes=$_.Value.bytes; files=$_.Value.files }
} | Sort-Object bytes -Descending)
$total = [long]0
foreach ($file in $files) { $total += $file.bytes }
$summary = [ordered]@{
    workspace = $rootPath; measured_utc = [DateTime]::UtcNow.ToString('o')
    logical_bytes = $total; file_count = $files.Count
    directory_count = $directories.Count; errors_or_untraversed_links = @($failures)
    largest_directories = @($directoryRows | Select-Object -First 70)
    largest_files = @($files | Sort-Object bytes -Descending | Select-Object -First 35)
}
$files | Export-Csv -LiteralPath (Join-Path $reportPath 'files.csv') -NoTypeInformation -Encoding utf8
$directoryRows | Export-Csv -LiteralPath (Join-Path $reportPath 'directories.csv') -NoTypeInformation -Encoding utf8
$summary | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $reportPath 'summary.json') -Encoding utf8
[pscustomobject]@{ bytes=$total; GiB=[math]::Round($total/1GB,3); files=$files.Count; folders=$directories.Count; report=$reportPath } | Format-List
$directoryRows | Where-Object { ($_.path.Split('\').Count -le 3) } | Select-Object -First 45 path,@{n='MiB';e={[math]::Round($_.bytes/1MB,1)}},files | Format-Table -AutoSize
