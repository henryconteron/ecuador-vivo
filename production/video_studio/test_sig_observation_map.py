"""An explicit observed date keeps the full scientific revision and real pixels."""
import copy,json
from pathlib import Path
import unittest
from unittest.mock import patch
import test_studio_map_temporal as fixtures

class SigObservationMapTests(unittest.TestCase):
    setUp=fixtures.TemporalLayersTests.setUp
    tearDown=fixtures.TemporalLayersTests.tearDown

    def test_selected_observation_preserves_revision_sources_decoder_and_calendar(self):
        from studio_map_bundles import prepare_bundle,read_bundle,BundleFrames
        from studio_temporal import attach_map_layers,calendar_at,calendar_receipt
        from studio_timeline import PreparedTimeline
        from studio_map_layers import MapLayerPainter
        p=copy.deepcopy(self.project);before=copy.deepcopy(p)
        with patch.object(MapLayerPainter,'render_observation',autospec=True,
                          side_effect=MapLayerPainter.render_observation) as paint:
            record=prepare_bundle(p,6/30,source_index=1,continent_size=(130,140),galapagos_size=(68,74))
        self.assertEqual([call.args[1] for call in paint.call_args_list],[1])
        manifest=read_bundle(record)
        self.assertEqual(manifest['source_records'],before['studio']['datasets'][record['source_dataset']])
        self.assertEqual(manifest['scientific_revision'],p['project_meta']['scientific_revision'])
        self.assertEqual(manifest['observation_selection'],{'mode':'single_observation','source_index':1})
        self.assertEqual(record['period'],['2025-01-03','2025-01-03'])
        with BundleFrames(record) as decoder:
            product=decoder.at(5)
            self.assertEqual(product['observation']['date'],'2025-01-03')
            self.assertEqual(product['observation']['source_index'],1)
            self.assertEqual(product['images']['galapagos'].getchannel('A').getextrema(),(0,0))
            for image in product['images'].values():image.close()
        with patch('data.load_values',side_effect=AssertionError('Presentation calculated')):
            candidate=attach_map_layers(p,record);prepared=PreparedTimeline(candidate)
            frame=prepared.rows[-1]['start_frame']+5
            self.assertEqual({v['date'] for v in calendar_at(candidate,frame)},{'2025-01-03'})
            self.assertEqual({v['source_index'] for v in calendar_at(candidate,frame)},{1})
            with prepared.frame_at(frame):pass
            self.assertEqual(calendar_receipt(candidate,prepared.rows)[0]['intervals'][0]['source_index'],1)
        self.assertEqual(p,before)

    def test_invalid_selection_is_rejected_before_paint_or_partial_publication(self):
        from studio_map_bundles import prepare_bundle
        from studio_map_layers import MapLayerPainter
        for index in (-1,2,True,1.5,'1'):
            with patch.object(MapLayerPainter,'render_observation',side_effect=AssertionError('Invalid selected source painted')):
                with self.assertRaises(ValueError):prepare_bundle(self.project,.2,source_index=index)
        self.assertEqual(self.project,self.before)

    def test_sig_opens_rgba_review_for_explicit_observed_date(self):
        from streamlit.testing.v1 import AppTest
        def script():
            import streamlit as st
            from studio_sig import show_sig
            from studio_project import source_projection
            show_sig(source_projection(st.session_state['project_document']))
        app=AppTest.from_function(script,default_timeout=20)
        app.session_state['project_document']=self.project
        with (patch('studio_workspace.STORE',Path(self.temp.name)),
              patch('studio_map_ui.start_map_job',return_value=Path(self.temp.name)/'newjob') as start,
              patch('studio_map_ui.map_status',return_value={'state':'queued'})):
            app.run();self.assertFalse(app.exception)
            app.selectbox(key='sig_layer_date').select('2025-01-03').run()
            app.button(key='sig_prepare_layers').click().run()
            self.assertFalse(app.exception)
            key=next(b.key for b in app.button if b.key and b.key.endswith('_map_start'))
            app.button(key=key).click().run()
            self.assertEqual(start.call_args.kwargs,{'representation':'rgba_observation_bundle','source_index':1})
        self.assertEqual(app.session_state['project_document'],self.project)

    def test_selected_manifest_cannot_change_or_hide_its_source_selection(self):
        from studio_map_bundles import prepare_bundle,read_bundle,_schema
        record=prepare_bundle(self.project,.2,source_index=1,continent_size=(130,140),galapagos_size=(68,74))
        manifest=read_bundle(record)
        for change in ('wrong_date','missing_selection'):
            bad=copy.deepcopy(manifest)
            if change=='wrong_date':bad['observation_selection']['source_index']=0
            else:bad.pop('observation_selection')
            with self.assertRaises(ValueError):_schema(bad)

    def test_worker_one_frame_duration_does_not_require_the_full_series_duration(self):
        from studio_map_jobs import start_map_job
        with (patch('studio_map_jobs.ROOT',Path(self.temp.name)/'workers'),
              patch('studio_map_jobs.subprocess.Popen') as process):
            process.return_value.pid=123
            job=start_map_job(self.project,1/30,representation='rgba_observation_bundle',source_index=1)
        request=json.loads((job/'request.json').read_text(encoding='utf-8'))
        self.assertEqual(request['duration'],1/30)
        self.assertEqual(request['source_index'],1)
        self.assertEqual(request['project'],self.project)
        self.assertEqual(self.project,self.before)

    def test_chirps_missing_crs_is_read_from_original_metadata_without_science(self):
        import gzip,rasterio
        from studio_map_bundles import observed_native_crs
        source=self.project['studio']['datasets']['sources.'+self.project['project_meta']['scientific_revision']][1]
        path=Path(source['file'])
        with rasterio.open(path) as dataset:expected=str(dataset.crs)
        compressed=Path(self.temp.name)/'observed.tif.gz'
        compressed.write_bytes(gzip.compress(path.read_bytes()))
        with patch('data.load_values',side_effect=AssertionError('Metadata calculated')):
            self.assertEqual(observed_native_crs({'native_crs':None},{**source,'file':str(compressed)},'chirps'),expected)
            self.assertEqual(observed_native_crs({'native_crs':'EPSG:3857'},source,'geotiff'),'EPSG:3857')

    def test_studio_dispatcher_opens_observation_dialog_and_cancel_clears_review(self):
        from streamlit.testing.v1 import AppTest
        from studio_project import workspace_key
        key=workspace_key(self.project)
        def script():
            import streamlit as st
            from studio_workspace import show_workspace
            from studio_project import source_projection,workspace_key
            project=st.session_state['project_document']
            show_workspace(source_projection(project),key=workspace_key(project),canonical=True)
        app=AppTest.from_function(script,default_timeout=20)
        app.session_state['project_document']=self.project
        app.session_state[key+'_dialog']='observation_layers'
        with patch('studio_workspace.STORE',Path(self.temp.name)):
            app.run();self.assertFalse(app.exception,[e.value for e in app.exception])
            app.selectbox(key=key+'_observation_date').select('2025-01-03').run()
            self.assertFalse(app.exception)
            app.session_state[key+'_layer_review_base']={'stale':'test'}
            app.session_state[key+'_layer_review_asset']='obsolete'
            app.button(key=key+'_map_close').click().run()
            self.assertFalse(app.exception)
        self.assertNotIn(key+'_dialog',app.session_state)
        self.assertNotIn(key+'_layer_review_base',app.session_state)
        self.assertNotIn(key+'_layer_review_asset',app.session_state)
        self.assertEqual(app.session_state['project_document']['studio'],self.project['studio'])

    def test_sig_pending_dates_are_isolated_and_accept_uses_durable_commit(self):
        from streamlit.testing.v1 import AppTest
        from studio_map_bundles import prepare_bundle
        from studio_project import workspace_key
        from studio_recovery import recover_snapshot
        record=prepare_bundle(self.project,.2,source_index=1,continent_size=(130,140),galapagos_size=(68,74))
        def script():
            import streamlit as st
            from studio_sig import show_sig
            from studio_project import source_projection
            show_sig(source_projection(st.session_state['project_document']))
        app=AppTest.from_function(script,default_timeout=20)
        app.session_state['project_document']=self.project
        key=workspace_key(self.project)
        with (patch('studio_workspace.STORE',Path(self.temp.name)),
              patch('studio_map_ui.map_status',return_value={'state':'complete'}),
              patch('studio_map_ui.read_bundle_resource',return_value=record),
              patch('data.load_values',side_effect=AssertionError('Publication recalculated'))):
            app.run()
            app.session_state[key+'_layers_map_job']='pending-full-series'
            app.session_state[key+'_layers_map_job_observation_0']='pending-other-date'
            app.session_state[key+'_layers_map_job_observation_1']='verified-date-job'
            app.selectbox(key='sig_layer_date').select('2025-01-03').run()
            app.button(key='sig_prepare_layers').click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state['project_document'],self.project)
            app.button(key=key+'_layers_prepare_again').click().run()
            self.assertEqual(app.session_state[key+'_dialog'],'observation_layers')
            self.assertFalse([b for b in app.button if b.key==key+'_layers_publish'])
            app.session_state[key+'_layers_map_job_observation_1']='verified-date-job'
            app.run()
            app.session_state[key+'_layer_review_base']['project']='0'*64
            app.button(key=key+'_layers_publish').click().run()
            self.assertTrue(any('proyecto cambió' in e.value for e in app.error))
            self.assertEqual(app.session_state['project_document'],self.project)
            self.assertFalse(app.session_state[key+'_workspace_history'])
            from studio_temporal import _hash
            app.session_state[key+'_layer_review_base']['project']=_hash(self.project)
            app.button(key=key+'_layers_publish').click().run()
            self.assertFalse(app.exception,[e.value for e in app.exception])
        accepted=app.session_state['project_document']
        self.assertEqual(accepted['studio']['calculations'],self.project['studio']['calculations'])
        self.assertEqual(accepted['studio']['scenes'][:-1],self.project['studio']['scenes'])
        self.assertEqual(len(accepted['studio']['timeline']),len(self.project['studio']['timeline'])+1)
        self.assertTrue(app.session_state['_pending_studio_navigation'])
        recovered,_=recover_snapshot(app.session_state[key+'_draft'])
        self.assertEqual(recovered,accepted)
        self.assertNotIn(key+'_layers_map_job_observation_1',app.session_state)
        self.assertEqual(app.session_state[key+'_layers_map_job'],'pending-full-series')
        self.assertEqual(app.session_state[key+'_layers_map_job_observation_0'],'pending-other-date')

if __name__=='__main__':unittest.main()
