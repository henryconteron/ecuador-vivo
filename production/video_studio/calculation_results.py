"""Immutable, JSON-backed views of existing scientific results.

This module never reads datasets or aggregates pixels. SummaryAccumulator is
still responsible for its science. Provenance names that methodology explicitly.
"""
import copy
import json
import math
from studio_model import validate_binding


def _value(value):
    if value is not None and (isinstance(value,bool) or not isinstance(value,(int,float))
                              or not math.isfinite(value)):
        raise ValueError('Un resultado debe ser finito o None (NoData).')


class CalculationResult:
    __slots__=('_encoded',)

    def __init__(self, payload):
        if not isinstance(payload,dict):
            raise ValueError('CalculationResult debe ser un objeto.')
        validate_binding({'result_id':payload.get('id'),'field':'value'})
        for name in ('variable','units'):
            if not isinstance(payload.get(name),str) or len(payload[name])>200:
                raise ValueError(f'{name} inválido en CalculationResult.')
        _value(payload.get('value'))
        rows=payload.get('rows',[])
        if not isinstance(rows,list) or len(rows)>10000:
            raise ValueError('Resultado tabular demasiado grande.')
        for row in rows:
            if not isinstance(row,dict) or not isinstance(row.get('name'),str):
                raise ValueError('Cada fila requiere name y value.')
            _value(row.get('value'))
        if not isinstance(payload.get('provenance'),dict):
            raise ValueError('El resultado requiere procedencia explícita.')
        try:
            encoded=json.dumps(payload,allow_nan=False,ensure_ascii=False,sort_keys=True)
        except (ValueError,TypeError,RecursionError) as error:
            raise ValueError('CalculationResult debe ser JSON finito.') from error
        if len(encoded)>4_000_000:
            raise ValueError('Resultado demasiado grande para el proyecto.')
        object.__setattr__(self,'_encoded',encoded)

    def __setattr__(self,name,value):
        raise AttributeError('CalculationResult es inmutable; crea una nueva revisión científica.')

    def to_dict(self):
        return json.loads(self._encoded)


def summary_results(project, summary):
    """Expose exact summary values; never infer or recalculate scientific data.

    Original raster units may be unknown for user imports: keep None rather
    than claiming that the effective physical unit is the raw source unit.
    Hashes/files are referenced through the existing receipt source_records.
    """
    requested_period={'start':project.get('start'),'end':project.get('end')}
    dates=sorted(row['date'] for row in project.get('entries',[]) if row.get('date')) if project.get('source')=='local' else []
    effective_period=summary.get('observed_period') or (
        {'start':dates[0],'end':dates[-1]} if dates else requested_period)
    provenance=dict(
        source=project.get('source'), variable=project.get('variable',''),
        source_units=project.get('source_units'), internal_units=project.get('units',''),
        period=copy.deepcopy(effective_period),requested_period=requested_period,
        bbox=copy.deepcopy(project.get('bbox')), scale=project.get('scale',1),
        offset=project.get('offset',0), weighting=summary.get('spatial_weighting'),
        method=summary.get('mean_method','legacy_summary'),
        calculation_method_version=summary.get('calculation_method_version',1),
        warnings=copy.deepcopy(summary.get('warnings',[])),
        source_records_ref='source_records', observed_dates=summary.get('days',0),
    )
    registry={}
    metrics=(('mean_period','mean','spatial_mean_per_date_then_date_mean'),
             ('peak_pixel_value','max','absolute_pixel_max'),
             ('minimum_pixel_value','min','absolute_pixel_min'),
             ('peak_date_mean','max','max_of_daily_spatial_means'),
             ('peak_month_value',summary.get('aggregation'),'daily_spatial_means'))
    for identifier,temporal,spatial in metrics:
        units=(summary.get('aggregate_units',project.get('units','')) if identifier=='peak_month_value'
               else project.get('units',''))
        method={**provenance,'spatial_domain':summary.get('spatial_domain','selected_bbox'),
                'temporal_operation':temporal,'spatial_operation':spatial,'output_units':units}
        if identifier in ('peak_pixel_value','minimum_pixel_value'):
            method['method']=summary.get('extreme_method','legacy_summary')
        # Annual cadence uses a year, not a month; the summary labels it.
        if identifier=='peak_month_value':
            method['period_kind']=summary.get('peak_period_kind','month')
            method['period_year']=summary.get('peak_month_year')
            method['period_month']=summary.get('peak_month_number')
        registry[identifier]=CalculationResult(dict(id=identifier,
            variable=project.get('variable',''),units=units,value=summary.get(identifier),
            provenance=method)).to_dict()
    units=summary.get('city_rank_units',summary.get('aggregate_units',project.get('units','')))
    registry['province_rank']=CalculationResult(dict(id='province_rank',variable=project.get('variable',''),
        units=units,value=None,rows=copy.deepcopy(summary.get('province_rank',[])),
        provenance={**provenance,'spatial_domain':summary.get('ranking_spatial_domain','province_parts_within_bbox'),
                    'temporal_operation':summary.get('aggregation'),
                    'spatial_operation':'native_adm1_zonal_mean','output_units':units})).to_dict()
    return registry


def resolve_binding(registry,binding):
    validate_binding(binding)
    result=registry.get(binding['result_id'])
    if not isinstance(result,dict) or binding['field'] not in result:
        raise ValueError('Binding apunta a un resultado/campo inexistente.')
    return copy.deepcopy(result[binding['field']])


def ordered_rows(rows, *, descending=True, top_n=None):
    """Display ordering only. Missing values excluded, negatives/zero retained.

    Equal values use name as deterministic tie breaker. Scientific values and
    their coverage are never rounded, truncated or replaced by display styling.
    """
    if type(descending) is not bool or (top_n is not None and
            (type(top_n) is not int or not 1<=top_n<=1000)):
        raise ValueError('Sort o Top N inválido.')
    if not isinstance(rows,list):
        raise ValueError('Se requieren filas tabulares.')
    valid=[]
    for row in rows:
        if not isinstance(row,dict) or not isinstance(row.get('name'),str):
            raise ValueError('Cada fila requiere name y value.')
        _value(row.get('value'))
        if row.get('value') is not None: valid.append(copy.deepcopy(row))
    valid.sort(key=lambda row:((-row['value'] if descending else row['value']),row['name']))
    return valid[:top_n] if top_n is not None else valid
