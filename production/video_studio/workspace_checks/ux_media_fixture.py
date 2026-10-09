from pathlib import Path
import subprocess,sys,json
from PIL import Image,ImageDraw
import imageio_ffmpeg
sys.path.insert(0,str(Path('production/video_studio').resolve()))
from model import default_project
from studio_editing import new_workspace,attach_snapshot,edit_scene
from studio_templates import template_scene
from output_profiles import profile_for
ROOT=Path('tmp/ux-redesign');ROOT.mkdir(exist_ok=True)
image=Image.new('RGB',(480,270),'#173948');d=ImageDraw.Draw(image);d.ellipse((120,40,360,250),fill='#67d7c2');image.save(ROOT/'media-image.png')
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-f','lavfi','-i','testsrc2=size=320x180:rate=30:duration=1','-f','lavfi','-i','sine=frequency=440:sample_rate=48000:duration=1','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',str(ROOT/'media-video.mp4')],check=True)
print('media fixtures ready')
