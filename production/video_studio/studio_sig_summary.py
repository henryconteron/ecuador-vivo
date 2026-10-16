"""SIG adapter to the existing native zonal engine and SummaryAccumulator.

No display pixels enter this module. Only verified daily CHIRPS is automated;
other products need an explicit measurement/interval contract before analysis.
"""
import copy,datetime as dt,hashlib,json,re
import numpy as np
import rasterio
from variables import aggregate_intervals
from data import _polygon_stats
from endcard import SummaryAccumulator
from calculation_results import CalculationResult
from studio_territory import boundaries
from studio_sig_raster import verify_source


def rainfall_contract(sources):
    if not sources:raise ValueError('Selecciona observaciones científicas.')
    for source in sources:
        url=source['provenance'].get('url','')
        if (source.get('semantics')!='precipitation' or source.get('units') not in ('mm/día','mm/day','mm')
            or not re.search(r'/chirps-v2\.0\.\d{4}\.\d{2}\.\d{2}\.tif\.gz$',url)
            or not source.get('date')):
            raise ValueError('Configura el tipo de medición y los intervalos del producto. El envío con métricas automáticas está verificado para CHIRPS v2 diario, acumulado de cada día; no se infiere del título.')
    if any(s['units']!=sources[0]['units'] for s in sources):
        raise ValueError('Unidades incompatibles en la serie científica.')
    return {'variable':'precipitation','family':'precipitation','units':sources[0]['units'],
            'spatial_support':'native raster cell','measurement':'interval_amount','operation':'sum',
            'interval':'[date 00:00, next date 00:00)','product':'CHIRPS v2 daily',
            'native_resolution':'0.05°; aproximadamente 5.6 km en el ecuador'}


def summarize_series(sources,insets,*,cadence='daily'):
    contract=rainfall_contract(sources)
    dates=[s['date'] for s in sources]
    if dates!=sorted(set(dates)):raise ValueError('Fechas científicas duplicadas o desordenadas.')
    if len(insets)!=len(sources) or any(inset is not None and any(inset[k]!=source[k] for k in ('date','units','semantics','variable')) for source,inset in zip(sources,insets)):
        raise ValueError('El calendario, variable y unidades de Galápagos deben coincidir con cada observación continental.')
    if cadence!='daily':raise ValueError('CHIRPS diario requiere cadencia diaria para sus métricas; no se agregaron intervalos en silencio.')
    payloads,records=boundaries();features=payloads['ADM1']['features']
    country={'type':'Feature','properties':{'name':'domain'},'geometry':payloads['ADM0']['features'][0]['geometry']}
    main=[f for f in features if f['properties']['shapeName']!='Galápagos'];gal=[f for f in features if f['properties']['shapeName']=='Galápagos']
    dates=[s['date'] for s in sources]
    config={'variable':'Precipitación diaria CHIRPS v2','units':contract['units'],'source':'local',
            'bbox':[-81.5,-5.2,-75.,1.8],'cadence':'Diaria','clip_ecuador':True,
            'start':dates[0],'end':dates[-1]}
    accumulator=SummaryAccumulator(config,payloads['ADM0']);daily=[];provenance=[]
    for source,inset in zip(sources,insets):
        parts=[];prov={}
        # If a native original includes both regions, do not count it twice.
        for entry,regions in ((source,main),(inset,gal)):
            if entry is None:continue
            path=verify_source(entry);meta=entry['raster']
            with rasterio.open(path) as ds:
                kwargs={'scale':meta['scale'],'offset':meta['offset'],
                        'source_nodata':meta['nodata'] if isinstance(meta['nodata'],(int,float)) else None,
                        'reject_negative':True,'include_empty':True}
                selected=_polygon_stats(ds,meta['band'],regions,**kwargs);prov.update(selected)
                # Union of this channel's province geometries: disjoint regions,
                # shared engine computes exact native support/area approximation.
                from shapely.geometry import shape,mapping
                from shapely.ops import unary_union
                domain={**country,'geometry':mapping(unary_union([shape(f['geometry']) for f in regions]))}
                stats=_polygon_stats(ds,meta['band'],[domain],**kwargs).get('domain')
                if stats and stats['mean'] is not None:parts.append(stats)
            provenance.append({'file':str(path),'sha256':entry['sha256'],'date':entry['date'],
                               'units':entry['units'],'crs':entry['native_crs'],'source':entry['provenance']})
        area=sum(r['area_weight_sum'] for r in parts)
        mean=sum(r['weighted_value_sum'] for r in parts)/area if area else None
        stats={'mean':mean,'max':max((r['max'] for r in parts),default=None),
               'min':min((r['min'] for r in parts),default=None),
               'coverage':sum(r['valid_pixels'] for r in parts)/max(1,sum(r['total_pixels'] for r in parts)),
               'weighting':'cosine_latitude_area_approximation'}
        samples={name:row['mean'] for name,row in prov.items()}
        accumulator.observe(source['date'],np.empty((0,0)),province_samples=samples,spatial_stats=stats)
        daily.append({'date':source['date'],'mean':mean,'coverage':stats['coverage'],
                      'maximum':stats['max'],'provinces':prov,'galapagos_available':inset is not None})
    summary=accumulator.to_dict()
    intervals=[{'start':row['date'],'end':(dt.date.fromisoformat(row['date'])+dt.timedelta(days=1)).isoformat(),
                'value':row['mean'],'units':contract['units']} for row in daily]
    total=aggregate_intervals(intervals,contract)
    names=[f['properties']['shapeName'] for f in features]
    rank={row['name']:row for row in summary['province_rank']}
    rows=[]
    for name in names:
        row=copy.deepcopy(rank.get(name,{'name':name,'value':None,'days':0,'coverage':0.}))
        if row['days']!=len(sources):row.update(observed_subtotal=row['value'],value=None)
        row['spatial_coverage']=min((r['provinces'].get(name,{}).get('coverage',0.) for r in daily),default=0.)
        rows.append(row)
    missing=sum(r['value'] is None for r in rows)
    warnings=[w for w in summary.get('warnings',[]) if 'mes destacado' not in w]
    if missing:warnings.append(f'{missing} de 24 provincias sin estimación completa; no se presentan como cero.')
    if total['gaps']:warnings.append('Periodo incompleto: faltan intervalos diarios; se usan solo fechas disponibles.')
    if not all(r['galapagos_available'] for r in daily):warnings.append('Cobertura nacional incompleta: Galápagos sin datos verificables en alguna fecha.')
    # Do not claim an annual result or a complete month for a short window.
    summary.update(province_rank=rows,days=len(dates),warnings=warnings,
                   spatial_domain='ecuador_continental_and_galapagos_native_support',
                   period_complete=not total['gaps'] and total['valid_intervals']==len(dates),
                   observed_period={'start':dates[0],'end':dates[-1]})
    method={'contract':contract,'period':summary['observed_period'],'observations':len(dates),
            'method':'native pixel-centre polygon mask; cosine(latitude) area approximation; temporal sum of daily spatial means',
            'boundary_cells':'Native cells whose centres fall in the polygon; no fractional-cell weighting. Small polygons with no centres return None.',
            'coverage_definition':'Finite native cells / polygon centres within the raster footprint; missing source/province remains explicitly absent.',
            'boundaries':records,'warnings':warnings,'daily':daily}
    identity=hashlib.sha256(json.dumps(['native_sig_summary_v4',contract,provenance,records],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    registry={}
    def result(key,label,value,units,rows=None):
        rid='calc.'+identity[:20]+'.'+key
        payload={'id':rid,'variable':label,'value':value,'units':units,'provenance':{**{k:v for k,v in method.items() if k!='daily'},'source_records_ref':'sources.'+identity,'detail_ref':'science.'+identity}}
        if rows is not None:payload['rows']=rows
        registry[key]=CalculationResult(payload).to_dict()
    result('sum_means','Suma de medias nacionales diarias',total['value'],'mm')
    result('mean_period','Media nacional por fecha',summary.get('mean_period'),contract['units'])
    result('peak_mean','Mayor media nacional diaria',summary.get('peak_date_mean'),contract['units'])
    result('peak_cell','Máximo de celda nativa',summary.get('peak_pixel_value'),contract['units'])
    result('province_rank','Suma de medias provinciales diarias',None,'mm',rows)
    result('daily_means','Medias nacionales por fecha',None,contract['units'],[{'name':r['date'],'value':r['mean'],'coverage':r['coverage']} for r in daily])
    return {'identity':identity,'results':registry,'summary':summary,'method':method,'source_records':provenance}
