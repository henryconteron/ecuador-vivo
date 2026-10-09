"""Persistent editorial groups preserve flat scientific scene elements."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
from streamlit.testing.v1 import AppTest
from studio_editing import new_workspace, duplicate_elements, patch_canvas
from studio_model import validate_scene
from studio_render import render_scene
from studio_ui import canvas_payload
from output_profiles import profile_for


class StudioCompositionTests(unittest.TestCase):
    def test_group_and_ungroup_are_pure_keep_pixels_and_survive_json(self):
        from studio_composition import group_elements
        project=new_workspace({'endcard_enabled':False});scene=project['studio']['scenes'][-1]
        before=copy.deepcopy(project);ids=[e['id'] for e in scene['elements'][:2]]
        grouped=group_elements(project,scene['id'],ids)
        after=grouped['studio']['scenes'][-1];members=after['elements'][:2]
        self.assertEqual(members[0]['group_id'],members[1]['group_id'])
        for old,new in zip(scene['elements'],after['elements']):
            self.assertEqual({k:v for k,v in new.items() if k!='group_id'},old)
        self.assertEqual(project,before)
        profile=profile_for(project['studio']['output_profile'])
        original=render_scene(scene,profile,{})
        self.assertEqual(render_scene(after,profile,{}).tobytes(),original.tobytes())
        payload=canvas_payload(render_scene(after,profile,{}),after,profile)
        self.assertEqual(payload['layers'][0]['group_id'],members[0]['group_id'])
        self.assertEqual(group_elements(json.loads(json.dumps(grouped)),scene['id'],ids[:1],action='ungroup'),project)

    def test_group_rejects_partial_membership_locks_and_unknown_ids(self):
        from studio_composition import group_elements
        project=new_workspace({'endcard_enabled':False});scene=project['studio']['scenes'][-1]
        ids=[e['id'] for e in scene['elements']]
        for selection in ([ids[0]], [ids[0],ids[0]], ['missing',ids[0]]):
            with self.assertRaises(ValueError): group_elements(project,scene['id'],selection)
        grouped=group_elements(project,scene['id'],ids[:2])
        with self.assertRaises(ValueError): group_elements(grouped,scene['id'],[ids[0],ids[-1]])
        grouped['studio']['scenes'][-1]['elements'][0]['locked']=True
        with self.assertRaises(ValueError): group_elements(grouped,scene['id'],ids[:1],action='ungroup')
        invalid=copy.deepcopy(scene);invalid['elements'][0]['group_id']='../bad'
        with self.assertRaises(ValueError): validate_scene(invalid)

    def test_group_copy_uses_new_membership_and_resize_preserves_bindings(self):
        from studio_composition import group_elements
        project=new_workspace({'endcard_enabled':False});scene=project['studio']['scenes'][-1]
        ids=[e['id'] for e in scene['elements'][:2]]
        project=group_elements(project,scene['id'],ids)
        old=project['studio']['scenes'][-1]['elements'][0]['group_id']
        duplicated=duplicate_elements(project,scene['id'],ids)
        clones=duplicated['studio']['scenes'][-1]['elements'][-2:]
        self.assertEqual(clones[0]['group_id'],clones[1]['group_id'])
        self.assertNotEqual(clones[0]['group_id'],old)
        resized=patch_canvas(project,scene['id'],{ids[0]:{'x':80},ids[1]:{'x':80}})
        for element in resized['studio']['scenes'][-1]['elements'][:2]: self.assertEqual(element['group_id'],old)

    def test_group_copy_at_canvas_edge_keeps_relative_offsets(self):
        from studio_composition import group_elements
        project=new_workspace({'endcard_enabled':False});scene=project['studio']['scenes'][-1]
        scene['elements']=scene['elements'][:2]
        scene['elements'][0]['transform']={'x':950,'y':20,'width':130,'height':80}
        scene['elements'][1]['transform']={'x':850,'y':30,'width':120,'height':80}
        ids=[e['id'] for e in scene['elements']]
        grouped=group_elements(project,scene['id'],ids)
        changed=duplicate_elements(grouped,scene['id'],ids)
        clones=changed['studio']['scenes'][-1]['elements'][-2:]
        self.assertEqual(clones[0]['transform']['x']-clones[1]['transform']['x'],100)
        self.assertEqual(clones[0]['transform']['y']-clones[1]['transform']['y'],-10)

    def test_copy_rejects_partial_or_locked_existing_groups(self):
        from studio_composition import group_elements
        project=new_workspace({'endcard_enabled':False});scene=project['studio']['scenes'][-1]
        ids=[e['id'] for e in scene['elements'][:2]]
        grouped=group_elements(project,scene['id'],ids)
        with self.assertRaises(ValueError): duplicate_elements(grouped,scene['id'],ids[:1])
        grouped['studio']['scenes'][-1]['elements'][1]['locked']=True
        with self.assertRaises(ValueError): duplicate_elements(grouped,scene['id'],ids)

    def test_ui_persistent_group_and_undo_without_scientific_reads(self):
        import studio_ui
        project=new_workspace({'endcard_enabled':False});scene=project['studio']['scenes'][-1]
        ids=[e['id'] for e in scene['elements'][:2]]
        script='import sys\nsys.path.insert(0,{!r})\nfrom studio_ui import show_studio\nshow_studio({!r},key="groups")'.format(str(Path(__file__).parent),project)
        with tempfile.TemporaryDirectory() as directory,patch.object(studio_ui,'STORE',Path(directory)),patch('data.load_values',side_effect=AssertionError('No scientific reads')):
            app=AppTest.from_string(script,default_timeout=30).run()
            next(s for s in app.multiselect if s.label=='Elementos del grupo').set_value(ids).run()
            next(b for b in app.button if b.label=='Agrupar elementos').click().run()
            self.assertFalse(app.exception);self.assertFalse(app.error)
            doc=app.session_state['groups_document']
            members=doc['studio']['scenes'][-1]['elements'][:2]
            self.assertEqual(members[0]['group_id'],members[1]['group_id'])
            next(b for b in app.button if b.label=='Deshacer').click().run()
            self.assertEqual(app.session_state['groups_document'],project)


if __name__=='__main__': unittest.main()
