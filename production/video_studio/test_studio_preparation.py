"""Preparation is private until explicit publication; fixtures are synthetic."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from test_studio_science import scientific_fixture
from jobs import write_json


class PreparationTests(unittest.TestCase):
    def job(self, root, source):
        job = Path(root) / 'one'
        job.mkdir()
        write_json(job / 'source.json', source)
        return job

    def test_review_is_immutable_and_publication_uses_factory_without_calculating(self):
        from studio_preparation import execute, read_review, create_from_review
        source, snapshot = scientific_fixture()
        before = copy.deepcopy(source)
        with tempfile.TemporaryDirectory() as root:
            job = self.job(root, source)
            with patch('studio_preparation.capture_snapshot', return_value=snapshot):
                execute(job, root=root)
            review = read_review(job, root=root)
            with patch('studio_preparation.verify_sources'), patch('data.load_values', side_effect=AssertionError('Recalculated')):
                project = create_from_review(review, {'id':'youtube'}, selected=['mean'])
            self.assertEqual(len(project['studio']['timeline']), 3)
            self.assertEqual(source, before)
            write_json(job / 'review.json', {**review, 'snapshot':{**snapshot, 'scientific_identity':'c'*64}})
            with self.assertRaises(ValueError): read_review(job, root=root)

    def test_cancellation_and_failure_never_offer_a_review(self):
        from studio_preparation import execute, read_review
        source, snapshot = scientific_fixture()
        for cancel in (True, False):
            with tempfile.TemporaryDirectory() as root:
                job = self.job(root, source)
                if cancel: (job / 'cancel.request').touch()
                with patch('studio_preparation.capture_snapshot', side_effect=ValueError('Invalid source')):
                    execute(job, root=root)
                with self.assertRaises(ValueError): read_review(job, root=root)
                self.assertFalse((job / 'review.json').exists())

    def test_cancel_during_capture_prevents_publication_and_preserves_source(self):
        from studio_preparation import execute, read_review
        source, snapshot = scientific_fixture()
        with tempfile.TemporaryDirectory() as root:
            job = self.job(root, source)
            def capture(*args, **kwargs):
                (job / 'cancel.request').touch()
                return snapshot
            with patch('studio_preparation.capture_snapshot', side_effect=capture): execute(job, root=root)
            with self.assertRaises(ValueError): read_review(job, root=root)
            self.assertFalse((job / 'review.json').exists())

    def test_missing_or_changed_original_is_rejected_before_publication(self):
        from studio_preparation import verify_sources
        from jobs import sha256
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'source.tif'; path.write_bytes(b'original')
            source, snapshot = scientific_fixture()
            snapshot['source_records'] = [{'file':str(path), 'sha256':sha256(path)}]
            with patch('studio_preparation.scientific_identity', return_value=snapshot['scientific_identity']):
                verify_sources(source, snapshot)
                path.write_bytes(b'changed')
                with self.assertRaises(ValueError): verify_sources(source, snapshot)

    def test_home_assistant_publishes_only_after_explicit_action_and_never_recalculates_style(self):
        from streamlit.testing.v1 import AppTest
        from studio_preparation import execute
        from studio_preparation import ROOT
        source, snapshot = scientific_fixture()
        import uuid
        job = ROOT / ('test-' + uuid.uuid4().hex)
        job.mkdir(parents=True)
        write_json(job / 'source.json', source)
        with patch('studio_preparation.capture_snapshot', return_value=snapshot): execute(job)
        def script():
            import streamlit as st
            from studio_home import show_home
            from model import default_project
            def opened(project): st.session_state['opened'] = project
            show_home(opened, document=default_project())
        app = AppTest.from_function(script, default_timeout=15)
        app.session_state['home_mode'] = 'scientific'
        app.session_state['science_job'] = str(job)
        app.run()
        self.assertFalse(app.exception)
        self.assertNotIn('opened', app.session_state)
        app.selectbox(key='science_profile_'+job.name).select('youtube').run()
        app.number_input(key='science_duration_'+job.name).set_value(.1).run()
        self.assertNotIn('opened', app.session_state)
        with patch('studio_preparation.verify_sources'), patch('data.load_values', side_effect=AssertionError('UI recalculated')):
            app.button(key='science_create').click().run()
        self.assertFalse(app.exception, [e.value for e in app.exception])
        self.assertFalse(app.error, [e.value for e in app.error])
        self.assertTrue(app.session_state['opened']['studio']['calculations'])
        self.assertTrue(app.session_state['_pending_studio_navigation'])

    def test_cancel_button_keeps_active_document(self):
        from streamlit.testing.v1 import AppTest
        from studio_preparation import ROOT
        import uuid
        job = ROOT / ('test-' + uuid.uuid4().hex); job.mkdir(parents=True)
        write_json(job / 'status.json', {'state':'running','progress':.3,'message':'Test synthetic worker'})
        def script():
            import streamlit as st
            from studio_home import show_home
            show_home(lambda p:st.session_state.update(opened=p))
        app = AppTest.from_function(script, default_timeout=15)
        app.session_state['home_mode'] = 'scientific'
        app.session_state['science_job'] = str(job)
        app.run(); app.button(key='science_cancel').click().run()
        self.assertFalse(app.exception)
        self.assertNotIn('opened', app.session_state)
        self.assertTrue((job / 'cancel.request').exists())

    def test_existing_revision_is_verified_and_reused_without_calculation(self):
        from studio_preparation import execute, read_review
        from studio_science import generate_scientific_project, restored_snapshot
        source, snapshot = scientific_fixture()
        project = generate_scientific_project(source,snapshot,{'id':'youtube'})
        self.assertEqual(restored_snapshot(project), snapshot)
        with tempfile.TemporaryDirectory() as root:
            job = self.job(root, project)
            with patch('studio_preparation.scientific_identity',return_value=snapshot['scientific_identity']), \
                    patch('studio_preparation.verify_sources') as verify, \
                    patch('studio_preparation.capture_snapshot',side_effect=AssertionError('Recalculated')):
                execute(job,root=root)
            verify.assert_called_once()
            self.assertEqual(read_review(job,root=root)['snapshot'],snapshot)

    def test_cancel_after_worker_completes_still_blocks_project_creation(self):
        from studio_preparation import execute, read_review, cancel_preparation
        source, snapshot = scientific_fixture()
        with tempfile.TemporaryDirectory() as root:
            job = self.job(root,source)
            with patch('studio_preparation.capture_snapshot',return_value=snapshot): execute(job,root=root)
            cancel_preparation(job,root=root)
            with self.assertRaises(ValueError): read_review(job,root=root)

    def test_capture_progress_and_cancellation_are_checked_between_source_dates(self):
        from visualization_ui import capture_snapshot
        source = scientific_fixture()[0]
        reports = []
        with patch('visualization_ui.scientific_identity', return_value='a'*64), \
                patch('data.rain_path', return_value=(Path('synthetic'), 'fixture')), \
                patch('jobs.sha256', return_value='b'*64):
            def cancelled(): return bool(reports)
            with self.assertRaises(InterruptedError):
                capture_snapshot(source, lambda p:self.fail('Cancelled source was calculated'),
                    progress=lambda *args:reports.append(args),cancelled=cancelled)
        self.assertEqual(reports, [(1,2,'2025-01-01')])

    def test_invalid_status_and_future_document_fail_without_a_worker(self):
        from studio_preparation import preparation_status, start_preparation
        source, _ = scientific_fixture()
        with tempfile.TemporaryDirectory() as root:
            job = self.job(root,source)
            write_json(job/'status.json',[])
            with self.assertRaises(ValueError): preparation_status(job,root=root)
            source['project_meta'] = {'document_version':999}
            with patch('studio_preparation.subprocess.Popen') as spawn:
                with self.assertRaises(ValueError): start_preparation(source,root=root)
                spawn.assert_not_called()


if __name__ == '__main__': unittest.main()
