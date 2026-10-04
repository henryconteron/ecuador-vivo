"""Independent conversational reading. Does not edit or retime existing video."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import wave
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent
V7 = ROOT / 'artifacts/serie_memoria_sismica/00_profundidad_danos/v7'
SCRIPT = V7 / 'guion_elevenlabs_v7_corregido.txt'
NAMES = ('cortes', 'gancho', 'foco', 'ruptura', 'particula',
         'resorte', 'p', 'cuerda', 's', 'velocidad', 'agua', 'superficie',
         'love', 'rayleigh', 'mezcla', 'registro', 'profundidad', 'distancia',
         'bolivia', 'magnitud', 'loreto', 'tena', 'suelo', 'ritmo', 'bus',
         'columpio', 'limites', 'pedernales', 'pelileo', 'piedemonte',
         'contraste', 'retorno', 'conciencia')


def parts():
    paragraphs = SCRIPT.read_text(encoding='utf-8').strip().split('\n\n')
    if len(paragraphs) != len(NAMES):
        raise ValueError('Narrative/beat mismatch')
    return dict(zip(NAMES, paragraphs))


def prepare():
    narration = parts()
    folder = V7 / 'audio_provisional'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'narration.json').write_text(json.dumps(narration, ensure_ascii=False, indent=2), encoding='utf-8')
    subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                    str(ROOT / 'synthesize_depth_story_v4.ps1'), '-OutputDirectory', str(folder)], check=True)
    segments = []
    cursor = 0
    full = folder / 'lectura_completa_v7.wav'
    with wave.open(str(full), 'wb') as dest:
        dest.setnchannels(1)
        dest.setsampwidth(2)
        dest.setframerate(16000)
        for name in NAMES:
            path = folder / f'voz_{name}.wav'
            with wave.open(str(path)) as audio:
                if (audio.getnchannels(), audio.getsampwidth(), audio.getframerate()) != (1, 2, 16000):
                    raise ValueError('Expected PCM16 mono 16kHz')
                frames = audio.getnframes()
                data = audio.readframes(frames)
            start = cursor / 16000
            dest.writeframes(b'\0' * 9600)
            dest.writeframes(data)
            dest.writeframes(b'\0' * 19200)
            cursor += 4800 + frames + 9600
            segments.append(dict(name=name, start=start, end=cursor / 16000,
                                 speech_start=start + .3, speech_seconds=frames / 16000,
                                 file=path.name, sha256=sha256(path.read_bytes()).hexdigest()))
    mp3 = V7 / 'lectura_guion_voz_provisional_v7_corregido.mp3'
    preview = V7 / 'avance_guion_voz_provisional_v7_corregido.mp3'
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    for path, options in ((mp3, []), (preview, ['-t', str(segments[1]['end'])])):
        subprocess.run([ffmpeg, '-v', 'error', '-i', str(full), *options,
                        '-c:a', 'libmp3lame', '-b:a', '128k', '-y', str(path)], check=True)
        subprocess.run([ffmpeg, '-v', 'error', '-i', str(path), '-f', 'null', '-'],
                       check=True, capture_output=True)
    report = dict(status='audio_only_narrative_review_not_publication',
                  script_file=SCRIPT.name, script_sha256=sha256(SCRIPT.read_bytes()).hexdigest(),
                  word_count=len(SCRIPT.read_text(encoding='utf-8').split()),
                  duration_seconds=cursor / 16000, segments=segments,
                  voice='Microsoft Helena Desktop, provisional local reading',
                  output=dict(file=mp3.name, sha256=sha256(mp3.read_bytes()).hexdigest(), full_decode='passed'),
                  preview=dict(file=preview.name, duration_seconds=segments[1]['end'],
                               sha256=sha256(preview.read_bytes()).hexdigest(), full_decode='passed'),
                  unchanged_video='v5/ondas_profundidad_3d_voz_provisional_v5.mp4',
                  limitations='Audio only, not a synchronized video. Synthetic delivery is not final acting; final voice and human listening review pending.')
    (V7 / 'audio_review_v7.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({key: report[key] for key in ('status', 'word_count', 'duration_seconds', 'output', 'preview')},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    prepare()
