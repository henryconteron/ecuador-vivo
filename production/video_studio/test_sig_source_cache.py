"""Warm representations never bypass file bytes, confinement or metadata checks."""
import copy,json,os
from pathlib import Path
import unittest
from unittest.mock import patch
import test_studio_geography as fixtures


class SigSourceCacheTests(unittest.TestCase):
    setUp=fixtures.GeographyTests.setUp
    tearDown=fixtures.GeographyTests.tearDown
    imported=fixtures.GeographyTests.imported

    def test_warm_reads_parse_once_and_returns_cannot_poison_cache(self):
        import studio_geography as geo
        project,_=self.imported();record=next(iter(project['studio']['geography']['sources'].values()))
        geo.clear_source_cache()
        with patch.object(geo,'parse_geojson',wraps=geo.parse_geojson) as parser,patch.object(geo,'_region',wraps=geo._region) as region:
            original=geo.read_source(record);original['features'][0]['geometry']['coordinates'][0][0]=[0,0]
            self.assertEqual(geo.read_source(record),self.original)
            geo.validate_geography(project['studio']);geo.validate_geography(project['studio'])
            self.assertEqual(parser.call_count,1);self.assertEqual(region.call_count,3)

    def test_same_size_and_mtime_tampering_detected_with_hot_cache(self):
        import studio_geography as geo
        project,_=self.imported();record=next(iter(project['studio']['geography']['sources'].values()))
        geo.read_source(record);path=Path(record['path']);stat=path.stat();original=path.read_bytes()
        changed=original.replace(b'Brasil',b'Brasix');self.assertEqual(len(changed),len(original))
        path.write_bytes(changed);os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns))
        with self.assertRaisesRegex(ValueError,'bytes'):geo.read_source(record)
        path.write_bytes(original);self.assertEqual(geo.read_source(record),self.original)

    def test_hot_cache_does_not_authorize_foreign_paths_or_metadata_or_regions(self):
        import studio_geography as geo
        project,_=self.imported();record=next(iter(project['studio']['geography']['sources'].values()));geo.read_source(record)
        for bad in ({**record,'path':str(Path(self.temp.name)/'outside.geojson')},
                    {**record,'provenance':{'citation':'','license':'CC0','url':''}},
                    {**record,'native_crs':'EPSG:3857'}):
            with self.assertRaises(ValueError):geo.read_source(bad)
        bad=copy.deepcopy(project);next(iter(bad['studio']['geography']['regions'].values()))['bbox']=[0,0,1,1]
        with self.assertRaises(ValueError):geo.validate_geography(bad['studio'])
        with patch.object(geo,'ROOT',Path(self.temp.name)/'other-root'):
            with self.assertRaises(ValueError):geo.read_source(record)

    def test_limits_and_eviction_apply_even_to_valid_cached_content(self):
        import studio_geography as geo
        from studio_geography import import_geojson
        project,_=self.imported();record=next(iter(project['studio']['geography']['sources'].values()))
        geo.clear_source_cache()
        with patch.object(geo,'SOURCE_CACHE_ENTRIES',1):
            geo.read_source(record)
            other=json.dumps({'type':'Feature','properties':{},'geometry':self.original['features'][1]['geometry']}).encode()
            second,_=import_geojson(project,other,'other.geojson',self.provenance)
            self.assertLessEqual(len(geo._SOURCE_CACHE),1)
            self.assertLessEqual(sum(map(len,geo._SOURCE_CACHE.values())),geo.SOURCE_CACHE_BYTES)
        with patch.object(geo,'COORDINATE_LIMIT',4),self.assertRaises(ValueError):geo.read_source(record)


if __name__=='__main__':unittest.main()
