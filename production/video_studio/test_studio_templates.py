"""Editable library contracts and compatibility with the existing five scenes."""
import copy
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import imageio_ffmpeg
from PIL import Image
sys.path.insert(0,str(Path(__file__).parent))
import studio_editing
from studio_templates import template_scene,TEMPLATES,THEMES,TYPOGRAPHY
import studio_templates
from output_profiles import profile_for,adaptive_regions
from studio_render import render_scene
from studio_timeline import PreparedTimeline,export_movie
from streamlit.testing.v1 import AppTest

NEW=('metric_focus','ranking_focus','comparison','quote','image_caption','methodology')
REGISTRY={
    'rain':{'id':'rain','value':132.4,'variable':'precipitation','units':'mm','provenance':{'warnings':[]}},
    'regions':{'id':'regions','value':None,'variable':'precipitation','units':'mm',
               'rows':[{'name':'A','value':-2,'coverage':1},{'name':'B','value':0,'coverage':1}],
               'provenance':{'warnings':[]}}}
BINDINGS={'metric':{'result_id':'rain','field':'value'},
          'ranking':{'result_id':'regions','field':'rows'},
          'comparison':{'result_id':'regions','field':'rows'}}


class StudioTemplateTests(unittest.TestCase):
    def test_finite_but_impossible_typography_metadata_is_rejected_cleanly(self):
        project=studio_editing.new_workspace({'endcard_enabled':False})
        sid=project['studio']['timeline'][0]
        project['studio']['scenes'][-1]['elements'][0]['typography_base_size']=1.7e308
        before=copy.deepcopy(project)
        with self.assertRaises(ValueError): studio_editing.apply_scene_design(project,sid,typography='Social Bold')
        self.assertEqual(project,before)

    def test_original_five_scenes_match_saved_contract(self):
        fixture=json.loads((Path(__file__).parent/'fixtures/studio_templates_v1.json').read_text(encoding='utf-8'))
        for identifier,templates in fixture.items():
            definition={'id':identifier,**({'width':160,'height':160} if identifier=='custom' else {})}
            with patch('studio_templates.uuid.uuid4',return_value=SimpleNamespace(hex='0'*32)):
                for template,expected in templates.items():
                    actual=template_scene(template,profile_for(definition))
                    for element in actual['elements']:
                        for name in ('typography_base_size','typography_applied_size','typography_role','typography_weight','typography_sizes'): element.pop(name,None)
                    self.assertEqual(actual,expected)

    def test_created_presets_have_actual_baselines_for_every_text_role(self):
        for definition in ({'id':'tiktok'},{'id':'youtube'},{'id':'instagram_square'},
                           {'id':'custom','width':160,'height':160}):
            profile=profile_for(definition)
            for template in TEMPLATES:
                expected=template_scene(template,profile,typography='Professional')
                for typography in TYPOGRAPHY:
                    project=studio_editing.new_workspace({'endcard_enabled':False})
                    scene=template_scene(template,profile,typography=typography)
                    project['studio']['scenes'].append(scene);project['studio']['timeline']=[scene['id']]
                    self.assertEqual(studio_editing.apply_scene_design(project,scene['id'],typography=typography),project)
                    changed=studio_editing.apply_scene_design(project,scene['id'],typography='Professional')
                    self.assertEqual(studio_editing.apply_scene_design(changed,scene['id'],typography=typography),project)
                    actual=changed['studio']['scenes'][-1]
                    for old,new in zip(expected['elements'],actual['elements']):
                        if old['type'] in ('text','source'):
                            with self.subTest(profile=definition,template=template,preset=typography,id=old['id']):
                                self.assertEqual(new['style']['font_size'],old['style']['font_size'])
                                self.assertEqual(new['style'].get('bold',False),old['style'].get('bold',False))

    def test_comparison_eligibility_and_maximum_margin_placeholders(self):
        registry=copy.deepcopy(REGISTRY)
        registry['many']={**copy.deepcopy(registry['regions']),'rows':[{'name':str(i),'value':i} for i in range(24)]}
        registry['partial']={**copy.deepcopy(registry['regions']),'rows':[{'name':'a','value':1,'coverage':1},{'name':'b','value':2,'coverage':.5}]}
        registry['missing']={**copy.deepcopy(registry['regions']),'rows':[{'name':'a','value':None},{'name':'b','value':2}]}
        self.assertEqual(studio_templates.template_result_ids('comparison',registry),['regions'])
        self.assertEqual(studio_templates.template_result_ids('metric_focus',registry),['rain'])
        profile=profile_for({'id':'custom','width':160,'height':160,'margin':40})
        for template in NEW:
            render_scene(template_scene(template,profile),profile,{})
        with self.assertRaises(ValueError): template_scene('metric_focus',profile,bindings=BINDINGS)

    def test_new_templates_render_placeholders_and_bound_results_without_mutation(self):
        self.assertTrue(set(NEW)<=set(TEMPLATES))
        profiles=[{'id':'tiktok'},{'id':'youtube'},{'id':'instagram_square'}]+[
            {'id':'custom','width':w,'height':h} for w,h in ((160,160),(160,320),(320,160),(160,3840),(3840,160))]
        for definition in profiles:
            profile=profile_for(definition)
            for template in NEW:
                for bindings in ({},BINDINGS):
                    with self.subTest(profile=definition,template=template,bound=bool(bindings)):
                        registry=copy.deepcopy(REGISTRY)
                        scene=template_scene(template,profile,bindings=bindings)
                        before=copy.deepcopy(scene)
                        image=render_scene(scene,profile,registry)
                        self.assertEqual(image.size,(profile.width,profile.height))
                        self.assertEqual(scene,before);self.assertEqual(registry,REGISTRY)
                        if not bindings: self.assertFalse(any(e.get('data_binding') for e in scene['elements']))
                        self.assertTrue(all(not e.get('locked') for e in scene['elements']))

    def test_full_body_reflows_only_on_explicit_adaptation(self):
        project=studio_editing.new_workspace({'unknown':{'keep':True},'endcard_enabled':False})
        profile=profile_for(project['studio']['output_profile'])
        scene=template_scene('metric_focus',profile,bindings=BINDINGS)
        project['studio']['calculations']=copy.deepcopy(REGISTRY)
        project=studio_editing.edit_scene(project,'add',scene=scene)
        before=copy.deepcopy(project)
        reopened=json.loads(json.dumps(project))
        self.assertEqual(studio_editing.new_workspace(reopened),project)
        adapted=studio_editing.adapt_profile(project,{'id':'youtube'})
        fresh=next(s for s in adapted['studio']['scenes'] if s['id']==scene['id'])
        region=adaptive_regions(profile_for({'id':'youtube'}))['body_full']
        metric=next(e for e in fresh['elements'] if e['type']=='metric')
        self.assertEqual(metric['transform'],{k:round(v) for k,v in region.items()})
        self.assertEqual(project,before);self.assertEqual(adapted['unknown'],project['unknown'])
        self.assertEqual(adapted['studio']['calculations'],REGISTRY)

    def test_image_template_has_visible_placeholder_or_explicit_asset(self):
        profile=profile_for({'id':'custom','width':160,'height':160})
        empty=template_scene('image_caption',profile)
        self.assertFalse(any(e['type']=='image' for e in empty['elements']))
        self.assertTrue(any('imagen' in e['style'].get('text','').lower() for e in empty['elements']))
        scene=template_scene('image_caption',profile,asset_id='asset.photo')
        image=next(e for e in scene['elements'] if e['type']=='image')
        self.assertEqual(image['style'],{'asset_id':'asset.photo','fit':'contain'})
        render_scene(scene,profile,{},assets={'asset.photo':Image.new('RGBA',(80,40),'red')})
        with self.assertRaises(ValueError): render_scene(scene,profile,{})
        with self.assertRaises(ValueError): template_scene('image_caption',profile,asset_id='../photo.png')

    def test_theme_command_is_pure_and_respects_locked_elements(self):
        project=studio_editing.new_workspace({'endcard_enabled':False,'unknown':{'keep':True}})
        sid=project['studio']['timeline'][0];scene=project['studio']['scenes'][-1]
        scene['elements'][0]['locked']=True
        scene['elements'][1]['data_binding']=BINDINGS['metric']
        project['studio']['calculations']=copy.deepcopy(REGISTRY)
        before=copy.deepcopy(project)
        changed=studio_editing.apply_scene_design(project,sid,theme='Scientific')
        after=changed['studio']['scenes'][-1]
        self.assertEqual(after['elements'][0],scene['elements'][0])
        for old,new in zip(scene['elements'],after['elements']):
            self.assertEqual(old['transform'],new['transform']);self.assertEqual(old.get('data_binding'),new.get('data_binding'))
            self.assertEqual(old['style'].get('font_size'),new['style'].get('font_size'))
        self.assertEqual(after['background'],THEMES['Scientific'][0])
        self.assertEqual(changed['studio']['calculations'],REGISTRY);self.assertEqual(project,before)
        with self.assertRaises(ValueError): studio_editing.apply_scene_design(project,'legacy.map',theme='Scientific')
        with self.assertRaises(ValueError): studio_editing.apply_scene_design(project,sid,theme='missing')

    def test_typography_round_trip_is_stable_and_manual_edits_define_new_base(self):
        project=studio_editing.new_workspace({'endcard_enabled':False})
        sid=project['studio']['timeline'][0];scene=project['studio']['scenes'][-1]
        original=copy.deepcopy(scene)
        for _ in range(5):
            for typography in TYPOGRAPHY:
                project=studio_editing.apply_scene_design(project,sid,typography=typography)
                self.assertEqual(studio_editing.apply_scene_design(project,sid,typography=typography),project)
        project=studio_editing.apply_scene_design(project,sid,typography='Professional')
        for before,after in zip(original['elements'],project['studio']['scenes'][-1]['elements']):
            self.assertEqual(after['style']['font_size'],before['style']['font_size'])
        project['studio']['scenes'][-1]['elements'][0]['style']['font_size']=37
        project=studio_editing.apply_scene_design(project,sid,typography='Social Bold')
        self.assertEqual(project['studio']['scenes'][-1]['elements'][0]['style']['font_size'],46)
        project=json.loads(json.dumps(project))
        project=studio_editing.apply_scene_design(project,sid,typography='Professional')
        self.assertEqual(project['studio']['scenes'][-1]['elements'][0]['style']['font_size'],37)

    def test_new_scene_preview_matches_encoded_movie(self):
        project=studio_editing.new_workspace({'endcard_enabled':False})
        project['studio']['output_profile']={'id':'custom','width':160,'height':160}
        scene=template_scene('comparison',profile_for(project['studio']['output_profile']),bindings=BINDINGS)
        scene['duration']=.1;project['studio']['scenes'].append(scene);project['studio']['timeline']=[scene['id']]
        project['studio']['calculations']=copy.deepcopy(REGISTRY);prepared=PreparedTimeline(project)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'comparison.mp4';export_movie(project,path)
            reader=imageio_ffmpeg.read_frames(str(path),pix_fmt='rgb24');next(reader)
            frames=list(reader);self.assertEqual(len(frames),3)
            for frame,raw in enumerate(frames):
                expected=prepared.frame_at(frame).convert('RGB').tobytes()
                self.assertLess(sum(abs(a-b) for a,b in zip(raw,expected))/len(raw),5)

    def test_ui_selects_binding_explicitly_and_theme_does_not_apply_typography(self):
        import studio_ui
        project=studio_editing.new_workspace({'endcard_enabled':False})
        project['studio']['calculations']=copy.deepcopy(REGISTRY)
        script='import sys\nsys.path.insert(0,{!r})\nfrom studio_ui import show_studio\nshow_studio({!r},key="library")'.format(str(Path(__file__).parent),project)
        with tempfile.TemporaryDirectory() as directory,patch.object(studio_ui,'STORE',Path(directory)), \
             patch('data.load_values',side_effect=AssertionError('Styling never computes science')):
            app=AppTest.from_string(script,default_timeout=30).run()
            next(s for s in app.selectbox if s.label=='Template').select('metric_focus').run()
            choice=next(s for s in app.selectbox if s.label=='Resultado del template')
            self.assertIsNone(choice.value)
            choice.select('rain').run()
            next(b for b in app.button if b.label=='Añadir escena desde template').click().run()
            self.assertFalse(app.exception);self.assertFalse(app.error)
            doc=copy.deepcopy(app.session_state['library_document']);selected=app.session_state['library_selected']
            scene=next(s for s in doc['studio']['scenes'] if s['id']==selected)
            self.assertEqual(next(e for e in scene['elements'] if e['type']=='metric')['data_binding'],BINDINGS['metric'])
            next(s for s in app.selectbox if s.label=='Estilo tipográfico').select('Social Bold').run()
            next(s for s in app.selectbox if s.label=='Tema').select('Scientific').run()
            next(b for b in app.button if b.label=='Aplicar tema a esta escena').click().run()
            after=next(s for s in app.session_state['library_document']['studio']['scenes'] if s['id']==selected)
            self.assertEqual(after['elements'][0]['style']['font_size'],scene['elements'][0]['style']['font_size'])
            next(b for b in app.button if b.label=='Aplicar tipografía a esta escena').click().run()
            self.assertFalse(app.exception);self.assertFalse(app.error)
            self.assertEqual(app.session_state['library_document']['studio']['calculations'],REGISTRY)


if __name__=='__main__': unittest.main()
