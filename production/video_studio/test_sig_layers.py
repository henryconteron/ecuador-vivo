"""SIG-U0: canonical sources/layers/view, immutable science and recovery."""
import copy,json
from pathlib import Path
import unittest
from unittest.mock import patch
import test_studio_geography as fixtures

class SigLayerTests(unittest.TestCase):
    setUp=fixtures.GeographyTests.setUp
    tearDown=fixtures.GeographyTests.tearDown
    def imported(self):
        from studio_sig_layers import add_geojson_layer
        return add_geojson_layer(self.project,self.content,'regions.geojson',self.provenance)

    def test_layers_reuse_g1_sources_regions_and_old_views_without_duplicate_registry(self):
        from studio_geography import import_geojson
        from studio_sig_layers import ensure_workspace,workspace_for,add_geojson_layer,map_payload
        old,rid=import_geojson(self.project,self.content,'regions.geojson',self.provenance)
        before=copy.deepcopy(old);candidate=ensure_workspace(old)
        for k in ('sources','regions','views'):self.assertEqual(candidate['studio']['geography'][k],before['studio']['geography'][k])
        self.assertEqual(old,before)
        repeated,lid=add_geojson_layer(candidate,self.content,'regions.geojson',self.provenance)
        self.assertEqual(repeated,candidate)
        self.assertEqual(len(workspace_for(candidate)['layers']),1)
        self.assertEqual(len(map_payload(candidate)['layers'][0]['features']),3)
        self.assertEqual(Path(next(iter(candidate['studio']['geography']['sources'].values()))['path']).read_bytes(),self.content)

    def test_two_sources_visibility_order_selection_style_and_view_are_real_pure_commands(self):
        from studio_sig_layers import add_geojson_layer,layer_command,workspace_for,map_payload
        first,lid=self.imported();original=copy.deepcopy(first)
        other=json.dumps({'type':'Feature','id':'fr.test','properties':{'name':'France fixture','value':12},
            'geometry':{'type':'Polygon','coordinates':fixtures.polygon(2,46,1)}}).encode()
        project,second=add_geojson_layer(first,other,'france.geojson',self.provenance)
        rid=next(rid for rid,r in project['studio']['geography']['regions'].items() if r['source_id']==workspace_for(project)['layers'][lid]['source_id'])
        project=layer_command(project,{'action':'select','layer_id':lid,'region_id':rid})
        self.assertEqual(workspace_for(project)['selection'],[rid])
        project=layer_command(project,{'action':'visibility','layer_id':lid,'visible':False})
        self.assertFalse(workspace_for(project)['layers'][lid]['visible']);self.assertEqual(workspace_for(project)['selection'],[])
        project=layer_command(project,{'action':'order','layer_id':lid,'offset':1})
        self.assertEqual(workspace_for(project)['order'],[second,lid])
        style={'fill':'#ff0000','stroke':'#00ff00','opacity':.3}
        project=layer_command(project,{'action':'style','layer_id':second,'style':style})
        project=layer_command(project,{'action':'view','bbox':[-60,-25,-40,-5]})
        self.assertEqual(map_payload(project)['view']['bbox'],[-60,-25,-40,-5])
        self.assertEqual(workspace_for(project)['layers'][second]['style'],style)
        self.assertEqual(first,original)
        for k in ('calculations','datasets','scenes','timeline'):self.assertEqual(project['studio'][k],first['studio'][k])

    def test_invalid_layer_source_crs_order_selection_and_view_never_mutate_document(self):
        from studio_sig_layers import layer_command
        project,lid=self.imported();before=copy.deepcopy(project)
        for message in ({'action':'view','bbox':[0,0,0,1]}, {'action':'view','bbox':[0,float('nan'),1,2]},
                        {'action':'visibility','layer_id':lid,'visible':1},
                        {'action':'select','layer_id':lid,'region_id':'invented'},
                        {'action':'style','layer_id':lid,'style':{'fill':'url(secret)','stroke':'#ffffff','opacity':1}},
                        {'action':'order','layer_id':lid,'offset':2}):
            with self.assertRaises(ValueError):layer_command(project,message)
            self.assertEqual(project,before)

    def test_remove_preserves_original_and_g1_view_references(self):
        from studio_sig_layers import layer_command,workspace_for
        from studio_geography import make_view,attach_view
        project,lid=self.imported();rid=next(iter(project['studio']['geography']['regions']))
        project,vid=make_view(project,rid);project,_=attach_view(project,vid)
        geo=copy.deepcopy(project['studio']['geography'])
        result=layer_command(project,{'action':'remove','layer_id':lid})
        for k in ('sources','regions','views'):self.assertEqual(result['studio']['geography'][k],geo[k])
        self.assertEqual(workspace_for(result)['layers'],{})
        self.assertEqual(result['studio']['scenes'],project['studio']['scenes'])

    def test_canonical_commit_persist_undo_reopen_preserve_refs_and_style(self):
        from studio_workspace import WorkspaceSession
        from studio_project import publish_document,workspace_key,source_projection
        from studio_sig_layers import layer_command
        from studio_recovery import recover_snapshot
        project,lid=self.imported();state={};publish_document(state,self.project);key=workspace_key(self.project)
        session=WorkspaceSession(state,key,source_projection(self.project),store=self.temp.name,canonical=True)
        with patch('data.load_values',side_effect=AssertionError('SIG presentation recalculated science')):
            session.commit(project)
            session.commit(layer_command(session.project,{'action':'view','bbox':[-54,-16,-47,-9]}))
            accepted=copy.deepcopy(session.project)
            recovered,_=recover_snapshot(state[key+'_draft']);self.assertEqual(recovered,accepted)
            for action in ('undo','redo'):session.dispatch({'action':action,'scene':session.selected,'version':session.version})
        self.assertEqual(session.project['studio'],accepted['studio'])
        self.assertEqual(session.project['studio']['calculations'],self.project['studio']['calculations'])

if __name__=='__main__':unittest.main()
