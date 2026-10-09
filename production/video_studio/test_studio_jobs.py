"""Actual UI -> subprocess -> receipt/downloads; isolated temporary products."""
import copy
from contextlib import contextmanager
from pathlib import Path
import sys
import tempfile
import subprocess
import time
import unittest
from unittest.mock import patch

import imageio_ffmpeg
from PIL import Image
from streamlit.testing.v1 import AppTest

sys.path.insert(0,str(Path(__file__).parent))
from studio_editing import new_workspace, attach_snapshot
from studio_model import Scene
from studio_jobs import start_studio_job
from studio_timeline import frame_at
from jobs import read_json


def small_project():
    project=new_workspace({'endcard_enabled':False,'unknown':{'preserve':True}})
    project=attach_snapshot(project,{'scientific_identity':'a'*64,
        'results':{'rain':{'id':'rain','variable':'precipitation','units':'mm','value':132.4,
            'provenance':{'warnings':['Cobertura parcial']}}},
        'source_records':[{'sha256':'b'*64}]})
    project['studio']['output_profile']={'id':'custom','width':320,'height':180}
    project['studio']['scenes']=[Scene(id='red',duration=.1,background='#ff0000').to_dict(),
                                Scene(id='blue',duration=.1,background='#0000ff').to_dict()]
    project['studio']['timeline']=['red','blue']
    return project


def wait_terminal(job):
    deadline=time.monotonic()+40
    while time.monotonic()<deadline:
        status=read_json(job/'status.json',{})
        if status.get('state') in ('complete','failed','cancelled'): return status
        time.sleep(.05)
    raise AssertionError('Studio worker timeout: '+(job/'worker.log').read_text(encoding='utf-8'))


@contextmanager
def tracked_workers():
    """Wait for OS handles to close before removing temporary Windows products."""
    original=subprocess.Popen
    children=[]
    def start(*args,**kwargs):
        child=original(*args,**kwargs);children.append(child);return child
    with patch.object(subprocess,'Popen',side_effect=start):
        try: yield
        finally:
            for child in children: child.wait(timeout=10)


class StudioJobTests(unittest.TestCase):
    def test_ui_exports_real_worker_and_exposes_complete_products(self):
        import studio_jobs
        import studio_ui
        project=small_project();before=copy.deepcopy(project)
        script='import sys\nsys.path.insert(0,{!r})\nfrom studio_ui import show_studio\nshow_studio({!r},key="jobui")'.format(str(Path(__file__).parent),project)
        with tempfile.TemporaryDirectory() as directory, patch.object(studio_jobs,'STORE',Path(directory)), \
             patch.object(studio_ui,'STORE',Path(directory)), \
             patch('data.load_values',side_effect=AssertionError('No scientific calculation during export')), tracked_workers():
            app=AppTest.from_string(script,default_timeout=30).run()
            self.assertFalse(app.exception);self.assertFalse(app.error)
            next(button for button in app.button if button.label=='Exportar timeline MP4').click().run()
            self.assertFalse(app.exception);self.assertFalse(app.error)
            job=Path(app.session_state['jobui_job'])
            status=wait_terminal(job)
            self.assertEqual(status['state'],'complete',(job/'worker.log').read_text(encoding='utf-8'))
            app.run();self.assertFalse(app.exception);self.assertFalse(app.error)
            downloads={element.proto.label for element in app.get('download_button')}
            self.assertTrue({'Descargar MP4','Descargar receipt'}.issubset(downloads),downloads)
            receipt=read_json(job/'receipt.json')
            self.assertEqual(receipt['total_frames'],6)
            self.assertEqual(receipt['calculations'],project['studio']['calculations'])
            self.assertEqual(receipt['datasets'],project['studio']['datasets'])
            self.assertEqual(read_json(job/'request.json'),before)
            reader=imageio_ffmpeg.read_frames(str(job/'video.mp4'),pix_fmt='rgb24')
            metadata=next(reader);frames=list(reader)
            self.assertEqual(metadata['size'],(320,180));self.assertEqual(len(frames),6)
            for index,frame in enumerate(frames):
                actual=Image.frombytes('RGB',(320,180),frame).getpixel((100,100))
                expected=frame_at(project,index).convert('RGB').getpixel((100,100))
                self.assertLessEqual(max(abs(a-b) for a,b in zip(actual,expected)),4)
        self.assertEqual(project,before)

    def test_real_worker_cancel_does_not_publish_complete_products(self):
        import studio_jobs
        project=small_project()
        with tempfile.TemporaryDirectory() as directory, patch.object(studio_jobs,'STORE',Path(directory)), tracked_workers():
            job=start_studio_job(project)
            (job/'cancel.request').write_text('cancel',encoding='utf-8')
            self.assertEqual(wait_terminal(job)['state'],'cancelled')
            self.assertFalse((job/'video.mp4').exists())
            self.assertFalse((job/'receipt.json').exists())
            self.assertFalse((job/'project.json').exists())


if __name__=='__main__': unittest.main()
