"""Synthetic permitted polygons: Brazil, Ecuador, holes and multipart."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from studio_home import create_project


def polygon(x,y,span=2):
    return [[[x,y],[x+span,y],[x+span,y+span],[x,y+span],[x,y]]]


def geographic_fixture():
    outer=polygon(-52,-15,4)[0];hole=polygon(-51,-14,1)[0]
    return {'type':'FeatureCollection','features':[
        {'type':'Feature','id':'br.test','properties':{'name':'Brasil sintético','population':0,'signed':-5},'geometry':{'type':'Polygon','coordinates':[outer,hole]}},
        {'type':'Feature','id':12,'properties':{'name':'Provincia ECU sintética','tags':['fixture']},'geometry':{'type':'Polygon','coordinates':polygon(-79,-2,1)}},
        {'type':'Feature','properties':{'name':'Multipart fuera de ECU'},'geometry':{'type':'MultiPolygon','coordinates':[polygon(-55,-20),polygon(-50,-18,1)]}}]}


class GeographyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.patch=patch('studio_geography.ROOT',Path(self.temp.name)/'geography');self.patch.start()
        self.project=create_project('free',{'id':'custom','width':320,'height':180})
        self.project['studio']['scenes'][-1]['duration']=.1
        self.before=copy.deepcopy(self.project);self.original=geographic_fixture()
        self.content=json.dumps(self.original,ensure_ascii=False,indent=2).encode('utf-8')
        self.provenance={'citation':'Synthetic test, no real administrative borders','license':'CC0 synthetic test','url':''}

    def tearDown(self):self.patch.stop();self.temp.cleanup()

    def imported(self):
        from studio_geography import import_geojson
        return import_geojson(self.project,self.content,'synthetic.geojson',self.provenance)

    def test_import_exact_bytes_attributes_crs_ids_and_idempotence(self):
        from studio_geography import import_geojson,read_source,validate_geography
        document,region=self.imported();registry=document['studio']['geography']
        source=next(iter(registry['sources'].values()))
        self.assertEqual(Path(source['path']).read_bytes(),self.content)
        self.assertEqual(read_source(source),self.original)
        self.assertEqual(source['native_crs'],'OGC:CRS84')
        self.assertEqual(len(registry['regions']),3)
        self.assertEqual(registry['regions'][region]['bbox'],[-52,-15,-48,-11])
        again,same=import_geojson(document,self.content,'different-label.geojson',self.provenance)
        self.assertEqual(again,document);self.assertEqual(same,region)
        self.assertNotIn('coordinates',json.dumps(registry))
        validate_geography(document['studio']);self.assertEqual(self.project,self.before)

    def test_hole_multipart_outside_ecu_and_real_view_scene_export_reopen(self):
        from studio_geography import make_view,attach_view,render_region
        from studio_recovery import save_snapshot,recover_snapshot
        from studio_timeline import PreparedTimeline,export_movie
        from studio_media import AssetFrames
        document,region=self.imported()
        with patch('data.load_values',side_effect=AssertionError('Generic route called ECU raster')),patch('data.boundary',side_effect=AssertionError('Generic route forced ECU boundary')):
            image,bbox=render_region(document,region)
            def pixel(lon,lat):return (int((lon-bbox[0])/(bbox[2]-bbox[0])*image.width),int((bbox[3]-lat)/(bbox[3]-bbox[1])*image.height))
            self.assertEqual(image.getpixel(pixel(-50.5,-13.5))[3],0)
            self.assertEqual(image.getpixel(pixel(-51.5,-14.5))[3],255);image.close()
            for rid in document['studio']['geography']['regions']:
                image,_=render_region(document,rid);self.assertGreater(image.getchannel('A').getextrema()[1],0);image.close()
            document,view=make_view(document,region)
            document,selected=attach_view(document,view,duration=7/30)
            again,reused=attach_view(document,view,duration=7/30)
            self.assertEqual(again,document);self.assertEqual(reused,selected)
            with AssetFrames(document['studio']['media']) as assets:
                rendered=PreparedTimeline(document).frame_at(3,assets=assets);self.assertEqual(rendered.size,(320,180));rendered.close()
            snapshot=Path(self.temp.name)/'saved.json';save_snapshot(snapshot,document)
            reopened,_=recover_snapshot(snapshot);self.assertEqual(reopened,document)
            target=Path(self.temp.name)/'export';target.mkdir();receipt=export_movie(reopened,target/'movie.mp4')
            self.assertTrue((target/'movie.mp4').is_file());self.assertEqual(receipt['geographic_views'][0]['region_id'],region)
        self.assertEqual(document['studio']['calculations'],self.before['studio']['calculations'])
        self.assertEqual(document['studio']['datasets'],self.before['studio']['datasets'])

    def test_invalid_geometry_crs_coordinates_ids_and_metadata_rejected(self):
        from studio_geography import import_geojson
        changes=[lambda g:g.update(crs={'type':'name','properties':{'name':'EPSG:3857'}}),
            lambda g:g['features'][0]['geometry'].update(type='Point',coordinates=[0,0]),
            lambda g:g['features'][0]['geometry'].update(coordinates=[[[179,0],[-179,0],[-179,2],[179,2],[179,0]]]),
            lambda g:g['features'][0]['geometry'].update(coordinates=[[[0,89],[2,89],[2,90],[0,89]]]),
            lambda g:g['features'][0]['geometry'].update(coordinates=[[[0,0],[1,1],[1,0],[0,1],[0,0]]]),
            lambda g:g['features'][0]['geometry'].update(coordinates=[[[0,0],[1,0],[1,1],[0,1]]]),
            lambda g:g['features'][1].update(id='br.test'),lambda g:g['features'][0].update(id=True),
            lambda g:g['features'][0]['geometry'].update(coordinates=[[[False,0],[1,0],[1,1],[False,0]]])]
        for change in changes:
            fixture=geographic_fixture();change(fixture)
            with self.subTest(change=change),self.assertRaises(ValueError):import_geojson(self.project,json.dumps(fixture).encode(),'bad.geojson',self.provenance)
        for content in (b'{"type":"FeatureCollection","type":"Feature","features":[]}',b'{"value":NaN}',b'\xff'):
            with self.assertRaises(ValueError):import_geojson(self.project,content,'bad.geojson',self.provenance)
        for url in ('https://user:secret@example.com/data','https://example.com/?token=secret'):
            with self.assertRaises(ValueError):import_geojson(self.project,self.content,'fixture.geojson',{**self.provenance,'url':url})
        self.assertEqual(self.project,self.before)

    def test_changed_or_missing_source_cannot_reopen_or_export_old_pixels(self):
        from studio_geography import make_view,attach_view
        from studio_timeline import PreparedTimeline
        document,region=self.imported();document,view=make_view(document,region);document,_=attach_view(document,view)
        source=next(iter(document['studio']['geography']['sources'].values()));path=Path(source['path']);old=path.read_bytes()
        path.write_bytes(old+b'changed')
        with self.assertRaises(ValueError):PreparedTimeline(document)
        path.write_bytes(old);path.rename(path.with_suffix('.preserved'))
        with self.assertRaises(ValueError):PreparedTimeline(document)

    def test_commit_undo_redo_and_presentation_do_not_change_source_or_geometry(self):
        from studio_geography import make_view,attach_view
        from studio_workspace import WorkspaceSession
        from studio_project import publish_document,source_projection,workspace_key
        document,region=self.imported();document,view=make_view(document,region);document,selected=attach_view(document,view)
        state={};publish_document(state,self.project);key=workspace_key(self.project)
        session=WorkspaceSession(state,key,source_projection(self.project),store=self.temp.name,canonical=True)
        session.commit(document);state[key+'_selected']=selected
        geo=copy.deepcopy(session.project['studio']['geography']);source=next(iter(geo['sources'].values()));original=Path(source['path']).read_bytes()
        element=next(s for s in document['studio']['scenes'] if s['id']==selected)['elements'][0]
        session.dispatch({'version':session.version,'scene':selected,'action':'canvas','entries':{element['id']:{'x':10,'y':20,'w':180,'h':100}}})
        self.assertEqual(session.project['studio']['geography'],geo)
        session.dispatch({'version':session.version,'scene':selected,'action':'undo'})
        session.dispatch({'version':session.version,'scene':selected,'action':'redo'})
        self.assertEqual(Path(source['path']).read_bytes(),original);self.assertEqual(session.project['studio']['geography'],geo)

    def test_apptest_import_select_save_send_uses_shared_document(self):
        from streamlit.testing.v1 import AppTest
        from types import SimpleNamespace
        from studio_project import publish_document,workspace_key
        def script():
            import streamlit as st
            from studio_project import source_projection,workspace_key,consume_studio_navigation
            from studio_workspace import WorkspaceSession
            from studio_geographic_ui import show_geography
            consume_studio_navigation(st.session_state)
            project=st.session_state['project_document']
            session=WorkspaceSession(st.session_state,workspace_key(project),source_projection(project),canonical=True)
            show_geography(session)
        app=AppTest.from_function(script,default_timeout=20);publish_document(app.session_state,self.project)
        fake=SimpleNamespace(name='synthetic.geojson',getvalue=lambda:self.content)
        with patch('studio_workspace.STORE',Path(self.temp.name)),patch('studio_geographic_ui.st.file_uploader',return_value=fake):
            app.run();self.assertFalse(app.exception)
            app.text_input(key='geographic_citation').input(self.provenance['citation'])
            app.text_input(key='geographic_license').input(self.provenance['license'])
            app.button(key='geographic_import').click().run();self.assertFalse(app.error);self.assertFalse(app.exception)
            key=workspace_key(self.project)+'_geographic_region'
            ids=list(app.session_state['project_document']['studio']['geography']['regions'])
            app.selectbox(key=key).select(ids[2]).run()
            app.button(key='geographic_save_view').click().run();self.assertFalse(app.error);self.assertFalse(app.exception)
            app.button(key='geographic_send').click().run();self.assertFalse(app.error);self.assertFalse(app.exception)
        document=app.session_state['project_document']
        self.assertEqual(document['project_meta']['id'],self.project['project_meta']['id'])
        self.assertEqual(len(document['studio']['geography']['views']),1)
        self.assertEqual(len(document['studio']['timeline']),2)
        self.assertEqual(app.session_state['section'],'Editor')
        self.assertEqual(document['studio']['calculations'],self.before['studio']['calculations'])

    def test_budgets_and_resealed_references_cannot_change_original_region(self):
        from studio_geography import import_geojson,validate_geography,make_view
        for name,limit in [('SOURCE_LIMIT',10),('REGION_LIMIT',2),('COORDINATE_LIMIT',4)]:
            with self.subTest(name=name),patch('studio_geography.'+name,limit),self.assertRaises(ValueError):self.imported()
        document,region=self.imported();document,view=make_view(document,region)
        source=next(iter(document['studio']['geography']['sources'].values()));original=Path(source['path']).read_bytes()
        for change in [lambda g:g['regions'][region].update(bbox=[0,0,1,1]),
                lambda g:g['regions'][region].update(feature_index=1),
                lambda g:g['views'][view].update(display_crs='EPSG:3857'),
                lambda g:g['views'][view].update(bbox=[0,0,1,1]),
                lambda g:next(iter(g['sources'].values())).update(path=str(Path(self.temp.name)/'outside.json'))]:
            changed=copy.deepcopy(document);change(changed['studio']['geography'])
            with self.subTest(change=change),self.assertRaises(ValueError):validate_geography(changed['studio'])
        fixture=geographic_fixture();fixture['features'][0]['id']=1;fixture['features'][1]['id']=1.0
        with self.assertRaises(ValueError):import_geojson(self.project,json.dumps(fixture).encode(),'duplicate.geojson',self.provenance)
        with self.assertRaises(ValueError):import_geojson(self.project,self.content[:-1]+b',"invalid":1e999}','invalid.geojson',self.provenance)
        self.assertEqual(Path(source['path']).read_bytes(),original);self.assertEqual(self.project,self.before)

    def test_geojson_view_preserves_existing_scientific_revision_and_results(self):
        from test_studio_science import scientific_fixture
        from studio_science import generate_scientific_project
        from studio_geography import import_geojson,make_view,attach_view
        source,snapshot=scientific_fixture()
        original=generate_scientific_project(source,snapshot,{'id':'custom','width':320,'height':180})
        frozen={key:copy.deepcopy(original['studio'][key]) for key in ('calculations','datasets')}
        with patch('data.load_values',side_effect=AssertionError('GeoJSON recalculated existing science')):
            document,region=import_geojson(original,self.content,'synthetic.geojson',self.provenance)
            document,view=make_view(document,region);document,_=attach_view(document,view,duration=.1)
        self.assertEqual(document['project_meta'],original['project_meta'])
        for key,value in frozen.items():self.assertEqual(document['studio'][key],value)
        self.assertEqual(document['studio']['scenes'][:-1],original['studio']['scenes'])

    def test_receipt_tracks_actual_retained_map_binding_and_visibility(self):
        from studio_geography import make_view,attach_view,geographic_receipt,validate_geography
        document,region=self.imported();document,view=make_view(document,region);document,selected=attach_view(document,view,duration=.1)
        scene=next(s for s in document['studio']['scenes'] if s['id']==selected);element=scene['elements'][0]
        element['visible']=False
        self.assertEqual(geographic_receipt(document)[0]['visibility'],{element['id']:False})
        element['editor_deleted']=True;self.assertEqual(geographic_receipt(document),[])
        scene['generation']['geographic_view_id']='view.absent'
        with self.assertRaises(ValueError):validate_geography(document['studio'])


if __name__=='__main__':unittest.main()
