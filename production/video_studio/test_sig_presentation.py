"""Presentation-only contracts: synthetic data, no climate claims."""
import asyncio,base64,copy,io,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image
from rasterio.transform import from_origin
import test_sig_raster as fixtures
from test_sig_raster import raster_bytes
from studio_sig_raster import add_raster,representation,settings,LEGACY_PALETTE
from studio_sig_layers import workspace_for,map_payload
from studio_sig_timelapse import configure,output_frame
from studio_territory import DEFAULT


class PresentationTests(unittest.TestCase):
    setUp=fixtures.RasterTests.setUp
    tearDown=fixtures.RasterTests.tearDown
    source=fixtures.RasterTests.source

    def series(self):
        p=self.project;ids=[]
        for n in range(3):
            p,lid=add_raster(p,raster_bytes(np.arange(800).reshape(20,40)+n,transform=from_origin(-94,5,.5,.5)),
                'synthetic'+str(n)+'.tif',self.provenance,observed_date=f'2024-09-0{n+1}',variable='Temperatura',units='°C',semantics='temperature')
            ids.append(lid)
        return p,ids

    def test_live_and_lazy_images_share_polygon_palette_bbox_and_sampling(self):
        from types import SimpleNamespace
        from studio_delivery import raster_response
        p,ids=self.series();p=configure(p,ids[:2],presentation={**DEFAULT,'territory':'province','province':'Napo'})
        payload=map_payload(p);records={r['id']:r for r in payload['layers']}
        current=records[ids[0]]
        self.assertFalse(records[ids[2]]['visible']) # unrelated product cannot shine through NoData
        self.assertTrue(workspace_for(p)['layers'][ids[2]]['visible']) # canonical visibility retained
        self.assertEqual(current['bbox'],output_frame(p)['bbox'])
        self.assertEqual(current['presentation']['resampling'],'bilinear')
        self.assertEqual(current['scale']['palette'],settings([self.source(p,i) for i in ids[:2]])['palette'])
        reply=asyncio.run(raster_response(SimpleNamespace(path_params={'token':current['playback_url'].split('/')[-1]})))
        self.assertEqual(reply.status_code,200)
        self.assertEqual(reply.body,base64.b64decode(current['image'].split(',')[1]))
        with Image.open(io.BytesIO(reply.body)) as image:
            from studio_territory import geometry
            mask,_,_=geometry(current['bbox'],image.size,current['presentation'])
            with mask:self.assertFalse(((np.asarray(image.getchannel('A'))>0)&(np.asarray(mask)==0)).any())
        self.assertEqual(reply.headers['X-Ecuador-Observation-Date'],'2024-09-01')

    def test_national_live_inset_uses_same_original_date_and_not_mainland(self):
        p,ids=self.series();p=configure(p,ids[:2],presentation=DEFAULT)
        records=map_payload(p)['layers'];current=records[0]
        self.assertIn('playback_inset_url',current);self.assertIn('inset_image',current)
        from studio_delivery import _rasters
        record=_rasters[current['playback_inset_url'].split('/')[-1]]
        self.assertEqual(record['source'],self.source(p,ids[0]))
        self.assertEqual(record['presentation'],DEFAULT)
        self.assertLess(record['box'][2],-88)

    def test_geometry_cache_is_immutable_and_matches_uncached_render(self):
        from studio_sig_raster import _display_geometry,_GEOMETRY
        from studio_territory import boundaries,geometry
        from maqueta import paint_map_outline
        box=[-82,-6,-74,3];size=(180,200);records=boundaries()[1]
        _GEOMETRY.clear()
        a,b=_display_geometry(box,size,DEFAULT,records)
        mask,rings,provinces=geometry(box,size,DEFAULT)
        ink=paint_map_outline(size,rings,provinces,province_color=(90,125,142,200))
        with a,b,mask,ink:
            self.assertEqual(a.tobytes(),mask.tobytes());self.assertEqual(b.tobytes(),ink.tobytes())
            a.paste(0,(0,0,a.width,a.height));b.paste((0,0,0,0),(0,0,b.width,b.height))
        c,d=_display_geometry(box,size,DEFAULT,records)
        with c,d:self.assertEqual(c.getextrema(),(0,255));self.assertGreater(d.getchannel('A').getextrema()[1],0)

    def test_social_template_reuses_sealed_media_and_keeps_user_layout(self):
        from studio_home import create_project
        from studio_sig_transfer import transfer_series
        from studio_map_bundles import read_bundle
        p,ids=self.series();p['studio']['output_profile']={'id':'tiktok'}
        p=configure(p,ids[:2],duration=.2,presentation=DEFAULT)
        with patch('studio_map_bundles.MEDIA_ROOT',Path(self.temp.name)/'media'):
            sent=transfer_series(p);scene=sent['studio']['scenes'][-1]
            self.assertEqual(scene['series_template'],'map')
            title=next(e for e in scene['elements'] if e.get('template_key')=='title')
            # Move an editable element, rather than altering science or dates.
            title['transform']['x']+=7;title['style']['text']='Mi título';title['visible']=False
            previous=copy.deepcopy(title);asset=sent['studio']['sig_map_transfer']['asset_id']
            with patch('studio_sig_transfer.prepare_geographic_bundle',side_effect=AssertionError('Unchanged data must reuse bundle')):
                again=transfer_series(sent)
            same=next(e for e in again['studio']['scenes'][-1]['elements'] if e['id']==title['id'])
            self.assertEqual(same['transform'],previous['transform']);self.assertEqual(same['style']['text'],'Mi título');self.assertFalse(same['visible'])
            self.assertEqual(again['studio']['sig_map_transfer']['asset_id'],asset)
            self.assertEqual(again['studio']['calculations'],p['studio']['calculations'])
            self.assertEqual(read_bundle(again['studio']['media'][asset])['units'],'°C')

    def test_long_calendar_does_not_evict_its_first_playback_date(self):
        from studio_delivery import register_raster_display,_rasters
        p,ids=self.series();source=self.source(p,ids[0]);scale=settings([source])
        first=None
        for day in range(400):
            # Capability identity fixture only; no synthetic source is rendered.
            current={**source,'name':'Fixture capability '+str(day)}
            token=register_raster_display(current,scale,box=[-82,-6,-74,3],presentation=DEFAULT).split('/')[-1]
            if first is None:first=token
        self.assertIn(first,_rasters)

    def test_metadata_and_hash_cache_keep_month_while_native_revision_is_unchanged(self):
        import studio_sig_raster as raster
        p=self.project;sources=[]
        for day in range(30):
            p,lid=add_raster(p,raster_bytes([[day]]),'Day '+str(day),self.provenance,
                observed_date=f'2024-09-{day+1:02d}',variable='Fixture',units='unit')
            sources.append(self.source(p,lid))
        raster._CACHE.clear();raster._DIGESTS.clear()
        with patch.object(raster,'metadata',wraps=raster.metadata) as meta,patch.object(raster,'digest',wraps=raster.digest) as digest:
            for _ in range(3):
                for source in sources:raster.verify_source(source)
            self.assertEqual(meta.call_count,30);self.assertEqual(digest.call_count,30)
            # A filesystem revision change forces another byte verification;
            # caching must not accept data solely because its name is the same.
            path=Path(sources[0]['path']);original=path.read_bytes()
            import os
            previous=path.stat().st_mtime_ns
            os.utime(path,ns=(path.stat().st_atime_ns,previous+1_000_000_000))
            raster.verify_source(sources[0])
            self.assertEqual(digest.call_count,31)
            self.assertEqual(path.read_bytes(),original)


if __name__=='__main__':unittest.main()
