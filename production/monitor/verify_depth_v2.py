"""Check encoded profiles-first V2, including consecutive animation frames."""
from hashlib import sha256
import json
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageChops

from prepare_depth_episode import FOLDER
from reel_depth_damage_v2 import DURATION


def verify():
    video=FOLDER/'profundidad_danos_cortes_3d_maqueta_sin_voz_v2.mp4'
    expected=json.loads((FOLDER/'draft_metadata_v2.json').read_text(encoding='utf-8'))
    checksum=sha256(video.read_bytes()).hexdigest()
    if checksum!=expected['sha256']:raise ValueError('Encoded V2 changed after export')
    frames,duration=imageio_ffmpeg.count_frames_and_secs(str(video))
    reader=imageio_ffmpeg.read_frames(str(video))
    try:meta=next(reader)
    finally:reader.close()
    if frames!=DURATION*30 or abs(duration-DURATION)>.04:raise ValueError('Incorrect V2 duration or frame count')
    if meta['size']!=(1080,1920) or meta['fps']!=30 or 'h264' not in meta['codec']:raise ValueError('Bad encoded format')
    if meta.get('audio_codec'):raise ValueError('This is a silent draft')
    picks=[0,330,510,511,1140,1141,1740,1741,2100,2101,2400,2790,3180,3630,3631,4110,4500]
    expression='+'.join(f'eq(n,{n})' for n in picks)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(video),'-vf',f"select='{expression}'",'-vsync','0','-q:v','2','-y',str(FOLDER/'qa_v2_encoded_%02d.jpg')],check=True,capture_output=True)
    motion={}
    for a,b,name,crop in [(3,4,'profile_reading',(165,470,900,830)),
                        (5,6,'deep',(120,530,915,1240)),(7,8,'intermediate',(120,530,915,1240)),
                        (9,10,'shallow',(120,530,915,1240)),(14,15,'slope',(120,645,900,1140))]:
        with Image.open(FOLDER/f'qa_v2_encoded_{a:02d}.jpg') as first, Image.open(FOLDER/f'qa_v2_encoded_{b:02d}.jpg') as second:
            if ImageChops.difference(first.crop(crop),second.crop(crop)).getbbox() is None:raise ValueError(f'Repeated encoded animation: {name}')
            motion[name]='consecutive diagram-region frames differ; progress bar excluded'
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(video),'-f','null','-'],check=True,capture_output=True)
    report=dict(status='silent_draft_not_for_publication',sha256=checksum,frames=frames,duration_seconds=duration,
                size=meta['size'],fps=meta['fps'],codec=meta['codec'],audio=None,full_decode='passed',
                encoded_frame_indices=picks,motion_checks=motion)
    (FOLDER/'verification_v2.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':verify()
