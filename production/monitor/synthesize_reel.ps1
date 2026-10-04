param([Parameter(Mandatory=$true)][string]$OutputDirectory)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$reelOutput = (Resolve-Path -LiteralPath $OutputDirectory).Path
$reelScript = Get-Content -LiteralPath (Join-Path $reelOutput 'narration.json') -Encoding UTF8 -Raw | ConvertFrom-Json
$reelSpeech = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $reelVoice = @($reelSpeech.GetInstalledVoices() | Where-Object { $_.VoiceInfo.Name -eq 'Microsoft Pablo' -and $_.VoiceInfo.Culture.Name -eq 'es-ES' })
    if ($reelVoice.Count -ne 1) { throw 'The configured Spanish system voice is not installed. Use --silent or configure an installed Spanish voice.' }
    $reelSpeech.SelectVoice('Microsoft Pablo')
    $reelSpeech.Rate = 0
    foreach ($reelPart in $reelScript.PSObject.Properties) {
        if ($reelPart.Name -notmatch '^[a-z]+$') { throw 'Invalid narration segment name.' }
        $reelWave = Join-Path $reelOutput ('voz_' + $reelPart.Name + '.wav')
        $reelSpeech.SetOutputToWaveFile($reelWave)
        $reelSpeech.Speak([string]$reelPart.Value)
        $reelSpeech.SetOutputToNull()
    }
    Write-Output 'Narration generated with Microsoft Pablo (es-ES), an installed synthetic system voice.'
} finally {
    $reelSpeech.Dispose()
}
