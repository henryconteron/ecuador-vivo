"""Declarative, bounded Blender recipes and owned local jobs."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest


class BlenderRecipeTests(unittest.TestCase):
    def test_malformed_progress_is_safe_and_actionable(self):
        from studio_blender import default_recipe,recipe_identity,job_root,job_status
        with tempfile.TemporaryDirectory() as folder:
            identifier=recipe_identity(default_recipe())+'-preview'
            job=job_root(identifier,Path(folder));job.mkdir(parents=True)
            for value in ([],None,{'state':'running','progress':'oops'}, {'state':'evil','progress':0}):
                (job/'status.json').write_text(json.dumps(value),encoding='utf8')
                self.assertEqual(job_status(identifier,Path(folder))['state'],'missing')

    def test_receipt_cannot_claim_another_frame_count(self):
        from studio_blender import default_recipe,recipe_identity,job_root,verified_product
        with tempfile.TemporaryDirectory() as folder:
            recipe=default_recipe();identifier=recipe_identity(recipe)+'-poster';job=job_root(identifier,Path(folder));job.mkdir(parents=True)
            (job/'request.json').write_text(json.dumps({'recipe':recipe,'mode':'poster'}),encoding='utf8')
            (job/'status.json').write_text('{"state":"complete"}',encoding='utf8')
            files={}
            for name in ('poster.png','scene.blend'):
                (job/name).write_bytes(b'test-only');files[name]=hashlib.sha256(b'test-only').hexdigest()
            receipt={'recipe_sha256':recipe_identity(recipe),'files':files,'frames':999,'fps':30,'size':[640,534],
                'engine':'Blender','version':'4.5.4 LTS'}
            (job/'receipt.json').write_text(json.dumps(receipt),encoding='utf8')
            with self.assertRaises(ValueError):verified_product(identifier,Path(folder))

    def test_defaults_are_bounded_illustration_not_scientific_calculations(self):
        from studio_blender import default_recipe,validate_recipe,recipe_identity
        recipe=default_recipe()
        self.assertEqual(validate_recipe(recipe),recipe)
        self.assertEqual(recipe['model'],'orographic')
        self.assertEqual(recipe['fps'],30)
        self.assertEqual(len(recipe_identity(recipe)),64)
        self.assertNotIn('datasets',recipe)

    def test_recipe_rejects_code_paths_bad_numbers_and_unbounded_duration(self):
        from studio_blender import default_recipe,validate_recipe
        for field,value in [('script','evil.py'),('duration',121),('duration',float('nan')),('yaw',True),('background','red'),('model','upload'),('fps',60)]:
            recipe=default_recipe();recipe[field]=value
            with self.assertRaises(ValueError):validate_recipe(recipe)

    def test_changed_camera_changes_identity_but_recipe_is_not_mutated(self):
        from studio_blender import default_recipe,validate_recipe,recipe_identity
        recipe=default_recipe();before=copy.deepcopy(recipe)
        validate_recipe(recipe)
        changed={**recipe,'yaw':45}
        self.assertNotEqual(recipe_identity(recipe),recipe_identity(changed))
        self.assertEqual(before,recipe)

    def test_job_paths_are_confined_and_missing_engine_is_clear(self):
        from studio_blender import job_root,start_job,default_recipe
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):job_root('../outside',Path(folder))
            with self.assertRaisesRegex(ValueError,'Blender'):
                start_job(default_recipe(),mode='poster',store=Path(folder),executable=Path(folder)/'missing.exe')


if __name__=='__main__':unittest.main()
