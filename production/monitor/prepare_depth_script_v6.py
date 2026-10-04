"""Build a local audio-only reading for the revised narrative; preserve V5 video."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import wave
import imageio_ffmpeg
from prepare_depth_story_v5 import V5

V6=V5.parent/'v6'
SCRIPT=V6/'guion_elevenlabs_v6.txt'
NAMES=('gancho','cortes','foco','material','p','s','internas','love','rayleigh','registro',
       'profundidad','distancia','bolivia','magnitud','loreto','ecuador','suelo','edificio',
       'pedernales','pelileo','reventador','retorno','cierre')


def parts():
    paragraphs=SCRIPT.read_text(encoding='utf-8').strip().split('\n\n')
    if len(paragraphs)!=len(NAMES):raise ValueError('Narrative/beat mismatch')
    return dict(zip(NAMES,paragraphs))


def prepare():
    narration=parts();folder=V6/'audio_provisional';folder.mkdir(parents=True,exist_ok=True)
    (folder/'narration.json').write_text(json.dumps(narration,ensure_ascii=False,indent=2),encoding='utf-8')
    subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',
        str(Path(__file__).with_name('synthesize_depth_story_v4.ps1')),'-OutputDirectory',str(folder)],check=True)
    segments=[];cursor=0;full=folder/'lectura_completa_v6.wav'
    with wave.open(str(full),'wb') as dest:
        dest.setnchannels(1);dest.setsampwidth(2);dest.setframerate(16000)
        for name in NAMES:
            path=folder/f'voz_{name}.wav'
            with wave.open(str(path)) as audio:
                if (audio.getnchannels(),audio.getsampwidth(),audio.getframerate())!=(1,2,16000):raise ValueError('Expected PCM16 mono 16kHz')
                frames=audio.getnframes();data=audio.readframes(frames)
            start=cursor/16000;dest.writeframes(b'\0'*6400);dest.writeframes(data);dest.writeframes(b'\0'*11200)
            cursor+=3200+frames+5600
            segments.append(dict(name=name,start=start,end=cursor/16000,speech_start=start+.2,
                speech_seconds=frames/16000,file=path.name,sha256=sha256(path.read_bytes()).hexdigest()))
    mp3=V6/'lectura_guion_voz_provisional_v6.mp3';ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ffmpeg,'-v','error','-i',str(full),'-c:a','libmp3lame','-b:a','128k','-y',str(mp3)],check=True)
    preview=V6/'avance_guion_voz_provisional_v6.mp3'
    # Opening, causal question, focus and traced material; no edited video implied.
    subprocess.run([ffmpeg,'-v','error','-i',str(full),'-t',str(segments[3]['end']),
        '-c:a','libmp3lame','-b:a','128k','-y',str(preview)],check=True)
    for path in (mp3,preview):subprocess.run([ffmpeg,'-v','error','-i',str(path),'-f','null','-'],check=True,capture_output=True)
    report=dict(status='audio_only_narrative_review_not_publication',script_sha256=sha256(SCRIPT.read_bytes()).hexdigest(),
        word_count=len(SCRIPT.read_text(encoding='utf-8').split()),duration_seconds=cursor/16000,
        segments=segments,voice='Microsoft Helena Desktop, provisional local reading',
        output=dict(file=mp3.name,sha256=sha256(mp3.read_bytes()).hexdigest(),full_decode='passed'),
        preview=dict(file=preview.name,duration_seconds=segments[3]['end'],sha256=sha256(preview.read_bytes()).hexdigest(),full_decode='passed'),
        unchanged_video='v5/ondas_profundidad_3d_voz_provisional_v5.mp4',
        limitations='Audio only; does not retime or change the V5 video. Final voice, edited scenes and human review pending.')
    (V6/'audio_review_v6.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({key:report[key] for key in ('status','word_count','duration_seconds','output','preview')},ensure_ascii=False,indent=2))


if __name__=='__main__':prepare()
