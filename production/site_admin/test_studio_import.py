"""Synthetic import fixtures: integrity is not scientific peer review."""
import hashlib, io, json, tempfile, unittest, zipfile
from pathlib import Path
from PIL import Image
from studio_import import inspect_package, import_draft, stage_draft, read_draft

def package(*, extra=None, bad_hash=False):
    png=io.BytesIO();Image.new('RGBA',(12,12),(0,100,150,255)).save(png,'PNG')
    # Container-header fixture only; no claim that this is a playable movie.
    files={'maps/0000-main.png':png.getvalue(),'video.mp4':b'\x00\x00\x00\x18ftypisom' + b'fixture'}
    case={'schema':'ecuador-vivo-evidence-v1','status':'draft','id':'studio-'+'a'*24,
        'title':'Serie sintética','variable':'Temperatura','units':'°C','period':{'start':'2024-09-01','end':'2024-09-01'},
        'observation_dates':['2024-09-01'],'maps':[{'date':'2024-09-01','channels':{'main':'maps/0000-main.png'}}],
        'sources':[{'date':'2024-09-01','sha256':'b'*64,'citation':'Fuente sintética','license':'Solo prueba','url':None}],
        'results':[],'metrics_status':'not_calculated','limitations':['Prueba, no datos reales.'],
        'video':'video.mp4','video_sha256':hashlib.sha256(files['video.mp4']).hexdigest(),
        'files':{n:{'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()} for n,b in files.items()}}
    if bad_hash:case['files']['video.mp4']['sha256']='0'*64
    files['case.json']=json.dumps(case,ensure_ascii=False).encode()
    files['LEEME.txt']=b'fixture'
    if extra:files.update(extra)
    output=io.BytesIO()
    with zipfile.ZipFile(output,'w') as z:
        for n,b in files.items():z.writestr(n,b)
    return output.getvalue()

class ImportTests(unittest.TestCase):
    def test_traversal_executable_extra_duplicates_and_tamper_are_refused(self):
        for extra in ({'../escape.txt':b'x'},{'assets/app.js':b'x'},{'maps/extra.png':b'x'}):
            with self.assertRaises(ValueError):inspect_package(package(extra=extra))
        with self.assertRaisesRegex(ValueError,'huella'):inspect_package(package(bad_hash=True))
        data=io.BytesIO(package())
        with zipfile.ZipFile(data,'a') as z:z.writestr('case.json',b'{}')
        with self.assertRaises(ValueError):inspect_package(data.getvalue())

    def test_import_is_private_idempotent_and_rechecks_files_before_staging(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);draft=import_draft(root,package())
            self.assertTrue(draft.is_relative_to((root/'_local/site-admin/studio-drafts').resolve()))
            self.assertFalse((root/'data').exists())
            self.assertEqual(import_draft(root,package()),draft)
            case,_=read_draft(root,draft.name);self.assertEqual(case['status'],'draft')
            writes=[]
            def save(relative,content,expected=None):
                writes.append(relative);path=root/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
            with self.assertRaisesRegex(ValueError,'revis'):stage_draft(root,draft.name,save,reviewed=False)
            stage_draft(root,draft.name,save,reviewed=True)
            self.assertIn('data/cases/studio-index.json',writes)
            index=json.loads((root/'data/cases/studio-index.json').read_bytes())
            self.assertEqual(index['cases'][0]['status'],'reviewed')
            (draft/'maps/0000-main.png').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'huella'):stage_draft(root,draft.name,save,reviewed=True)

    def test_limits_reject_before_archive_is_opened(self):
        with self.assertRaises(ValueError):inspect_package(b'not a zip')
        from unittest.mock import patch
        with patch('studio_import.PACKAGE_LIMIT',10):
            with self.assertRaisesRegex(ValueError,'tamaño'):inspect_package(package())

    def test_panel_empty_state_does_not_write_or_scan_the_project(self):
        from streamlit.testing.v1 import AppTest
        def script(folder):
            from pathlib import Path
            from studio_import_ui import show_studio_import
            def forbidden(*args,**kwargs):raise AssertionError('No writes on rerun')
            show_studio_import(Path(folder),forbidden)
        with tempfile.TemporaryDirectory() as d:
            app=AppTest.from_function(script,args=(d,),default_timeout=20).run()
            self.assertFalse(app.exception)
            self.assertFalse(list(Path(d).iterdir()))
            self.assertTrue(any('No se muestra contenido' in item.value for item in app.info))

    def test_panel_imported_draft_is_readonly_until_reviewed(self):
        from streamlit.testing.v1 import AppTest
        from unittest.mock import patch
        def script(folder):
            from pathlib import Path
            from studio_import_ui import show_studio_import
            def forbidden(*args,**kwargs):raise AssertionError('No writes on rerun')
            show_studio_import(Path(folder),forbidden)
        with tempfile.TemporaryDirectory() as d:
            import_draft(Path(d),package())
            app=AppTest.from_function(script,args=(d,),default_timeout=20)
            with patch('studio_import.read_draft',side_effect=AssertionError('No full hash/image read on idle rerun')):app.run()
            self.assertFalse(app.exception)
            self.assertFalse(app.checkbox[0].value)
            self.assertTrue(next(b for b in app.button if b.label=='Incorporar a Andes Pulso local').disabled)
            self.assertFalse((Path(d)/'data').exists())

if __name__=='__main__':unittest.main()
