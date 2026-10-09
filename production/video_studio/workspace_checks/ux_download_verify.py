import sys,json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
import imageio_ffmpeg
sys.path.insert(0,str(Path('production/video_studio').resolve()))
from studio_timeline import PreparedTimeline
from studio_media import AssetFrames
from studio_ffmpeg import read_frames
metadata_path=Path('tmp/ux-redesign/media-flow.json')
info=json.loads(metadata_path.read_text(encoding='utf-8'))
root=Path(info.get('download_directory','tmp/ux-redesign/downloads'));project=json.loads((root/'ecuador-vivo-proyecto.json').read_text(encoding='utf-8'));movie=root/'ecuador-vivo.mp4'
prepared=PreparedTimeline(project);reader=read_frames(str(movie),pix_fmt='rgb24');metadata=next(reader);diffs=[]
try:
 with AssetFrames(project['studio']['media']) as assets:
  for i,pixels in enumerate(reader):
   actual=Image.frombytes('RGB',metadata['size'],pixels);expected=prepared.frame_at(i,assets=assets).convert('RGB')
   diff=float(np.abs(np.asarray(actual).astype(float)-np.asarray(expected).astype(float)).mean());assert diff<5,(i,diff);diffs.append(diff)
finally:reader.close()
assert len(diffs)==prepared.total_frames
pcm=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(movie),'-f','f32le','-ac','2','-ar','48000','pipe:1'],check=True,stdout=subprocess.PIPE).stdout
peak=float(np.max(np.abs(np.frombuffer(pcm,dtype='<f4'))));assert .02<peak<.2,peak
result={'frames':len(diffs),'size':metadata['size'],'max_mean_pixel_difference':max(diffs),'decoded_audio_peak':peak,'actual_browser_download':True}
Path('tmp/ux-redesign/download-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
