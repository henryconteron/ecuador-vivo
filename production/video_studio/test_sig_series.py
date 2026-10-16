"""Regression: legacy documents and generic dated sources, not real climate data."""
import copy,hashlib,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import test_sig_raster as fixtures
from test_sig_raster import raster_bytes
from studio_sig_raster import add_raster,query
from studio_sig_layers import workspace_for
from studio_sig_timelapse import configure,output_frame


class SeriesTests(unittest.TestCase):
    setUp=fixtures.RasterTests.setUp
    tearDown=fixtures.RasterTests.tearDown
    def test_empty_document_is_readable_and_configure_is_actionable(self):
        from studio_sig_series import series_groups
        self.assertEqual(series_groups(self.project),[])
        with self.assertRaisesRegex(ValueError,'al menos dos'):configure(self.project,[])
        with self.assertRaisesRegex(ValueError,'ráster'):configure(self.project,['unknown','missing'])
        self.assertEqual(self.project,self.before)

    def test_distinct_products_and_variables_are_not_mixed(self):
        from studio_sig_series import series_groups
        p=self.project
        for i,(variable,citation) in enumerate([('Temperatura','Product A'),('Viento','Product A'),('Temperatura','Product B')]):
            p,_=add_raster(p,raster_bytes([[i+1]]),'fixture.tif',{**self.provenance,'citation':citation},
                observed_date='2024-09-01',variable=variable,units='unit')
        self.assertEqual(len(series_groups(p)),3)

    def test_multiband_admission_preserves_dates_masks_scaling_and_origin(self):
        from rasterio.io import MemoryFile
        from rasterio.transform import from_origin
        import numpy as np
        from studio_sig_series import admit_download
        with MemoryFile() as memory:
            with memory.open(driver='GTiff',width=2,height=1,count=2,dtype='float32',crs='EPSG:4326',transform=from_origin(-79,0,1,1),nodata=-999) as ds:
                ds.write(np.array([[[0,-999]],[[20,-2]]],dtype='float32'));ds.scales=(.1,.1);ds.offsets=(5,5)
            content=memory.read()
        path=Path(self.temp.name)/'download.tif';path.write_bytes(content)
        downloaded={'provider':'NASA POWER','variable':'Test temperature','units':'°C','profile_kind':'temperature',
            'citation':'NASA POWER test fixture','manifest':{'source_url':'https://power.larc.nasa.gov/','time_standard':'UTC'},
            'entries':[{'path':str(path),'band':i,'date':day,'artifact_sha256':hashlib.sha256(content).hexdigest()} for i,day in enumerate(['2024-09-01','2024-09-02'],1)]}
        p,ids=admit_download(self.project,downloaded)
        sources=[p['studio']['geography']['sources'][workspace_for(p)['layers'][lid]['source_id']] for lid in ids]
        self.assertNotEqual(sources[0]['id'],sources[1]['id'])
        self.assertEqual([s['date'] for s in sources],['2024-09-01','2024-09-02'])
        self.assertEqual(query(sources[0],-78.5,-.5)['value'],5)
        self.assertIsNone(query(sources[0],-77.5,-.5)['value'])
        self.assertAlmostEqual(query(sources[1],-77.5,-.5)['value'],4.8)
        self.assertEqual(admit_download(p,downloaded)[0],p)
        self.assertEqual(self.project,self.before)

    def test_scopes_mask_to_selected_polygon_and_expand_full_bounds(self):
        from studio_territory import validate,DEFAULT,geometry,territory_bbox,province_names
        self.assertEqual(len(province_names()),24)
        p=self.project;ids=[]
        for n,day in enumerate(['2024-09-01','2024-09-02']):
            p,lid=add_raster(p,raster_bytes([[n+1]]),'fixture.tif',self.provenance,observed_date=day,variable='Test',units='unit');ids.append(lid)
        for scope in ['continent','galapagos','province']:
            options={**DEFAULT,'territory':scope,**({'province':'Napo'} if scope=='province' else {})}
            validate(options);q=configure(p,ids,presentation=options);frame=output_frame(q);box=territory_bbox(options)
            self.assertLessEqual(frame['bbox'][0],box[0]);self.assertGreaterEqual(frame['bbox'][2],box[2])
            mask,_,_=geometry(frame['bbox'],(256,256),options)
            with mask:
                self.assertEqual(mask.getextrema(),(0,255))
        with self.assertRaises(ValueError):validate({**DEFAULT,'territory':'province','province':'Not a province'})

    def test_empty_panel_opens_without_mutation(self):
        from streamlit.testing.v1 import AppTest
        script='''from types import SimpleNamespace
from studio_home import create_project
from studio_sig_raster_ui import timelapse_panel
import streamlit as st
st.session_state.setdefault('document',create_project('free',{'id':'tiktok'}))
timelapse_panel(SimpleNamespace(project=st.session_state.document,key='test',state=st.session_state))
'''
        app=AppTest.from_string(script).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertNotIn('geography',app.session_state.document['studio'])
        self.assertTrue(any('Fuente' in w.label for w in app.selectbox))

    def test_generic_temperature_and_wind_transfer_without_rain_labels(self):
        from studio_sig_transfer import transfer_series
        from studio_territory import DEFAULT
        from studio_timeline import PreparedTimeline
        from rasterio.transform import from_origin
        for variable,units,semantics in [('Temperatura','°C','temperature'),('Viento','m/s','scalar')]:
            p=self.project;ids=[]
            for value,day in ([(20,'2024-09-01'),(21,'2024-09-02')] if semantics=='temperature' else [(2,'2024-09-01'),(3,'2024-09-02')]):
                p,lid=add_raster(p,raster_bytes([[value]*20]*20,transform=from_origin(-81,2,.4,.4)),variable+day+'.tif',
                    {**self.provenance,'citation':'NASA POWER synthetic '+variable},observed_date=day,variable=variable,units=units,semantics=semantics);ids.append(lid)
            p=configure(p,ids,duration=.2,presentation={**DEFAULT,'territory':'province','province':'Napo'})
            with patch('studio_map_bundles.MEDIA_ROOT',Path(self.temp.name)/('media-'+variable)):
                q=transfer_series(p);prepared=PreparedTimeline(q)
                self.assertEqual(q['studio']['calculations'],p['studio']['calculations'])
                text=' '.join(e.get('style',{}).get('text','') for e in q['studio']['scenes'][-1]['elements'])
                self.assertIn(variable,text);self.assertNotIn('CHIRPS',text)
                self.assertEqual(len(q['studio']['timeline']),1)
                with prepared.frame_at(0) as frame:self.assertEqual(frame.size,(320,180))
                again=transfer_series(q);self.assertEqual(len(again['studio']['timeline']),1)

    def test_panel_applies_province_profile_and_dates_together(self):
        from streamlit.testing.v1 import AppTest
        p=self.project
        for day,value in [('2024-09-01',1),('2024-09-02',2),('2024-09-03',3)]:
            p,_=add_raster(p,raster_bytes([[value]]),'test'+day+'.tif',self.provenance,observed_date=day,variable='Test',units='unit')
        app=AppTest.from_string('''import streamlit as st
from types import SimpleNamespace
from studio_sig_raster_ui import timelapse_panel
def commit(candidate): st.session_state.document=candidate
timelapse_panel(SimpleNamespace(project=st.session_state.document,key='test',state=st.session_state,commit=commit))
''')
        app.session_state.document=p;app.run(timeout=30)
        self.assertFalse(app.exception)
        app.selectbox(key='sig_export_territory').select('province').run()
        app.selectbox(key='sig_export_province').select('Napo')
        app.selectbox(key='sig_timelapse_profile').select('tiktok')
        app.button(key='sig_timelapse_apply').click().run(timeout=30)
        self.assertFalse(app.exception)
        result=app.session_state.document
        self.assertEqual(workspace_for(result)['raster_time']['presentation']['province'],'Napo')
        self.assertEqual(result['studio']['output_profile'],{'id':'tiktok'})
        self.assertEqual(len(workspace_for(result)['raster_time']['layers']),3)

    def test_previous_sealed_rain_video_does_not_block_new_sig_selection(self):
        from studio_sig_transfer import transfer_series,validate_transfer
        from studio_territory import DEFAULT
        from rasterio.transform import from_origin
        p=self.project;ids=[]
        for value,day in [(1,'2024-09-01'),(2,'2024-09-02')]:
            provenance={**self.provenance,'url':'https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/2024/chirps-v2.0.'+day.replace('-','.')+'.tif.gz'}
            p,lid=add_raster(p,raster_bytes([[value]*20]*20,transform=from_origin(-81,2,.4,.4)),'Rain test'+day+'.tif',provenance,
                observed_date=day,variable='Rain fixture',units='mm/día',semantics='precipitation');ids.append(lid)
        p=configure(p,ids,duration=.2,cadence='daily',presentation=DEFAULT)
        with patch('studio_map_bundles.MEDIA_ROOT',Path(self.temp.name)/'media-old-rain'):
            sent=transfer_series(p,endcard_duration=.2);validate_transfer(sent)
            new_ids=[]
            for value,day in [(20,'2024-09-01'),(21,'2024-09-02')]:
                sent,lid=add_raster(sent,raster_bytes([[value]*20]*20,transform=from_origin(-81,2,.4,.4)),'Temperature test'+day+'.tif',self.provenance,
                    observed_date=day,variable='Temperature fixture',units='°C',semantics='temperature');new_ids.append(lid)
            prepared=configure(sent,new_ids,duration=.2,presentation={**DEFAULT,'territory':'province','province':'Napo'})
            validate_transfer(prepared)
            new=transfer_series(prepared)
            self.assertEqual(len(new['studio']['timeline']),1)
            self.assertEqual(new['studio']['calculations'],sent['studio']['calculations'])
            back=configure(new,ids,duration=.2,cadence='daily',presentation=DEFAULT)
            again=transfer_series(back,endcard_duration=.2)
            self.assertEqual(len(again['studio']['timeline']),2)


if __name__=='__main__':unittest.main()
