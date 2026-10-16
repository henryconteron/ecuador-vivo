"""Scientific resource authoring stays separate from the user's video."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

class ResourceWorkbenchTests(unittest.TestCase):
    def test_draft_starts_in_canvas_without_converting_or_mutating_video(self):
        from studio_home import create_project
        from studio_resource_workbench import resource_draft
        video=create_project('free',{'id':'tiktok'},name='Mi video');before=copy.deepcopy(video)
        state={};draft=resource_draft(state,video)
        self.assertIn('resource',draft['project_meta']);self.assertEqual(video,before)
        self.assertNotEqual(draft['project_meta']['id'],video['project_meta']['id'])
        self.assertEqual(resource_draft(state,video),draft)

    def test_open_save_and_send_preserve_video_science_and_authored_elements(self):
        from studio_home import create_project
        from studio_workspace import WorkspaceSession
        from studio_resource_workbench import resource_draft,resource_command
        video=create_project('free',{'id':'tiktok'},name='Mi video');before=copy.deepcopy(video)
        with tempfile.TemporaryDirectory() as folder:
            state={'project_document':video};session=WorkspaceSession(state,'resources',resource_draft(state,video),store=folder)
            def command(action,**kwargs):return resource_command(session,{'action':action,'version':session.version,'scene':session.selected,**kwargs})
            command('resource_open',resource_id='enso_anomaly')
            self.assertEqual(session.project['studio']['scenes'][0]['resource']['id'],'enso_anomaly')
            self.assertGreaterEqual(len(list((Path(folder)/'projects').glob('*.json'))),2)
            target=command('resource_send')
            self.assertEqual(video,before);self.assertEqual(target['studio']['calculations'],before['studio']['calculations'])
            self.assertEqual(len(target['studio']['timeline']),len(before['studio']['timeline'])+1)
            self.assertEqual(target['name'],'Mi video');self.assertNotIn('resource',target['project_meta'])

    def test_invalid_template_or_stale_message_does_not_accept_pending_edits(self):
        from studio_workspace import WorkspaceSession
        from studio_resource_workbench import resource_draft,resource_command
        with tempfile.TemporaryDirectory() as folder:
            state={};session=WorkspaceSession(state,'resources',resource_draft(state,None),store=folder)
            original=copy.deepcopy(session.project)
            for values in [{'resource_id':'unknown','version':0},{'resource_id':'rain_volume','version':-1}]:
                with self.assertRaises(ValueError):resource_command(session,{'action':'resource_open','scene':session.selected,**values})
                self.assertEqual(session.project,original)

    def test_route_mounts_resource_canvas_without_a_gallery_form(self):
        from studio_resource_workbench import show_resource_workbench
        def run():
            import streamlit as st
            from studio_resource_workbench import show_resource_workbench
            show_resource_workbench(st.session_state.get('video'))
        with patch('studio_resource_workbench.show_workspace') as mount:
            app=AppTest.from_function(run).run();self.assertFalse(app.exception)
            self.assertEqual(mount.call_count,1)
            self.assertFalse(mount.call_args.kwargs['canonical'])

if __name__=='__main__':unittest.main()
