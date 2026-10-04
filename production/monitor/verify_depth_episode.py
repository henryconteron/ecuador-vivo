"""Validate the actual encoded reel, not just its source renders."""
from hashlib import sha256
import json
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageChops

from prepare_depth_episode import FOLDER
from reel_depth_damage import DURATION


def verify():
    video=FOLDER/'profundidad_danos_maqueta_sin_voz_v1.mp4'
    expected=json.loads((FOLDER/'draft_metadata.json').read_text(encoding='utf-8'))
    checksum=sha256(video.read_bytes()).hexdigest()
    if checksum!=expected['sha256']: raise ValueError('Video changed after export')
    frames,duration=imageio_ffmpeg.count_frames_and_secs(str(video))
    reader=imageio_ffmpeg.read_frames(str(video))
    try: meta=next(reader)
    finally: reader.close()
    if frames!=DURATION*30 or abs(duration-DURATION)>.04: raise ValueError('Bad frame count/duration')
    if meta['size']!=(1080,1920) or meta['fps']!=30 or 'h264' not in meta['codec']: raise ValueError('Bad encoded format')
    if meta.get('audio_codec'): raise ValueError('Maqueta must be silent')
    picks=[0,510,630,900,1140,1141,1950,2460,2970,2971,3570,4110]
    expression='+'.join(f'eq(n,{n})' for n in picks)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(video),'-vf',f"select='{expression}'",'-vsync','0','-q:v','2','-y',str(FOLDER/'qa_encoded_%02d.jpg')],check=True,capture_output=True)
    motion={}
    for a,b,name,crop in [(5,6,'comparison',(110,610,920,1010)),(9,10,'landslide_concept',(120,645,900,1140))]:
        with Image.open(FOLDER/f'qa_encoded_{a:02d}.jpg') as first, Image.open(FOLDER/f'qa_encoded_{b:02d}.jpg') as second:
            if ImageChops.difference(first.crop(crop),second.crop(crop)).getbbox() is None: raise ValueError('Repeated diagram motion frame')
            motion[name]='consecutive encoded diagram-region frames differ (progress bar excluded)'
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(video),'-f','null','-'],check=True,capture_output=True)
    report=dict(sha256=checksum,frames=frames,duration_seconds=duration,size=meta['size'],fps=meta['fps'],codec=meta['codec'],audio=None,full_decode='passed',encoded_frame_indices=picks,motion_checks=motion,status='silent_draft_not_for_publication')
    (FOLDER/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__': verify()
