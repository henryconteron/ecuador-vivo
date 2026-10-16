"""Regression tests for compact tools and unchanged native verification."""
import copy,unittest
from pathlib import Path
from unittest.mock import patch
from test_sig_raster import RasterTests
import studio_sig_raster as raster

class NativeReadTests(unittest.TestCase):
    setUp=RasterTests.setUp;tearDown=RasterTests.tearDown;pair=RasterTests.pair;source=RasterTests.source
    def test_unchanged_source_reuses_hash_but_still_checks_file_revision(self):
        project,ids=self.pair();source=self.source(project,ids[0])
        with raster._LOCK:raster._DIGESTS.clear()
        with patch.object(raster.rasterio,'open',wraps=raster.rasterio.open) as opened,patch.object(raster,'digest',wraps=raster.digest) as hashed:
            for _ in range(3):raster.verify_source(source)
            self.assertEqual(opened.call_count,0)
            self.assertEqual(hashed.call_count,1)
        changed=copy.deepcopy(source);changed['raster_operation']={'tool':'mean','inputs':[1,2]}
        with self.assertRaises(ValueError):raster.verify_source(changed)
    def test_request_proof_expires_and_detects_same_size_restored_mtime_edit(self):
        import os
        from studio_sig_read_scope import native_read_scope
        project,ids=self.pair();source=self.source(project,ids[0]);path=Path(source['path'])
        with raster._LOCK:raster._DIGESTS.clear()
        with patch.object(raster,'digest',wraps=raster.digest) as hashed:
            with native_read_scope():
                for _ in range(3):raster.verify_source(source)
            self.assertEqual(hashed.call_count,1)
            with native_read_scope():raster.verify_source(source)
            self.assertEqual(hashed.call_count,1)
        original=path.read_bytes();stat=path.stat()
        with self.assertRaises(ValueError):
            with native_read_scope():
                raster.verify_source(source)
                path.write_bytes(original[:-1]+bytes([original[-1]^1]))
                os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns))
                raster.verify_source(source)

    def test_digest_cache_rehashes_same_size_edit_when_mtime_is_restored(self):
        import os
        project,ids=self.pair();source=self.source(project,ids[0]);path=Path(source['path'])
        original=path.read_bytes();stat=path.stat()
        with raster._LOCK:raster._DIGESTS.clear()
        with patch.object(raster,'digest',wraps=raster.digest) as hashed:
            raster.verify_source(source)
            self.assertEqual(hashed.call_count,1)
            with self.assertRaisesRegex(ValueError,'original cambió'):
                path.write_bytes(original[:-1]+bytes([original[-1]^1]))
                os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns))
                raster.verify_source(source)
            self.assertEqual(hashed.call_count,2)

class CompactToolsTests(unittest.TestCase):
    def test_tools_have_fixed_mode_without_duplicate_selector(self):
        from studio_sig_workspace import tools_panel
        import inspect
        self.assertIn('fixed_tool',inspect.signature(tools_panel).parameters)
    def test_only_open_project_uses_modal(self):
        source=Path(__file__).with_name('studio_sig_shell.py').read_text(encoding='utf8')
        self.assertIn("key='sig_tool_window'",source)
        self.assertNotIn("else preferences(session)['tool'],width='large'",source)

class ToolWindowUITests(unittest.TestCase):
    setUp=RasterTests.setUp;tearDown=RasterTests.tearDown;pair=RasterTests.pair;source=RasterTests.source
    def app(self,project,tool):
        from streamlit.testing.v1 import AppTest
        script='''import streamlit as st
from studio_sig_shell import shell_dialog
class Session:
    key='tools';version=0;state=st.session_state
    @property
    def project(self):return st.session_state['document']
    def commit(self,candidate):st.session_state['document']=candidate
shell_dialog(Session())
'''
        app=AppTest.from_string(script,default_timeout=30)
        app.session_state['document']=project
        app.session_state['tools_sig_dialog']='tools'
        app.session_state['tools_sig_ui']={'tool':tool}
        return app
    def test_vector_operation_is_compact_and_still_switches_parameters(self):
        from studio_sig_layers import add_geojson_layer
        p,_=add_geojson_layer(self.project,self.content,'Control vector',self.provenance)
        app=self.app(p,'Análisis vectorial').run()
        self.assertFalse(app.exception,[e.value for e in app.exception])
        self.assertEqual(len(app.selectbox),1)
        self.assertEqual(len(app.get('dialog')),0)
        self.assertEqual(app.text_input(key='sig_analysis_crs').label,'CRS de cálculo en metros')
        app.selectbox(key='tools_vector_operation').select('Disolver').run()
        self.assertFalse(app.exception,[e.value for e in app.exception])
        self.assertEqual(app.selectbox(key='sig_dissolve_field').label,'Disolver por campo')
        app.button(key='sig_tool_close').click().run()
        self.assertFalse(app.exception,[e.value for e in app.exception])
        self.assertFalse(app.button)
    def test_raster_and_temporal_tools_do_not_open_modal_or_tool_selector(self):
        p,_=self.pair()
        for tool in ('Ráster y tiempo','Preparar timelapse'):
            with self.subTest(tool=tool):
                app=self.app(p,tool).run()
                self.assertFalse(app.exception,[e.value for e in app.exception])
                self.assertEqual(len(app.get('dialog')),0)
                self.assertNotIn('Herramienta',[w.label for w in app.selectbox])
    def test_actual_component_package_registers_with_its_built_assets(self):
        from test_sig_map_ui import SigMapUiTests
        p,_=self.pair();probe=SigMapUiTests();probe.project=p;probe.temp=self.temp
        with patch('studio_workspace.STORE',Path(self.temp.name)):
            app=probe.app(p).run(timeout=30)
        self.assertFalse(app.exception,[e.value for e in app.exception])
        self.assertFalse(app.error,[e.value for e in app.error])

class PaletteTests(unittest.TestCase):
    setUp=RasterTests.setUp;tearDown=RasterTests.tearDown;pair=RasterTests.pair;source=RasterTests.source
    def test_palette_changes_shared_presentation_not_science(self):
        from studio_sig_palette import change_palette,PALETTES
        from studio_sig_layers import map_payload,workspace_for
        project,ids=self.pair();before=copy.deepcopy(project)
        candidate=change_palette(project,'viridis')
        old=map_payload(project);new=map_payload(candidate)
        self.assertEqual(candidate['studio']['geography']['sources'],project['studio']['geography']['sources'])
        self.assertEqual(new['layers'][0]['scale']['palette'],PALETTES['viridis']['colors'])
        self.assertEqual(new['layers'][0]['scale'],new['layers'][1]['scale'])
        self.assertEqual(old['layers'][0]['scale']['stops'],new['layers'][0]['scale']['stops'])
        self.assertNotEqual(old['layers'][0]['image'],new['layers'][0]['image'])
        with self.assertRaises(ValueError):change_palette(project,'unknown')
        self.assertEqual(project,before)
    def test_palette_survives_configure_and_export_binding(self):
        from studio_sig_palette import change_palette,PALETTES
        from studio_sig_timelapse import configure
        from studio_map_bundles import prepare_geographic_bundle,read_bundle
        from studio_sig_layers import workspace_for
        from studio_sig_raster import verify_series_binding
        project,ids=self.pair();project=configure(change_palette(project,'thermal'),ids)
        self.assertEqual(workspace_for(project)['raster_time']['palette'],'thermal')
        manifest=read_bundle(prepare_geographic_bundle(project,.2),verify_tiles=False)
        self.assertEqual(manifest['geographic_binding']['scale']['palette'],PALETTES['thermal']['colors'])
        verify_series_binding(project,manifest)
        manifest['geographic_binding']['palette']='viridis'
        with self.assertRaises(ValueError):verify_series_binding(project,manifest)
    def test_palette_and_opacity_commit_once_and_preserve_native_values(self):
        from studio_sig_shell import shell_event
        from types import SimpleNamespace
        p,_=self.pair();commits=[]
        session=SimpleNamespace(project=p,version=3,commit=lambda candidate,**kw:commits.append(candidate))
        shell_event(session,{'action':'series_style','version':3,'opacity':.4,'palette':'ocean'})
        self.assertEqual(len(commits),1)
        state=commits[0]['studio']['geography']['map_workspace']
        self.assertEqual(state['raster_time']['palette'],'ocean')
        self.assertTrue(all(state['layers'][lid]['style']['opacity']==.4 for lid in state['raster_time']['layers']))
        self.assertEqual(commits[0]['studio']['geography']['sources'],p['studio']['geography']['sources'])
    def test_map_callback_palette_is_saved_and_undo_restores_previous_style(self):
        from test_sig_map_ui import SigMapUiTests
        from studio_project import workspace_key
        from studio_recovery import recover_snapshot
        from studio_sig_palette import PALETTES
        p,_=self.pair();probe=SigMapUiTests();probe.project=p;probe.temp=self.temp
        app=probe.app(p)
        with probe.patches():
            app.run();probe.assert_clean(app)
            probe.event(app,'series_style',opacity=.6,palette='viridis')
            self.assertEqual(probe.payload['raster_time']['palette'],'viridis')
            self.assertTrue(all(layer['scale']['palette']==PALETTES['viridis']['colors'] for layer in probe.payload['layers']))
            saved,_=recover_snapshot(app.session_state[workspace_key(app.session_state.project_document)+'_draft'])
            self.assertEqual(saved['studio']['geography']['map_workspace']['raster_time']['palette'],'viridis')
            probe.event(app,'undo')
            self.assertNotIn('palette',probe.payload['raster_time'])
            self.assertEqual(app.session_state.project_document['studio']['geography']['sources'],p['studio']['geography']['sources'])

if __name__=='__main__':unittest.main()
