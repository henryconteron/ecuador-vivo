"""Check the encoded video independently, including real GPU-motion regions."""
from hashlib import sha256
import json
import subprocess
import wave
import imageio_ffmpeg
import numpy as np
from PIL import Image,ImageChops
from reel_depth_damage_v5 import V5,OUTPUT,AUDIO,SCRIPT,FPS


def verify():
    meta=json.loads((V5/'draft_metadata_v5.json').read_text(encoding='utf-8'))
    timeline=json.loads((AUDIO/'timeline.json').read_text(encoding='utf-8'))
    if sha256(OUTPUT.read_bytes()).hexdigest()!=meta['sha256']:raise ValueError('Encoded file changed')
    if sha256(SCRIPT.read_bytes()).hexdigest()!=timeline['script_sha256']:raise ValueError('Script changed')
    frames,duration=imageio_ffmpeg.count_frames_and_secs(str(OUTPUT));reader=imageio_ffmpeg.read_frames(str(OUTPUT))
    try:encoding=next(reader)
    finally:reader.close()
    if frames!=meta['frames'] or abs(duration-meta['duration_seconds'])>.06:raise ValueError('Wrong video duration')
    if encoding['size']!=(1080,1920) or encoding['fps']!=FPS or not encoding.get('audio_codec'):raise ValueError('Wrong format or missing audio')
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe();pairs=[]
    picks=[round((a+b)/2*FPS) for a,b,_ in timeline['scenes']]
    for name in ('p','s','love','rayleigh','bolivia','loreto','reventador'):
        a,b,_=next(s for s in timeline['scenes'] if s[2]==name)
        n=round((a+(b-a)*.65)*FPS);pairs.append((name,n));picks.extend([n,n+1])
    a,b,_=next(s for s in timeline['scenes'] if s[2]=='pedernales')
    photo_time=a+(timeline['cues']['pedernales']['Esta foto']+timeline['cues']['pedernales']['Cerca de'])/2
    picks.append(round(photo_time*FPS))
    picks=sorted(set(picks));expr='+'.join(f'eq(n,{n})' for n in picks)
    subprocess.run([ffmpeg,'-v','error','-i',str(OUTPUT),'-vf',f"select='{expr}'",'-vsync','0','-q:v','2','-y',str(V5/'qa_encoded_%02d.jpg')],check=True,capture_output=True)
    motion={}
    for name,n in pairs:
        i=picks.index(n)+1;j=picks.index(n+1)+1
        with Image.open(V5/f'qa_encoded_{i:02d}.jpg') as a,Image.open(V5/f'qa_encoded_{j:02d}.jpg') as b:
            # Geometry only: exclude captions, labels and progress.
            crop=(180,580,900,1140)
            if ImageChops.difference(a.crop(crop),b.crop(crop)).getbbox() is None:raise ValueError('Frozen geometry '+name)
        motion[name]='consecutive encoded GPU geometry frames differ'
    decoded=AUDIO/'qa_decoded_mp4.wav'
    subprocess.run([ffmpeg,'-v','error','-i',str(OUTPUT),'-vn','-ac','1','-ar','16000','-c:a','pcm_s16le','-y',str(decoded)],check=True,capture_output=True)
    with wave.open(str(decoded)) as audio:
        rate=audio.getframerate();samples=np.frombuffer(audio.readframes(audio.getnframes()),dtype='<i2')
    if abs(len(samples)/rate-meta['duration_seconds'])>.1:raise ValueError('Truncated audio')
    segments=[]
    for part in timeline['segments']:
        pcm=samples[round(part['speech_start']*rate):round((part['speech_start']+part['speech_seconds'])*rate)].astype(np.int32)
        rms=float(np.sqrt(np.mean(pcm.astype(float)**2)));peak=int(np.abs(pcm).max())
        if rms<100 or peak>=32767:raise ValueError('Missing/clipped speech')
        segments.append(dict(scene=part['scene'],rms_pcm16=round(rms,2),peak_pcm16=peak))
    subprocess.run([ffmpeg,'-v','error','-i',str(OUTPUT),'-f','null','-'],check=True,capture_output=True)
    # Include the new hook as well as every wave, with provisional voice/subtitles.
    start=0;end=next(b for a,b,n in timeline['scenes'] if n=='rayleigh')
    clip=V5/'avance_ondas_3d_v5.mp4'
    subprocess.run([ffmpeg,'-v','error','-ss',f'{start:.6f}','-i',str(OUTPUT),'-t',f'{end-start:.6f}',
        '-c:v','libx264','-crf','18','-preset','veryfast','-threads','2','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart','-y',str(clip)],check=True,capture_output=True)
    cf,cs=imageio_ffmpeg.count_frames_and_secs(str(clip))
    if cf!=round((end-start)*FPS) or abs(cs-(end-start))>.06:raise ValueError('Preview duration mismatch')
    subprocess.run([ffmpeg,'-v','error','-i',str(clip),'-f','null','-'],check=True,capture_output=True)
    report=dict(status='provisional_internal_review_not_publication',sha256=meta['sha256'],frames=frames,duration_seconds=duration,full_decode='passed',size=encoding['size'],fps=FPS,
        audio_duration_seconds=len(samples)/rate,voice_segments=segments,motion_checks=motion,encoded_frame_indices=picks,
        captions=dict(count=len(timeline['captions']),method=timeline['caption_method'],status='provisional, retime to final voice'),
        preview=dict(file=clip.name,frames=cf,duration_seconds=cs,sha256=sha256(clip.read_bytes()).hexdigest(),full_decode='passed'),
        limits='Conceptual wave fields; not an event waveform, damage model or human listening review')
    (V5/'verification_v5.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':verify()
