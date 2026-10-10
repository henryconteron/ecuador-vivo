"""Workspace shell, linked attribute selection and non-destructive reopening."""
import copy
import json
from pathlib import Path
from unittest.mock import patch
import unittest
import test_sig_map_ui as map_tests
import test_studio_geography as geography_tests


class WorkspaceTests(unittest.TestCase):
    setUp=geography_tests.GeographyTests.setUp
    tearDown=geography_tests.GeographyTests.tearDown

    def session(self):
        from studio_sig_layers import add_geojson_layer
        from studio_project import publish_document,workspace_key,source_projection
        from studio_workspace import WorkspaceSession
        project,lid=add_geojson_layer(self.project,self.content,'regions.geojson',self.provenance)
        state={};publish_document(state,project)
        return WorkspaceSession(state,workspace_key(project),source_projection(project),store=Path(self.temp.name),canonical=True),lid

    def test_attributes_keep_ids_zero_negative_missing_and_originals(self):
        from studio_sig_workspace import attribute_rows
        session,lid=self.session();before=copy.deepcopy(session.project)
        ids,rows=attribute_rows(session.project,lid)
        self.assertEqual(ids,list(before['studio']['geography']['regions']))
        self.assertEqual(rows[0],{'name':'Brasil sintético','population':0,'signed':-5})
        rows[0]['population']=123
        self.assertEqual(session.project,before)

    def test_table_select_clear_undo_and_reopen_real_snapshot(self):
        from studio_sig_workspace import attribute_rows,select_attribute,open_copy
        from studio_sig_layers import workspace_for
        from studio_recovery import recover_snapshot
        session,lid=self.session();ids,_=attribute_rows(session.project,lid)
        select_attribute(session,lid,ids,[1],session.version)
        self.assertEqual(workspace_for(session.project)['selection'],[ids[1]])
        durable,_=recover_snapshot(session.state[session.key+'_draft'])
        self.assertEqual(workspace_for(durable)['selection'],[ids[1]])
        session.dispatch({'action':'undo','version':session.version,'scene':session.selected})
        self.assertEqual(workspace_for(session.project)['selection'],[])
        session.dispatch({'action':'redo','version':session.version,'scene':session.selected})
        self.assertEqual(workspace_for(session.project)['selection'],[ids[1]])
        select_attribute(session,lid,ids,[],session.version)
        self.assertEqual(workspace_for(session.project)['selection'],[])
        original=copy.deepcopy(session.project);open_copy(session,original)
        self.assertEqual(session.state['project_document']['studio']['geography'],original['studio']['geography'])
        self.assertNotEqual(session.state['project_document']['project_meta']['id'],original['project_meta']['id'])

    def test_stale_invalid_and_save_failure_selection_leave_document_intact(self):
        from studio_sig_workspace import attribute_rows,select_attribute
        session,lid=self.session();ids,_=attribute_rows(session.project,lid);before=copy.deepcopy(session.project)
        for rows,version in [([0],-1),([-1],session.version),([True],session.version),([0,1],session.version)]:
            with self.assertRaises(ValueError):select_attribute(session,lid,ids,rows,version)
            self.assertEqual(session.project,before)
        with patch('studio_workspace.save_snapshot',side_effect=OSError('Test storage unavailable')):
            with self.assertRaises(OSError):select_attribute(session,lid,ids,[0],session.version)
        self.assertEqual(session.project,before)

    def test_invalid_open_copy_cannot_replace_live_state(self):
        from studio_sig_workspace import open_copy
        session,_=self.session();before=copy.deepcopy(session.project)
        invalid=copy.deepcopy(before);invalid['studio']['geography']['map_workspace']['active_layer']='nonexistent'
        with self.assertRaises((ValueError,KeyError)):open_copy(session,invalid)
        self.assertEqual(session.project,before)

    def test_panel_preferences_never_change_document_or_revision(self):
        from studio_sig_workspace import preferences,choose_tool,apply_requested_tool
        session,_=self.session();before=copy.deepcopy(session.project);version=session.version
        ui=preferences(session);ui.update(left=False,right=False,dock=True)
        choose_tool(session,'Mapa observado');apply_requested_tool(session)
        self.assertEqual(session.state[session.key+'_sig_tool'],'Mapa observado')
        self.assertEqual(session.project,before);self.assertEqual(session.version,version)


class WorkspaceUiTests(map_tests.SigMapUiTests):
    # Inherit the five existing integration regressions and add shell behaviors.
    def test_collapsing_panels_preserves_payload_and_document(self):
        from studio_sig_layers import add_geojson_layer
        from studio_project import workspace_key
        project,_=add_geojson_layer(self.project,self.content,'regions.geojson',self.provenance)
        app=self.app(project)
        with self.patches():
            app.run();before=copy.deepcopy(app.session_state['project_document']);payload=copy.deepcopy(self.payload)
            for key in ('sig_toggle_left','sig_toggle_right','sig_toggle_dock'):
                app.button(key=key).click().run();self.assert_clean(app)
            self.assertEqual(app.session_state['project_document'],before)
            self.assertEqual(self.payload['version'],payload['version'])
            self.assertTrue(self.payload['workspace_layout']['dock_open'])
            self.assertTrue(app.dataframe)
            app.button(key='sig_toggle_right').click().run();self.assert_clean(app)
            self.assertEqual(app.session_state[workspace_key(project)+'_sig_ui']['tool'],'Propiedades')

    def test_topbar_data_opens_existing_import_after_properties(self):
        from studio_sig_layers import add_geojson_layer
        project,_=add_geojson_layer(self.project,self.content,'regions.geojson',self.provenance)
        app=self.app(project)
        with self.patches():
            app.run();app.button(key='sig_add_data').click().run();self.assert_clean(app)
            self.assertTrue(app.text_input(key='sig_u1_citation'))

    def test_unavailable_job_does_not_block_map_and_running_map_has_actual_status(self):
        from studio_project import workspace_key
        app=self.app();key=workspace_key(self.project)
        app.session_state['science_job']='missing-test-job'
        app.session_state[key+'_sig_preparation_sequence_map_job']='test-private-job'
        with self.patches(),patch('studio_map_jobs.map_status',return_value={'state':'running','message':'1/2 · componiendo 2025-01-01'}):
            app.run();self.assert_clean(app)
            self.assertTrue(any('Mapa: 1/2' in c.value for c in app.caption))
            self.assertEqual(app.session_state['project_document'],self.project)
            self.assertTrue(app.session_state[key+'_sig_messages'])

    def test_closed_preparation_cannot_reopen_on_rerun_or_leak_studio_dialog(self):
        # Load consumers before patching: their module-level from-imports must
        # never retain this deliberately minimal UI snapshot in later tests.
        import studio_map_ui,studio_sig,studio_preparation
        from studio_project import workspace_key
        app=self.app();key=workspace_key(self.project);calls=[]
        snapshot={'source_records':[{'date':'2024-01-01'}]}
        def close(session,prep_key,**kwargs):
            calls.append(prep_key)
            session.state.pop(prep_key+'_dialog',None)
            import streamlit as st
            st.rerun()
        with self.patches(),patch('studio_science.restored_snapshot',return_value=snapshot),patch('studio_map_ui.show_map_dialog',close):
            app.run();app.button(key='sig_toggle_time').click().run()
            app.button(key='sig_prepare_layers').click().run();self.assert_clean(app)
            self.assertEqual(len(calls),1)
            app.run();self.assert_clean(app);self.assertEqual(len(calls),1)
            self.assertNotIn(key+'_dialog',app.session_state)
            self.assertEqual(app.session_state[key+'_sig_ui']['tool'],'Propiedades')
            app.button(key='sig_prepare_layers').click().run();self.assertEqual(len(calls),2)

    def test_search_filters_list_without_mutating_visibility_or_sources(self):
        from studio_sig_layers import add_geojson_layer
        project,lid=add_geojson_layer(self.project,self.content,'regions.geojson',self.provenance)
        app=self.app(project)
        with self.patches():
            app.run();before=copy.deepcopy(app.session_state['project_document'])
            app.text_input(key=__import__('studio_project').workspace_key(project)+'_sig_layer_search').input('missing').run()
            self.assert_clean(app);self.assertEqual(app.session_state['project_document'],before)
            self.assertFalse(any(b.key=='sig_active_'+lid for b in app.button))


class PresentationTests(unittest.TestCase):
    setUp=WorkspaceTests.setUp
    tearDown=WorkspaceTests.tearDown
    session=WorkspaceTests.session
    def test_breakpoint_and_time_preferences_never_commit_science(self):
        from studio_sig_workspace import presentation_event,preferences
        session,_=self.session();before=copy.deepcopy(session.project);version=session.version
        presentation_event(session,{'action':'viewport','width':768})
        ui=preferences(session)
        self.assertTrue(ui['compact']);self.assertFalse(ui['left']);self.assertFalse(ui['right'])
        ui['left']=True
        presentation_event(session,{'action':'viewport','width':768})
        self.assertTrue(ui['left'])
        for message in [{'action':'viewport','width':True},{'action':'viewport','width':float('nan')},{'action':'view','bbox':[0,0,1,1]}]:
            with self.assertRaises(ValueError):presentation_event(session,message)
        presentation_event(session,{'action':'viewport','width':1920})
        self.assertFalse(ui['compact']);self.assertTrue(ui['left'])
        self.assertEqual(session.project,before);self.assertEqual(session.version,version)


if __name__=='__main__':unittest.main()
