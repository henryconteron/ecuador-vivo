"""Independent encoded-file QA: complete audio, actual mesh motion, full decode."""
from hashlib import sha256
import json
import subprocess
import wave
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageChops
from prepare_depth_episode import FOLDER
from reel_depth_damage_v3 import OUTPUT, AUDIO, FPS


def verify():
    expected=json.loads((FOLDER/'draft_metadata_v3.json').read_text(encoding='utf-8'))
    timeline=json.loads((AUDIO/'timeline.json').read_text(encoding='utf-8'))
    checksum=sha256(OUTPUT.read_bytes()).hexdigest()
    if checksum!=expected['sha256']: raise ValueError('Encoded file changed')
    frames,duration=imageio_ffmpeg.count_frames_and_secs(str(OUTPUT))
    reader=imageio_ffmpeg.read_frames(str(OUTPUT))
    try: meta=next(reader)
    finally: reader.close()
    if frames!=expected['frames'] or abs(duration-expected['duration_seconds'])>.05: raise ValueError('Wrong duration/frame count')
    if meta['size']!=(1080,1920) or meta['fps']!=FPS or not meta.get('audio_codec') or 'h264' not in meta['codec']: raise ValueError('Missing audio or wrong format')
    picks=[round((a+b)/2*FPS) for a,b,_ in timeline['scenes']]
    start,end,_=next(s for s in timeline['scenes'] if s[2]=='reventador')
    slope=[round((start+(end-start)*q)*FPS) for q in (.10,.26,.56,.94)]
    slide=round((start+(end-start)*.56)*FPS); flow=round((start+(end-start)*.94)*FPS)
    picks=sorted(set(picks+slope+[slide+1,flow+1]))
    expression='+'.join(f'eq(n,{n})' for n in picks)
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ffmpeg,'-v','error','-i',str(OUTPUT),'-vf',f"select='{expression}'",'-vsync','0','-q:v','2','-y',str(FOLDER/'qa_v3_encoded_%02d.jpg')],check=True,capture_output=True)
    motion={}
    for frame,name in [(slide,'landslide'),(flow,'channel_transport')]:
        i=picks.index(frame)+1; j=picks.index(frame+1)+1
        with Image.open(FOLDER/f'qa_v3_encoded_{i:02d}.jpg') as a,Image.open(FOLDER/f'qa_v3_encoded_{j:02d}.jpg') as b:
            # Only mesh area: excludes text phase labels and progress bar.
            if ImageChops.difference(a.crop((190,667,890,1082)),b.crop((190,667,890,1082))).getbbox() is None: raise ValueError('Frozen encoded mesh')
            motion[name]='consecutive encoded 3D-region frames differ'
    decoded=AUDIO/'qa_decoded_mp4.wav'
    subprocess.run([ffmpeg,'-v','error','-i',str(OUTPUT),'-vn','-ac','1','-ar','22050','-c:a','pcm_s16le','-y',str(decoded)],check=True,capture_output=True)
    with wave.open(str(decoded),'rb') as audio:
        rate=audio.getframerate(); samples=np.frombuffer(audio.readframes(audio.getnframes()),dtype='<i2')
    if abs(len(samples)/rate-expected['duration_seconds'])>.08: raise ValueError('Truncated audio')
    checks=[]
    for part in timeline['segments']:
        chunk=samples[round(part['speech_start']*rate):round((part['speech_start']+part['speech_seconds'])*rate)]
        rms=float(np.sqrt(np.mean(chunk.astype(float)**2)))
        if rms<100: raise ValueError(f'Missing speech: {part["scene"]}')
        checks.append(dict(scene=part['scene'],rms_pcm16=round(rms,2),peak_pcm16=int(np.abs(chunk.astype(np.int32)).max())))
    subprocess.run([ffmpeg,'-v','error','-i',str(OUTPUT),'-f','null','-'],check=True,capture_output=True)
    # Small, frame-accurate review clip of only the revised scene, with voice.
    preview=FOLDER/'piedemonte_3d_voz_provisional_v3.mp4'
    subprocess.run([ffmpeg,'-v','error','-ss',f'{start:.6f}','-i',str(OUTPUT),'-t',f'{end-start:.6f}',
                    '-c:v','libx264','-crf','18','-preset','veryfast','-threads','2','-pix_fmt','yuv420p',
                    '-c:a','aac','-b:a','128k','-movflags','+faststart','-y',str(preview)],check=True,capture_output=True)
    clip_frames,clip_seconds=imageio_ffmpeg.count_frames_and_secs(str(preview))
    if clip_frames!=round((end-start)*FPS) or abs(clip_seconds-(end-start))>.05: raise ValueError('Bad scene preview duration')
    subprocess.run([ffmpeg,'-v','error','-i',str(preview),'-f','null','-'],check=True,capture_output=True)
    report=dict(status='provisional_internal_review_not_publication',sha256=checksum,frames=frames,duration_seconds=duration,size=meta['size'],fps=meta['fps'],codec=meta['codec'],audio_codec=meta['audio_codec'],audio_duration_seconds=len(samples)/rate,full_decode='passed',motion_checks=motion,encoded_frame_indices=picks,slope_frame_indices=slope,audio_segments=checks,listening_review='User preview still required; signal checks do not verify pronunciation')
    report['piedmont_preview']=dict(file=preview.name,frames=clip_frames,duration_seconds=clip_seconds,sha256=sha256(preview.read_bytes()).hexdigest(),full_decode='passed')
    (FOLDER/'verification_v3.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':verify()
