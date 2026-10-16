import copy
import unittest
from studio_home import create_project
from studio_blender import default_recipe


class BlenderSceneTests(unittest.TestCase):
    def test_vertical_editorial_elements_keep_bottom_and_right_clear(self):
        from studio_blender_scene import create_scene_project
        asset={'kind':'video','path':'local.mp4','sha256':'a'*64,'size':[1080,900],'duration':10.,'name':'Orography'}
        scene=create_scene_project(default_recipe(),asset,'job-id','La montaña no fabrica agua',{'id':'tiktok'})['studio']['scenes'][0]
        for element in scene['elements']:
            box=element['transform']
            self.assertLessEqual(box['x']+box['width'],1080*.861)
            self.assertLessEqual(box['y']+box['height'],1920*.86)

    def test_recipe_and_text_remain_editable_without_scientific_results(self):
        from studio_blender_scene import create_scene_project
        asset={'kind':'video','path':'verified-local.mp4','sha256':'a'*64,'size':[1080,900],'duration':10.,'name':'Orography'}
        project=create_scene_project(default_recipe(),asset,'job-id','¿Por qué llueve junto a la montaña?',{'id':'tiktok'})
        scene=project['studio']['scenes'][0]
        self.assertEqual(scene['resource']['blender']['recipe'],default_recipe())
        self.assertEqual(project['studio']['calculations'],{})
        self.assertEqual(project['source'],'local')
        self.assertEqual(project['variable'],'Ilustración 3D')
        self.assertEqual(project['citation'],'Base conceptual: NOAA / NWS')
        self.assertEqual((project['start'],project['end']),('',''))
        self.assertEqual(len([e for e in scene['elements'] if e['type']=='video']),1)
        self.assertTrue([e for e in scene['elements'] if e['type']=='text'])
        self.assertTrue(all(not e['locked'] for e in scene['elements']))

    def test_recipe_regeneration_keeps_manual_composition_and_other_scenes(self):
        from studio_blender_scene import create_scene_project,replace_render
        asset={'kind':'video','path':'local.mp4','sha256':'a'*64,'size':[1080,900],'duration':10.,'name':'Orography'}
        project=create_scene_project(default_recipe(),asset,'job-id','Montaña',{'id':'youtube'})
        scene=project['studio']['scenes'][0]
        scene['elements'][0]['transform']['x']=110
        before=copy.deepcopy(project)
        new_asset={**asset,'sha256':'b'*64,'path':'new.mp4'}
        changed={**default_recipe(),'yaw':40.}
        result=replace_render(project,scene['id'],changed,new_asset,'new-id')
        self.assertEqual(project,before)
        self.assertEqual(result['studio']['scenes'][0]['elements'][0]['transform'],scene['elements'][0]['transform'])
        self.assertEqual(result['studio']['scenes'][0]['resource']['blender']['recipe']['yaw'],40.)


if __name__=='__main__':unittest.main()
