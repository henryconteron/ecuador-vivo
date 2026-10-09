"""Small profiles retain editable templates, complete text and render parity."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest
import unicodedata
from unittest.mock import patch
from PIL import Image
import imageio_ffmpeg
sys.path.insert(0,str(Path(__file__).parent))
from output_profiles import profile_for,adaptive_regions
from studio_templates import template_scene,TEMPLATES,TYPOGRAPHY
from studio_render import render_scene
from studio_editing import new_workspace,adapt_profile
from studio_timeline import PreparedTimeline,export_movie
from studio_ui import canvas_payload
from studio_model import Scene,Element


class StudioSmallFormatTests(unittest.TestCase):
    def test_wrapping_preserves_bound_whitespace_and_class_zero_marks(self):
        import studio_render
        for content in ('  A  B\u00a0C\t D  '*8, 'A\u034f'*80, '\u0915\u093e'*80,
                        '\U0001f469\U0001f3fd\u200d\U0001f52c'*30, 'A \u0301'*40):
            calls=[];factory=studio_render.ImageDraw.Draw
            def instrument(*args,**kwargs):
                draw=factory(*args,**kwargs);original=draw.text
                def text(position,value,*args,**kwargs):
                    calls.append(value);return original(position,value,*args,**kwargs)
                draw.text=text;return draw
            scene=Scene(id='bound',elements=[Element(id='t',type='text',
                transform={'x':10,'y':10,'width':140,'height':140},
                style={'text':'{{value}}','font_size':20},
                data_binding={'result_id':'identifier','field':'units'}).to_dict()]).to_dict()
            registry={'identifier':{'value':1,'units':content,'variable':'identifier','provenance':{'warnings':[]}}}
            with self.subTest(content=content), patch.object(studio_render.ImageDraw,'Draw',side_effect=instrument):
                render_scene(scene,profile_for({'id':'custom','width':160,'height':160}),registry)
                self.assertEqual(''.join(calls),content)
                self.assertGreater(len(calls),1)
                self.assertTrue(all(not line or not unicodedata.category(line[0]).startswith('M') for line in calls))
                self.assertTrue(all(not line or not 0x1f3fb<=ord(line[0])<=0x1f3ff for line in calls))
                self.assertTrue(all(not line.endswith('\u200d') for line in calls))

    def test_wrapping_preserves_combining_characters_in_rendered_lines(self):
        import studio_render
        calls=[];factory=studio_render.ImageDraw.Draw
        def instrument(*args,**kwargs):
            draw=factory(*args,**kwargs);original=draw.text
            def text(position,content,*args,**kwargs):
                calls.append(content);return original(position,content,*args,**kwargs)
            draw.text=text;return draw
        content='A\u0301'*80
        scene=Scene(id='unicode',elements=[Element(id='t',type='text',
            transform={'x':10,'y':10,'width':140,'height':140},style={'text':content,'font_size':20}).to_dict()]).to_dict()
        with patch.object(studio_render.ImageDraw,'Draw',side_effect=instrument):
            render_scene(scene,profile_for({'id':'custom','width':160,'height':160}),{})
        self.assertEqual(''.join(calls),content)
        self.assertTrue(all(not line or not unicodedata.combining(line[0]) for line in calls))

    def test_empty_text_is_transparent_even_in_one_pixel_box(self):
        profile=profile_for({'id':'custom','width':160,'height':160})
        scene=Scene(id='empty',background='#000000',elements=[Element(id='t',type='text',
            transform={'x':10,'y':10,'width':1,'height':1},style={'text':'','font_size':20}).to_dict()]).to_dict()
        image=render_scene(scene,profile,{})
        self.assertEqual(image.getpixel((10,10)),(0,0,0,255))
        scene['elements'][0]['style']['alignment']='invalid'
        with self.assertRaises(ValueError): render_scene(scene,profile,{})

    def test_starter_templates_render_at_minimum_profiles(self):
        for width,height in ((160,160),(160,320),(320,160),(160,3840),(3840,160)):
            profile=profile_for({'id':'custom','width':width,'height':height})
            for template in TEMPLATES:
                for typography in TYPOGRAPHY:
                    with self.subTest(size=(width,height),template=template,typography=typography):
                        scene=template_scene(template,profile,typography=typography)
                        before=copy.deepcopy(scene)
                        image=render_scene(scene,profile,{})
                        self.assertEqual(image.size,(width,height));self.assertEqual(scene,before)
                        self.assertTrue(all(row['font_size']>=8 for row in canvas_payload(image,scene,profile)['layers'] if row['font_size']))

    def test_regions_accommodate_existing_visualization_minimum_when_space_exists(self):
        for size in ((160,160),(160,320),(320,160)):
            profile=profile_for({'id':'custom','width':size[0],'height':size[1]})
            regions=adaptive_regions(profile)
            self.assertGreaterEqual(regions['metric']['width'],80)
            self.assertGreaterEqual(regions['metric']['height'],80)
            registry={'rain':{'value':132.4,'variable':'precipitation','units':'mm','provenance':{'warnings':[]}}}
            scene=template_scene('map_metric',profile,bindings={'metric':{'result_id':'rain','field':'value'}})
            before=copy.deepcopy(registry);render_scene(scene,profile,registry)
            self.assertEqual(registry,before)

    def test_long_token_wraps_without_truncating_bound_content(self):
        profile=profile_for({'id':'custom','width':160,'height':160})
        content='ABCDEFGHIJKLMN0123456789'*4
        scene=Scene(id='text',duration=.1,elements=[Element(id='t',type='text',
            transform={'x':10,'y':10,'width':140,'height':140},style={'text':'{{value}}','font_size':20},
            data_binding={'result_id':'identifier','field':'units'}).to_dict()]).to_dict()
        registry={'identifier':{'value':1,'units':content,'variable':'identifier','provenance':{'warnings':[]}}}
        before=copy.deepcopy(registry)
        rendered=render_scene(scene,profile,registry)
        self.assertEqual(rendered.info['visual_scene'].items[0]['text'],content)
        self.assertEqual(registry,before)
        with self.assertRaises(ValueError):
            bad=copy.deepcopy(scene);bad['elements'][0]['transform'].update(width=1,height=1)
            render_scene(bad,profile,registry)

    def test_explicit_adaptation_and_small_mp4_share_preview(self):
        project=new_workspace({'endcard_enabled':False})
        profile=profile_for({'id':'custom','width':160,'height':160})
        scene=template_scene('cover',profile);scene['duration']=.1
        project['studio']['scenes']=[scene];project['studio']['timeline']=[scene['id']]
        before=copy.deepcopy(project)
        project=adapt_profile(project,{'id':'custom','width':160,'height':160})
        self.assertEqual(before['studio']['output_profile']['id'],'tiktok')
        prepared=PreparedTimeline(project)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'small.mp4';receipt=export_movie(project,path)
            reader=imageio_ffmpeg.read_frames(str(path),pix_fmt='rgb24');next(reader);frames=list(reader)
            self.assertEqual(len(frames),3);self.assertEqual(receipt['dimensions'],[160,160])
            for frame,raw in enumerate(frames):
                actual=Image.frombytes('RGB',(160,160),raw)
                expected=prepared.frame_at(frame).convert('RGB')
                self.assertLess(sum(abs(a-b) for a,b in zip(actual.tobytes(),expected.tobytes()))/len(raw),5)


if __name__=='__main__': unittest.main()
