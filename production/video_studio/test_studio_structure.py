"""Whole-structure proposals preserve immutable results and human choices."""
import copy
import unittest
from unittest.mock import patch
from test_studio_science import scientific_fixture
from studio_science import generate_scientific_project


class StructureTests(unittest.TestCase):
    def project(self):
        source,snapshot = scientific_fixture()
        from visualization_ui import scientific_identity
        snapshot['scientific_identity']=scientific_identity(source)
        return generate_scientific_project(source,snapshot,{'id':'custom','width':320,'height':180})

    def test_proposal_is_pure_preserves_selected_edits_and_archives_replaced_scenes(self):
        from studio_science import propose_structure, apply_structure
        project = self.project()
        metric = next(s for s in project['studio']['scenes'] if s.get('generation',{}).get('role')=='metric')
        metric['name']='Human title'; metric['duration']=.2
        before=copy.deepcopy(project)
        with patch('data.load_values',side_effect=AssertionError('Recalculated')):
            proposal=propose_structure(project,theme='Ecuador Vivo')
            self.assertEqual(project,before)
            self.assertTrue(next(c for c in proposal['changes'] if c['id']==metric['id'])['modified'])
            self.assertEqual(apply_structure(project,proposal,'preserve'),before)
            accepted=apply_structure(project,proposal,'replace',preserve_ids=[metric['id']])
        self.assertIn(metric['id'],accepted['studio']['timeline'])
        self.assertEqual(accepted['studio']['calculations'],project['studio']['calculations'])
        self.assertEqual(accepted['studio']['datasets'],project['studio']['datasets'])
        self.assertTrue(set(before['studio']['timeline']).issubset({s['id'] for s in accepted['studio']['scenes']}))
        self.assertEqual(accepted['studio']['structure_history'][-1]['timeline'],before['studio']['timeline'])

    def test_stale_and_forged_proposals_are_rejected(self):
        from studio_science import propose_structure, apply_structure
        project=self.project(); proposal=propose_structure(project)
        changed=copy.deepcopy(project); changed['name']='Another edit'
        with self.assertRaises(ValueError): apply_structure(changed,proposal,'replace')
        proposal['after']['scenes'][1]['elements']=[]
        with self.assertRaises(ValueError): apply_structure(project,proposal,'replace')

    def test_manual_addition_is_preserved_by_explicit_choice(self):
        from studio_science import propose_structure, apply_structure
        from studio_templates import template_scene
        from output_profiles import profile_for
        project=self.project()
        manual=template_scene('quote',profile_for(project['studio']['output_profile']))
        project['studio']['scenes'].append(manual)
        project['studio']['timeline'].insert(1,manual['id'])
        proposal=propose_structure(project)
        result=apply_structure(project,proposal,'replace',preserve_ids=[manual['id']])
        self.assertEqual(result['studio']['timeline'][1],manual['id'])
        self.assertEqual(next(s for s in result['studio']['scenes'] if s['id']==manual['id']),manual)

    def test_durable_restore_and_canonical_undo_redo_keep_results(self):
        import tempfile
        from studio_science import propose_structure,apply_structure,restore_structure
        from studio_workspace import WorkspaceSession
        with tempfile.TemporaryDirectory() as store:
            state={}; session=WorkspaceSession(state,'structure',self.project(),store=store,canonical=True)
            original=copy.deepcopy(session.project)
            session.commit(apply_structure(session.project,propose_structure(session.project),'replace'))
            accepted=copy.deepcopy(session.project)
            self.assertNotEqual(accepted['studio']['timeline'],original['studio']['timeline'])
            self.assertEqual(restore_structure(accepted)['studio']['timeline'],original['studio']['timeline'])
            session.dispatch({'action':'undo','version':session.version,'scene':session.selected})
            self.assertEqual(session.project['studio']['timeline'],original['studio']['timeline'])
            session.dispatch({'action':'redo','version':session.version,'scene':session.selected})
            self.assertEqual(session.project['studio']['timeline'],accepted['studio']['timeline'])
            self.assertEqual(session.project['studio']['calculations'],original['studio']['calculations'])

    def test_invalid_preservation_and_duplicate_slots_are_explicit(self):
        from studio_science import propose_structure,apply_structure
        project=self.project()
        duplicate=copy.deepcopy(project['studio']['scenes'][1]); duplicate['id']='scene.duplicate'
        project['studio']['scenes'].append(duplicate); project['studio']['timeline'].append(duplicate['id'])
        proposal=propose_structure(project)
        self.assertIsNone(proposal['changes'][-1]['replacement_id'])
        with self.assertRaises(ValueError): apply_structure(project,proposal,'replace',preserve_ids=['missing'])

    def test_real_summary_receipt_pointer_survives_attachment_and_restoration(self):
        from studio_science import restored_snapshot,propose_structure
        source,snapshot=scientific_fixture()
        from visualization_ui import scientific_identity
        snapshot['scientific_identity']=scientific_identity(source)
        for result in snapshot['results'].values():
            result['provenance']['source_records_ref']='source_records'
        project=generate_scientific_project(source,snapshot,{'id':'youtube'})
        self.assertEqual(restored_snapshot(project),snapshot)
        self.assertTrue(propose_structure(project)['changes'])
        project['start']='2025-01-02'
        with self.assertRaisesRegex(ValueError,'Cambió la fuente'): propose_structure(project)


if __name__=='__main__': unittest.main()
