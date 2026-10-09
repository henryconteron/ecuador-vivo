"""Portable authoring families, explicit role assignment and shared pixels."""
import copy
import io
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
from PIL import ImageFont
import imageio_ffmpeg
from streamlit.testing.v1 import AppTest
from editorial import editorial_font
from studio_editing import new_workspace, apply_scene_design
from studio_render import render_scene
from studio_ui import canvas_payload
from studio_templates import TEMPLATES, template_scene
from studio_timeline import PreparedTimeline, export_movie
from output_profiles import profile_for
from visualizations import VisualizationSpec, render_visualization


class StudioTypographyTests(unittest.TestCase):
    def test_prepared_font_assets_match_fixed_manifest_and_licenses(self):
        directory=Path(__file__).parent/'assets'/'fonts'
        manifest=json.loads((directory/'studio-fonts-manifest.json').read_text(encoding='utf-8'))
        for row in manifest:
            payload=(directory/row['file']).read_bytes()
            self.assertEqual(len(payload),row['bytes'])
            self.assertEqual(hashlib.sha256(payload).hexdigest(),row['sha256'])
        for filename in ('OFL-BarlowCondensed.txt','OFL-AtkinsonHyperlegible.txt','OFL-Lora.txt'):
            self.assertIn('SIL OPEN FONT LICENSE',(directory/filename).read_text(encoding='utf-8'))

    def test_resolver_is_portable_strict_and_does_not_share_variable_weight(self):
        from studio_typography import studio_font, FONT_FAMILIES
        for family in FONT_FAMILIES:
            regular = studio_font(28, family=family)
            bold = studio_font(28, family=family, bold=True)
            self.assertIsInstance(regular, ImageFont.FreeTypeFont)
            self.assertNotEqual(bytes(regular.getmask('Ecuador')), bytes(bold.getmask('Ecuador')))
            original = regular.getlength('Ecuador')
            studio_font(28, family=family, bold=True)
            self.assertEqual(regular.getlength('Ecuador'), original)
        for family in ('../Lora.ttf', 'Arial', '', None, [], True):
            with self.assertRaises(ValueError): studio_font(28, family=family)
        for size in (True, 0, 601, 20.5):
            with self.assertRaises(ValueError): studio_font(size)
        with patch('studio_typography._font_bytes', side_effect=OSError('missing')):
            with self.assertRaises(ValueError): studio_font(28, family='Lora')

    def test_default_barlow_pixels_and_all_templates_are_preserved(self):
        from studio_typography import studio_font
        for bold in (False, True):
            self.assertEqual(bytes(studio_font(28, bold=bold).getmask('Árbol 12')),
                             bytes(editorial_font(28, bold=bold).getmask('Árbol 12')))
        profile = profile_for({'id':'custom','width':320,'height':320})
        for name in TEMPLATES:
            scene = template_scene(name, profile)
            original = render_scene(scene, profile, {}).tobytes()
            explicit = copy.deepcopy(scene)
            for element in explicit['elements']:
                if element['type'] in ('text','source'): element['style']['font_family'] = 'Barlow Condensed'
            self.assertEqual(render_scene(explicit, profile, {}).tobytes(), original)

    def test_explicit_barlow_keeps_large_visualization_size_and_ink_fits_new_families(self):
        from studio_render import _text_layer
        registry={'rain':{'id':'rain','variable':'Lluvia','units':'mm','value':1,'provenance':{'warnings':[]}}}
        binding={'result_id':'rain','field':'value'}
        original=render_visualization(VisualizationSpec('metric',binding,style={'font_size':200}),registry,(1920,1080))
        explicit=render_visualization(VisualizationSpec('metric',binding,style={'font_size':200,'font_family':'Barlow Condensed'}),registry,(1920,1080))
        self.assertEqual(original.tobytes(),explicit.tobytes())
        from studio_typography import studio_font
        for family in ('Lora','Atkinson Hyperlegible'):
            content='ÁÉÍÓÚj'
            font=studio_font(32,family=family)
            bbox=font.getbbox(content,anchor='lt')
            width=max(round(font.getlength(content)),bbox[2])-min(0,bbox[0])
            expected_height=bbox[3]-bbox[1]
            tile,pixels,_=_text_layer({'font_family':family,'font_size':32},(width,expected_height),content)
            # Authoring auto-fit must account for actual ink height, not nominal em.
            self.assertLessEqual(tile.getbbox()[3],tile.height)

    def test_new_family_fitting_keeps_full_combining_mark_ink(self):
        from studio_render import _text_layer
        from studio_typography import studio_font
        for family in ('Lora','Atkinson Hyperlegible'):
            content='A'+'\u0301'*8
            tile,pixels,_=_text_layer({'font_family':family,'font_size':32},(200,36),content)
            box=studio_font(pixels,family=family).getbbox(content,anchor='lt')
            self.assertLessEqual(box[3]-box[1],tile.height)


    def test_scene_roles_are_explicit_pure_and_respect_locks_science_and_sizes(self):
        project = new_workspace({'endcard_enabled':False,'unknown':{'keep':True}})
        scene = project['studio']['scenes'][-1];sid = scene['id']
        scene['elements'][-1]['locked'] = True
        before = copy.deepcopy(project)
        changed = apply_scene_design(project, sid, font_roles={'title':'Lora','body':'Atkinson Hyperlegible','source':'Lora','data':'Lora'})
        after = changed['studio']['scenes'][-1]
        self.assertEqual(after['elements'][-1], scene['elements'][-1])
        for old, new in zip(scene['elements'][:-1], after['elements'][:-1]):
            if old['type'] == 'text':
                self.assertEqual(new['style']['font_family'], 'Lora' if old['typography_role']=='title' else 'Atkinson Hyperlegible')
                self.assertEqual({k:v for k,v in new['style'].items() if k!='font_family'}, old['style'])
            self.assertEqual(new['transform'],old['transform'])
            self.assertEqual(new.get('data_binding'),old.get('data_binding'))
        self.assertEqual(project,before)
        self.assertEqual(changed['studio']['calculations'],before['studio']['calculations'])
        self.assertEqual(apply_scene_design(json.loads(json.dumps(changed)),sid,font_roles={'title':'Lora','body':'Atkinson Hyperlegible','source':'Lora','data':'Lora'}),changed)
        for roles in ({'unknown':'Lora'}, {'title':'Arial'}, {'title':None}):
            with self.assertRaises(ValueError): apply_scene_design(project,sid,font_roles=roles)

    def test_family_reaches_canvas_visualization_and_movie(self):
        project = new_workspace({'endcard_enabled':False})
        project['studio']['output_profile']={'id':'custom','width':320,'height':320}
        profile=profile_for(project['studio']['output_profile'])
        result={'id':'rain','variable':'Precipitación','units':'mm','value':132.4,'provenance':{'warnings':[]}}
        registry={'rain':result}
        for family in ('Atkinson Hyperlegible','Lora'):
            spec=VisualizationSpec('metric',{'result_id':'rain','field':'value'},style={'font_family':family})
            self.assertNotEqual(render_visualization(spec,registry,(320,200)).tobytes(),
                                render_visualization(VisualizationSpec('metric',spec.binding),registry,(320,200)).tobytes())
            scene=template_scene('cover',profile);scene['duration']=.1
            for element in scene['elements']:
                if element['type'] in ('text','source'): element['style']['font_family']=family
            project['studio']['scenes'].append(scene);project['studio']['timeline']=[scene['id']]
            prepared=PreparedTimeline(project);rendered=render_scene(scene,profile,{})
            payload=canvas_payload(rendered,scene,profile)
            self.assertTrue(payload['layers'])
            self.assertEqual(rendered.convert('RGB').tobytes(),prepared.frame_at(0).convert('RGB').tobytes())
            with tempfile.TemporaryDirectory() as directory:
                path=Path(directory)/'font.mp4';export_movie(project,path)
                reader=imageio_ffmpeg.read_frames(str(path),pix_fmt='rgb24');next(reader)
                try: frames=list(reader)
                finally: reader.close()
                self.assertEqual(len(frames),3)
                for index,raw in enumerate(frames):
                    expected=prepared.frame_at(index).convert('RGB').tobytes()
                    self.assertLess(sum(abs(a-b) for a,b in zip(raw,expected))/len(raw),5)

    def test_unknown_family_is_rejected_even_for_empty_text(self):
        project=new_workspace({'endcard_enabled':False});scene=project['studio']['scenes'][-1]
        scene['elements']=scene['elements'][:1]
        scene['elements'][0]['style'].update(text='',font_family='../file.ttf')
        with self.assertRaises(ValueError): render_scene(scene,profile_for(project['studio']['output_profile']),{})

    def test_ui_scene_and_element_family_role_survive_undo_without_science(self):
        import studio_ui
        project=new_workspace({'endcard_enabled':False})
        script='import sys\nsys.path.insert(0,{!r})\nfrom studio_ui import show_studio\nshow_studio({!r},key="fonts")'.format(str(Path(__file__).parent),project)
        with tempfile.TemporaryDirectory() as directory, patch.object(studio_ui,'STORE',Path(directory)), patch('data.load_values',side_effect=AssertionError('No science during style')):
            app=AppTest.from_string(script,default_timeout=30).run()
            next(s for s in app.selectbox if s.label=='Familia · título').select('Lora').run()
            next(b for b in app.button if b.label=='Aplicar familias por rol').click().run()
            self.assertFalse(app.exception);self.assertFalse(app.error)
            doc=copy.deepcopy(app.session_state['fonts_document'])
            self.assertEqual(doc['studio']['scenes'][-1]['elements'][0]['style']['font_family'],'Lora')
            next(s for s in app.selectbox if s.label=='Familia del elemento').select('Atkinson Hyperlegible')
            next(s for s in app.selectbox if s.label=='Rol tipográfico').select('body')
            next(b for b in app.button if b.label=='Aplicar propiedades').click().run()
            self.assertFalse(app.exception);self.assertFalse(app.error)
            element=app.session_state['fonts_document']['studio']['scenes'][-1]['elements'][0]
            self.assertEqual(element['style']['font_family'],'Atkinson Hyperlegible')
            self.assertEqual(element['typography_role'],'body')
            next(b for b in app.button if b.label=='Deshacer').click().run()
            self.assertEqual(app.session_state['fonts_document'],doc)

    def test_failed_draft_write_does_not_advance_document_or_undo(self):
        import studio_ui
        project=new_workspace({'endcard_enabled':False})
        script='import sys\nsys.path.insert(0,{!r})\nfrom studio_ui import show_studio\nshow_studio({!r},key="draftfailure")'.format(str(Path(__file__).parent),project)
        with tempfile.TemporaryDirectory() as directory, patch.object(studio_ui,'STORE',Path(directory)):
            app=AppTest.from_string(script,default_timeout=30).run()
            document=copy.deepcopy(app.session_state['draftfailure_document'])
            history=copy.deepcopy(app.session_state['draftfailure_history'])
            version=app.session_state.get('draftfailure_version',0)
            next(s for s in app.selectbox if s.label=='Familia · título').select('Lora').run()
            with patch.object(studio_ui,'write_json',side_effect=OSError('disk full')):
                next(b for b in app.button if b.label=='Aplicar familias por rol').click().run()
            self.assertFalse(app.exception);self.assertTrue(app.error)
            self.assertEqual(app.session_state['draftfailure_document'],document)
            self.assertEqual(app.session_state['draftfailure_history'],history)
            self.assertEqual(app.session_state.get('draftfailure_version',0),version)


if __name__=='__main__': unittest.main()
