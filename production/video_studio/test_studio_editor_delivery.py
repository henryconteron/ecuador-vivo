"""Focused delivery and unchanged-resource integrity regressions."""
import copy
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from studio_cache import StudioPreviewCache, _PreviewSession
from studio_ui import canvas_payload
from studio_home import create_project
from studio_model import Element
from studio_timeline import PreparedTimeline
from studio_validation_cache import ResourceProofs


class EditorDeliveryTests(unittest.TestCase):
    def test_failed_background_preparation_preserves_pixels_and_can_recover(self):
        project=create_project('free',{'id':'youtube'})
        sid=project['studio']['timeline'][0]
        scene=next(s for s in project['studio']['scenes'] if s['id']==sid)
        scene['duration']=.1
        scene['elements']=[Element(id='title',type='text',style={'text':'Antes','font_size':24},
            transform={'x':40,'y':40,'width':600,'height':80}).to_dict()]
        cache=StudioPreviewCache()
        try:
            original,pending=cache.workspace_products(project,sid,0,canvas_payload)
            self.assertFalse(pending)
            changed=copy.deepcopy(project)
            next(s for s in changed['studio']['scenes'] if s['id']==sid)['elements'][0]['style']['text']='Después'
            with patch.object(_PreviewSession,'preview',side_effect=RuntimeError('Fallo controlado de preparación')):
                retained,pending=cache.workspace_products(changed,sid,0,canvas_payload)
                self.assertTrue(pending);self.assertEqual(retained,original)
                with self.assertRaisesRegex(RuntimeError,'Fallo controlado'):cache._future.result(timeout=20)
                failed,pending=cache.workspace_products(changed,sid,0,canvas_payload)
            self.assertFalse(pending);self.assertEqual(failed,original)
            self.assertEqual(cache.visual_error,'Fallo controlado de preparación')
            recovered=copy.deepcopy(changed);recovered['name']='Recuperado'
            cache.workspace_products(recovered,sid,0,canvas_payload)
            cache._future.result(timeout=20)
            current,pending=cache.workspace_products(recovered,sid,0,canvas_payload)
            self.assertFalse(pending);self.assertIsNone(cache.visual_error)
            self.assertNotEqual(current['identity'],original['identity'])
            self.assertNotEqual(current['preview'],original['preview'])
        finally:cache.clear()

    def test_reduced_preview_preserves_project_clock_and_authored_text(self):
        project=create_project('free',{'id':'tiktok'})
        scene=next(s for s in project['studio']['scenes'] if s['id']==project['studio']['timeline'][0]);scene['duration']=.1
        scene['elements']=[Element(id='date',type='text',style={'text':'2024-01-03','font_size':16},
            transform={'x':40,'y':40,'width':600,'height':60}).to_dict()]
        original=copy.deepcopy(project);full=PreparedTimeline(project);preview=PreparedTimeline(project,preview_max_side=640)
        self.assertEqual(full.rows,preview.rows);self.assertEqual(full.total_frames,preview.total_frames)
        self.assertEqual(preview.frame_at(0).size,(360,640));self.assertEqual(full.frame_at(0).size,(1080,1920))
        self.assertEqual(preview.project,original);self.assertEqual(project,original)
        scene['elements'][0]['style']['font_size']=7
        with self.assertRaises(ValueError):PreparedTimeline(project,preview_max_side=640).frame_at(0)

    def test_file_revision_expires_proof_even_when_size_and_mtime_restored(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'resource';path.write_bytes(b'original')
            project=create_project('free',{'id':'youtube'})
            project['studio']['geography']={'sources':{'r':{'path':str(path)}}}
            proof=ResourceProofs();checks=[];digest=hashlib.sha256(path.read_bytes()).hexdigest()
            def validate():
                checks.append(True)
                if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise ValueError('Recurso alterado')
            proof.verify(project,validate)
            renamed=copy.deepcopy(project);renamed['name']='Nuevo nombre';proof.verify(renamed,validate)
            self.assertEqual(len(checks),1)
            stat=path.stat();path.write_bytes(b'changed!');os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns))
            with self.assertRaises(ValueError):proof.verify(renamed,validate)
            self.assertEqual(len(checks),2)

if __name__=='__main__':unittest.main()
