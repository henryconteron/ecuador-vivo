"""Real raster/compositor/MP4 fixtures; calendar, immutable publication and recovery."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import rasterio
from rasterio.io import MemoryFile
from rasterio.transform import from_bounds

from model import STORE
from jobs import write_json, sha256
from studio_map_jobs import execute, read_resource
from studio_temporal import attach_map, observation, calendar_receipt, validate_resource, _hash
from studio_timeline import PreparedTimeline, export_movie
from studio_science import generate_scientific_project
from visualization_ui import scientific_identity
from test_studio_science import scientific_fixture

SHAPE = {'type':'FeatureCollection','features':[]}


def raster_project():
    source, snapshot = scientific_fixture()
    with MemoryFile() as memory:
        with memory.open(driver='GTiff',width=4,height=4,count=2,dtype='float32',crs='EPSG:4326',
                transform=from_bounds(-80,-3,-78,-1,4,4),nodata=-9999) as raster:
            raster.write(np.full((4,4),2,dtype='float32'),1)
            values=np.full((4,4),40,dtype='float32'); values[0,0]=-9999; raster.write(values,2)
        payload=memory.read()
    import hashlib
    path=STORE/'imports'/('studio-temporal-fixture-'+hashlib.sha256(payload).hexdigest()+'.tif')
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists(): path.write_bytes(payload)
    source.update(source='local',entries=[{'date':'2025-01-01','path':str(path),'band':1},
        {'date':'2025-01-03','path':str(path),'band':2}],cadence='Por observación',
        start='2025-01-01',end='2025-01-03',
        bbox=[-80,-3,-78,-1],clip_ecuador=False,show_galapagos=False,show_provinces=False,
        width=720,duration=7/30,layout='original',citation='Synthetic raster fixture',units='mm/día')
    snapshot['scientific_identity']=scientific_identity(source)
    snapshot['source_records']=[{'date':r['date'],'band':r['band'],'file':str(path),
                                'sha256':sha256(path),'source_url':None} for r in source['entries']]
    return generate_scientific_project(source,snapshot,{'id':'custom','width':320,'height':180})


class TemporalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.project=raster_project()
        cls.job=Path(cls.temp.name)/'ready'; cls.job.mkdir()
        write_json(cls.job/'request.json',{'project':cls.project,'duration':7/30})
        with patch('data.boundary',return_value=SHAPE), \
                patch('endcard.summary_for_project',side_effect=AssertionError('Recalculated')):
            execute(cls.job,root=cls.temp.name)
        cls.record=read_resource(cls.job,root=cls.temp.name)

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def test_real_compositor_calendar_and_no_imputed_missing_dates(self):
        m=self.record['temporal_map']
        self.assertEqual(m['renderer'],'render.compose')
        self.assertEqual([(i['date'],i['start_frame'],i['end_frame']) for i in m['intervals']],
            [('2025-01-01',0,3),('2025-01-03',3,7)])
        self.assertEqual(m['nodata']['override'],None)
        self.assertFalse(m['temporal_interpolation'])
        from studio_media import AssetFrames
        e={'id':'map','type':'video','style':{'asset_id':'a'}}
        with AssetFrames({'a':self.record}) as assets:
            first=assets.at(0,[e])['video.map'].tobytes()
            last=assets.at(3/30,[e])['video.map'].tobytes()
            self.assertNotEqual(first,last)
        from studio_ffmpeg import read_frames
        reader=read_frames(self.record['path'])
        next(reader)
        try: self.assertEqual(sum(1 for _ in reader),7)
        finally: reader.close()

    def test_boundary_trim_loop_hold_share_decoded_frame_indices(self):
        style={'trim_in':1/30,'trim_out':6/30,'loop':True}
        expected=[1,2,3,4,5,1,2,3,4,5,1]
        actual=[observation(self.record,style,f) for f in range(11)]
        self.assertEqual([r['source_frame'] for r in actual],expected)
        self.assertEqual([r['date'] for r in actual],
            ['2025-01-01' if f<3 else '2025-01-03' for f in expected])
        self.assertEqual(observation(self.record,{},100)['source_frame'],6)
        self.assertEqual(observation(self.record,{},3)['date'],'2025-01-03')
        from studio_media import AssetFrames
        original={'id':'original','type':'video','style':{'asset_id':'a'}}
        clipped={'id':'clipped','type':'video','style':{'asset_id':'a',**style}}
        with AssetFrames({'a':self.record}) as assets:
            references=[assets.at(f/30,[original])['video.original'].tobytes() for f in range(7)]
            for frame,index in enumerate(expected):
                self.assertEqual(assets.at(frame/30,[clipped])['video.clipped'].tobytes(),references[index])

    def test_insert_preserves_all_science_and_old_scenes_and_receipt_uses_global_time(self):
        before=copy.deepcopy(self.project)
        with patch('data.load_values',side_effect=AssertionError('Presentation reloaded rasters')):
            candidate=attach_map(self.project,self.record)
            prepared=PreparedTimeline(candidate)
            row=prepared.rows[-1]
            spans=calendar_receipt(candidate,prepared.rows)[0]['intervals']
            self.assertEqual(spans[0]['start_frame'],row['start_frame'])
            self.assertEqual(spans[-1]['end_frame'],row['end_frame'])
            with tempfile.TemporaryDirectory() as root:
                receipt=export_movie(candidate,Path(root)/'movie.mp4')
                self.assertEqual(receipt['scientific_calendar'][0]['intervals'],spans)
        self.assertEqual(self.project,before)
        self.assertEqual(candidate['studio']['calculations'],before['studio']['calculations'])
        self.assertEqual(candidate['studio']['datasets'],before['studio']['datasets'])
        self.assertEqual(len(candidate['studio']['media']),1)

    def test_corrupted_hash_calendar_dataset_and_crop_are_rejected(self):
        bad=copy.deepcopy(self.record); bad['temporal_map']['intervals'][1]['start_frame']=2
        with self.assertRaises(ValueError): validate_resource(bad)
        bad['temporal_manifest_sha256']=_hash(bad['temporal_map'])
        with self.assertRaises(ValueError): validate_resource(bad)
        candidate=attach_map(self.project,self.record)
        candidate['studio']['scenes'][-1]['elements'][0]['style']['fit']='cover'
        with self.assertRaises(ValueError): PreparedTimeline(candidate)
        candidate=attach_map(self.project,self.record)
        candidate['studio']['datasets'].clear()
        with self.assertRaises(ValueError): PreparedTimeline(candidate)
        candidate=attach_map(self.project,self.record)
        candidate['studio']['scenes'][-1]['elements'][0]['style']['trim_in']=self.record['duration']-.001
        with self.assertRaises(ValueError): PreparedTimeline(candidate)

    def test_cancel_and_failed_source_never_offer_a_resource_or_change_document(self):
        from jobs import read_json
        before=copy.deepcopy(self.project)
        for name,cancel in [('cancel',True),('changed',False)]:
            job=Path(self.temp.name)/name; job.mkdir()
            write_json(job/'request.json',{'project':self.project,'duration':7/30})
            if cancel: (job/'cancel.request').touch()
            with patch('studio_map_jobs.verify_sources',side_effect=ValueError('Source changed')):
                execute(job,root=self.temp.name)
            self.assertEqual(read_json(job/'status.json')['state'],'cancelled' if cancel else 'failed')
            with self.assertRaises(ValueError): read_resource(job,root=self.temp.name)
            self.assertFalse((job/'resource.json').exists())
        self.assertEqual(self.project,before)

    def test_changed_scientific_context_or_revision_cannot_relabel_map(self):
        candidate=copy.deepcopy(self.project); candidate['scale']=2
        with self.assertRaises(ValueError): attach_map(candidate,self.record)
        candidate=copy.deepcopy(self.project); candidate['project_meta']['scientific_revision']='f'*64
        with self.assertRaises(ValueError): attach_map(candidate,self.record)

    def test_roundtrip_recovery_undo_and_redo_retain_map_and_calendar(self):
        from studio_workspace import WorkspaceSession
        from studio_project import publish_document
        from studio_recovery import recover_snapshot
        with tempfile.TemporaryDirectory() as root:
            state={}; publish_document(state,self.project)
            session=WorkspaceSession(state,'editor',self.project,root,canonical=True)
            session.commit(attach_map(session.project,self.record))
            accepted=copy.deepcopy(session.project)
            recovered,_=recover_snapshot(state['editor_draft'])
            self.assertEqual(recovered,accepted)
            session.dispatch({'action':'undo','version':session.version,'scene':session.selected})
            self.assertFalse(session.project['studio']['media'])
            session.dispatch({'action':'redo','version':session.version,'scene':session.selected})
            self.assertEqual(session.project['studio']['media'],accepted['studio']['media'])

    def test_dialog_prepares_privately_then_explicitly_publishes(self):
        from streamlit.testing.v1 import AppTest
        def script():
            import streamlit as st
            from studio_map_ui import show_map_dialog
            class Session:
                project=st.session_state['document']
                def commit(self,candidate): st.session_state['published']=candidate
            show_map_dialog(Session(),'test')
        app=AppTest.from_function(script,default_timeout=20)
        app.session_state['document']=self.project
        app.session_state['test_map_job']=str(self.job)
        with patch('studio_map_ui.map_status',return_value={'state':'complete'}), \
                patch('studio_map_ui.read_resource',return_value=self.record):
            app.run()
            self.assertFalse(app.exception)
            self.assertNotIn('published',app.session_state)
            with patch('data.load_values',side_effect=AssertionError('Recalculated')):
                app.button(key='test_map_publish').click().run()
        self.assertFalse(app.exception,[e.value for e in app.exception])
        self.assertEqual(len(app.session_state['published']['studio']['media']),1)

    def test_map_revision_checks_calculations_and_survives_new_current_source(self):
        candidate=attach_map(self.project,self.record)
        key=next(k for k in candidate['studio']['calculations'] if k.endswith('.mean'))
        candidate['studio']['calculations'][key]['value']=123
        with self.assertRaises(ValueError): PreparedTimeline(candidate)
        candidate=attach_map(self.project,self.record)
        # Existing maps remain usable from their original results/datasets offline.
        candidate['scale']=2
        candidate['project_meta']['scientific_revision']='f'*64
        candidate['project_meta']['scientific_identity']='e'*64
        with patch('data.load_values',side_effect=AssertionError('Reloaded old source')):
            prepared=PreparedTimeline(candidate)
            prepared.frame_at(prepared.rows[-1]['start_frame'])
