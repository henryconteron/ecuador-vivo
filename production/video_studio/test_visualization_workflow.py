"""The UI styles cached results; PNG snapshots reach actual FFmpeg montage."""
import copy
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import imageio_ffmpeg
import numpy as np
from PIL import Image
from streamlit.testing.v1 import AppTest
sys.path.insert(0,str(Path(__file__).parent))
import storyboard as S
import visualization_ui as V
from visualizations import VisualizationSpec,render_visualization
from model import default_project
from calculation_results import summary_results


class VisualizationWorkflowTests(unittest.TestCase):
    def snapshot(self,project):
        summary=dict(days=1,mean_period=132.4,province_rank=[dict(name='Pichincha',value=132.4,coverage=1)],
                     units='mm/día',aggregate_units='mm',city_rank_units='mm',aggregation='sum')
        return dict(results=summary_results(project,summary),source_records=[{'sha256':'a'*64}],
                    scientific_identity=V.scientific_identity(project))

    def test_style_and_chart_changes_do_not_recalculate_and_changed_science_blocks_stale_snapshot(self):
        def script():
            import streamlit as st
            from model import default_project
            from visualization_ui import show_visualizations
            st.session_state.setdefault('project',default_project())
            st.session_state.setdefault('computations',0)
            def calculate(project):
                st.session_state.computations+=1
                return {}
            show_visualizations(st.session_state.project,calculate)
        def capture(project,calculate):
            calculate(project)
            return self.snapshot(project)
        with patch('visualization_ui.capture_snapshot',side_effect=capture) as operation:
            app=AppTest.from_function(script,default_timeout=15).run()
            self.assertFalse(app.exception)
            app.button(key='visualizations_load').click().run()
            self.assertEqual(app.session_state.computations,1)
            app.text_input(key='visualizations_title').set_value('Una historia').run()
            app.selectbox(key='visualizations_kind').select('dot').run()
            self.assertFalse(app.exception)
            self.assertEqual(operation.call_count,1)
            self.assertEqual(app.session_state.computations,1)
            app.session_state.project['start']='2020-01-01'
            app.run()
            self.assertTrue(app.warning)
            self.assertFalse(any(button.key=='visualizations_add' for button in app.button))

    def test_snapshot_png_preview_mp4_and_receipt_use_the_same_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with patch.object(S,'MEDIA_ROOT',root/'media'):
                project=default_project()
                project.update(duration=.1,endcard_enabled=False,
                               delivery={'output_profile':{'id':'custom','width':640,'height':360}})
                snapshot=self.snapshot(project)
                spec=VisualizationSpec('kpi',{'result_id':'mean_period','field':'value'})
                before=copy.deepcopy(snapshot)
                identifier=V.add_visualization_card(project,spec,snapshot)
                row=project['storyboard']['cards'][-1]
                row['duration']=.1
                self.assertEqual(row['id'],identifier)
                self.assertEqual(row['data_visualization']['result']['value'],132.4)
                expected=render_visualization(spec,snapshot['results'],(640,360)).convert('RGB')
                self.assertEqual(S.card_preview(row,project).tobytes(),expected.tobytes())
                self.assertEqual(snapshot,before)
                source=root/'source.mp4'
                writer=imageio_ffmpeg.write_frames(str(source),(640,360),fps=30,
                    codec='libx264',pix_fmt_in='rgb24',macro_block_size=1)
                writer.send(None)
                for _ in range(3): writer.send(np.zeros((360,640,3),dtype='uint8'))
                writer.close()
                video,receipt=S.assemble(root,source,project,map_duration=.1,endcard_duration=0)
                self.assertEqual(receipt['cards'][-1]['data_visualization']['result']['value'],132.4)
                self.assertEqual(receipt['cards'][-1]['data_visualization']['source_records'],snapshot['source_records'])
                reader=imageio_ffmpeg.read_frames(str(video),pix_fmt='rgb24')
                try:
                    metadata=next(reader)
                    frames=[np.frombuffer(frame,dtype='uint8').reshape(360,640,3) for frame in reader]
                finally: reader.close()
                self.assertEqual(metadata['size'],(640,360))
                stage_counts=[]
                for clip in [source,*sorted((root/'montage').glob('*.mp4'))]:
                    clip_reader=imageio_ffmpeg.read_frames(str(clip),pix_fmt='rgb24')
                    try:
                        clip_metadata=next(clip_reader)
                        stage_counts.append((clip.name,len(list(clip_reader)),clip_metadata))
                    finally: clip_reader.close()
                self.assertEqual(len(frames),6,msg=str(stage_counts)+' final='+str(metadata))
                # MP4 is lossy; compare all pixels with a mean error tolerance.
                self.assertLess(np.abs(frames[-1].astype(float)-np.asarray(expected)).mean(),5)

    def test_scientific_snapshot_cannot_be_cropped_or_contain_forged_bindings(self):
        with tempfile.TemporaryDirectory() as directory,patch.object(S,'MEDIA_ROOT',Path(directory)):
            project=default_project()
            spec=VisualizationSpec('kpi',{'result_id':'mean_period','field':'value'})
            V.add_visualization_card(project,spec,self.snapshot(project))
            cropped=copy.deepcopy(project)
            cropped['storyboard']['cards'][-1]['fit']='cover'
            with self.assertRaises(ValueError): S.cards_for(cropped)
            forged=copy.deepcopy(project)
            forged['storyboard']['cards'][-1]['data_visualization']['spec']['binding']['result_id']='missing'
            with self.assertRaises(ValueError): S.cards_for(forged)
            falsified=copy.deepcopy(project)
            falsified['storyboard']['cards'][-1]['data_visualization']['result']['value']=999
            with self.assertRaises(ValueError): S.cards_for(falsified)
            from visualizations import snapshot_checksum
            payload=falsified['storyboard']['cards'][-1]['data_visualization']
            payload['snapshot_sha256']=snapshot_checksum(payload)
            with self.assertRaisesRegex(ValueError,'PNG'): S.cards_for(falsified)

    def test_chirps_file_versions_invalidate_identity_without_downloading(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'source.tif.gz';path.write_bytes(b'original')
            project=default_project();project.update(start='2024-01-01',end='2024-01-01')
            with patch('data.rain_path',return_value=(path,'official')) as resolver:
                identity=V.scientific_identity(project)
                path.write_bytes(b'changed and larger')
                self.assertNotEqual(V.scientific_identity(project),identity)
                self.assertTrue(all(call.kwargs.get('allow_download') is False for call in resolver.call_args_list))

    def test_capture_rejects_a_source_changed_during_calculation(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'imports'/'source.tif';path.parent.mkdir();path.write_bytes(b'original')
            project=default_project();project.update(source='local',entries=[{'date':'2025-01-01','path':str(path),'band':1}])
            def calculate(settings):
                path.write_bytes(b'different revision')
                return {'days':1,'mean_period':132.4}
            with patch('model.STORE',Path(directory)), self.assertRaisesRegex(ValueError,'cambi'):
                V.capture_snapshot(project,calculate)


if __name__=='__main__': unittest.main()
