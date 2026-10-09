"""Free-scene rendering shares captured geometry and pixels with export."""
import copy
import io
import sys
import unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).parent))
from studio_model import Element, Scene, DataBinding
from output_profiles import profile_for
from studio_render import render_scene


class StudioRenderTests(unittest.TestCase):
    def test_metric_chart_and_map_share_one_scene_without_changing_results(self):
        registry={'rain':dict(value=132.4,units='mm',variable='Lluvia'),
                  'provinces':dict(rows=[dict(name='Pichincha',value=132.4)],units='mm')}
        before=copy.deepcopy(registry)
        elements=[Element(id='title',type='text',style={'text':'¿Dónde llovió más?'}),
                  Element(id='kpi',type='metric',transform={'x':100,'y':200,'width':300,'height':180},
                          data_binding=DataBinding('rain').to_dict()),
                  Element(id='ranking',type='chart',transform={'x':10,'y':400,'width':700,'height':500},
                          style={'visualization':{'kind':'horizontal_bar'}},
                          data_binding=DataBinding('provinces','rows').to_dict()),
                  Element(id='map',type='map',transform={'x':20,'y':950,'width':600,'height':500},
                          style={'asset_id':'map.ecuador'})]
        scene=Scene(id='scene',elements=elements).to_dict()
        image=render_scene(scene,profile_for({'id':'tiktok'}),registry,
                           assets={'map.ecuador':Image.new('RGBA',(200,100),'red')})
        payload=image.info['visual_scene'].payload()
        self.assertEqual([r['id'] for r in payload['layers']],['title','kpi','ranking','map'])
        bounds={r['id']:r for r in payload['layers']}
        self.assertEqual((bounds['kpi']['x'],bounds['kpi']['y'],bounds['kpi']['w'],bounds['kpi']['h']),
                         (100,200,300,180))
        self.assertEqual(bounds['map']['w']/bounds['map']['h'],2)
        self.assertEqual(registry,before)
        output=io.BytesIO();image.save(output,format='PNG');output.seek(0)
        self.assertEqual(Image.open(output).tobytes(),image.tobytes())

    def test_every_profile_uses_native_dimensions_and_manual_pixels(self):
        for identifier in ('tiktok','instagram_portrait','instagram_square','youtube'):
            profile=profile_for({'id':identifier})
            scene=Scene(id='s',elements=[Element(id='box',type='shape',
                transform={'x':12,'y':34,'width':56,'height':78},
                style={'fill':'#ffffff'},locked=True)]).to_dict()
            image=render_scene(scene,profile,{})
            self.assertEqual(image.size,(profile.width,profile.height))
            row=image.info['visual_scene'].payload()['layers'][0]
            self.assertEqual((row['x'],row['y'],row['w'],row['h']),(12,34,56,78))
            self.assertTrue(row['locked'])
            self.assertEqual(image.getpixel((12,34)),(255,255,255,255))

    def test_unsupported_render_features_fail_instead_of_exporting_missing_content(self):
        for element in (Element(id='v',type='video'),Element(id='e',type='shape',
                        transform={'rotation':361}),Element(id='e',type='text',
                        animation={'in':'fade'})):
            with self.assertRaises(ValueError):
                render_scene(Scene(id='s',elements=[element]).to_dict(),profile_for({'id':'youtube'}),{})
        with self.assertRaises(ValueError):
            render_scene(Scene(id='s',renderer='legacy').to_dict(),profile_for({'id':'youtube'}),{})

    def test_missing_bindings_paths_and_outside_canvas_are_rejected(self):
        for element in (Element(id='i',type='image',style={'asset_id':'../../secret'}),
                        Element(id='m',type='metric',data_binding=DataBinding('missing').to_dict()),
                        Element(id='box',type='shape',transform={'x':2000,'width':50})):
            with self.assertRaises(ValueError):
                render_scene(Scene(id='s',elements=[element]).to_dict(),profile_for({'id':'youtube'}),{})


if __name__=='__main__': unittest.main()
