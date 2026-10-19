"""Dated optical/radar evidence for public Ecuador case 2435, NOT a farm boundary."""
import argparse
from datetime import date,timedelta
import hashlib
import json
from collections import defaultdict
import tarfile
import numpy as np
from pyproj import Transformer
from shapely.geometry import box,mapping,shape
from tools.parcelas.catalog import discover
from tools.parcelas.process_api import ROOT,EVALSCRIPT
from rasterio.io import MemoryFile

WORK=ROOT/'_local/parcelas/ecuador-2435'


def sensor_request(sensor):
    if sensor=='radar':
        return EVALSCRIPT,50,'sentinel-1-grd'
    if sensor=='optical':
        return '''//VERSION=3
function setup(){return {input:[{bands:["B04","B03","B02","B08","SCL","dataMask"],
 units:["REFLECTANCE","REFLECTANCE","REFLECTANCE","REFLECTANCE","DN","DN"]}],mosaicking:"ORBIT",
 output:{id:"default",bands:6,sampleType:"FLOAT32"}};}
function evaluatePixel(samples){for(let s of samples){if(s.dataMask)return [s.B04,s.B03,s.B02,s.B08,s.SCL,s.dataMask];}return [0,0,0,0,0,0];}
function updateOutputMetadata(scenes,inputMetadata,outputMetadata){outputMetadata.userData={orbits:scenes.orbits,inputMetadata:inputMetadata,
 bands:["red","green","blue","nir","SCL","dataMask"],units:["reflectance","reflectance","reflectance","reflectance","DN","DN"]};}
''',100,'sentinel-2-l2a'
    raise ValueError('Unsupported sensor')


def build_payload(sensor,day,bounds,direction=None,epsg=32718):
    script,size,collection=sensor_request(sensor)
    end=(date.fromisoformat(day)+timedelta(days=1)).isoformat()
    filtering={'timeRange':{'from':day+'T00:00:00Z','to':end+'T00:00:00Z'}}
    processing={'upsampling':'NEAREST','downsampling':'NEAREST'}
    step=10 if sensor=='optical' else 20
    width=(bounds[2]-bounds[0])/step; height=(bounds[3]-bounds[1])/step
    if epsg not in (32717,32718) or not width.is_integer() or not height.is_integer() or not 0<width*height<=10000:
        raise ValueError('Unsupported CRS, grid or output size')
    if sensor=='radar':
        if direction not in ('ASCENDING','DESCENDING'): raise ValueError('Explicit orbit direction required')
        filtering.update(acquisitionMode='IW',polarization='DV',orbitDirection=direction,resolution='HIGH')
        processing.update(backCoeff='GAMMA0_TERRAIN',orthorectify=True,demInstance='COPERNICUS_30',speckleFilter={'type':'NONE'})
    return {'input':{'bounds':{'bbox':bounds,'properties':{'crs':f'http://www.opengis.net/def/crs/EPSG/0/{epsg}'}},
        'data':[{'type':collection,'dataFilter':filtering,'processing':processing}]},
        'output':{'width':int(width),'height':int(height),'responses':[{'identifier':'default','format':{'type':'image/tiff'}},
                    {'identifier':'userdata','format':{'type':'application/json'}}]},'evalscript':script}


def plan():
    WORK.mkdir(exist_ok=True)
    if (WORK/'plan.json').exists():
        print('Existing Ecuador plan retained'); return
    references=json.loads((ROOT/'_local/parcelas/validacion/referencias-wri-ecuador/candidatos-ecuador.geojson').read_text())
    feature=next(f for f in references['features'] if f['properties']['ID']=='2435')
    lon,lat=feature['geometry']['coordinates']
    x,y=Transformer.from_crs(4326,32718,always_xy=True).transform(lon,lat)
    x,y=int(round(x/20)*20),int(round(y/20)*20)
    bounds=[x-500,y-500,x+500,y+500]
    geographic=Transformer.from_crs(32718,4326,always_xy=True).transform_bounds(*bounds)
    geometry=box(*geographic)
    collections={}; optical=[]
    for year in (2020,2022):
        for sensor,collection in [('optical','sentinel-2-l2a'),('radar','sentinel-1-grd')]:
            cache=WORK/f'catalog-{year}-{sensor}.json'
            if cache.exists(): batch=json.loads(cache.read_text())
            else:
                found,complete=discover(collection,list(geographic),f'{year}-10-01',f'{year+1}-01-01')
                if not complete: raise ValueError('Incomplete catalog')
                batch={'features':found,'complete':complete}; cache.write_text(json.dumps(batch),encoding='utf-8')
            covering=[i for i in batch['features'] if shape(i['geometry']).covers(geometry)]
            collections[(year,sensor)]=covering
            print(f'{year} {sensor}: {len(covering)} covering candidates',flush=True)
        by_day={}
        for item in sorted(collections[(year,'optical')],key=lambda i:(i['properties'].get('eo:cloud_cover',100),i['properties']['datetime'],i['id'])):
            by_day.setdefault(item['properties']['datetime'][:10],item)
        chosen=list(by_day.values())[:3]
        if len(chosen)<2: raise ValueError('Insufficient optical days')
        optical.extend(chosen)
    groups=defaultdict(list)
    for year in (2020,2022):
        for i in collections[(year,'radar')]:
            p=i['properties']
            if p.get('platform')=='sentinel-1a' and p.get('sar:instrument_mode')=='IW' and {'VV','VH'}.issubset(p.get('sar:polarizations',[])):
                groups[(p['sat:relative_orbit'],p['sat:orbit_state'])].append(i)
    viable=[]
    for key,candidates in groups.items():
        matches=[]
        for item in optical:
            day=date.fromisoformat(item['properties']['datetime'][:10])
            ranked=sorted(candidates,key=lambda r:(abs((date.fromisoformat(r['properties']['datetime'][:10])-day).days),r['id']))
            candidate=ranked[0]
            delta=abs((date.fromisoformat(candidate['properties']['datetime'][:10])-day).days)
            matches.append((delta,candidate))
        if max(v[0] for v in matches)<=12: viable.append((sum(v[0] for v in matches),key,matches))
    if not viable: raise ValueError('No compatible radar group within 12 days of all optical candidates')
    _,group,matching=min(viable,key=lambda v:(v[0],v[1]))
    observations={}; pairs=[]
    for optical_item,(delta,radar_item) in zip(optical,matching):
        keys=[]
        for sensor,item in [('optical',optical_item),('radar',radar_item)]:
            day=item['properties']['datetime'][:10]; key=sensor+'-'+day
            observations[key]={'key':key,'sensor':sensor,'date':day,'product':item['id'],'folder':key}
            keys.append(key)
        pairs.append({'optical':keys[0],'radar':keys[1],'separation_days':delta,'period':optical_item['properties']['datetime'][:4]})
    data={'case':'2435','area_type':'1 km x 1 km observation context; NOT a cadastral farm or reconstructed source plot',
        'bounds':bounds,'epsg':32718,'reference':feature,'relative_orbit':group[0],'direction':group[1].upper(),
        'observations':list(observations.values()),'pairs':pairs,
        'selection':'Three lowest scene-cloud distinct covering optical days in Oct-Dec 2020 and 2022; matching same-group radar within 12 days; no event date presumed'}
    (WORK/'plan.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    for row in data['observations']: prepare(row['key'])
    print(f'Prepared {len(observations)} bounded requests for real Ecuador case.')


def prepare(key):
    config=json.loads((WORK/'plan.json').read_text())
    if config['case']!='2435' or not 4<=len(config['observations'])<=12: raise ValueError('Unexpected plan')
    row=next(r for r in config['observations'] if r['key']==key)
    if key!=row['sensor']+'-'+date.fromisoformat(row['date']).isoformat() or row['folder']!=key:
        raise ValueError('Unsafe output key')
    if not row['date'].startswith(('2020-','2022-')): raise ValueError('Date outside case')
    payload=build_payload(row['sensor'],row['date'],config['bounds'],config['direction'])
    folder=WORK/key; folder.mkdir(exist_ok=True)
    path=folder/'request.json'
    if path.exists():
        if json.loads(path.read_text())!=payload: raise ValueError('Request changed')
    else: path.write_text(json.dumps(payload,indent=2),encoding='utf-8')


def verify_source(metadata,sensor,product):
    field='sentinel2ProductId' if sensor=='optical' else 'sentinel1ProductId'
    ids={t.get(field,'').removesuffix('.SAFE') for o in metadata.get('orbits',[]) for t in o.get('tiles',[])}
    if ids!={product}: raise ValueError('Service product differs from selected catalog scene')
    return 'product_id_matched_catalog'


def read_observation(config,row,base_folder=None):
    folder=(WORK if base_folder is None else base_folder)/row['key']; path=folder/'response.tar'
    if path.stat().st_size>5_000_000: raise ValueError('Response too large')
    expected=build_payload(row['sensor'],row['date'],config['bounds'],config['direction'],config.get('epsg',32718))
    if json.loads((folder/'request.json').read_text())!=expected: raise ValueError('Processing request differs')
    with tarfile.open(path) as tar:
        members=tar.getmembers()
        if len(members)!=2 or {m.name for m in members}!={'default.tif','userdata.json'} or any(not m.isfile() or m.size>5_000_000 for m in members):
            raise ValueError('Unsafe response members')
        metadata=json.load(tar.extractfile('userdata.json'))
        with MemoryFile(tar.extractfile('default.tif').read()) as memory, memory.open() as source:
            bands=6 if row['sensor']=='optical' else 5
            if source.crs.to_epsg()!=config.get('epsg',32718) or source.shape!=(expected['output']['height'],expected['output']['width']) or source.count!=bands or tuple(source.bounds)!=tuple(config['bounds']):
                raise ValueError('Raster grid mismatch')
            values=source.read()
    if row['sensor']=='optical':
        if not np.isin(values[4],range(12)).all() or not np.isin(values[5],[0,1]).all():
            raise ValueError('Invalid optical categorical masks')
        valid=(values[5]==1)&np.isin(values[4],[4,5,6])&np.isfinite(values).all(axis=0)
        valid&=(values[0]>=0)&(values[3]>=0)&((values[0]+values[3])>0)
    else:
        if not np.isin(values[2:4],[0,1]).all(): raise ValueError('Invalid radar masks')
        valid=(values[2]==1)&(values[3]==0)&np.isfinite(values).all(axis=0)&(values[0]>0)&(values[1]>0)
    metadata_status=verify_source(metadata,row['sensor'],row['product'])
    receipt={**row,'valid_fraction':float(valid.mean()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
             'metadata':metadata,'lineage_status':metadata_status,'valid_centres':int(valid.sum())}
    return values,valid,receipt


def report(refresh=False):
    config=json.loads((WORK/'plan.json').read_text())
    result=WORK/'resultado'
    if result.exists():
        if not refresh: print('Existing Ecuador report retained'); return
        hashes=json.loads((result/'huellas.json').read_text())
        if set(hashes)!={'INFORME.md','evidencia.json','comparacion.png'}:
            raise ValueError('Unexpected report ownership manifest')
        if any(hashlib.sha256((result/name).read_bytes()).hexdigest()!=digest for name,digest in hashes.items()):
            raise ValueError('Report modified externally; preserve user edits')
    arrays={}; masks={}; receipts={}
    for row in config['observations']:
        prepare(row['key'])
        arrays[row['key']],masks[row['key']],receipts[row['key']]=read_observation(config,row)
        print(row['key'],receipts[row['key']]['valid_fraction'],flush=True)
    best=[]
    for period in ('2020','2022'):
        candidates=[p for p in config['pairs'] if p['period']==period]
        best.append(min(candidates,key=lambda p:(-receipts[p['optical']]['valid_fraction'],p['optical'])))
    optical_common=masks[best[0]['optical']]&masks[best[1]['optical']]
    radar_common=masks[best[0]['radar']]&masks[best[1]['radar']]
    measurements=[]
    for pair in best:
        data=arrays[pair['optical']]; ndvi=np.full(data.shape[1:],np.nan)
        np.divide(data[3]-data[0],data[3]+data[0],out=ndvi,where=optical_common)
        radar=arrays[pair['radar']]
        measurements.append({'period':pair['period'],'optical':pair['optical'],'radar':pair['radar'],
            'separation_days':pair['separation_days'],
            'ndvi_mean_common':float(ndvi[optical_common].mean()) if optical_common.any() else None,
            'VV_db_of_mean_linear_common':float(10*np.log10(radar[0][radar_common].mean(dtype='float64'))) if radar_common.any() else None,
            'VH_db_of_mean_linear_common':float(10*np.log10(radar[1][radar_common].mean(dtype='float64'))) if radar_common.any() else None})
    summary={'case':'2435','area_type':config['area_type'],'bbox_utm18s':config['bounds'],
        'radar_relative_orbit':config['relative_orbit'],'radar_direction':config['direction'],
        'measurements':measurements,'optical_common_centres':int(optical_common.sum()),
        'radar_common_centres':int(radar_common.sum()),'observations':list(receipts.values()),
        'selection':config['selection'],'status':'observations_not_validated_deforestation',
        'event_date':'unknown','parcel_boundary':'not_available',
        'warning':'Dates bracket two observation periods, NOT a verified deforestation event. NDVI and radar are not fused into a decision.'}
    result.mkdir(exist_ok=refresh)
    (result/'evidencia.json').write_text(json.dumps(summary,indent=2,allow_nan=False),encoding='utf-8')
    render(result,config,best,arrays,masks)
    lines=['# Ecuador Vivo · Ecuador: radar y óptico con fechas reales','',
        '**Caso público 2435, área de observación, NO finca verificada ni dictamen EUDR.**','',
        'Área de contexto de 1 km × 1 km centrada en la referencia pública WRI; no se inventó un lindero de propiedad.',
        'La referencia humana indica agricultura permanente con confianza alta en una unidad de ~1 km para 2001–2022.',
        'Eso no identifica fecha exacta de conversión ni prueba que el cultivo sea cacao.','',
        '## Comparación','', '![Imágenes ópticas y radar](comparacion.png)','',
        'Sentinel-2 visible/NIR: grilla de 10 m; máscara SCL original de 20 m, remuestreada por vecino más cercano.',
        'Sentinel-1 RTC: grilla de 20 m, no resolución submétrica; misma órbita relativa y dirección en las dos épocas.',
        'Sin IA generativa ni superresolución. Las zonas ópticas descartadas por nubes/sombra aparecen en gris.', '',
        f'Órbita radar: {config["relative_orbit"]}, {config["direction"]}; Sentinel-1A, IW, VV/VH, gamma0 terreno, DEM Copernicus30, sin speckle.',
        f'Soporte común entre épocas: óptico {int(optical_common.sum())} centros; radar {int(radar_common.sum())} centros.', '',
        '| Época | Óptico | Radar | Separación | NDVI medio común |', '|---|---|---|---:|---:|']
    for m in measurements:
        label='Sin soporte' if m['ndvi_mean_common'] is None else f'{m["ndvi_mean_common"]:.4f}'
        lines.append(f'| {m["period"]} | {m["optical"]} | {m["radar"]} | {m["separation_days"]} días | {label} |')
    lines+=['', '## Calidad y límites','',
        '- Se examinaron tres fechas ópticas por época, preseleccionadas por nubosidad de escena; se eligió la mayor fracción válida dentro del área. No es búsqueda exhaustiva.',
        '- Nubes/sombra/nodata preservados; no se interpretan como suelo desnudo. La fracción válida depende de SCL y no es una evaluación humana de nubes. Para NDVI se excluyen reflectancias roja/NIR negativas o suma no positiva; no se recortan sus valores.',
        '- Estadísticas ópticas y radar conservadas por separado: sensores, grillas y unidades distintas. No restar sus valores entre sí.',
        '- Radar y óptico: ID de producto devuelto por el servicio coincide con la escena seleccionada del catálogo; no es validación independiente del procesamiento remoto.',
        '- No se conoce la fecha del cambio de cobertura; 2020 y 2022 son ventanas de observación, no «antes/después» de un evento probado.',
        '- Una diferencia de NDVI o retrodispersión no identifica por sí sola tala, causa ni legalidad. Humedad, cosecha, sombras y relieve requieren revisión.', '',
        '## Procedencia','', '- Copernicus Sentinel-1 GRD y Sentinel-2 L2A, API oficial autenticada; solicitudes, respuestas y huellas locales.',
        '- https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S1GRD.html',
        '- https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L2A.html',
        '- WRI / Google DeepMind, validación humana CC BY 4.0: https://zenodo.org/records/15224684', '',
        'Autor del proyecto: Henry P. Conteron Moreta · Ecuador Vivo / Andes Pulso. Revisión científica humana pendiente.']
    (result/'INFORME.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    (result/'huellas.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in result.iterdir() if p.is_file() and p.name!='huellas.json'},indent=2),encoding='utf-8')
    print(json.dumps({'optical_common':int(optical_common.sum()),'radar_common':int(radar_common.sum()),'selected':measurements}))


def render(result,config,best,arrays,masks):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,2,figsize=(10,10),layout='constrained',facecolor='#f7f2e4')
    radar_values=[10*np.log10(arrays[p['radar']][1][masks[p['radar']]]) for p in best if masks[p['radar']].any()]
    low,high=np.percentile(np.concatenate(radar_values),[2,98]) if radar_values else (-25,-5)
    if high<=low: high=low+1
    for column,pair in enumerate(best):
        data=arrays[pair['optical']]; rgb=np.moveaxis(np.clip(data[:3]/.3,0,1),0,-1)
        rgb[~masks[pair['optical']]]=[.65,.65,.65]
        axes[0,column].imshow(rgb,interpolation='nearest'); axes[0,column].set_title(pair['optical']+' · 10 m')
        radar=np.full(masks[pair['radar']].shape,np.nan)
        radar[masks[pair['radar']]]=10*np.log10(arrays[pair['radar']][1][masks[pair['radar']]])
        im=axes[1,column].imshow(radar,vmin=low,vmax=high,cmap='viridis',interpolation='nearest')
        axes[1,column].set_title(pair['radar']+' · paso 20 m')
        for axis in axes[:,column]: axis.set_xticks([]); axis.set_yticks([])
    fig.colorbar(im,ax=axes[1,:],shrink=.75,label='VH gamma0 terreno (dB) · escala visual común p2–p98')
    fig.suptitle('Ecuador Vivo / Andes Pulso · caso 2435\nÁrea de observación 1 km × 1 km, NO lindero de finca',color='#123d37')
    fig.savefig(result/'comparacion.png',dpi=160); plt.close(fig)


def verify():
    config=json.loads((WORK/'plan.json').read_text())
    result=WORK/'resultado'
    hashes=json.loads((result/'huellas.json').read_text())
    if set(hashes)!={'INFORME.md','evidencia.json','comparacion.png'}:
        raise ValueError('Unexpected output manifest')
    if any(hashlib.sha256((result/name).read_bytes()).hexdigest()!=digest for name,digest in hashes.items()):
        raise ValueError('Output integrity failure')
    saved=json.loads((result/'evidencia.json').read_text())
    receipts={r['key']:r for r in saved['observations']}
    if set(receipts)!={r['key'] for r in config['observations']}:
        raise ValueError('Observation set changed')
    for row in config['observations']:
        prepare(row['key'])
        _,_,receipt=read_observation(config,row)
        if receipt['sha256']!=receipts[row['key']]['sha256']:
            raise ValueError('Source image changed')
    print('Ecuador case: 12 source products, grids, masks and report hashes verified offline.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('mode',choices=['plan','prepare','report','verify']); parser.add_argument('--key'); parser.add_argument('--refresh',action='store_true')
    args=parser.parse_args()
    if args.mode=='plan': plan()
    elif args.mode=='prepare': prepare(args.key)
    elif args.mode=='report': report(args.refresh)
    else: verify()
