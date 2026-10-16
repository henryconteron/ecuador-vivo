import copy
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace


class ResourceActionTests(unittest.TestCase):
    def test_save_scene_creates_reusable_copy_without_changing_video(self):
        from studio_resource_projects import create_resource_project,resource_files,load_resource
        from studio_resource_actions import persist_resource
        project=create_resource_project('Original',{'id':'tiktok'},resource_id='rain_volume')
        before=copy.deepcopy(project)
        with tempfile.TemporaryDirectory() as folder:
            session=SimpleNamespace(project=project,selected=project['studio']['timeline'][0],store=Path(folder))
            path=persist_resource(session,'Mi recurso','Lluvia')
            self.assertEqual(project,before)
            self.assertTrue(path.is_file())
            entries=resource_files(folder)
            self.assertEqual(len(entries),1)
            self.assertEqual(entries[0]['name'],'Mi recurso')
            restored=load_resource(path,folder)
            self.assertEqual(len(restored['studio']['timeline']),1)
            self.assertEqual(restored['project_meta']['resource']['category'],'Lluvia')

    def test_graphic_palette_is_insertable_using_existing_renderer(self):
        from studio_resource_projects import create_resource_project
        from studio_resource_actions import GRAPHIC_ELEMENTS
        from studio_workspace_commands import workspace_command
        from studio_timeline import PreparedTimeline
        for shape in GRAPHIC_ELEMENTS:
            project=create_resource_project('Símbolo',{'id':'instagram_square'})
            sid=project['studio']['timeline'][0]
            project=workspace_command(project,sid,{'action':'add_element','kind':'shape','shape':shape})
            self.assertEqual(project['studio']['scenes'][0]['elements'][0]['style']['shape'],shape)
            image=PreparedTimeline(project,preview_max_side=280).frame_at(0)
            image.close()


if __name__=='__main__':unittest.main()
