param([Parameter(Mandatory=$true)][string]$OutputDirectory)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$depthOutput = (Resolve-Path -LiteralPath $OutputDirectory).Path
$depthParts = Get-Content -LiteralPath (Join-Path $depthOutput 'narration.json') -Encoding UTF8 -Raw | ConvertFrom-Json
$depthSpeech = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $depthSpeech.SelectVoice('Microsoft Helena Desktop')
    $depthSpeech.Rate = 0
    foreach ($depthPart in $depthParts.PSObject.Properties) {
        if ($depthPart.Name -notmatch '^[a-z]+$') { throw 'Invalid segment name' }
        $depthSpeech.SetOutputToWaveFile((Join-Path $depthOutput ('voz_' + $depthPart.Name + '.wav')))
        $depthSpeech.Speak([string]$depthPart.Value)
        $depthSpeech.SetOutputToNull()
    }
    Write-Output 'Microsoft Helena Desktop (es-ES): provisional narration generated locally.'
} finally { $depthSpeech.Dispose() }
