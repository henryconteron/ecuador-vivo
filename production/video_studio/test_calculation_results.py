"""Result bindings consume existing science without recomputing or mutating it."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).parent))
from calculation_results import CalculationResult, summary_results, resolve_binding, ordered_rows
from studio_model import DataBinding


class CalculationResultTests(unittest.TestCase):
    def test_imported_dates_define_effective_period_separately_from_requested_period(self):
        project,summary=self.fixture()
        project['entries']=[{'date':'2025-03-02'},{'date':'2025-03-01'}]
        result=summary_results(project,summary)['mean_period']['provenance']
        self.assertEqual(result['period'],{'start':'2025-03-01','end':'2025-03-02'})
        self.assertEqual(result['requested_period'],{'start':'2024-01-01','end':'2024-01-02'})

    def fixture(self):
        project=dict(source='local',variable='Precipitación',units='mm/día',
                     scale=1,offset=0,start='2024-01-01',end='2024-01-02',bbox=[-81,-5,-75,2])
        summary=dict(days=2,mean_period=5,peak_pixel_value=12,minimum_pixel_value=0,
                     peak_date_mean=7,peak_month_value=10,aggregate_units='mm',
                     province_rank=[dict(name='Pichincha',value=132.4,coverage=1),
                                    dict(name='Azuay',value=0,coverage=.5),
                                    dict(name='Napo',value=132.4,coverage=1)],
                     city_rank_units='mm',aggregation='sum',
                     spatial_domain='ecuador_continental',ranking_spatial_domain='ecuador_24_provinces',
                     spatial_weighting='cosine_latitude_area_approximation',
                     mean_method='native_source_pixels',calculation_method_version=2,
                     warnings=['Cobertura parcial'])
        return project,summary

    def test_result_registry_preserves_values_units_and_distinct_domains(self):
        project,summary=self.fixture()
        before=copy.deepcopy(summary)
        registry=summary_results(project,summary)
        self.assertEqual(summary,before)
        self.assertEqual(registry['mean_period']['value'],5)
        self.assertEqual(registry['mean_period']['units'],'mm/día')
        self.assertEqual(registry['province_rank']['rows'][0]['value'],132.4)
        self.assertEqual(registry['province_rank']['units'],'mm')
        self.assertEqual(registry['province_rank']['provenance']['spatial_domain'],'ecuador_24_provinces')
        self.assertEqual(registry['mean_period']['provenance']['source_records_ref'],'source_records')
        self.assertIsNone(registry['mean_period']['provenance']['source_units'])

    def test_result_is_immutable_and_bindings_return_independent_copies(self):
        registry=summary_results(*self.fixture())
        result=CalculationResult(registry['province_rank'])
        snapshot=result.to_dict()
        snapshot['rows'][0]['value']=999
        self.assertEqual(result.to_dict()['rows'][0]['value'],132.4)
        with self.assertRaises(AttributeError):
            result._encoded='{}'
        binding=DataBinding(result_id='province_rank',field='rows').to_dict()
        bound=resolve_binding(registry,binding)
        bound[0]['value']=42
        self.assertEqual(registry['province_rank']['rows'][0]['value'],132.4)

    def test_sort_top_n_missing_zero_negatives_and_ties_are_explicit(self):
        rows=[dict(name='Z',value=2),dict(name='A',value=2),dict(name='zero',value=0),
              dict(name='negative',value=-3),dict(name='missing',value=None)]
        self.assertEqual([r['name'] for r in ordered_rows(rows,top_n=2)],['A','Z'])
        self.assertEqual([r['value'] for r in ordered_rows(rows,descending=False)],[-3,0,2,2])
        self.assertEqual(rows[-1]['value'],None)
        for top in (0,-1,True,1001):
            with self.assertRaises(ValueError): ordered_rows(rows,top_n=top)

    def test_invalid_bindings_values_and_non_json_are_rejected(self):
        registry=summary_results(*self.fixture())
        for binding in ({'result_id':'missing','field':'value'},
                        {'result_id':'mean_period','field':'__import__(os)'},
                        {'result_id':'mean_period','field':'missing'}):
            with self.assertRaises(ValueError): resolve_binding(registry,binding)
        invalid=copy.deepcopy(registry['mean_period'])
        invalid['value']=float('nan')
        with self.assertRaises(ValueError): CalculationResult(invalid)

    def test_no_observations_preserves_missing_metrics(self):
        project,summary=self.fixture()
        summary.update(days=0,mean_period=None,peak_pixel_value=None,
                       minimum_pixel_value=None,peak_date_mean=None,peak_month_value=None,
                       province_rank=[])
        registry=summary_results(project,summary)
        self.assertIsNone(registry['mean_period']['value'])
        self.assertEqual(registry['province_rank']['rows'],[])


if __name__=='__main__': unittest.main()
