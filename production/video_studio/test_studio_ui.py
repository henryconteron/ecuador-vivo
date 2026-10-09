"""Real Streamlit reruns around the shared CCv2 editor and command callbacks."""
import copy
import tempfile
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
from streamlit.testing.v1 import AppTest
from studio_editing import new_workspace, patch_canvas, adapt_profile, attach_snapshot, duplicate_elements
from studio_ui import canvas_payload
from studio_model import Element
from studio_render import render_scene
from studio_timeline import validate_export
from output_profiles import profile_for
from PIL import Image


class StudioUITests(unittest.TestCase):
    def test_mixed_timeline_offers_explicit_resolution_before_render(self):
        import studio_ui
        project=new_workspace({'endcard_enabled':False})
        free=project['studio']['timeline'][0]
        project['studio']['timeline']=['legacy.map',free]
        script='import sys\nsys.path.insert(0,{!r})\nfrom studio_ui import show_studio\nshow_studio({!r},key="mixed")'.format(str(Path(__file__).parent),project)
        with tempfile.TemporaryDirectory() as directory, patch.object(studio_ui,'STORE',Path(directory)):
            app=AppTest.from_string(script,default_timeout=30).run()
            self.assertFalse(app.exception);self.assertFalse(app.error)
            next(b for b in app.button if b.label=='Editar solo escenas libres').click().run()
            self.assertFalse(app.exception);self.assertFalse(app.error)
            document=app.session_state['mixed_document']
            self.assertEqual(document['studio']['timeline'],[free])
            self.assertEqual(document['studio']['scenes'],project['studio']['scenes'])
            self.assertIn('legacy.map',document['studio']['legacy_timeline'])

    def test_canvas_uses_resolved_font_for_implicit_and_fitted_text(self):
        project=new_workspace({'endcard_enabled':False})
        scene=project['studio']['scenes'][-1]
        profile=profile_for(project['studio']['output_profile'])
        for style in ({'text':'Hello'}, {'text':'Hello','font_size':400}):
            scene['elements']=[Element(id='text',type='text',
                transform={'x':20,'y':20,'width':160,'height':80},style=style).to_dict()]
            rendered=render_scene(scene,profile,{})
            resolved=rendered.info['visual_scene'].items[0]['font_size']
            row=canvas_payload(rendered,scene,profile)['layers'][0]
            self.assertEqual(row['font_size'],resolved)
            self.assertEqual(row['original']['font_size'],resolved)
            changed=patch_canvas(project,scene['id'],{'text':{
                'w':row['w']*2,'h':row['h']*2,'font_size':resolved*2}})
            after=changed['studio']['scenes'][-1]
            self.assertEqual(render_scene(after,profile,{}).info['visual_scene'].items[0]['font_size'],resolved*2)

    def test_canvas_long_text_unknown_fields_and_default_lock_metadata(self):
        project=new_workspace({'endcard_enabled':False})
        scene=project['studio']['scenes'][-1]
        scene['elements']=[Element(id='text',type='text',locked=True,style={'text':'hello'}).to_dict()]
        profile=profile_for(project['studio']['output_profile'])
        payload=canvas_payload(render_scene(scene,profile,{}),scene,profile)
        row=payload['layers'][0]
        patch_data={'x':row['x'],'y':row['y'],'w':row['w'],'h':row['h'],'name':row['label'],'locked':False}
        # Canvas emits the resolved font only when it changes; unlocking must
        # preserve authored style, including its implicit font.
        unlocked=patch_canvas(project,scene['id'],{'text':patch_data})
        self.assertFalse(unlocked['studio']['scenes'][-1]['elements'][0]['locked'])
        self.assertNotIn('font_size',unlocked['studio']['scenes'][-1]['elements'][0]['style'])
        text='a '*300
        changed=patch_canvas(unlocked,scene['id'],{'text':{'text':text}})
        self.assertEqual(changed['studio']['scenes'][-1]['elements'][0]['style']['text'],text)
        for patch_data in ({'rotation':45},{'hidden':'false'},{'x':True}):
            with self.assertRaises(ValueError): patch_canvas(unlocked,scene['id'],{'text':patch_data})

    def test_reruns_add_duplicate_undo_and_recovery_without_scientific_reads(self):
        script='''import sys
sys.path.insert(0, {!r})
from studio_ui import show_studio
show_studio({{"endcard_enabled":False,"visual_layout":{{"map":{{"legacy":{{"x":12}}}}}}}},key="teststudio")
'''.format(str(Path(__file__).parent))
        import studio_ui
        with tempfile.TemporaryDirectory() as directory, patch.object(studio_ui,'STORE',Path(directory)), \
             patch('data.load_values',side_effect=AssertionError('No scientific reads during UI editing')):
            app=AppTest.from_string(script,default_timeout=30).run()
            self.assertFalse(app.exception)
            self.assertFalse(app.error)
            document=copy.deepcopy(app.session_state['teststudio_document'])
            def click(label):
                next(b for b in app.button if b.label==label).click().run()
                self.assertFalse(app.exception)
                self.assertFalse(app.error)
            click('Añadir escena')
            self.assertEqual(len(app.session_state['teststudio_document']['studio']['timeline']),2)
            click('Duplicar escena')
            self.assertEqual(len(app.session_state['teststudio_document']['studio']['timeline']),3)
            click('Deshacer')
            self.assertEqual(len(app.session_state['teststudio_document']['studio']['timeline']),2)
            click('Quitar de timeline')
            self.assertEqual(len(app.session_state['teststudio_document']['studio']['timeline']),1)
            click('Recuperar')
            self.assertEqual(len(app.session_state['teststudio_document']['studio']['timeline']),2)
            self.assertEqual(app.session_state['teststudio_document']['visual_layout'],document['visual_layout'])
            self.assertTrue(Path(app.session_state['teststudio_draft']).is_file())

    def test_contain_payload_move_does_not_accumulate_offset(self):
        project=new_workspace({'endcard_enabled':False})
        scene=project['studio']['scenes'][-1]
        scene['elements']=[Element(id='map',type='map',transform={'x':20,'y':50,'width':600,'height':500},
                          style={'asset_id':'map'}).to_dict()]
        profile=profile_for(project['studio']['output_profile'])
        assets={'map':Image.new('RGBA',(200,100),'red')}
        first=render_scene(scene,profile,{},assets=assets)
        payload=canvas_payload(first,scene,profile)
        row=payload['layers'][0]
        self.assertEqual((row['x'],row['y'],row['w'],row['h']),(20,50,600,500))
        updated=patch_canvas(project,scene['id'],{'map':{'x':30,'y':60,'w':600,'h':500}})
        after=updated['studio']['scenes'][-1]
        second=render_scene(after,profile,{},assets=assets)
        self.assertEqual(second.info['visual_scene'].items[0]['y'],160)
        row=canvas_payload(second,after,profile)['layers'][0]
        self.assertEqual(row['y'],60)
        repeated=patch_canvas(updated,scene['id'],{'map':{'x':30,'y':60,'w':600,'h':500}})
        self.assertEqual(repeated,updated)

    def test_scientific_revisions_and_design_operations_do_not_replace_bindings(self):
        project=new_workspace({'endcard_enabled':False})
        result={'id':'rain','variable':'precipitation','units':'mm','value':132.4,'provenance':{'warnings':[]}}
        snapshot={'scientific_identity':'a'*64,'results':{'rain':result},'source_records':[{'sha256':'b'*64}]}
        attached=attach_snapshot(project,snapshot)
        rid=next(iter(attached['studio']['calculations']))
        scene=attached['studio']['scenes'][-1]
        scene['elements'][0]['data_binding']={'result_id':rid,'field':'value'}
        before=copy.deepcopy(attached['studio']['calculations'])
        duplicated=duplicate_elements(attached,scene['id'],[scene['elements'][0]['id']])
        adapted=adapt_profile(duplicated,{'id':'youtube'})
        self.assertEqual(adapted['studio']['calculations'],before)
        self.assertEqual(adapted['studio']['scenes'][-1]['elements'][-1]['data_binding'],scene['elements'][0]['data_binding'])
        validate_export(adapted)
        changed=copy.deepcopy(snapshot);changed['results']['rain']['value']=200
        # A new revision must be stored under a different ID, preserving the old binding.
        newer=attach_snapshot(attached,changed)
        self.assertEqual(newer['studio']['calculations'][rid]['value'],132.4)
        self.assertEqual(len(newer['studio']['calculations']),2)


if __name__=='__main__': unittest.main()
