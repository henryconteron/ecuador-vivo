"""Ordered local gestures; canonical durable commit, no stale/partial mutation."""
import copy
import unittest
from unittest.mock import patch
import test_sig_layers as fixtures


class SigProtocolTests(unittest.TestCase):
    setUp=fixtures.SigLayerTests.setUp
    tearDown=fixtures.SigLayerTests.tearDown
    imported=fixtures.SigLayerTests.imported

    def session(self):
        from studio_workspace import WorkspaceSession
        from studio_project import publish_document,source_projection,workspace_key
        project,self.lid=self.imported();state={};publish_document(state,project)
        return WorkspaceSession(state,workspace_key(project),source_projection(project),store=self.temp.name,canonical=True)

    def message(self,session,commands,*,base=None):
        return {'client':'a'*32,'version':session.version if base is None else base,
                'sequence':commands[-1]['sequence'],'commands':commands}

    def test_overlap_gestures_and_selection_save_once_each_and_reopen(self):
        from studio_sig_protocol import apply_map_intents
        from studio_sig_layers import workspace_for
        from studio_recovery import recover_snapshot
        s=self.session();before=copy.deepcopy(s.project);base=s.version
        first={'sequence':1,'action':'view','bbox':[-54,-16,-46,-8]}
        second={'sequence':2,'action':'select','layer_id':self.lid,'region_id':next(iter(s.project['studio']['geography']['regions']))}
        apply_map_intents(s,self.message(s,[first],base=base));version=s.version
        apply_map_intents(s,self.message(s,[first,second],base=base))
        self.assertEqual(s.version,version+1)
        apply_map_intents(s,self.message(s,[first,second],base=base));self.assertEqual(s.version,version+1)
        reopened,_=recover_snapshot(s.state[s.key+'_draft']);self.assertEqual(reopened,s.project)
        self.assertEqual(workspace_for(reopened)['selection'],[second['region_id']])
        for key in ('sources','regions','views'):self.assertEqual(reopened['studio']['geography'][key],before['studio']['geography'][key])
        for action in ('undo','redo'):s.dispatch({'action':action,'version':s.version,'scene':s.selected})
        self.assertEqual(workspace_for(s.project)['selection'],[second['region_id']])

    def test_obsolete_other_commit_or_sequence_gap_rejected(self):
        from studio_sig_protocol import apply_map_intents
        s=self.session();base=s.version
        first={'sequence':1,'action':'view','bbox':[-54,-16,-46,-8]}
        apply_map_intents(s,self.message(s,[first]));s.commit(s.project,record=False)
        before=copy.deepcopy(s.project)
        for entries in ([first,{'sequence':2,'action':'clear_selection'}],[{'sequence':4,'action':'clear_selection'}]):
            with self.assertRaises(ValueError):apply_map_intents(s,self.message(s,entries,base=base))
            self.assertEqual(s.project,before)

    def test_invalid_second_command_and_disk_failure_leave_no_partial_ack(self):
        from studio_sig_protocol import apply_map_intents
        s=self.session();before=copy.deepcopy(s.project);version=s.version
        first={'sequence':1,'action':'view','bbox':[-54,-16,-46,-8]}
        with self.assertRaises(ValueError):apply_map_intents(s,self.message(s,[first,{'sequence':2,'action':'select','region_id':'missing'}]))
        self.assertEqual(s.project,before);self.assertNotIn(s.key+'_sig_clients',s.state)
        with patch('studio_workspace.save_snapshot',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):apply_map_intents(s,self.message(s,[first]))
        self.assertEqual(s.project,before);self.assertEqual(s.version,version)
        self.assertNotIn(s.key+'_sig_clients',s.state)


if __name__=='__main__':unittest.main()
