import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from shapely.geometry import box, mapping
from tools.parcelas.expediente import select_quarterly, evidence_status, report


def scene(day, orbit=45):
    return {'id':day, 'geometry':mapping(box(0,0,2,2)), 'collection':'sentinel-1-grd',
            'properties':{'datetime':day+'T18:00:00Z', 'platform':'sentinel-1a',
                'sar:instrument_mode':'IW', 'sat:relative_orbit':orbit,
                'sat:orbit_state':'ascending', 'sar:polarizations':['VV','VH']}}


class ExpedienteTests(unittest.TestCase):
    def test_existing_result_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            work=Path(directory); (work/'resultado').mkdir()
            sentinel=work/'resultado/INFORME.md'; sentinel.write_text('original')
            with patch('tools.parcelas.expediente.WORK',work), patch('tools.parcelas.expediente.load_plan',return_value={}):
                report()
            self.assertEqual(sentinel.read_text(),'original')

    def test_wrong_collection_excluded(self):
        item=scene('2021-01-01'); item['collection']='other'
        self.assertEqual(select_quarterly([item],box(.5,.5,1,1)),[])

    def test_one_scene_per_quarter_same_orbit(self):
        selected = select_quarterly([scene('2021-01-01'),scene('2021-02-14'),scene('2021-04-02'),scene('2021-02-15',99)], box(.5,.5,1,1))
        self.assertEqual([s['id'] for s in selected], ['2021-02-14','2021-04-02'])

    def test_incomplete_footprint_excluded(self):
        self.assertEqual(select_quarterly([scene('2021-01-01')],box(0,0,3,3)), [])

    def test_duplicates_do_not_create_observations(self):
        self.assertEqual(len(select_quarterly([scene('2021-01-01')]*2,box(.5,.5,1,1))),1)

    def test_more_dates_never_become_compliance(self):
        self.assertEqual(evidence_status(28,124), 'insufficient_for_deforestation_conclusion')

    def test_no_support_explicit(self):
        self.assertEqual(evidence_status(28,0),'no_common_valid_support')
