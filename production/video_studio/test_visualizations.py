"""Scientific values stay independent of visualization choices and geometry."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from visualizations import VisualizationSpec, visualization_geometry, render_visualization
from studio_model import DataBinding


class VisualizationTests(unittest.TestCase):
    def test_scientific_warning_is_visible_in_exported_metric(self):
        registry=self.registry()
        registry['rain']['provenance']={'warnings':['Ningún mes está completo: datos parciales y no comparables.']}
        spec=self.spec('kpi')
        warned=render_visualization(spec,registry,(640,360))
        self.assertTrue(warned.info['visualization_geometry']['warnings'])
        registry['rain']['provenance']['warnings']=[]
        clean=render_visualization(spec,registry,(640,360))
        self.assertNotEqual(warned.tobytes(),clean.tobytes())

    def registry(self):
        return {'rain':dict(value=132.4,units='mm'), 'rows':dict(units='°C',rows=[
            dict(name='A',value=-5),dict(name='B',value=0),dict(name='C',value=10),dict(name='D',value=None)])}

    def spec(self,kind,**kwargs):
        return VisualizationSpec(kind=kind,binding=DataBinding(
            result_id='rain' if kind in ('kpi','metric') else 'rows',
            field='value' if kind in ('kpi','metric') else 'rows').to_dict(),**kwargs)

    def test_metric_consumes_the_same_value_and_unit_without_rounding_data(self):
        registry=self.registry()
        for kind in ('kpi','metric'):
            geometry=visualization_geometry(self.spec(kind),registry,(640,360))
            self.assertEqual(geometry['value'],132.4)
            self.assertEqual(geometry['value_label'],'132.4 mm')
        self.assertEqual(registry['rain']['value'],132.4)

    def test_bars_have_zero_baseline_and_negative_values_extend_left(self):
        geometry=visualization_geometry(self.spec('horizontal_bar',descending=False),self.registry(),(640,360))
        plot=geometry['plot']
        self.assertAlmostEqual(geometry['zero'],plot[0]+(plot[2]-plot[0])/3)
        self.assertLess(geometry['marks'][0]['end'],geometry['zero'])
        self.assertEqual(geometry['marks'][1]['end'],geometry['zero'])
        self.assertGreater(geometry['marks'][2]['end'],geometry['zero'])

    def test_top_n_ties_missing_and_zero_are_not_silently_rewritten(self):
        registry={'rows':dict(units='mm',rows=[dict(name='Z',value=2),dict(name='A',value=2),
                                              dict(name='zero',value=0),dict(name='missing',value=None)])}
        geometry=visualization_geometry(self.spec('ranking',top_n=2),registry,(640,360))
        self.assertEqual([m['name'] for m in geometry['marks']],['A','Z'])

    def test_dot_and_lollipop_share_exact_data_positions(self):
        registry=self.registry()
        dot=visualization_geometry(self.spec('dot'),registry,(640,360))
        lollipop=visualization_geometry(self.spec('lollipop'),registry,(640,360))
        self.assertEqual(dot['marks'],lollipop['marks'])

    def test_line_preserves_sequence_and_breaks_at_missing_data(self):
        registry={'rows':dict(units='mm',rows=[dict(name='Jan',value=2),dict(name='Feb',value=3),
                                              dict(name='Mar',value=None),dict(name='Apr',value=1)])}
        geometry=visualization_geometry(self.spec('line'),registry,(640,360))
        self.assertEqual([m['name'] for m in geometry['marks']],['Jan','Feb','Mar','Apr'])
        self.assertIsNone(geometry['marks'][2]['point'])
        self.assertEqual(len(geometry['segments']),1)

    def test_comparison_requires_two_valid_observations(self):
        with self.assertRaises(ValueError):
            visualization_geometry(self.spec('comparison'),self.registry(),(640,360))
        registry={'rows':dict(units='mm',rows=[dict(name='2024',value=0),dict(name='2026',value=10)])}
        geometry=visualization_geometry(self.spec('comparison'),registry,(640,360))
        self.assertEqual([m['value'] for m in geometry['marks']],[0,10])

    def test_all_renderers_keep_output_dimensions_bounds_and_science(self):
        registry=self.registry()
        before=copy.deepcopy(registry)
        for size in ((1080,1920),(1080,1350),(1080,1080),(1920,1080)):
            for kind in ('kpi','metric','horizontal_bar','vertical_bar','dot','lollipop','line','ranking'):
                spec=self.spec(kind,style={'color':'#00aabb','title':'Una historia'})
                rendered=render_visualization(spec,registry,size)
                self.assertEqual(rendered.size,size)
                geometry=rendered.info['visualization_geometry']
                for mark in geometry.get('marks',[]):
                    point=mark.get('point')
                    if point:
                        self.assertTrue(0<=point[0]<=size[0] and 0<=point[1]<=size[1])
        self.assertEqual(registry,before)

    def test_binding_and_style_inputs_are_declarative(self):
        for changes in ({'kind':'eval'}, {'style':{'color':'url(file://secret)'}},
                        {'top_n':0}, {'binding':{'result_id':'rain','field':'a.b'}}):
            candidate=dict(kind='kpi',binding={'result_id':'rain','field':'value'})
            candidate.update(changes)
            with self.assertRaises(ValueError): VisualizationSpec(**candidate).to_dict()


if __name__=='__main__': unittest.main()
