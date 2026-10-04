param([Parameter(Mandatory=$true)][string]$OutputDirectory)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
Add-Type -ReferencedAssemblies System.Speech -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.Speech.Synthesis;
public class DepthWordMark {
    public string Text {get;set;}
    public int Character {get;set;}
    public double Seconds {get;set;}
}
public static class DepthSpeechClock {
    public static List<DepthWordMark> Marks = new List<DepthWordMark>();
    public static void OnProgress(object sender, SpeakProgressEventArgs e) {
        Marks.Add(new DepthWordMark { Text=e.Text, Character=e.CharacterPosition, Seconds=e.AudioPosition.TotalSeconds });
    }
    public static void Attach(SpeechSynthesizer voice) { voice.SpeakProgress += OnProgress; }
}
'@
$storyOutput = (Resolve-Path -LiteralPath $OutputDirectory).Path
$storyParts = Get-Content -LiteralPath (Join-Path $storyOutput 'narration.json') -Encoding UTF8 -Raw | ConvertFrom-Json
$storySpeech = New-Object System.Speech.Synthesis.SpeechSynthesizer
$storyFormat = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo -ArgumentList 16000,([System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen),([System.Speech.AudioFormat.AudioChannel]::Mono)
$storyClock = @{}
try {
    $storySpeech.SelectVoice('Microsoft Helena Desktop')
    $storySpeech.Rate = 0
    [DepthSpeechClock]::Attach($storySpeech)
    foreach ($storyPart in $storyParts.PSObject.Properties) {
        if ($storyPart.Name -notmatch '^[a-z]+$') { throw 'Invalid segment name' }
        [DepthSpeechClock]::Marks.Clear()
        # Explicit format avoids a .NET SpeakProgress clock/sample-rate mismatch
        # observed with the default Helena 22050-Hz WAV output on this machine.
        $storySpeech.SetOutputToWaveFile((Join-Path $storyOutput ('voz_' + $storyPart.Name + '.wav')), $storyFormat)
        $storySpeech.Speak([string]$storyPart.Value)
        $storySpeech.SetOutputToNull()
        $storyClock[$storyPart.Name] = @([DepthSpeechClock]::Marks.ToArray())
    }
    $storyClock | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $storyOutput 'word_marks.json') -Encoding UTF8
    Write-Output 'Helena: local provisional narration with word timestamps; no paid service.'
} finally { $storySpeech.Dispose() }
