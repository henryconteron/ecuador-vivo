"""Workspace commands preserve science, legacy and durable history."""
import copy
from pathlib import Path
import sys
import unittest
import tempfile
import re
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
from test_studio_jobs import small_project
from studio_workspace_commands import workspace_command

class WorkspaceCommandsTests(unittest.TestCase):
    def setUp(self): self.project=small_project()
    def command(self,action,**values):
        before=copy.deepcopy(self.project)
        result=workspace_command(self.project,'red',{'action':action,**values})
        self.assertEqual(self.project,before)
        self.assertEqual(result['studio']['calculations'],before['studio']['calculations'])
        self.assertEqual(result['studio']['datasets'],before['studio']['datasets'])
        self.assertEqual(result['unknown'],before['unknown'])
        return result
    def test_project_name_preserves_unknown_and_science(self):
        self.assertEqual(self.command('rename',name='Proyecto científico')['name'],'Proyecto científico')
    def test_add_shape_and_text_and_update_properties(self):
        self.project=self.command('add_element',kind='text')
        e=self.project['studio']['scenes'][0]['elements'][0]
        result=self.command('properties',ids=[e['id']],style={'text':'Explicación','font_family':'Lora','alignment':'center'})
        self.assertEqual(result['studio']['scenes'][0]['elements'][0]['style']['text'],'Explicación')
    def test_locked_properties_rejected(self):
        self.project=self.command('add_element',kind='shape')
        e=self.project['studio']['scenes'][0]['elements'][0];e['locked']=True
        with self.assertRaises(ValueError):self.command('properties',ids=[e['id']],style={'fill':'#123456'})
    def test_duplicate_and_reorder_are_real_scene_commands(self):
        p=self.command('scene_duplicate');self.assertEqual(len(p['studio']['timeline']),3)
        self.assertEqual(self.command('reorder',order=['blue','red'])['studio']['timeline'],['blue','red'])
    def test_unknown_property_rejected(self):
        self.project=self.command('add_element',kind='text');e=self.project['studio']['scenes'][0]['elements'][0]
        with self.assertRaises(ValueError):self.command('properties',ids=[e['id']],style={'executable':'bad'})
    def test_all_templates_remain_available(self):
        from studio_templates import TEMPLATES
        self.assertEqual(len(TEMPLATES),11)
        for template in TEMPLATES:
            p=self.command('template',template=template)
            self.assertEqual(len(p['studio']['timeline']),3)
    def test_duration_quantizes_and_invalid_order_rejected(self):
        self.assertEqual(self.command('scene_properties',duration=.15)['studio']['scenes'][0]['duration'],4/30)
        with self.assertRaises(ValueError):self.command('reorder',order=['red'])
    def test_profile_and_scene_recovery_keep_originals(self):
        p=self.command('profile',profile={'id':'instagram_square'})
        self.assertEqual(p['studio']['output_profile']['id'],'instagram_square')
        self.project=self.command('scene_delete')
        p=workspace_command(self.project,'blue',{'action':'scene_recover','id':'red'})
        self.assertEqual(p['studio']['timeline'],['blue','red'])

class WorkspaceSessionTests(unittest.TestCase):
    def setUp(self):
        from studio_workspace import WorkspaceSession
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.state={};self.session=WorkspaceSession(self.state,'test',small_project(),store=self.temp.name)
    def send(self,action,**values):self.session.dispatch({'version':self.session.version,'scene':self.session.selected,'action':action,**values})
    def test_history_includes_project_name_and_durable_recovery(self):
        from studio_recovery import recover_snapshot
        self.send('rename',name='Nuevo nombre');self.send('undo');self.assertNotEqual(self.session.project.get('name'),'Nuevo nombre')
        self.send('redo');self.assertEqual(self.session.project['name'],'Nuevo nombre')
        p,_=recover_snapshot(self.state['test_draft']);self.assertEqual(p,self.session.project)
    def test_failed_disk_write_keeps_document_and_history(self):
        before=copy.deepcopy(self.session.project)
        with patch('studio_workspace.save_snapshot',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):self.send('rename',name='No se acepta')
        self.assertEqual(self.session.project,before);self.assertEqual(self.session.version,0);self.assertFalse(self.state['test_workspace_history'])
    def test_stale_command_rejected(self):
        self.send('rename',name='Aceptado')
        with self.assertRaises(ValueError):self.session.dispatch({'version':0,'scene':'red','action':'rename','name':'Obsoleto'})
        self.assertEqual(self.session.project['name'],'Aceptado')
    def test_invalid_navigation_with_pending_edit_is_atomic(self):
        with self.assertRaises(ValueError):self.send('seek',frame=-1,entries={'custom.pending':{'text':'Pending','x':1,'y':1,'w':80,'h':40}})
        self.assertEqual(self.session.version,0)
        self.assertEqual(self.session.project['studio']['scenes'][0]['elements'],[])

class WorkspaceDeliveryTests(unittest.IsolatedAsyncioTestCase):
    async def test_delivery_range_and_expiry(self):
        from starlette.testclient import TestClient
        from starlette.applications import Starlette
        from starlette.routing import Route
        import studio_delivery
        with tempfile.TemporaryDirectory() as directory,patch.object(studio_delivery,'STORE',Path(directory)):
            job=Path(directory)/'jobs'/'studio-test';job.mkdir(parents=True)
            (job/'video.mp4').write_bytes(b'0123456789');(job/'receipt.json').write_text('{}')
            url=studio_delivery.register_movie(job)
            with TestClient(Starlette(routes=[Route('/studio-media/{token}',studio_delivery.movie_response)])) as client:
                response=client.get(url,headers={'Range':'bytes=2-5'});self.assertEqual(response.status_code,206);self.assertEqual(response.content,b'2345')
                self.assertEqual(response.headers['content-type'],'video/mp4')
                self.assertIn('attachment',client.get(url+'?download=1').headers['content-disposition'])
                self.assertEqual(client.get('/studio-media/unknown').status_code,404)
            with patch.object(studio_delivery.time,'monotonic',return_value=10**20):
                self.assertEqual((await studio_delivery.movie_response(type('Request',(),{'path_params':{'token':url.rsplit('/',1)[1]}})())).status_code,404)

class WorkspaceCallbackTests(unittest.TestCase):
    def test_callbacks_acknowledge_transient_actions_and_preserve_science(self):
        import studio_workspace
        import streamlit as st
        from streamlit.testing.v1 import AppTest
        payloads=[]
        def component(**values):
            payloads.append(values['data'])
            message=st.session_state.pop('test_command',None)
            if message:
                st.session_state[values['key']]={'command':message}
                values['on_command_change']()
        script='import sys\nsys.path.insert(0,{!r})\nfrom studio_workspace import show_workspace\nshow_workspace({!r},key="callback")'.format(str(Path(__file__).parent),small_project())
        with tempfile.TemporaryDirectory() as directory,patch.object(studio_workspace,'STORE',Path(directory)),patch.object(studio_workspace,'_COMPONENT',component),patch('data.load_values',side_effect=AssertionError('Science read during styling')):
            app=AppTest.from_string(script,default_timeout=30).run();self.assertFalse(app.exception)
            original=copy.deepcopy(app.session_state['callback_document'])
            def send(action,**values):
                app.session_state['test_command']={'action':action,'scene':app.session_state.get('callback_selected','red'),'version':app.session_state['callback_version'],**values}
                app.run();self.assertFalse(app.exception)
            send('status');self.assertEqual(app.session_state['callback_command_ack'],1)
            send('add_element',kind='shape');self.assertEqual(app.session_state['callback_version'],1)
            self.assertEqual(app.session_state['callback_document']['studio']['calculations'],original['studio']['calculations'])
            send('seek',frame=-1);self.assertEqual(app.session_state['callback_version'],1)
            self.assertEqual(app.session_state['callback_command_ack'],3)
            send('undo');self.assertEqual(app.session_state['callback_document'],original)
            send('recover',path=payloads[-1]['recovery'][0]['path'])
            app.run();self.assertFalse(app.exception)
            self.assertEqual(payloads[-1]['error'],'')
            self.assertTrue(payloads[-1].get('notice','').startswith('Copia recuperada'))

class WorkspacePresentationTests(unittest.TestCase):
    def test_tokens_keep_text_focus_and_input_boundaries_readable(self):
        from test_interface import contrast
        css=(Path(__file__).parent/'workspace_frontend/workspace.css').read_text(encoding='utf-8-sig')
        colors=dict(re.findall(r'--(bg|surface|raised|control-line|muted|focus|text):\s*(#[0-9a-f]{6})',css))
        for surface in ('bg','surface','raised'):
            self.assertGreaterEqual(contrast(colors['text'],colors[surface]),4.5)
            self.assertGreaterEqual(contrast(colors['muted'],colors[surface]),4.5)
            self.assertGreaterEqual(contrast(colors['control-line'],colors[surface]),3)
            self.assertGreaterEqual(contrast(colors['focus'],colors[surface]),3)
        self.assertGreaterEqual(contrast(colors['focus'],'#07231e'),4.5)
    def test_controller_targets_are_present_and_unique(self):
        from test_interface import Controls,literal
        html=(Path(__file__).parent/'workspace_frontend/workspace.html').read_text(encoding='utf-8')
        parser=Controls();parser.feed(html);ids=[attrs['id'] for _,attrs in parser.nodes if 'id' in attrs]
        self.assertEqual(len(ids),len(set(ids)))
        targets=set(re.findall(r"q\('([a-z]+)'\)",literal('JS')))
        self.assertFalse(targets-set(ids))
        self.assertIn('canvas-stage',ids);self.assertIn('timeline-playhead',ids)

if __name__=='__main__': unittest.main()
