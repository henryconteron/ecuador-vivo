"""Bounded observations of original valid ReforesTree field polygons; not certification."""
import argparse
from collections import defaultdict
from datetime import date
import hashlib
import json
import re
import numpy as np
from affine import Affine
from pyproj import Transformer
from rasterio.features import geometry_mask
from shapely.geometry import shape, box
from shapely.ops import transform
from tools.parcelas.ecuador_case import build_payload, read_observation
from tools.parcelas.field_cases import eligible_plot
from tools.parcelas.process_api import ROOT

BASE=ROOT/'_local/parcelas/parcelas-campo-ecuador'
WORK=BASE/'observaciones'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def field(plot):
    path=BASE/plot/'parcela.geojson'
    feature=json.loads(path.read_text())['features'][0]
    if not eligible_plot(feature['properties']): raise ValueError('Original valid geometry required')
    geometry=shape(feature['geometry'])
    if not geometry.is_valid: raise ValueError('Invalid polygon')
    projected=transform(Transformer.from_crs(4326,32717,always_xy=True).transform,geometry)
    x,y=(round(v/20)*20 for v in (projected.centroid.x,projected.centroid.y))
    bounds=[x-100,y-100,x+100,y+100]
    if not box(*bounds).covers(projected): raise ValueError('Field outside bounded context')
    return geometry,projected,{'epsg':32717,'bounds':bounds,'parcel_sha256':digest(path)}

def create_plan():
    observations={}; fields={}; pairs=[]
    for plot in ('RF05','RF06'):
        geometry,_,config=field(plot)
        optical=[]; groups=defaultdict(list)
        for year in (2020,2025):
            batch=json.loads((BASE/plot/f'catalog-{year}.json').read_text())
            if not all(batch['pagination_complete'].values()): raise ValueError('Incomplete catalogue')
            items=[i for i in batch['features'] if shape(i['geometry']).covers(geometry)]
            by_day={}
            for i in sorted(items,key=lambda i:(i['properties'].get('eo:cloud_cover',100),i['id'])):
                p=i['properties']
                if i['collection']=='sentinel-2-l2a': by_day.setdefault(p['datetime'][:10],i)
                elif p.get('platform')=='sentinel-1a' and p.get('sar:instrument_mode')=='IW' and {'VV','VH'}.issubset(p.get('sar:polarizations',[])):
                    groups[(p['sat:relative_orbit'],p['sat:orbit_state'])].append(i)
            if len(by_day)<3: raise ValueError('Insufficient optical candidates')
            optical.extend(list(by_day.values())[:3])
        viable=[]
        for group,candidates in groups.items():
            matches=[]
            for o in optical:
                day=date.fromisoformat(o['properties']['datetime'][:10])
                ranked=sorted(candidates,key=lambda r:(abs((date.fromisoformat(r['properties']['datetime'][:10])-day).days),r['id']))
                r=ranked[0]; delta=abs((date.fromisoformat(r['properties']['datetime'][:10])-day).days)
                matches.append((delta,r))
            if max(m[0] for m in matches)<=12: viable.append((sum(m[0] for m in matches),group,matches))
        if not viable: raise ValueError('No compatible radar group')
        _,group,matches=min(viable,key=lambda v:(v[0],v[1]))
        config.update(direction=group[1].upper(),relative_orbit=group[0]); fields[plot]=config
        for o,(delta,r) in zip(optical,matches):
            keys=[]
            for sensor,item in (('optical',o),('radar',r)):
                day=item['properties']['datetime'][:10]; key=f'{plot}-{sensor}-{day}'
                observations[key]={'key':key,'folder':key,'plot_id':plot,'sensor':sensor,'date':day,'product':item['id']}
                keys.append(key)
            pairs.append({'plot_id':plot,'period':o['properties']['datetime'][:4],'optical':keys[0],'radar':keys[1],'separation_days':delta})
    return {'case':'RF05-RF06','fields':fields,'observations':list(observations.values()),'pairs':pairs}

def plan():
    WORK.mkdir(exist_ok=True)
    proposed=create_plan(); path=WORK/'plan.json'
    if path.exists():
        if json.loads(path.read_text())!=proposed: raise ValueError('Existing plan differs; preserve it')
    else: path.write_text(json.dumps(proposed,indent=2),encoding='utf-8')
    print('Bounded observations:',len(proposed['observations']))

def load_plan():
    saved=json.loads((WORK/'plan.json').read_text())
    if saved!=create_plan(): raise ValueError('Plan/source changed')
    return saved

def prepare(key):
    config=load_plan()
    if not re.fullmatch(r'RF0[56]-(optical|radar)-(2020|2025)-\d{2}-\d{2}',key): raise ValueError('Unsafe key')
    row=next(r for r in config['observations'] if r['key']==key)
    f=config['fields'][row['plot_id']]
    payload=build_payload(row['sensor'],row['date'],f['bounds'],f['direction'],f['epsg'])
    folder=WORK/key; folder.mkdir(exist_ok=True); path=folder/'request.json'
    if path.exists():
        if json.loads(path.read_text())!=payload: raise ValueError('Request changed')
    else: path.write_text(json.dumps(payload,indent=2),encoding='utf-8')

def support(geometry,bounds,step):
    west,south,east,north=bounds; n=int((east-west)/step)
    inside=geometry_mask([geometry.__geo_interface__],(n,n),Affine(step,0,west,0,-step,north),invert=True)
    full=np.zeros_like(inside)
    for r,c in np.argwhere(inside):
        full[r,c]=geometry.covers(box(west+c*step,north-(r+1)*step,west+(c+1)*step,north-r*step))
    return inside,full

def report(refresh=False):
    config=load_plan(); result=WORK/'resultado'
    if result.exists():
        verify()
        if not refresh: print('Verified existing report retained'); return
    arrays={}; masks={}; receipts=[]
    for row in config['observations']:
        data,mask,receipt=read_observation(config['fields'][row['plot_id']],row,WORK)
        arrays[row['key']]=data; masks[row['key']]=mask; receipts.append(receipt)
    summaries=[]; figures={}
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    for plot in ('RF05','RF06'):
        _,geometry,_=field(plot); f=config['fields'][plot]
        supports={sensor:support(geometry,f['bounds'],step) for sensor,step in (('optical',10),('radar',20))}
        best=[]
        for year in ('2020','2025'):
            candidates=[p for p in config['pairs'] if p['plot_id']==plot and p['period']==year]
            best.append(min(candidates,key=lambda p:(-int((masks[p['optical']]&supports['optical'][0]).sum()),p['optical'])))
        measurements=[]; counts={}
        for sensor in ('optical','radar'):
            common=masks[best[0][sensor]]&masks[best[1][sensor]]
            for label,spatial in zip(('centres','full_cells'),supports[sensor]):
                valid=common&spatial; counts[f'{sensor}_{label}']=int(valid.sum())
                for p in best:
                    d=arrays[p[sensor]]
                    value=None
                    if valid.any():
                        value=float(((d[3][valid]-d[0][valid])/(d[3][valid]+d[0][valid])).mean(dtype='float64')) if sensor=='optical' else float(10*np.log10(d[1][valid].mean(dtype='float64')))
                    measurements.append({'period':p['period'],'sensor':sensor,'support':label,'value':value,'unit':'NDVI' if sensor=='optical' else 'VH gamma0 terrain dB of mean linear'})
        summaries.append({'plot_id':plot,'selected':best,'common_valid_support':counts,'measurements':measurements})
        fig,axes=plt.subplots(2,2,figsize=(9,9),layout='constrained',facecolor='#f7f2e4')
        west,south,east,north=f['bounds']; extent=[west,east,south,north]
        geometries=list(geometry.geoms) if hasattr(geometry,'geoms') else [geometry]
        for col,p in enumerate(best):
            d=arrays[p['optical']]; rgb=np.moveaxis(np.clip(d[:3]/.3,0,1),0,-1); rgb[~masks[p['optical']]]=.65
            axes[0,col].imshow(rgb,extent=extent,interpolation='nearest')
            d=arrays[p['radar']]; radar=np.full(d.shape[1:],np.nan); v=masks[p['radar']]; radar[v]=10*np.log10(d[1][v])
            image=axes[1,col].imshow(radar,extent=extent,vmin=-30,vmax=-5,cmap='viridis',interpolation='nearest')
            for row,sensor in enumerate(('optical','radar')):
                axes[row,col].set_title(p[sensor]); axes[row,col].set_xticks([]); axes[row,col].set_yticks([])
                if not (masks[p[sensor]]&supports[sensor][0]).any():
                    axes[row,col].text(.5,.93,'SIN DATOS VÁLIDOS EN LA PARCELA',transform=axes[row,col].transAxes,
                        ha='center',fontsize=9,color='white',bbox={'facecolor':'#333333','alpha':.85,'pad':5})
                for g in geometries:
                    x,y=g.exterior.xy; axes[row,col].plot(x,y,color='#ff5555',linewidth=1.5)
        fig.colorbar(image,ax=axes[1,:],label='VH gamma0 terreno (dB) · escala común')
        fig.suptitle(f'Ecuador Vivo · {plot}\nContexto 200 × 200 m; lindero de estudio en rojo, no catastral')
        figures[plot]=fig
    result.mkdir(exist_ok=refresh)
    evidence={'status':'observations_not_validated_deforestation','plan_sha256':digest(WORK/'plan.json'),'plots':summaries,'observations':receipts}
    (result/'evidencia.json').write_text(json.dumps(evidence,indent=2,allow_nan=False),encoding='utf-8')
    lines=['# Ecuador Vivo · parcelas reales RF05 y RF06','', 'Comparación exploratoria 2020–2025, no certificación ni demostración de deforestación.', '',
        'Referencia: ReforesTree, CC BY 4.0, https://zenodo.org/records/6813783. Polígonos originales válidos, no límites catastrales.',
        'Óptico: reflectancia Sentinel-2 L2A a paso 10 m; QA SCL de 20 m con vecino más cercano. Radar: Sentinel-1A IW VV/VH, gamma0 terreno, paso 20 m, sin filtro speckle.',
        'Tres candidatos ópticos por época, preseleccionados por nubosidad de escena; selección final por soporte válido dentro de la parcela. Radar de una misma órbita relativa por parcela, separación máxima 12 días.',
        'Las estadísticas usan soporte válido común entre épocas; se muestran centros interiores y celdas totalmente contenidas por separado. No son observaciones independientes ni una precisión posicional.',
        'Gris en el óptico = datos descartados por QA; no significa suelo desnudo ni pérdida de vegetación. Contexto exterior visible únicamente como referencia; no entra en las estadísticas.',
        'Octubre–diciembre agrupa meses distintos: la estacionalidad, el manejo y la humedad siguen siendo factores de confusión. Dos fechas no demuestran una tendencia persistente.', '']
    for s in summaries:
        plot=s['plot_id']; figures[plot].savefig(result/f'{plot}.png',dpi=160); plt.close(figures[plot])
        counts=s['common_valid_support']; f=config['fields'][plot]
        lines.extend([f'## {plot}',f'![Comparación {plot}]({plot}.png)',
            f"Radar: órbita relativa {f['relative_orbit']}, {f['direction']}; EPSG:{f['epsg']}.",
            f"Soporte común óptico: {counts['optical_centres']} centros / {counts['optical_full_cells']} celdas completas. Radar: {counts['radar_centres']} centros / {counts['radar_full_cells']} celdas completas.",
            '', '| Época | Óptico | Radar | Separación |','|---|---|---|---:|'])
        for p in s['selected']: lines.append(f"| {p['period']} | {p['optical']} | {p['radar']} | {p['separation_days']} días |")
        lines.extend(['', '| Época | Sensor | Soporte | Valor | Unidad |','|---|---|---|---:|---|'])
        for m in s['measurements']:
            value=f"{m['value']:.4f}" if m['value'] is not None else 'Sin soporte'
            lines.append(f"| {m['period']} | {m['sensor']} | {m['support']} | {value} | {m['unit']} |")
    lines.extend(['','NDVI no identifica tala. Cambios de radar pueden reflejar humedad, estructura, manejo o geometría. Pocas celdas completas, nubes y errores de registro limitan las inferencias.',
        'No se conoce fecha de tala ni bosque previo; años de siembra del inventario no son fechas de deforestación. Revisión humana y referencia histórica independiente pendientes.',
        'Métodos del proveedor: https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S1GRD.html y https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L2A.html',
        'Autor: Henry P. Conteron Moreta · Ecuador Vivo / Andes Pulso.'])
    (result/'INFORME.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    (result/'huellas.json').write_text(json.dumps({p.name:digest(p) for p in result.iterdir() if p.is_file() and p.name!='huellas.json'},indent=2),encoding='utf-8')
    print(json.dumps([s['common_valid_support'] for s in summaries]))

def verify():
    config=load_plan(); result=WORK/'resultado'
    hashes=json.loads((result/'huellas.json').read_text())
    if set(hashes)!={'INFORME.md','evidencia.json','RF05.png','RF06.png'}: raise ValueError('Unexpected manifest')
    if any(digest(result/name)!=value for name,value in hashes.items()): raise ValueError('Output changed')
    saved=json.loads((result/'evidencia.json').read_text())
    if saved['plan_sha256']!=digest(WORK/'plan.json'): raise ValueError('Plan changed')
    receipts={r['key']:r for r in saved['observations']}
    if set(receipts)!={r['key'] for r in config['observations']}: raise ValueError('Missing receipts')
    for row in config['observations']:
        _,_,receipt=read_observation(config['fields'][row['plot_id']],row,WORK)
        if receipt!=receipts[row['key']]: raise ValueError('Source changed')
    print('Verified field sources, product IDs, grids and report hashes offline')

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('action',choices=['plan','prepare','report','verify']); parser.add_argument('--key'); args=parser.parse_args()
    if args.action=='prepare': prepare(args.key)
    else: {'plan':plan,'report':report,'verify':verify}[args.action]()
