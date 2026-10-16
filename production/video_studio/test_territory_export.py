"""Focused presentation regression; synthetic observations, explicit test borders."""
import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image
from test_sig_raster import RasterTests,raster_bytes
from studio_sig_raster import representation,settings,query,zonal
from studio_sig_timelapse import configure,output_frame
from studio_sig_layers import workspace_for,layer_command
from studio_territory import DEFAULT,LEGACY,geometry,recover_insets,boundaries


class TerritoryTests(unittest.TestCase):
    setUp=RasterTests.setUp
    tearDown=RasterTests.tearDown
    pair=RasterTests.pair
    source=RasterTests.source

    def test_resampling_preserves_missing_support_zero_science_and_original_bytes(self):
        p,ids=self.pair();source=self.source(p,ids[0]);before=Path(source['path']).read_bytes()
        scale=settings([source]);samples=[query(source,-78.5,-.5),query(source,-77.5,-1.5)]
        images=[]
        for method in ('nearest','bilinear'):
            image,_=representation(source,scale,size=80,presentation={**LEGACY,'resampling':method})
            images.append(image)
            self.assertEqual(image.getpixel((20,20))[3],255) # valid zero
            self.assertEqual(image.getpixel((60,60))[3],0) # native nodata
        self.assertTrue(np.array_equal(np.asarray(images[0].getchannel('A')),np.asarray(images[1].getchannel('A'))))
        self.assertFalse(np.array_equal(np.asarray(images[0]),np.asarray(images[1])))
        for image in images:image.close()
        self.assertEqual(samples,[query(source,-78.5,-.5),query(source,-77.5,-1.5)])
        self.assertEqual(Path(source['path']).read_bytes(),before)

    def test_geographic_holes_and_coast_apply_after_value_resampling(self):
        p,ids=self.pair();source=self.source(p,ids[0]);scale=settings([source])
        outer=[[-79,0],[-77.2,0],[-77.2,-1.8],[-79,-1.8],[-79,0]]
        hole=[[-78.8,-.2],[-78.6,-.2],[-78.6,-.4],[-78.8,-.4],[-78.8,-.2]]
        payload={'type':'FeatureCollection','features':[{'type':'Feature','geometry':{'type':'Polygon','coordinates':[outer,hole]},'properties':{}}]}
        with patch('studio_territory.boundaries',return_value=({'ADM0':payload,'ADM1':payload},[{'sha256':'test-boundary'}])):
            for method in ('nearest','bilinear'):
                options={**DEFAULT,'resampling':method,'borders':False,'provinces':False}
                image,box=representation(source,scale,size=200,presentation=options)
                mask,_,_=geometry(box,image.size,options)
                alpha=np.asarray(image.getchannel('A'))
                self.assertFalse(((alpha>0)&(np.asarray(mask)==0)).any())
                self.assertEqual(image.getpixel((30,30))[3],0) # geographic hole
                self.assertEqual(image.getpixel((190,30))[3],0) # outside country
                self.assertEqual(image.getpixel((150,150))[3],0) # native nodata
                image.close();mask.close()

    def test_categories_reject_bilinear_and_nearest_keeps_class_colors(self):
        p,ids=self.pair();source=self.source(p,ids[0])
        scale={'kind':'categorical','legend':'Synthetic classes','units':'','classes':[
            {'value':0,'label':'zero','color':'#ff0000'},{'value':-5,'label':'signed','color':'#00ff00'},
            {'value':10,'label':'ten','color':'#0000ff'}]}
        with self.assertRaisesRegex(ValueError,'categorías'):
            representation(source,scale,presentation={**LEGACY,'resampling':'bilinear'})
        image,_=representation(source,scale,size=30,presentation=LEGACY)
        values=np.asarray(image);colors=set(map(tuple,values[values[:,:,3]>0,:3]))
        self.assertEqual(colors,{(255,0,0),(0,255,0),(0,0,255)});image.close()

    def test_territory_and_sampling_change_derivative_identity_keep_old_bundles(self):
        from studio_map_bundles import prepare_geographic_bundle,read_bundle
        from studio_temporal import attach_map_layers,calendar_receipt
        from studio_timeline import PreparedTimeline
        p,ids=self.pair();before=copy.deepcopy(p);hashes=[];old=[]
        with patch('studio_map_bundles.MEDIA_ROOT',Path(self.temp.name)/'media'):
            for options in (LEGACY,{**DEFAULT,'resampling':'nearest'},DEFAULT):
                candidate=configure(p,ids,duration=.2,presentation=options)
                if options['territory']=='view':self.assertEqual(workspace_for(candidate)['view'],workspace_for(p)['view'])
                else:
                    from studio_sig_timelapse import output_frame
                    self.assertEqual(workspace_for(candidate)['view']['bbox'],output_frame(candidate)['bbox'])
                record=prepare_geographic_bundle(candidate,.2);manifest=read_bundle(record)
                hashes.append(record['scientific_identity']);old.append(record)
                self.assertEqual(manifest['geographic_binding']['presentation'],options)
                self.assertFalse(manifest['geographic_binding']['basemap_included'])
                attached=attach_map_layers(candidate,record)
                self.assertEqual(attached['studio']['calculations'],p['studio']['calculations'])
                prepared=PreparedTimeline(attached)
                receipt=calendar_receipt(attached,prepared.rows)[-1]
                self.assertEqual(receipt['geographic_presentation']['presentation'],options)
                if options['territory']=='ecuador':
                    gal=next(e for e in attached['studio']['scenes'][-1]['elements'] if e.get('temporal_binding',{}).get('channel')=='galapagos')
                    self.assertFalse(gal['locked']);self.assertGreater(gal['transform']['width'],0)
                    self.assertTrue(all(o['layers']['galapagos']['state']=='no_coverage' for o in manifest['observations']))
            self.assertEqual(len(set(hashes)),3)
            for record in old:read_bundle(record)
        self.assertEqual(p,before)

    def test_unknown_product_cannot_borrow_chirps_island_values(self):
        p,ids=self.pair();insets,warnings=recover_insets(p,[self.source(p,lid) for lid in ids])
        self.assertEqual(insets,[None,None]);self.assertEqual(len(warnings),2)

    def test_outlines_cannot_create_observations_in_nodata_cells(self):
        p,ids=self.pair();source=self.source(p,ids[0]);scale=settings([source])
        off={**DEFAULT,'borders':False,'provinces':False}
        plain,_=representation(source,scale,size=240,presentation=off)
        outlined,_=representation(source,scale,size=240,presentation=DEFAULT)
        self.assertTrue(np.array_equal(np.asarray(plain.getchannel('A')),np.asarray(outlined.getchannel('A'))))
        plain.close();outlined.close()

    def test_pinned_real_boundaries_declare_crs_and_include_multiple_islands(self):
        from shapely.geometry import shape,box
        payloads,records=boundaries()
        self.assertEqual(len(payloads['ADM1']['features']),24)
        self.assertTrue(all(r['native_crs'].endswith('CRS84') for r in records))
        country=shape(payloads['ADM0']['features'][0]['geometry'])
        islands=country.intersection(box(-92.2,-1.8,-88.8,1.9))
        self.assertGreater(len(islands.geoms),10)

    def test_horizontal_adaptation_reflows_date_legend_and_inset_without_overlap(self):
        from studio_territory import element_regions
        from output_profiles import profile_for
        slots=element_regions(profile_for({'id':'youtube'}),{'continent':{'size':[560,720]},'galapagos':{'size':[140,152]}})
        def overlaps(a,b):
            return a['x']<b['x']+b['width'] and b['x']<a['x']+a['width'] and a['y']<b['y']+b['height'] and b['y']<a['y']+a['height']
        keys=('continent','galapagos','date','legend_static','title','source')
        for i,key in enumerate(keys):
            for other in keys[i+1:]:self.assertFalse(overlaps(slots[key],slots[other]),(key,other))


if __name__=='__main__':unittest.main()
