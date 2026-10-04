"""Inspect the encoded v9 video, audio and every shot, not just design sources."""
from hashlib import sha256
import json
import math
import re
import subprocess
import wave
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw
import reel_river_satellite_story as s

def main():
    meta=json.loads((s.FOLDER/'video_metadata.json').read_text(encoding='utf-8'))
    sources=json.loads((s.FOLDER/'sources_manifest.json').read_text(encoding='utf-8'))
    assert sha256(s.OUTPUT.read_bytes()).hexdigest()==meta['video_sha256']
    for field,file in (('source_manifest_sha256','sources_manifest.json'),('script_sha256','narration.json')):
        assert sha256((s.FOLDER/file).read_bytes()).hexdigest()==meta[field]
    for row in sources['images']:
        assert sha256((s.FOLDER/row['file']).read_bytes()).hexdigest()==row['sha256']
    for file,digest in sources['local_files'].items():
        assert sha256((s.EVIDENCE/file).read_bytes()).hexdigest()==digest
    for file,digest in sources['previous_renders'].items():
        assert sha256(s.Path(file).read_bytes()).hexdigest()==digest
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    probe=subprocess.run([ff,'-hide_banner','-i',str(s.OUTPUT)],capture_output=True,text=True)
    assert re.search(r'Video: h264.*1080x1920.*30 fps',probe.stderr)
    assert 'Audio: aac' in probe.stderr
    decode=subprocess.run([ff,'-v','error','-i',str(s.OUTPUT),'-map','0:v:0','-an','-progress','pipe:1','-f','null','-'],capture_output=True,text=True,check=True)
    frames=[int(n) for n in re.findall(r'^frame=(\d+)$',decode.stdout,re.M)]
    assert frames[-1]==meta['frames'] and not decode.stderr.strip()
    print(f'Full decode: {frames[-1]} frames',flush=True)
    audio=subprocess.run([ff,'-v','error','-i',str(s.OUTPUT),'-vn','-ar','16000','-ac','1','-f','f32le','-'],capture_output=True,check=True)
    samples=np.frombuffer(audio.stdout,dtype='<f4')
    assert abs(len(samples)/16000-meta['duration_seconds'])<.15
    sheet=Image.new('RGB',(1350,math.ceil(len(s.BEATS)/5)*510),s.INK)
    design=s.Design()
    reports=[]
    for i,(beat,scene) in enumerate(zip(s.BEATS,meta['scenes'])):
        sid=beat[0]
        with wave.open(str(s.FOLDER/f'voz_{sid}.wav')) as voice:
            duration=voice.getnframes()/voice.getframerate()
        assert duration<scene['frames']/s.FPS
        start=scene['start_frame']/s.FPS
        seg=samples[round(start*16000):round((start+duration)*16000)]
        rms=float(np.sqrt(np.mean(seg**2)))
        assert rms>.001
        timing=json.loads((s.FOLDER/f'times_{sid}.json').read_text(encoding='utf-8'))
        word=timing['words'][-1]
        tail=samples[round((start+word['start'])*16000):round((start+word['end'])*16000)]
        assert tail.size and np.sqrt(np.mean(tail**2))>.001
        for cue in scene['cues']:design.render(beat,.6,cue['text'])
        target=s.FOLDER/f'encoded_{sid}.jpg'
        subprocess.run([ff,'-v','error','-y','-ss',str(start+scene['frames']/s.FPS*.55),'-i',str(s.OUTPUT),'-frames:v','1','-q:v','2',str(target)],check=True)
        with Image.open(target) as im:
            assert im.size==(1080,1920)
            sheet.paste(im.resize((270,480),Image.Resampling.LANCZOS),((i%5)*270,(i//5)*510))
            ImageDraw.Draw(sheet).text(((i%5)*270+8,(i//5)*510+484),sid,fill=s.PAPER)
        reports.append(dict(shot=sid,audio_rms=rms,final_word_signal=True,captions_fit=True))
    sheet.save(s.FOLDER/'storyboard_encoded.jpg',quality=92)
    report=dict(status='technical checks passed; human final listening and scientific review recommended',
        video_sha256=meta['video_sha256'],decoded_frames=frames[-1],duration_seconds=meta['duration_seconds'],
        dimensions=[1080,1920],fps=30,audio_seconds=len(samples)/16000,previous_versions_unchanged=True,
        scene_checks=reports,limitation='Shot samples and timing checks do not constitute full human listening or scientific peer review.')
    (s.FOLDER/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(f'{len(reports)} shots verified: audio, last-word signal, captions, encoded dimensions',flush=True)

if __name__=='__main__':main()
