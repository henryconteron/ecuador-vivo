"""Explicit color semantics, readable legends and immutable scientific values."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import imageio_ffmpeg
from streamlit.testing.v1 import AppTest
from visualizations import VisualizationSpec, visualization_geometry, render_visualization
from studio_templates import PALETTES, template_scene
from studio_editing import new_workspace
from studio_timeline import PreparedTimeline, export_movie
from output_profiles import profile_for

ROWS={'id':'regions','variable':'Anomalía','units':'°C','rows':[
    {'name':'A','value':-5}, {'name':'B','value':2}, {'name':'C','value':10},
    {'name':'D','value':None}], 'provenance':{'warnings':[]}}
REGISTRY={'regions':ROWS}
BINDING={'result_id':'regions','field':'rows'}


class StudioPaletteTests(unittest.TestCase):
    def test_explicit_diverging_center_and_missing_values_have_legend_and_colors(self):
        scale={'palette':'Temperature','domain':[-5,10],'center':2}
        before=copy.deepcopy(REGISTRY)
        spec=VisualizationSpec('horizontal_bar',BINDING,style={'color_scale':scale})
        geometry=visualization_geometry(spec,REGISTRY,(640,480))
        colors={m['name']:m['color'] for m in geometry['marks']}
        self.assertEqual([colors[name] for name in ('A','B','C')],list(PALETTES['Temperature']['colors']))
        self.assertEqual(colors['D'],geometry['scale']['missing_color'])
        labels=[row['label'] for row in geometry['scale']['legend']]
        self.assertEqual(labels,['-5 °C','2 °C','10 °C','Sin datos'])
        image=render_visualization(spec,REGISTRY,(640,480))
        self.assertEqual(image.info['visualization_geometry'],geometry)
        self.assertEqual(REGISTRY,before)
        self.assertEqual([m['value'] for m in geometry['marks']],[10,2,-5,None])

    def test_sequential_and_categorical_scales_never_infer_domains_or_categories(self):
        spec=VisualizationSpec('ranking',BINDING,style={'color_scale':{'palette':'Earth','domain':[-5,10]}})
        geometry=visualization_geometry(spec,REGISTRY,(640,480))
        colors={m['name']:m['color'] for m in geometry['marks']}
        self.assertEqual(colors['A'],PALETTES['Earth']['colors'][0])
        self.assertEqual(colors['C'],PALETTES['Earth']['colors'][-1])
        categorical=VisualizationSpec('line',BINDING,style={'color_scale':{'palette':'Editorial','categories':['C','A','B']}})
        geometry=visualization_geometry(categorical,REGISTRY,(640,480))
        self.assertEqual([m['name'] for m in geometry['marks']],['A','B','C','D'])
        self.assertEqual(geometry['marks'][0]['color'],PALETTES['Editorial']['colors'][1])
        self.assertEqual([row['label'] for row in geometry['scale']['legend']],['C','A','B','Sin datos'])
        for scale in ({'palette':'Earth'},{'palette':'Temperature','domain':[-5,10]},
                      {'palette':'Editorial'},{'palette':'Editorial','categories':['A','B']},
                      {'palette':'Editorial','categories':['A','A']},
                      {'palette':'Earth','domain':[0,10]},{'palette':'Earth','domain':[-5,9]},
                      {'palette':'Temperature','domain':[-5,10],'center':10},
                      {'palette':'Earth','domain':[True,10]}, {'palette':'Earth','domain':[0,float('inf')]},
                      {'palette':'Earth','domain':[-5,10],'unknown':1}):
            with self.subTest(scale=scale),self.assertRaises(ValueError):
                render_visualization(VisualizationSpec('ranking',BINDING,style={'color_scale':scale}),REGISTRY,(640,480))

    def test_legend_draws_full_labels_and_refuses_insufficient_space(self):
        spec=VisualizationSpec('ranking',BINDING,style={'color_scale':{'palette':'Earth','domain':[-5,10]}})
        drawn=[]
        from PIL import ImageDraw
        original=ImageDraw.ImageDraw.text
        def capture(draw,xy,content,*args,**kwargs):
            drawn.append(content);return original(draw,xy,content,*args,**kwargs)
        with patch.object(ImageDraw.ImageDraw,'text',capture): render_visualization(spec,REGISTRY,(320,240))
        for label in ('-5 °C','10 °C','Sin datos'): self.assertIn(label,drawn)
        with self.assertRaises(ValueError): render_visualization(spec,REGISTRY,(80,80))
        long=copy.deepcopy(REGISTRY);long['regions']['units']='m'*200
        with self.assertRaises(ValueError): render_visualization(spec,long,(160,160))

    def test_extreme_finite_domain_and_scalar_no_data_are_explicit(self):
        from studio_palettes import scale_color
        scale={'palette':'Temperature','domain':[-1e308,1e308],'center':0}
        self.assertEqual(scale_color(scale,0),PALETTES['Temperature']['colors'][1])
        self.assertEqual(scale_color(scale,1e308),PALETTES['Temperature']['colors'][-1])
        integer_scale={'palette':'Temperature','domain':[-10**308,10**308],'center':0}
        self.assertEqual(scale_color(integer_scale,0),PALETTES['Temperature']['colors'][1])
        result={'id':'rain','variable':'Lluvia','units':'mm','value':None,'provenance':{'warnings':[]}}
        spec=VisualizationSpec('metric',{'result_id':'rain','field':'value'},style={'color_scale':{'palette':'Rainfall','domain':[0,200]}})
        image=render_visualization(spec,{'rain':result},(320,240))
        geometry=image.info['visualization_geometry']
        self.assertEqual(geometry['value_label'],'Sin datos')
        self.assertEqual(geometry['value_color'],geometry['scale']['missing_color'])

    def test_invalid_multiline_category_or_unit_cannot_overrun_legend(self):
        scale={'palette':'Editorial','categories':['A\nline','B','C']}
        with self.assertRaises(ValueError):
            VisualizationSpec('ranking',BINDING,style={'color_scale':scale}).to_dict()
        registry=copy.deepcopy(REGISTRY);registry['regions']['units']='°C\n'+('extra\n'*15)
        with self.assertRaises(ValueError):
            render_visualization(VisualizationSpec('ranking',BINDING,style={'color_scale':{'palette':'Earth','domain':[-5,10]}}),registry,(640,480))

    def test_top_n_preserves_explicit_selection_and_missing_legend(self):
        spec=VisualizationSpec('ranking',BINDING,top_n=1,style={'color_scale':{'palette':'Earth','domain':[9,11]}})
        geometry=visualization_geometry(spec,REGISTRY,(640,480))
        self.assertEqual([m['name'] for m in geometry['marks']],['C'])
        self.assertEqual(geometry['scale']['legend'][-1]['label'],'Sin datos')
        self.assertEqual(REGISTRY['regions']['rows'],ROWS['rows'])

    def test_line_points_keep_scale_color_and_warning_never_covers_legend(self):
        registry=copy.deepcopy(REGISTRY)
        registry['regions']['provenance']['warnings']=['Periodo parcial']
        spec=VisualizationSpec('line',BINDING,style={'color_scale':{'palette':'Temperature','domain':[-5,10],'center':2}})
        image=render_visualization(spec,registry,(640,480))
        geometry=image.info['visualization_geometry']
        for mark in geometry['marks']:
            if mark['point']:
                x,y=map(round,mark['point'])
                expected=tuple(int(mark['color'][i:i+2],16) for i in (1,3,5))
                self.assertEqual(image.getpixel((x,y))[:3],expected)
        from studio_palettes import legend_height
        top=480-max(24,round(480*.08))-legend_height(geometry['scale'])
        for index,row in enumerate(geometry['scale']['legend']):
            y=top+6+index*16
            expected=tuple(int(row['color'][i:i+2],16) for i in (1,3,5))
            self.assertEqual(image.getpixel((16,y+4))[:3],expected)
            self.assertLess(y+10,480-max(24,round(480*.08)))

    def test_inspector_submits_palette_domain_colors_and_family_together(self):
        import studio_ui
        project=new_workspace({'endcard_enabled':False})
        project['studio']['output_profile']={'id':'custom','width':640,'height':480}
        scene=template_scene('ranking_focus',profile_for(project['studio']['output_profile']),bindings={'ranking':BINDING})
        project['studio']['scenes'].append(scene);project['studio']['timeline']=[scene['id']]
        project['studio']['calculations']=copy.deepcopy(REGISTRY)
        chart=next(e for e in scene['elements'] if e['type']=='ranking')
        script='import sys\nsys.path.insert(0,{!r})\nfrom studio_ui import show_studio\nshow_studio({!r},key="scaleform")'.format(str(Path(__file__).parent),project)
        with tempfile.TemporaryDirectory() as directory,patch.object(studio_ui,'STORE',Path(directory)):
            app=AppTest.from_string(script,default_timeout=30).run()
            next(s for s in app.selectbox if s.label=='Propiedades del elemento').select(chart).run()
            prefix='scaleform_element_scale_fields_'+scene['id']+'_'+chart['id']
            before=copy.deepcopy(app.session_state['scaleform_document'])
            next(s for s in app.selectbox if s.label=='Escala del elemento').select('Temperature')
            app.number_input(key=prefix+'_minimum').set_value(-5.)
            app.number_input(key=prefix+'_maximum').set_value(10.)
            app.number_input(key=prefix+'_center').set_value(2.)
            next(s for s in app.selectbox if s.label=='Familia del elemento').select('Lora')
            next(b for b in app.button if b.label=='Aplicar propiedades').click().run()
            self.assertFalse(app.exception);self.assertFalse(app.error)
            doc=app.session_state['scaleform_document']
            element=next(e for e in doc['studio']['scenes'][-1]['elements'] if e['id']==chart['id'])
            style=element['style']['visualization']['style']
            self.assertEqual(style['color_scale'],{'palette':'Temperature','domain':[-5.,10.],'center':2.})
            self.assertEqual(style['font_family'],'Lora')
            self.assertEqual(element['data_binding'],chart['data_binding'])
            next(b for b in app.button if b.label=='Deshacer').click().run()
            self.assertEqual(app.session_state['scaleform_document'],before)

    def test_scale_json_preview_and_encoded_export_use_identical_semantics(self):
        project=new_workspace({'endcard_enabled':False})
        project['studio']['output_profile']={'id':'custom','width':640,'height':480}
        scene=template_scene('ranking_focus',profile_for(project['studio']['output_profile']),bindings={'ranking':BINDING})
        chart=next(e for e in scene['elements'] if e['type']=='ranking')
        chart['style']['visualization']['style'].update(font_family='Atkinson Hyperlegible',
            color_scale={'palette':'Temperature','domain':[-5,10],'center':2})
        scene['duration']=.1;project['studio']['scenes'].append(scene);project['studio']['timeline']=[scene['id']]
        project['studio']['calculations']=copy.deepcopy(REGISTRY)
        project=json.loads(json.dumps(project));before=copy.deepcopy(project)
        prepared=PreparedTimeline(project)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'palette.mp4';export_movie(project,path)
            reader=imageio_ffmpeg.read_frames(str(path),pix_fmt='rgb24');next(reader)
            try: frames=list(reader)
            finally: reader.close()
            self.assertEqual(len(frames),3)
            for index,raw in enumerate(frames):
                expected=prepared.frame_at(index).convert('RGB').tobytes()
                self.assertLess(sum(abs(a-b) for a,b in zip(raw,expected))/len(raw),5)
        self.assertEqual(project,before)

    def test_ui_palette_is_explicit_preserves_science_and_supports_undo(self):
        import studio_ui
        project=new_workspace({'endcard_enabled':False})
        project['studio']['calculations']=copy.deepcopy(REGISTRY)
        script='import sys\nsys.path.insert(0,{!r})\nfrom studio_ui import show_studio\nshow_studio({!r},key="palettes")'.format(str(Path(__file__).parent),project)
        with tempfile.TemporaryDirectory() as directory,patch.object(studio_ui,'STORE',Path(directory)),patch('data.load_values',side_effect=AssertionError('No recalculation')):
            app=AppTest.from_string(script,default_timeout=30).run()
            next(s for s in app.selectbox if s.label=='Paleta').select('Temperature').run()
            next(c for c in app.checkbox if c.label=='Usar paleta como escala de datos').check().run()
            for label,value in (('Mínimo del dominio',-5.),('Máximo del dominio',10.),('Centro de la escala',2.)):
                next(n for n in app.number_input if n.label==label).set_value(value).run()
            before=copy.deepcopy(app.session_state['palettes_document'])
            next(b for b in app.button if b.label=='Añadir visualización vinculada').click().run()
            self.assertFalse(app.exception);self.assertFalse(app.error)
            doc=app.session_state['palettes_document']
            chart=doc['studio']['scenes'][-1]['elements'][-1]
            self.assertEqual(chart['style']['visualization']['style']['color_scale'],{'palette':'Temperature','domain':[-5.,10.],'center':2.})
            self.assertEqual(doc['studio']['calculations'],REGISTRY)
            next(b for b in app.button if b.label=='Deshacer').click().run()
            self.assertEqual(app.session_state['palettes_document'],before)


if __name__=='__main__': unittest.main()
