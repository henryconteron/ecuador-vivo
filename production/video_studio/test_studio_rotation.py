"""Media rotation preserves full native boxes and the shared temporal raster."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from PIL import Image
import imageio_ffmpeg
from studio_model import Element, Scene
from studio_render import render_scene
from studio_ui import canvas_payload
from studio_editing import new_workspace, patch_canvas
from studio_timeline import PreparedTimeline, export_movie
from output_profiles import profile_for


class StudioRotationTests(unittest.TestCase):
    def test_clockwise_media_rotation_keeps_corners_and_native_canvas_box(self):
        profile=profile_for({'id':'custom','width':320,'height':240})
        asset=Image.new('RGBA',(40,20),'red');asset.paste('blue',(0,0,20,20))
        element=Element(id='photo',type='image',transform={'x':20,'y':30,'width':80,'height':40,'rotation':90},
                        style={'asset_id':'asset.photo','fit':'contain'}).to_dict()
        scene=Scene(id='s',elements=[element]).to_dict();before=copy.deepcopy(scene)
        image=render_scene(scene,profile,{},assets={'asset.photo':asset})
        row=canvas_payload(image,scene,profile)['layers'][0]
        self.assertEqual((row['x'],row['y'],row['w'],row['h']),(20,30,80,40))
        self.assertEqual(image.getpixel((60,35))[:3],(0,0,255))
        self.assertEqual(image.getpixel((60,65))[:3],(255,0,0))
        self.assertEqual(scene,before)
        project=new_workspace({'endcard_enabled':False});project['studio']['output_profile']={'id':'custom','width':320,'height':240}
        project['studio']['scenes'].append(scene);project['studio']['timeline']=['s']
        moved=patch_canvas(project,'s',{'photo':{'x':30,'y':40,'w':80,'h':40}})
        after=moved['studio']['scenes'][-1]
        self.assertEqual(after['elements'][0]['transform']['rotation'],90)
        row=canvas_payload(render_scene(after,profile,{},assets={'asset.photo':asset}),after,profile)['layers'][0]
        self.assertEqual((row['x'],row['y'],row['w'],row['h']),(30,40,80,40))

    def test_rotation_zero_is_unchanged_and_unsupported_text_or_angle_fails(self):
        profile=profile_for({'id':'custom','width':320,'height':240})
        element=Element(id='box',type='shape',transform={'x':20,'y':20,'width':80,'height':40}).to_dict()
        scene=Scene(id='s',elements=[element]).to_dict()
        element=scene['elements'][0]
        before=render_scene(scene,profile,{}).tobytes()
        element['transform']['rotation']=0
        self.assertEqual(render_scene(scene,profile,{}).tobytes(),before)
        for angle in (-361,361):
            element['transform']['rotation']=angle
            with self.assertRaises(ValueError): render_scene(scene,profile,{})
        element['transform']['rotation']=30;element['type']='text';element['style']={'text':'Texto'}
        with self.assertRaises(ValueError): render_scene(scene,profile,{})

    def test_rotated_animation_preview_matches_exported_frames(self):
        project=new_workspace({'endcard_enabled':False})
        project['studio']['output_profile']={'id':'custom','width':320,'height':240}
        scene=Scene(id='s',duration=.2,elements=[Element(id='box',type='shape',
            transform={'x':40,'y':40,'width':160,'height':80,'rotation':45},
            style={'fill':'#cc5522','opacity':.5},animation={'in':'fade','duration':.1})]).to_dict()
        project['studio']['scenes'].append(scene);project['studio']['timeline']=['s']
        prepared=PreparedTimeline(project)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'rotation.mp4';export_movie(project,path)
            reader=imageio_ffmpeg.read_frames(str(path),pix_fmt='rgb24');next(reader)
            try: frames=list(reader)
            finally: reader.close()
            self.assertEqual(len(frames),6)
            for index,raw in enumerate(frames):
                expected=prepared.frame_at(index).convert('RGB').tobytes()
                self.assertLess(sum(abs(a-b) for a,b in zip(raw,expected))/len(raw),5)


if __name__=='__main__': unittest.main()
