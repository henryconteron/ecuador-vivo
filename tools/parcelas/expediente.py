"""Bounded, resumable Ghana pilot: public discovery, plan and local evidence report."""
import argparse
import csv
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import zipfile

import numpy as np
from shapely.geometry import shape
from tools.parcelas.catalog import discover, validate_parcel
from tools.parcelas.process_api import ROOT, PILOT, DATES, build_request, output_folder, inspect, source_product
from tools.parcelas.radar_series import temporal_gaps, summarize_series

WORK = PILOT/'expediente'
PARCEL = ROOT/'_local/parcelas/referencias/cersgis-16579443/parcela-piloto.geojson'
GROUP = ('sentinel-1a','IW',45,'ascending')


def select_quarterly(items, geometry):
    buckets = {}
    for item in {item['id']:item for item in items}.values():
        if item.get('collection') != 'sentinel-1-grd':
            continue
        p = item['properties']
        key = tuple(p.get(k) for k in ('platform','sar:instrument_mode','sat:relative_orbit','sat:orbit_state'))
        if key != GROUP or not {'VV','VH'}.issubset(p.get('sar:polarizations',[])) or not shape(item['geometry']).covers(geometry):
            continue
        day = date.fromisoformat(p['datetime'][:10])
        quarter = (day.month-1)//3
        target = date(day.year,quarter*3+2,15)
        rank = (abs((day-target).days),p['datetime'],item['id'])
        bucket = (day.year,quarter)
        if bucket not in buckets or rank < buckets[bucket][0]:
            buckets[bucket] = (rank,item)
    return [buckets[key][1] for key in sorted(buckets)]


def evidence_status(count, centres):
    return 'no_common_valid_support' if not centres else 'insufficient_for_deforestation_conclusion'


def plan():
    WORK.mkdir(exist_ok=True)
    if (WORK/'plan.json').exists():
        print('Existing plan retained; use complete to resume.')
        return
    parcel = json.loads(PARCEL.read_text())
    info = validate_parcel(parcel)
    items = []
    for year in range(2020,2026):
        cache = WORK/f'catalog-{year}.json'
        if cache.exists():
            batch = json.loads(cache.read_text())
        else:
            end = f'{year+1}-01-01' if year < 2025 else '2025-03-21'
            found,complete = discover('sentinel-1-grd',info['bbox'],f'{year}-01-01',end)
            if not complete:
                raise ValueError('Catalog incomplete; refusing silent selection')
            batch = {'queried_utc':datetime.now(timezone.utc).isoformat(),'complete':complete,'features':found}
            cache.write_text(json.dumps(batch),encoding='utf-8')
        items.extend(batch['features'])
        print(f'Catalog {year}: {len(batch["features"])} items',flush=True)
    selected = select_quarterly(items,shape(parcel['features'][0]['geometry']))
    for day in DATES:
        matches = [item for item in items if item['properties']['datetime'].startswith(day)
                   and tuple(item['properties'].get(k) for k in ('platform','sar:instrument_mode','sat:relative_orbit','sat:orbit_state')) == GROUP]
        if len(matches) != 1:
            raise ValueError('Known acquisition not unique')
        selected.append(matches[0])
    unique = {item['properties']['datetime'][:10]:item for item in selected}
    if not 4 <= len(unique) <= 28:
        raise ValueError('Pilot limit: 4..28 days')
    observations = []
    for day,item in sorted(unique.items()):
        folder = output_folder(day) if day in DATES else WORK/('radar-'+day.replace('-',''))
        observations.append({'date':day,'product':item['id'], 'folder':str(folder.relative_to(PILOT)).replace('\\','/')})
    data = {'version':1,'parcel_sha256':hashlib.sha256(PARCEL.read_bytes()).hexdigest(),
        'selection':'One acquisition nearest middle of each quarter, plus four prior dates; not continuous monitoring',
        'start':'2020-01-01','end_exclusive':'2025-03-21','observations':observations}
    (WORK/'plan.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    print(f'Plan: {len(observations)} dates; capped at 28, sequential only.')


def load_plan():
    data = json.loads((WORK/'plan.json').read_text())
    rows = data['observations']
    if data['version'] != 1 or not 4 <= len(rows) <= 28 or data['parcel_sha256'] != hashlib.sha256(PARCEL.read_bytes()).hexdigest():
        raise ValueError('Invalid plan or parcel changed')
    temporal_gaps([r['date'] for r in rows])
    for row in rows:
        day = date.fromisoformat(row['date'])
        if not date(2020,1,1) <= day <= date(2025,3,20):
            raise ValueError('Date outside fixed pilot')
        expected = output_folder(row['date']) if row['date'] in DATES else WORK/('radar-'+row['date'].replace('-',''))
        if (PILOT/row['folder']).resolve() != expected.resolve():
            raise ValueError('Unexpected output path')
    return data


def prepare(day):
    config = load_plan()
    rows = {r['date']:r for r in config['observations']}
    if day not in rows:
        raise ValueError('Date not selected')
    folder = PILOT/rows[day]['folder']
    request = build_request(day,tuple(rows))
    folder.mkdir(exist_ok=True)
    path = folder/'request.json'
    if path.exists():
        if json.loads(path.read_text()) != request:
            raise ValueError('Request changed')
    else:
        path.write_text(json.dumps(request,indent=2),encoding='utf-8')


def report():
    started = time.monotonic()
    config = load_plan()
    destination = WORK/'resultado'
    if destination.exists():
        print('Existing result retained; no overwrite.')
        return
    parcel = json.loads(PARCEL.read_text())
    info = validate_parcel(parcel)
    geometry = shape(parcel['features'][0]['geometry'])
    items = {item['id']:item for path in sorted(WORK.glob('catalog-*.json'))
             for item in json.loads(path.read_text())['features']}
    rows,arrays,masks,proof = [],[],[],[]
    for observation in config['observations']:
        day = observation['date']; folder = PILOT/observation['folder']
        expected = build_request(day,tuple(r['date'] for r in config['observations']))
        if json.loads((folder/'request.json').read_text()) != expected:
            raise ValueError('Processing contract changed')
        inspected,data,valid = inspect(day,write=False,folder=folder)
        product = source_product(inspected['metadata'])
        if product != observation['product'] or product not in items:
            raise ValueError('Service lineage differs from selected catalog product')
        item = items[product]; p=item['properties']
        key=tuple(p.get(k) for k in ('platform','sar:instrument_mode','sat:relative_orbit','sat:orbit_state'))
        if item.get('collection') != 'sentinel-1-grd' or key != GROUP or not {'VV','VH'}.issubset(p.get('sar:polarizations',[])) or not p['datetime'].startswith(day) or not shape(item['geometry']).covers(geometry):
            raise ValueError('Acquisition or footprint differs')
        if inspected['bands'] != ['VV','VH','dataMask','shadowMask','localIncidenceAngle']:
            raise ValueError('Wrong band order')
        saved = folder/'inspection.json'
        if saved.exists() and json.loads(saved.read_text())['sha256'] != inspected['sha256']:
            raise ValueError('Image changed after initial inspection')
        rows.append({'date':day,'product':product,'valid_centres':int(valid.sum()),
                     'parcel_centres':inspected['parcel_centres'], 'shadow_centres':inspected['shadow_centres'],
                     'incidence_min':inspected['incidence_range_degrees'][0] if valid.any() else None,
                     'incidence_max':inspected['incidence_range_degrees'][1] if valid.any() else None})
        arrays.append(data); masks.append(valid)
        proof.append({'date':day,'sha256':inspected['sha256'],'metadata':inspected['metadata'],
                      'request_sha256':hashlib.sha256((folder/'request.json').read_bytes()).hexdigest()})
        print('Verified '+day,flush=True)
    common=np.logical_and.reduce(masks)
    results={band:summarize_series([a[index] for a in arrays],common) for index,band in enumerate(('VV','VH'))}
    for i,row in enumerate(rows):
        row.update({'common_centres':int(common.sum()),**{band+'_db_of_mean_linear':results[band][i]['db_of_mean_linear'] for band in ('VV','VH')}})
    days=[r['date'] for r in rows]
    gaps=temporal_gaps(days)
    maximum_gap=max((date.fromisoformat(b)-date.fromisoformat(a)).days for a,b in zip(days,days[1:]))
    status=evidence_status(len(rows),int(common.sum()))
    destination.mkdir()
    # All artifacts are private and self-contained; no credential files are copied.
    with (destination/'serie.csv').open('x',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    (destination/'parcela.geojson').write_bytes(PARCEL.read_bytes())
    optical_path=PILOT/'calidad-optica-202503/optical-quality.json'
    optical=json.loads(optical_path.read_text()) if optical_path.exists() else {'status':'not_available'}
    summary={'version':1,'status':status,'review':'pending_human_review','area_ha':info['area_ha'],
        'acquisition_group':GROUP,'selection':config['selection'],'observations':rows,'common_centres':int(common.sum()),
        'maximum_gap_days':maximum_gap,'gaps_over_30_days':gaps,'interpolation':'none',
        'crop_reference':'Cocoa portion observed March 2025; not property boundary',
        'crop_before_2021':'unknown','deforestation_assessment':'not_performed','eudr_decision':'not_performed',
        'optical_diagnostic':optical,'lineage':proof,
        'generated_utc':datetime.now(timezone.utc).isoformat()}
    (destination/'evidencia.json').write_text(json.dumps(summary,indent=2,allow_nan=False),encoding='utf-8')
    render_figures(destination,days,arrays,masks,common,rows,parcel)
    lines=['# Ecuador Vivo · informe técnico de evidencia satelital', '',
        '**BORRADOR PARA REVISIÓN HUMANA · EVIDENCIA INSUFICIENTE PARA CONCLUIR DEFORESTACIÓN**', '',
        'Autor del proyecto: Henry P. Conteron Moreta · Ecuador Vivo / Andes Pulso.', '',
        '## Resumen', '',
        f'Referencia pública CERSGIS 352, Asunafo North, Ghana: {info["area_ha"]:.4f} ha de una porción de cacao con sombra observada en marzo de 2025.',
        'No es lindero catastral. No demuestra cuándo se estableció el cultivo ni valida resultados en Ecuador.', '',
        f'{len(rows)} adquisiciones reales entre {days[0]} y {days[-1]}; {int(common.sum())} centros válidos comunes.',
        f'Muestreo trimestral más cuatro fechas anteriores. Mayor separación entre observaciones: {maximum_gap} días.',
        'No es seguimiento continuo: puede omitir cambios breves o ocurridos entre adquisiciones. No se rellenan ni interpolan huecos.', '',
        '## Serie radar', '', '![Serie radar: puntos observados](serie-radar.png)', '',
        'Valores: 10 log10 de la media de potencia lineal gamma0 terreno. No media de dB ni porcentaje de cobertura vegetal.',
        'Todos los puntos usan los mismos centros válidos; estos no son muestras estadísticamente independientes.', '',
        '## Mapas de señal', '', '![Mapas de retrodispersión VH](mapas-radar.png)', '',
        'Escala cromática común, extremos recortados SOLO para visualización según percentiles 2–98; los datos no se alteran.',
        'Color no equivale a bosque, cacao, tala o cumplimiento. Los píxeles se muestran sin suavizado generativo.', '',
        '## Método y controles', '',
        '- Catálogo público CDSE, paginación completa por año; selección determinista antes de inspeccionar valores.',
        '- Sentinel-1A, IW, ascendente, órbita relativa 45, VV/VH; productos devueltos por API contrastados con catálogo y huellas.',
        '- Process API: GAMMA0_TERRAIN, ortorrectificación Copernicus DEM30, sin speckle, NEAREST.',
        '- Grilla común EPSG:32630 de 72×62 celdas, paso exacto 20 m. Paso no equivale a exactitud o resolución independiente.',
        '- NoData, sombras radar señaladas, valores no finitos/no positivos excluidos; soporte común sobre toda la serie.',
        '- shadowMask no excluye todo layover o error del terreno. Incidencia local registrada por fecha.',
        '- La conversión de coeficientes la realiza el proveedor; no se recalibran los recortes con SNAP.', '',
        '## Diagnóstico óptico', '',
        'Se conserva el diagnóstico Sentinel-2 anterior: dos fechas examinadas (9 y 19 de marzo de 2025), sin centros despejados SCL 4/5/6.',
        'Esto no prueba que todo marzo esté nublado. No se genera NDVI con esos datos ni se rellenan nubes.', '',
        '## Interpretación y límites', '',
        'Observación: existe una serie de retrodispersión con procedencia y calidad documentadas.',
        'Interpretación: las diferencias pueden combinar humedad, estructura vegetal, geometría, speckle y terreno.',
        '**No se ha entrenado ni validado un detector de deforestación. No se estima área deforestada ni se emite «sin deforestación» o «cumple EUDR».**',
        'La referencia de cultivo es de 2025 y no aporta una historia independiente de cambios antes/después de 2020.',
        'Para usar comercialmente: parcela ecuatoriana autorizada con historia comprobada, validación independiente, revisión profesional y evaluación legal del informe.', '',
        '## Fechas y controles', '', '| Fecha | Válidos | Comunes | VV dB | VH dB |','|---|---:|---:|---:|---:|']
    for row in rows:
        vv,vh=row['VV_db_of_mean_linear'],row['VH_db_of_mean_linear']
        values='Sin soporte | Sin soporte' if vv is None else f'{vv:.3f} | {vh:.3f}'
        lines.append(f'| {row["date"]} | {row["valid_centres"]} | {row["common_centres"]} | {values} |')
    lines += ['', '## Fuentes y licencia', '',
        '- CERSGIS v2.0, referencia pública de cacao (CC BY 4.0): https://zenodo.org/records/16579443',
        '- Copernicus Sentinel-1 GRD: https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S1GRD.html',
        '- Metadatos API: https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Evalscript/resources/metadata_sh_docs.html',
        '- ESA SNAP: https://step.esa.int/docs/tutorials/SNAP_CommandLine_Tutorial.pdf', '',
        '## Revisión pendiente', '', '- [ ] Validar historia independiente de cobertura/cambios.',
        '- [ ] Revisar incertidumbre, terreno y estacionalidad.', '- [ ] Validar transferencia a Ecuador.',
        '- [ ] Aprobar la interpretación y firmar con responsabilidad profesional antes de entregar a un cliente.', '',
        'Archivo numérico: `serie.csv`. Procedencia, parámetros y máscaras: `evidencia.json` y archivos originales del paquete.']
    (destination/'INFORME.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    inputs={'parcel_sha256':config['parcel_sha256'],'plan_sha256':hashlib.sha256((WORK/'plan.json').read_bytes()).hexdigest(),
        'report_processing_seconds':time.monotonic()-started,
        'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in destination.iterdir() if p.is_file()}}
    (destination/'huellas.json').write_text(json.dumps(inputs,indent=2),encoding='utf-8')
    package=WORK/'ecuador-vivo-piloto-352.zip'
    with package.open('xb') as stream, zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(destination.iterdir()):
            archive.write(path,'informe/'+path.name)
        archive.write(WORK/'plan.json','plan.json')
        for path in sorted(WORK.glob('catalog-*.json')):
            archive.write(path,'catalogos/'+path.name)
        for row in config['observations']:
            folder=PILOT/row['folder']
            for name in ('request.json','response.tar'):
                archive.write(folder/name,'evidencia/'+row['date']+'/'+name)
    print(f'READY: {len(rows)} dates, {common.sum()} common centres, {maximum_gap} day maximum gap. Package {package.stat().st_size} bytes.',flush=True)


def render_figures(destination,days,arrays,masks,common,rows,parcel):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.dates import DateFormatter
    from rasterio.warp import transform_geom
    plt.rcParams.update({'font.family':'DejaVu Sans','figure.facecolor':'#f7f2e4','axes.facecolor':'#f7f2e4','text.color':'#123d37','axes.labelcolor':'#123d37'})
    fig,ax=plt.subplots(figsize=(12,4.8),layout='constrained')
    for band,color in [('VV','#157f73'),('VH','#b75b36')]:
        ax.scatter([date.fromisoformat(d) for d in days],[r[band+'_db_of_mean_linear'] for r in rows],label=band,color=color,s=28)
    ax.axvline(date(2020,12,31),color='#64726d',linestyle='--',linewidth=1,label='31 dic 2020: referencia temporal')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    ax.set(ylabel='Gamma0 terreno · dB de media lineal',xlabel='Adquisición UTC · solo puntos observados, sin interpolación',title='Ecuador Vivo / Andes Pulso · señal radar de la parcela de referencia')
    ax.grid(alpha=.18); ax.legend(loc='best'); fig.savefig(destination/'serie-radar.png',dpi=160); plt.close(fig)
    indices=sorted(set(np.linspace(0,len(days)-1,6,dtype=int).tolist()))
    values=[10*np.log10(a[1][m]) for a,m in zip(arrays,masks) if m.any()]
    low,high=np.percentile(np.concatenate(values),[2,98]) if values else (-25,-5)
    if high <= low: high=low+1
    fig,axes=plt.subplots(2,3,figsize=(12,8),layout='constrained')
    projected=transform_geom('EPSG:4326','EPSG:32630',parcel['features'][0]['geometry'])
    polygon=shape(projected); parts=[polygon] if polygon.geom_type=='Polygon' else polygon.geoms
    for axis,index in zip(axes.flat,indices):
        image=np.full(masks[index].shape,np.nan)
        image[masks[index]]=10*np.log10(arrays[index][1][masks[index]])
        im=axis.imshow(image,extent=[528200,529640,754180,755420],origin='upper',vmin=low,vmax=high,cmap='viridis',interpolation='nearest')
        for part in parts:
            x,y=part.exterior.xy; axis.plot(x,y,color='#bd542e',linewidth=1.2)
        axis.set_title(days[index]); axis.set_xlabel('UTM 30N · E (m)'); axis.set_ylabel('N (m)')
        axis.ticklabel_format(style='plain',useOffset=False)
        axis.tick_params(labelsize=8)
    if len(indices)<6:
        for axis in list(axes.flat)[len(indices):]: axis.set_visible(False)
    fig.colorbar(im,ax=axes,shrink=.75,label='VH gamma0 terreno (dB) · solo visualización')
    fig.suptitle('Referencia CERSGIS 352 · Ghana · señal radar, NO mapa de deforestación')
    fig.savefig(destination/'mapas-radar.png',dpi=160); plt.close(fig)


def verify():
    config=load_plan()
    destination=WORK/'resultado'
    hashes=json.loads((destination/'huellas.json').read_text())
    if hashes['parcel_sha256'] != hashlib.sha256(PARCEL.read_bytes()).hexdigest() or hashes['plan_sha256'] != hashlib.sha256((WORK/'plan.json').read_bytes()).hexdigest():
        raise ValueError('Parcel or plan changed since report generation')
    for name,digest in hashes['files'].items():
        if Path(name).name != name or hashlib.sha256((destination/name).read_bytes()).hexdigest() != digest:
            raise ValueError('Report artifact changed')
    evidence=json.loads((destination/'evidencia.json').read_text())
    if evidence['status'] not in ('insufficient_for_deforestation_conclusion','no_common_valid_support') or len(evidence['lineage']) != len(config['observations']):
        raise ValueError('Invalid evidence status or count')
    by_date={r['date']:r for r in evidence['lineage']}
    with zipfile.ZipFile(WORK/'ecuador-vivo-piloto-352.zip') as archive:
        if archive.testzip() is not None:
            raise ValueError('Package CRC failure')
        for path in destination.iterdir():
            if path.is_file() and archive.read('informe/'+path.name) != path.read_bytes():
                raise ValueError('Package differs from report')
        for row in config['observations']:
            folder=PILOT/row['folder']; receipt=by_date[row['date']]
            if hashlib.sha256((folder/'response.tar').read_bytes()).hexdigest() != receipt['sha256']:
                raise ValueError('Source image changed')
            if hashlib.sha256((folder/'request.json').read_bytes()).hexdigest() != receipt['request_sha256']:
                raise ValueError('Source request changed')
            if source_product(receipt['metadata']) != row['product']:
                raise ValueError('Wrong source lineage')
            for name in ('response.tar','request.json'):
                if archive.read('evidencia/'+row['date']+'/'+name) != (folder/name).read_bytes():
                    raise ValueError('Package evidence changed')
    print(f'Integrity verified offline: {len(config["observations"])} acquisitions, report hashes and ZIP CRC. Human scientific review still pending.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['plan','prepare','report','verify'])
    parser.add_argument('--date')
    args = parser.parse_args()
    if args.mode == 'plan':
        plan()
    elif args.mode == 'prepare':
        prepare(args.date)
    elif args.mode == 'report':
        report()
    else:
        verify()
