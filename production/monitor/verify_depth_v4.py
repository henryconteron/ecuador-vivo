"""Independent checks of encoded V4 audio/video, geometry motion and sources."""
from hashlib import sha256
import json
import subprocess
import wave
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageChops
from prepare_depth_story_v4 import V4
from reel_depth_damage_v4 import OUTPUT, AUDIO, SCRIPT, FPS


def verify():
    expected=json.loads((V4/'draft_metadata_v4.json').read_text(encoding='utf-8'))
    timeline=json.loads((AUDIO/'timeline.json').read_text(encoding='utf-8'))
    if expected['sha256']!=sha256(OUTPUT.read_bytes()).hexdigest(): raise ValueError('Encoded file changed')
    if timeline['script_sha256']!=sha256(SCRIPT.read_bytes()).hexdigest(): raise ValueError('Narration script changed')
    frames,duration=imageio_ffmpeg.count_frames_and_secs(str(OUTPUT))
    reader=imageio_ffmpeg.read_frames(str(OUTPUT))
    try: meta=next(reader)
    finally: reader.close()
    if frames!=expected['frames'] or abs(duration-expected['duration_seconds'])>.06: raise ValueError('Wrong frame count or duration')
    if meta['size']!=(1080,1920) or meta['fps']!=FPS or not meta.get('audio_codec') or 'h264' not in meta['codec']: raise ValueError('Wrong format/missing audio')
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    picks=[round((a+b)/2*FPS) for a,b,_ in timeline['scenes']]
    pairs=[]
    for name in ('bolivia','loreto','pelileo','reventador'):
        a,b,_=next(s for s in timeline['scenes'] if s[2]==name)
        frame=round((a+(b-a)*.65)*FPS); picks.extend([frame,frame+1]); pairs.append((name,frame))
    a,b,_=next(s for s in timeline['scenes'] if s[2]=='pedernales')
    picks.append(round((a+4)*FPS))
    picks=sorted(set(picks)); expression='+'.join(f'eq(n,{n})' for n in picks)
    subprocess.run([ffmpeg,'-v','error','-i',str(OUTPUT),'-vf',f"select='{expression}'",'-vsync','0','-q:v','2','-y',str(V4/'qa_encoded_%02d.jpg')],check=True,capture_output=True)
    motion={}
    for name,frame in pairs:
        i=picks.index(frame)+1; j=picks.index(frame+1)+1
        with Image.open(V4/f'qa_encoded_{i:02d}.jpg') as a,Image.open(V4/f'qa_encoded_{j:02d}.jpg') as b:
            # Geometry only: no moving progress bar/phase labels/credits.
            if ImageChops.difference(a.crop((180,653,900,1103)),b.crop((180,653,900,1103))).getbbox() is None: raise ValueError('Frozen geometry: '+name)
        motion[name]='consecutive encoded geometry frames differ'
    decoded=AUDIO/'qa_decoded_mp4.wav'
    subprocess.run([ffmpeg,'-v','error','-i',str(OUTPUT),'-vn','-ac','1','-ar','16000','-c:a','pcm_s16le','-y',str(decoded)],check=True,capture_output=True)
    with wave.open(str(decoded)) as audio:
        rate=audio.getframerate(); samples=np.frombuffer(audio.readframes(audio.getnframes()),dtype='<i2')
    if abs(len(samples)/rate-expected['duration_seconds'])>.09: raise ValueError('Truncated audio')
    checks=[]
    for segment in timeline['segments']:
        start=segment['speech_start']; end=start+segment['speech_seconds']
        part=samples[round(start*rate):round(end*rate)].astype(np.int32)
        rms=float(np.sqrt(np.mean(part.astype(float)**2))); peak=int(np.abs(part).max())
        if rms<100: raise ValueError('Missing voice segment')
        if end>segment['end']-.79: raise ValueError('Truncated scene narration')
        checks.append(dict(scene=segment['scene'],rms_pcm16=round(rms,2),peak_pcm16=peak))
    subprocess.run([ffmpeg,'-v','error','-i',str(OUTPUT),'-f','null','-'],check=True,capture_output=True)
    # A short review clip of the deep real case; preserves provisional narration.
    a,b,_=next(s for s in timeline['scenes'] if s[2]=='bolivia')
    clip=V4/'avance_bolivia_3d_v4.mp4'
    subprocess.run([ffmpeg,'-v','error','-ss',f'{a:.6f}','-i',str(OUTPUT),'-t',f'{b-a:.6f}',
        '-c:v','libx264','-crf','18','-preset','veryfast','-threads','2','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart','-y',str(clip)],check=True,capture_output=True)
    clip_frames,clip_seconds=imageio_ffmpeg.count_frames_and_secs(str(clip))
    if clip_frames!=round((b-a)*FPS) or abs(clip_seconds-(b-a))>.05: raise ValueError('Preview wrong duration')
    subprocess.run([ffmpeg,'-v','error','-i',str(clip),'-f','null','-'],check=True,capture_output=True)
    report=dict(status='provisional_internal_review_not_publication',sha256=expected['sha256'],frames=frames,duration_seconds=duration,size=meta['size'],fps=FPS,
        full_decode='passed',audio_codec=meta['audio_codec'],audio_duration_seconds=len(samples)/rate,voice_segments=checks,motion_checks=motion,encoded_frame_indices=picks,
        preview=dict(file=clip.name,sha256=sha256(clip.read_bytes()).hexdigest(),frames=clip_frames,duration_seconds=clip_seconds,full_decode='passed'),
        limits='signal checks are not human listening review; animation is conceptual, not a seismic or damage model')
    (V4/'verification_v4.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__': verify()
