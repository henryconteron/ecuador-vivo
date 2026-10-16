"""Presentation regressions: unchanged values, editable layers, portable graphics."""
import copy
import unittest
from output_profiles import profile_for
from studio_editorial import graphic, ICON_NAMES, DISPLAY
from studio_render import render_scene
from studio_social_template import scenes
from studio_typography import studio_font
from visualizations import VisualizationSpec, render_visualization


class EditorialTests(unittest.TestCase):
    def fixture(self):
        rows=[{'name':f'Provincia {i+1}','value':float(24-i)} for i in range(24)]
        rows[-1]={'name':'Galápagos','value':0.0}
        results={key:{'id':key,'value':12.3,'units':'mm' if key=='sum_means' else 'mm/día'}
                 for key in ('sum_means','mean_period','peak_mean','peak_cell')}
        results['province_rank']={'id':'provinces','rows':rows,'units':'mm'}
        summary={'days':7,'observed_period':{'start':'2024-01-01','end':'2024-01-07'},
            'period_complete':True,'peak_date':'2024-01-02','peak_pixel_date':'2024-01-03',
            'province_rank':rows,'warnings':[]}
        return {'summary':summary,'results':results}

    def test_graphics_have_transparency_and_are_deterministic(self):
        for name in ('panel','pill_outline','play','marker',*('icon.'+s for s in ICON_NAMES)):
            a=graphic(name,(96,96));b=graphic(name,(96,96))
            self.assertEqual(a.size,(96,96));self.assertIsNotNone(a.getbbox())
            self.assertEqual(a.tobytes(),b.tobytes())
        self.assertGreater(studio_font(80,family=DISPLAY).getlength('ECUADOR'),100)

    def test_gradient_changes_ink_not_alpha_or_text_geometry(self):
        from studio_render import _text_layer
        style={'font_size':60,'font_family':DISPLAY,'bold':True,'color':'#f3f7f9'}
        plain,_,_=_text_layer(style,(500,80),'FINALES')
        tinted,_,_=_text_layer({**style,'gradient':['#65bde9','#d4edf5']},(500,80),'FINALES')
        self.assertEqual(plain.getchannel('A').tobytes(),tinted.getchannel('A').tobytes())
        self.assertNotEqual(plain.tobytes(),tinted.tobytes())

    def test_editorial_metric_uses_actual_units_even_in_small_boxes(self):
        for units,value in (('°C',-2.4),('m/s',4.1),('mm',0),('registros',None)):
            registry={'value':{'units':units,'value':value}}
            before=copy.deepcopy(registry)
            spec=VisualizationSpec('metric',{'result_id':'value','field':'value'},
                style={'presentation':'editorial_value','font_size':40,'font_family':DISPLAY})
            out=render_visualization(spec,registry,(200,44))
            self.assertEqual(out.info['visualization_geometry']['value'],value)
            self.assertEqual(registry,before)
        with self.assertRaises(ValueError):
            render_visualization(VisualizationSpec('metric',{'result_id':'value','field':'value'}),registry,(200,44))

    def test_rank_pages_preserve_zero_missing_and_negative_values(self):
        registry={'rows':{'units':'°C','rows':[{'name':'A','value':-5},{'name':'B','value':0},
            {'name':'C','value':10},{'name':'Sin dato','value':None}]}}
        before=copy.deepcopy(registry)
        spec=VisualizationSpec('ranking',{'result_id':'rows','field':'rows'},include_missing=True,
            style={'presentation':'editorial_ranking','font_size':28})
        out=render_visualization(spec,registry,(900,400))
        self.assertEqual([m['value'] for m in out.info['visualization_geometry']['marks']],[10,0,-5,None])
        self.assertEqual(registry,before)

    def test_reference_card_fits_output_formats_without_touching_science(self):
        snapshot=self.fixture();before=copy.deepcopy(snapshot)
        record={'manifest_sha256':'a'*64,'duration':1.,'total_frames':30,
            'layers':{'continent':{'size':[800,900]},'galapagos':{'size':[240,240]}}}
        manifest={'geographic_binding':{'opacity':1.},'layers':{'continent':{'bbox':[-81.5,-5.2,-75,1.8]}}}
        for pid in ('tiktok','instagram_reels','youtube','instagram_square','instagram_portrait'):
            project={'studio':{'output_profile':{'id':pid}},'author':'Henry P. Conteron Moreta'}
            main,card=scenes(project,record,manifest,snapshot)
            image=render_scene(card,profile_for({'id':pid}),{r['id']:r for r in snapshot['results'].values()})
            self.assertEqual(image.size,(profile_for({'id':pid}).width,profile_for({'id':pid}).height))
            self.assertEqual(len([e for e in card['elements'] if e['type']=='ranking']),2)
            self.assertEqual(len([e for e in main['elements'] if e['type']=='map']),2)
            self.assertTrue(all(e.get('template_key') for e in card['elements']))
        self.assertEqual(snapshot,before)


if __name__=='__main__':unittest.main()
