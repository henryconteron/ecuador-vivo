import json
import unittest

from PIL import ImageChops

from prepare_depth_episode import FOLDER, HASH, load_history, rows_from_snapshot
from reel_depth_damage import DepthDesign, SCENES, DURATION, distance, history_year, PROFILE_SCALE


class DepthEpisodeTests(unittest.TestCase):
    def test_published_snapshot_preserves_scope_and_unknowns(self):
        rows = load_history()
        self.assertEqual(len(rows), 2661)
        self.assertEqual(min(r['year'] for r in rows), 1901)
        self.assertEqual(sum(r['depth_km'] is None for r in rows), 1)
        self.assertGreater(len({r['magnitude_type'] for r in rows}), 1)

    def test_case_values_and_dates_are_not_mixed_between_providers(self):
        rows = {r['id']:r for r in load_history()}
        for identity, mag, kind, depth, local_date in [
            ('us20005j32',7.8,'mww',20.59,'2016-04-16'),
            ('usb000s27f',5.1,'mb',11.88,'2014-08-12'),
            ('usp000330w',7.2,'mw',10,'1987-03-05')]:
            row = rows[identity]
            self.assertEqual((row['magnitude'],row['magnitude_type'],row['depth_km']),(mag,kind,depth))
            self.assertTrue(row['local_time'].startswith(local_date))

    def test_invalid_and_duplicate_data_fail(self):
        f = {'id':'test','geometry':{'coordinates':[-78,0,None]},'properties':{'mag':5,'magType':'mb','time':0,'url':'test'}}
        self.assertIsNone(rows_from_snapshot({'features':[f]})[0]['depth_km'])
        with self.assertRaises(ValueError): rows_from_snapshot({'features':[f,f]})
        f['geometry']['coordinates'][0] = -90
        with self.assertRaises(ValueError): rows_from_snapshot({'features':[f]})

    def test_history_comes_first_with_monotone_years(self):
        self.assertEqual(SCENES[0][2],'historia')
        self.assertEqual(SCENES[-1][1],DURATION)
        self.assertTrue(all(a[1]==b[0] for a,b in zip(SCENES,SCENES[1:])))
        years = [history_year(n/30) for n in range(18*30)]
        self.assertEqual(years, sorted(years))
        self.assertEqual((years[0],years[-1]),(1900,2025))

    def test_controlled_geometry_has_same_horizontal_distance_and_scale(self):
        self.assertEqual(PROFILE_SCALE,1.7)
        self.assertAlmostEqual(distance(40,10),41.231056256)
        self.assertAlmostEqual(distance(40,150),155.241747)
        self.assertGreater(distance(40,150),distance(40,10))

    def test_all_scene_boundaries_fit_and_diagrams_move(self):
        design=DepthDesign()
        for start,end,name in SCENES:
            for second in (start,start+.5,(start+end)/2,end-1/30):
                self.assertEqual(design.render(second).size,(1080,1920),name)
        for a,b,crop in [(38,38+1/30,(110,610,920,1010)),(99,99+1/30,(120,645,900,1140))]:
            first,second=design.render(a),design.render(b)
            self.assertIsNotNone(ImageChops.difference(first.crop(crop),second.crop(crop)).getbbox())

    def test_media_evidence_is_bound_to_current_license_and_files(self):
        from hashlib import sha256
        audit=json.loads((FOLDER/'evidence.json').read_text(encoding='utf-8'))
        self.assertEqual(audit['snapshot_sha256'],HASH)
        for key,meta in audit['media'].items():
            self.assertEqual(meta['license'],'CC BY-SA 2.0')
            self.assertEqual(sha256((FOLDER/f'archive_{key}.jpg').read_bytes()).hexdigest(),meta['sha256'])
            self.assertTrue(meta['photographer'].endswith('/ ANDES'))
            self.assertEqual(sha256((FOLDER/f'rights_{key}.html').read_bytes()).hexdigest(),meta['sha256_rights'])
            original=json.loads((FOLDER/f'rights_{key}_flickr.json').read_text(encoding='utf-8'))
            self.assertEqual(original['license'],meta['license'])
            self.assertEqual(original['url'],meta['original_url'])
        for row in audit['cases']:
            raw=json.loads((FOLDER/f"{row['id']}_verified.geojson").read_text(encoding='utf-8'))
            self.assertEqual(raw['geometry']['coordinates'],[row['longitude'],row['latitude'],row['depth_km']])
            self.assertEqual((raw['properties']['mag'],raw['properties']['magType']),(row['magnitude'],row['magnitude_type']))

    def test_caption_limits_and_no_old_voice(self):
        for name in ('descripcion_instagram_borrador.txt','descripcion_tiktok_borrador.txt'):
            self.assertLessEqual(len((FOLDER/name).read_text(encoding='utf-8')),2200)
        self.assertLessEqual(len((FOLDER/'guion_elevenlabs.txt').read_text(encoding='utf-8').split()),370)


if __name__=='__main__': unittest.main()
