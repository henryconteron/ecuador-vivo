"""Decode the delivered MP4 and compare it with the editable composition."""
import hashlib
import json
import sys
import zipfile
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'production/video_studio'))
from studio_ffmpeg import read_frames
from studio_media import AssetFrames
from studio_timeline import PreparedTimeline


def verify(job):
    output=ROOT/'tmp/editorial-design-20261011'
    project=json.loads((job/'project.json').read_text(encoding='utf-8'))
    receipt=json.loads((job/'receipt.json').read_text(encoding='utf-8'))
    original=json.loads((ROOT/'_local/video-studio/projects/andes-pulso-entrega-20261011.json').read_text(encoding='utf-8'))
    for key in ('calculations','datasets','media','geography','sig_transfer','timeline'):
        assert project['studio'][key]==original['studio'][key],key
    assert hashlib.sha256((job/'video.mp4').read_bytes()).hexdigest()==receipt['video_sha256']
    assert hashlib.sha256(json.dumps(project,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()==receipt['project_sha256']
    reader=read_frames(job/'video.mp4');metadata=next(reader)
    selected={0,18,36,54,72,90,108,126,198,275};frames={}
    count=0
    for count,pixels in enumerate(reader,1):
        if count-1 in selected:frames[count-1]=Image.frombytes('RGB',tuple(metadata['size']),pixels)
    assert count==276 and tuple(metadata['size'])==(1080,1920) and metadata['fps']==30
    timeline=PreparedTimeline(project);errors={};small_text=[]
    with AssetFrames(project['studio']['media']) as assets:
        for index,frame in frames.items():
            with timeline.frame_at(index,assets=assets) as expected:
                errors[str(index)]=float(np.abs(np.asarray(frame,dtype='float32')-np.asarray(expected.convert('RGB'),dtype='float32')).mean())
                assert errors[str(index)]<2
                if index==126:
                    small_text=[{'name':item['label'],'size':item['font_size']} for item in expected.info['visual_scene'].items
                                if item.get('font_size') and item['font_size']<20]
            frame.save(output/f'mp4-{index:03d}.png');frame.close()
    with zipfile.ZipFile(job/'andes-pulso.zip') as package:
        assert package.testzip() is None
        assert hashlib.sha256(package.read('video.mp4')).hexdigest()==receipt['video_sha256']
        contents=package.namelist()
    report={'job':str(job),'size':metadata['size'],'fps':metadata['fps'],'frames':count,'duration':count/metadata['fps'],
            'science_unchanged':True,'video_sha256':receipt['video_sha256'],
            'decoded_frame_mean_RGB_error':errors,'small_text':small_text,'package_contents':contents}
    (output/'movie-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':verify(Path(sys.argv[1]).resolve())
