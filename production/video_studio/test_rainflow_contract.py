"""Physical contract examples with known answers; no provider downloads."""
import copy,datetime as dt,unittest
from unittest.mock import patch
import numpy as np
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
from variables import aggregate_intervals,resolve_aggregation
from data import _polygon_stats
from endcard import SummaryAccumulator
from visualizations import VisualizationSpec,visualization_geometry


def contract(measurement='interval_amount',operation='sum',units='mm',family='precipitation'):
    return dict(variable=family,family=family,measurement=measurement,operation=operation,units=units,spatial_support='native cell')


def interval(start,end,value,units='mm'):
    return dict(start=start,end=end,value=value,units=units)


class RainContractTests(unittest.TestCase):
    def test_accumulation_zero_and_absence(self):
        rows=[interval('2024-01-01','2024-01-02',0),interval('2024-01-02','2024-01-03',None),interval('2024-01-03','2024-01-04',5)]
        result=aggregate_intervals(rows,contract())
        self.assertEqual(result['value'],5);self.assertEqual(result['valid_intervals'],2)
        self.assertAlmostEqual(result['duration_coverage'],2/3)

    def test_rate_integrates_duration(self):
        rows=[interval('2024-01-01T00:00','2024-01-01T02:00',3,'mm/h'),interval('2024-01-01T02:00','2024-01-01T03:00',2,'mm/h')]
        self.assertEqual(aggregate_intervals(rows,contract('rate','integral','mm/h'))['value'],8)

    def test_temperature_duration_weights(self):
        rows=[interval('2024-01-01','2024-01-02',10,'°C'),interval('2024-01-02','2024-01-04',20,'°C')]
        self.assertAlmostEqual(aggregate_intervals(rows,contract('interval_mean','duration_weighted_mean','°C','temperature'))['value'],50/3)
        with self.assertRaises(ValueError):aggregate_intervals(rows,contract('interval_mean','sum','°C','temperature'))

    def test_duplicate_and_overlap_rejected(self):
        a=interval('2024-01-01','2024-01-03',2)
        for b in (a,interval('2024-01-02','2024-01-04',1)):
            with self.assertRaises(ValueError):aggregate_intervals([a,b],contract())

    def test_incompatible_units_rejected(self):
        with self.assertRaises(ValueError):aggregate_intervals([interval('2024-01-01','2024-01-02',5,'°C')],contract())
        with self.assertRaises(ValueError):aggregate_intervals([interval('2024-01-01','2024-01-02',5,'°C')],contract(units='°C'))

    def test_leap_year_and_gaps(self):
        start=dt.date(2024,1,1)
        rows=[interval((start+dt.timedelta(days=i)).isoformat(),(start+dt.timedelta(days=i+1)).isoformat(),1) for i in range(366)]
        result=aggregate_intervals(rows,contract());self.assertEqual(result['value'],366);self.assertFalse(result['gaps'])
        self.assertIn('2024-02-29',[r['start'] for r in rows])
        self.assertTrue(aggregate_intervals(rows[:40]+rows[41:],contract())['gaps'])

    def test_unknown_categories_directions_require_method(self):
        for family in ('category','wind_direction'):
            with self.assertRaises(ValueError):aggregate_intervals([],contract('interval_mean','duration_weighted_mean','degrees',family))
        for p in ({'variable':'desconocida','units':'widgets'},{'variable':'Precipitación','units':'mm/h','cadence':'Diaria'}):
            with self.assertRaises(ValueError):resolve_aggregation(p)

    def test_empty_intervals_preserve_absence(self):
        self.assertIsNone(aggregate_intervals([],contract())['value'])
        self.assertIsNone(aggregate_intervals([interval('2024-01-01','2024-01-02',None)],contract())['value'])

    def test_native_zonal_weighting_and_no_centres(self):
        values=np.array([[10,10],[0,-9999]],dtype='float32')
        feature=lambda name,coords:dict(type='Feature',properties={'name':name},geometry={'type':'Polygon','coordinates':[coords]})
        full=feature('domain',[(0,0),(2,0),(2,60),(0,60),(0,0)])
        small=feature('tiny',[(0,0),(.1,0),(.1,.1),(0,.1),(0,0)])
        with MemoryFile() as memory:
            with memory.open(driver='GTiff',width=2,height=2,count=1,dtype='float32',crs='EPSG:4326',transform=from_origin(0,60,1,30),nodata=-9999) as ds:
                ds.write(values,1);rows=_polygon_stats(ds,1,[full,small],include_empty=True)
        w1=np.cos(np.radians(45));w2=np.cos(np.radians(15))
        self.assertAlmostEqual(rows['domain']['mean'],20*w1/(2*w1+w2),places=6)
        self.assertEqual(rows['domain']['min'],0);self.assertEqual(rows['domain']['valid_pixels'],3)
        self.assertIsNone(rows['tiny']['mean'])

    def test_ranking_all_24_including_missing(self):
        rows=[dict(name=f'Provincia {i}',value=i if i<23 else None) for i in range(24)]
        registry={'r':{'id':'r','variable':'Provincia','units':'mm','rows':rows,'provenance':{}}}
        first=visualization_geometry(VisualizationSpec('ranking',{'result_id':'r','field':'rows'},top_n=12,include_missing=True),(registry),(480,600))
        last=visualization_geometry(VisualizationSpec('ranking',{'result_id':'r','field':'rows'},top_n=12,offset=12,include_missing=True),registry,(480,600))
        self.assertEqual(len(first['marks'])+len(last['marks']),24);self.assertIsNone(last['marks'][-1]['value'])

    def test_ranking_pages_share_axis_without_clipping(self):
        registry={'r':{'id':'r','variable':'Provincia','units':'mm','rows':[dict(name=str(i),value=i) for i in range(24)],'provenance':{}}}
        binding={'result_id':'r','field':'rows'}
        pages=[visualization_geometry(VisualizationSpec('ranking',binding,style={'axis_domain':[0,23]},offset=i,top_n=12),registry,(480,600)) for i in (0,12)]
        self.assertEqual(pages[0]['maximum'],pages[1]['maximum'])
        with self.assertRaises(ValueError):visualization_geometry(VisualizationSpec('ranking',binding,style={'axis_domain':[0,1]}),registry,(480,600))

    def test_geographic_registry_accepts_366_raster_references(self):
        from studio_geography import validate_geography
        sources={}
        for i in range(366):
            digest=f'{i:064x}';sid='source.'+digest
            sources[sid]={'id':sid,'sha256':digest,'type':'raster','bytes':65536}
        studio={'geography':{'version':1,'sources':sources,'regions':{},'views':{}},'scenes':[],'media':{}}
        # Only registry budgets: no invented observations are opened as files.
        with patch('studio_sig_raster.verify_source') as verify:
            validate_geography(studio);self.assertEqual(verify.call_count,366)
        for source in sources.values():source['bytes']=1024*1024
        with patch('studio_sig_raster.verify_source'),self.assertRaisesRegex(ValueError,'256 MiB'):
            validate_geography(studio)

    def test_island_calendar_mismatch_rejected_before_reading_data(self):
        from studio_sig_summary import summarize_series,rainfall_contract
        s={'date':'2024-01-01','variable':'Precipitación','units':'mm/día','semantics':'precipitation',
           'provenance':{'url':'https://data.chc.ucsb.edu/chirps-v2.0.2024.01.01.tif.gz'}}
        with self.assertRaises(ValueError):summarize_series([s],[])
        with self.assertRaises(ValueError):summarize_series([s],[{**s,'date':'2024-01-02'}])
        with self.assertRaises(ValueError):summarize_series([s,s],[None,None])
        self.assertEqual(rainfall_contract([s,s])['product'],'CHIRPS v2 daily') # Two display channels can share a date.


if __name__=='__main__':unittest.main()
