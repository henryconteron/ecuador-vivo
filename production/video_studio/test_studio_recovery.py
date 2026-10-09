"""Recovery preserves accepted documents, backups and scientific registries."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
from studio_editing import new_workspace
from studio_recovery import save_snapshot, recover_snapshot, list_snapshots


class StudioRecoveryTests(unittest.TestCase):
    def test_atomic_snapshot_backup_and_unknown_fields(self):
        project=new_workspace({'endcard_enabled':False,'unknown':{'retain':[1,2]}});before=copy.deepcopy(project)
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'borrador-studio-test.json'
            save_snapshot(target,project)
            changed=copy.deepcopy(project);changed['studio']['scenes'][-1]['name']='Cambio'
            save_snapshot(target,changed)
            self.assertEqual(recover_snapshot(target),(changed,False))
            self.assertEqual(recover_snapshot(target.with_name(target.stem+'.previous.json')),(project,False))
            self.assertEqual(list_snapshots(Path(directory)),[target.resolve()])
            self.assertFalse(list(Path(directory).glob('*.tmp')))
        self.assertEqual(project,before)

    def test_corruption_uses_previous_with_explicit_flag(self):
        project=new_workspace({'endcard_enabled':False})
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'borrador-studio-test.json';save_snapshot(target,project);save_snapshot(target,project)
            target.write_text('{broken',encoding='utf-8')
            self.assertEqual(recover_snapshot(target),(project,True))
            self.assertEqual(target.read_text(encoding='utf-8'),'{broken')
            target.write_text(json.dumps({'storyboard':[]}),encoding='utf-8')
            self.assertEqual(recover_snapshot(target),(project,True))

    def test_disk_failure_preserves_last_accepted_snapshot_and_removes_owned_temp(self):
        import studio_recovery
        project=new_workspace({'endcard_enabled':False})
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'borrador-studio-test.json';save_snapshot(target,project)
            changed=copy.deepcopy(project);changed['studio']['scenes'][-1]['name']='No guardar'
            with patch.object(studio_recovery.os,'fsync',side_effect=OSError('disk full')),self.assertRaises(OSError): save_snapshot(target,changed)
            self.assertEqual(recover_snapshot(target),(project,False));self.assertFalse(list(Path(directory).glob('*.tmp')))

    def test_invalid_or_future_project_and_oversize_do_not_replace_snapshot(self):
        import studio_recovery
        project=new_workspace({'endcard_enabled':False})
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);target=root/'borrador-studio-test.json';save_snapshot(target,project)
            invalid=copy.deepcopy(project);invalid['schema_version']=999
            with self.assertRaises(ValueError): save_snapshot(target,invalid)
            with patch.object(studio_recovery,'MAX_BYTES',1),self.assertRaises(ValueError): recover_snapshot(target)
            self.assertEqual(recover_snapshot(target),(project,False))
            (root/'other.json').write_text('{}',encoding='utf-8')
            self.assertEqual(list_snapshots(root),[target.resolve()])

    def test_initial_autosave_reopen_in_new_session_preserves_all_templates_and_results(self):
        import studio_ui
        from streamlit.testing.v1 import AppTest
        project=new_workspace({'endcard_enabled':False,'unknown':{'preserve':True}})
        script='import sys\nsys.path.insert(0,{!r})\nfrom studio_ui import show_studio\nshow_studio({!r},key="recover")'.format(str(Path(__file__).parent),project)
        with tempfile.TemporaryDirectory() as directory,patch.object(studio_ui,'STORE',Path(directory)), \
             patch('data.load_values',side_effect=AssertionError('No science during recovery')):
            app=AppTest.from_string(script,default_timeout=30).run()
            saved=Path(app.session_state['recover_draft']);self.assertTrue(saved.is_file())
            next(b for b in app.button if b.label=='Añadir forma').click().run()
            accepted=copy.deepcopy(app.session_state['recover_document'])
            second=AppTest.from_string(script,default_timeout=30).run()
            next(s for s in second.selectbox if s.label=='Borrador guardado').select(str(saved))
            next(b for b in second.button if b.label=='Abrir copia recuperada').click().run()
            self.assertFalse(second.exception);self.assertFalse(second.error)
            self.assertEqual(second.session_state['recover_document'],accepted)
            self.assertNotEqual(second.session_state['recover_draft'],str(saved))
            self.assertEqual(json.loads(saved.read_text(encoding='utf-8')),accepted)


if __name__=='__main__': unittest.main()
