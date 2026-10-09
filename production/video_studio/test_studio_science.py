"""Scientific scene factory consumes existing immutable revisions only."""
import copy
import unittest
from unittest.mock import patch
from model import default_project
from studio_timeline import PreparedTimeline


def scientific_fixture():
    source=default_project();source.update(name='Synthetic fixture',start='2025-01-01',end='2025-01-02')
    snapshot={'scientific_identity':'a'*64,'source_records':[{'date':'2025-01-01','sha256':'b'*64}],
              'results':{'mean':{'id':'mean','variable':'Rain','units':'mm/day','value':3.,'provenance':{'fixture':True}},
                         'rank':{'id':'rank','variable':'Rain','units':'mm','value':None,
                                 'rows':[{'name':'A','value':2.},{'name':'B','value':None}], 'provenance':{'fixture':True}},
                         'missing':{'id':'missing','variable':'Rain','units':'mm','value':None,'provenance':{'fixture':True}}}}
    return source,snapshot


class ScientificFactoryTests(unittest.TestCase):
    def test_available_results_become_editable_bound_scenes_without_recalculation(self):
        from studio_science import generate_scientific_project
        source,snapshot=scientific_fixture();before=copy.deepcopy((source,snapshot))
        with patch('data.load_values',side_effect=AssertionError('Presentation recalculated science')):
            project=generate_scientific_project(source,snapshot,{'id':'custom','width':320,'height':180})
            self.assertEqual(len(project['studio']['timeline']),4)
            active=[s for s in project['studio']['scenes'] if s['id'] in project['studio']['timeline']]
            bindings=[e['data_binding'] for s in active for e in s['elements'] if e.get('data_binding')]
            self.assertEqual({b['field'] for b in bindings},{'value','rows'})
            self.assertFalse(any(b['result_id'].endswith('.missing') for b in bindings))
            self.assertTrue(all(s.get('generation') for s in active))
            prepared=PreparedTimeline(project)
            for row in prepared.rows:
                self.assertEqual(prepared.frame_at(row['start_frame']).size,(320,180))
        self.assertEqual((source,snapshot),before)

    def test_all_nodata_does_not_create_empty_metric_or_chart_scenes(self):
        from studio_science import generate_scientific_project
        source,snapshot=scientific_fixture()
        snapshot['results']={'missing':snapshot['results']['missing']}
        project=generate_scientific_project(source,snapshot,{'id':'youtube'})
        self.assertEqual(len(project['studio']['timeline']),2)

    def test_regeneration_proposal_is_explicit_and_stale_proposal_is_rejected(self):
        from studio_science import generate_scientific_project, propose_template, apply_proposal
        source,snapshot=scientific_fixture()
        project=generate_scientific_project(source,snapshot,{'id':'youtube'})
        scene=next(s for s in project['studio']['scenes'] if s.get('generation',{}).get('role')=='metric')
        scene['elements'][0]['style']['text']='Human edit'
        before=copy.deepcopy(project)
        proposal=propose_template(project,scene['id'],'map_metric')
        self.assertEqual(project,before)
        self.assertTrue(proposal['changes'])
        self.assertEqual(apply_proposal(project,proposal,'preserve'),before)
        changed=copy.deepcopy(project);changed['name']='Another edit'
        with self.assertRaises(ValueError):apply_proposal(changed,proposal,'replace')
        accepted=apply_proposal(project,proposal,'replace')
        self.assertEqual(accepted['studio']['calculations'],before['studio']['calculations'])
        active=next(s for s in accepted['studio']['scenes'] if s['id']==scene['id'])
        self.assertEqual([e['data_binding'] for e in active['elements'] if e.get('data_binding')],
                         [e['data_binding'] for e in scene['elements'] if e.get('data_binding')])
        self.assertGreater(len(accepted['studio']['scenes']),len(before['studio']['scenes']))

    def test_forged_proposal_cannot_remove_scientific_bindings(self):
        from studio_science import generate_scientific_project,propose_template,apply_proposal
        source,snapshot=scientific_fixture()
        project=generate_scientific_project(source,snapshot,{'id':'youtube'})
        scene=next(s for s in project['studio']['scenes'] if s.get('generation',{}).get('role')=='metric')
        proposal=propose_template(project,scene['id'],'cover')
        proposal['after']['elements']=[e for e in proposal['after']['elements'] if not e.get('data_binding')]
        with self.assertRaises(ValueError):apply_proposal(project,proposal,'replace')

    def test_ui_loaded_snapshot_can_create_studio_project_without_recapturing(self):
        from streamlit.testing.v1 import AppTest
        from test_visualization_workflow import VisualizationWorkflowTests
        def script():
            import streamlit as st
            from model import default_project
            from visualization_ui import show_visualizations
            from studio_science import generate_scientific_project
            source=default_project()
            def create(snapshot):st.session_state['created']=generate_scientific_project(source,snapshot,{'id':'custom','width':320,'height':180})
            show_visualizations(source,lambda p:{},key='factory_ui',on_create_studio=create)
        source=default_project()
        snapshot=VisualizationWorkflowTests().snapshot(source)
        with patch('visualization_ui.capture_snapshot',return_value=snapshot) as capture:
            app=AppTest.from_function(script,default_timeout=15).run()
            app.button(key='factory_ui_load').click().run()
            app.button(key='factory_ui_studio').click().run()
            self.assertFalse(app.exception);self.assertFalse(app.error,[e.value for e in app.error])
            self.assertEqual(capture.call_count,1)
            self.assertTrue(app.session_state['created']['studio']['calculations'])


if __name__=='__main__':unittest.main()
