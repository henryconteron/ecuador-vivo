import base64,copy,io,json,tempfile,unittest
from pathlib import Path
from PIL import Image
from unittest.mock import patch

class ResourceToolImportTests(unittest.TestCase):
    def test_real_asset_roundtrip_renders_in_both_social_and_landscape_profiles(self):
        from studio_resource_tool_import import import_tool_artifact
        from studio_media import AssetFrames
        from studio_model import validate_studio
        from studio_render import render_scene
        from output_profiles import profile_for
        from studio_resource_projects import create_resource_project
        _,payload=self.fixture()
        with tempfile.TemporaryDirectory() as folder,patch('storyboard.MEDIA_ROOT',Path(folder)):
            for preset in ('tiktok','youtube'):
                project=create_resource_project('Figura',{'id':preset})
                result=import_tool_artifact(project,project['studio']['timeline'][0],payload)
                restored=json.loads(json.dumps(result));validate_studio(restored['studio'])
                self.assertEqual(restored['studio']['scenes'][0]['elements'][-1]['source_document']['recipe'],payload['recipe'])
                with AssetFrames(restored['studio']['media']) as assets:
                    frame=render_scene(restored['studio']['scenes'][0],profile_for({'id':preset}),{},assets=assets.images,time=3)
                    self.assertEqual(frame.size,(1080,1920) if preset=='tiktok' else (1920,1080))
                    self.assertGreater(sum(count for count,pixel in frame.getcolors(frame.width*frame.height) if pixel[:3]==(0,255,255)),100)
                    frame.close()
    def fixture(self):
        from studio_resource_projects import create_resource_project
        data=io.BytesIO();Image.new('RGBA',(120,80),'cyan').save(data,format='PNG')
        return create_resource_project('Mi figura',{'id':'youtube'}),{'tool':'vector','png':'data:image/png;base64,'+base64.b64encode(data.getvalue()).decode(),'recipe':{'objects':[]}}
    def test_tool_object_keeps_recipe_and_original_and_can_replace_without_moving_it(self):
        from studio_resource_tool_import import import_tool_artifact
        project,payload=self.fixture();before=copy.deepcopy(project)
        with patch('studio_resource_tool_import.import_asset',return_value={'kind':'image','sha256':'a'*64,'size':[120,80]}) as imported:
            result=import_tool_artifact(project,project['studio']['timeline'][0],payload)
            element=result['studio']['scenes'][0]['elements'][-1];self.assertEqual(element['source_document']['recipe'],payload['recipe']);self.assertEqual(project,before)
            transform=copy.deepcopy(element['transform'])
            updated=import_tool_artifact(result,result['studio']['timeline'][0],{**payload,'element_id':element['id']})
            self.assertEqual(len(updated['studio']['scenes'][0]['elements']),1);self.assertEqual(updated['studio']['scenes'][0]['elements'][0]['transform'],transform)
    def test_unknown_tool_invalid_png_and_excess_recipe_rejected_before_storage(self):
        from studio_resource_tool_import import import_tool_artifact
        project,payload=self.fixture()
        with patch('studio_resource_tool_import.import_asset') as imported:
            for bad in [{**payload,'tool':'execute'},{**payload,'png':'data:text/html;base64,YQ=='},{**payload,'recipe':{'text':'x'*2_100_000}}]:
                with self.assertRaises(ValueError):import_tool_artifact(project,project['studio']['timeline'][0],bad)
            self.assertFalse(imported.called)
