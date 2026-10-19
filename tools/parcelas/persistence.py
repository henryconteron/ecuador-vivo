"""Experimental persistent signal-change candidates. NOT deforestation detection."""
from datetime import date
import json
import hashlib
import numpy as np
from affine import Affine
from rasterio.features import shapes
from rasterio.warp import transform_geom
from tools.parcelas.ecuador_case import WORK,read_observation


def persistent_drop(before,after,before_valid,after_valid,drop_db=3):
    if before.ndim!=3 or after.ndim!=3 or before.shape[1:]!=after.shape[1:] or before.shape!=before_valid.shape or after.shape!=after_valid.shape:
        raise ValueError('Mismatched temporal grids')
    if min(before.shape[0],after.shape[0])<3 or not 0<drop_db<=20:
        raise ValueError('At least three observations per epoch and explicit bounded threshold required')
    valid_before=before_valid&np.isfinite(before)&(before>0)
    valid_after=after_valid&np.isfinite(after)&(after>0)
    supported=valid_before.all(axis=0)&valid_after.all(axis=0)
    baseline=np.median(before,axis=0)
    cutoff=baseline*10**(-drop_db/10)
    return supported&(after<=cutoff).all(axis=0)


def main():
    destination=WORK/'persistencia-experimental'
    if destination.exists(): raise ValueError('Preserve existing analysis')
    config=json.loads((WORK/'plan.json').read_text())
    groups={}; receipts=[]
    for epoch in ('2020','2022'):
        rows=sorted([r for r in config['observations'] if r['sensor']=='radar' and r['date'].startswith(epoch)],key=lambda r:r['date'])
        if len(rows)<3 or (date.fromisoformat(rows[-1]['date'])-date.fromisoformat(rows[0]['date'])).days<60:
            raise ValueError('Three observations spanning at least 60 days per epoch required')
        values=[]; masks=[]
        for row in rows:
            data,valid,receipt=read_observation(config,row)
            values.append(data[1]); masks.append(valid); receipts.append(receipt)
        groups[epoch]=(np.stack(values),np.stack(masks),[r['date'] for r in rows])
    before,before_mask,dates_before=groups['2020']; after,after_mask,dates_after=groups['2022']
    flags=persistent_drop(before,after,before_mask,after_mask)
    bounds=config['bounds']; transform=Affine(20,0,bounds[0],0,-20,bounds[3])
    features=[]
    for geom,value in shapes(flags.astype('uint8'),mask=flags,transform=transform,connectivity=4):
        if value==1:
            features.append({'type':'Feature','geometry':transform_geom('EPSG:32718','EPSG:4326',geom),
                'properties':{'type':'experimental_VH_signal_drop_candidate','deforestation':'not_assessed',
                    'threshold_db':3,'post_observations_required':len(dates_after),'review':'required'}})
    summary={'status':'experimental_signal_change_only','baseline_dates':dates_before,'post_dates':dates_after,
        'method':'median linear VH baseline; >=3 dB decrease in every post observation, all dates valid',
        'threshold_origin':'heuristic engineering diagnostic; NOT calibrated or validated for forest loss',
        'candidate_centres':int(flags.sum()),'candidate_polygon_count':len(features),
        'common_centres':int((before_mask.all(axis=0)&after_mask.all(axis=0)).sum()),
        'persistent_means':'repeated at observed dates only, not proof of uninterrupted state between them',
        'baseline_forest':'not_verified','event_date':'unknown_between_epochs','deforestation_assessment':'not_performed',
        'source_hashes':{r['key']:r['sha256'] for r in receipts}}
    destination.mkdir()
    (destination/'candidatos.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},indent=2),encoding='utf-8')
    (destination/'diagnostico.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    lines=['# Ecuador Vivo · persistencia experimental de señal radar','',
        '**No es un mapa ni una prueba de deforestación.**','',
        f'{int(flags.sum())} centros de píxel con descenso VH de al menos 3 dB frente a mediana lineal de 2020, en las tres adquisiciones de 2022.',
        f'{len(features)} polígonos de celdas candidatas para revisión; no linderos de fincas ni hectáreas deforestadas.',
        'Fechas base: '+', '.join(dates_before)+'.','Fechas posteriores: '+', '.join(dates_after)+'.','',
        'El umbral de 3 dB es una hipótesis de trabajo, NO un criterio forestal validado. No se ajustó para obtener un resultado deseado.',
        'Se excluyen sombras/nodata y se exige soporte válido en todas las fechas. Persistencia significa repetición observada, no continuidad demostrada.',
        'No conocemos la cobertura forestal inicial ni la causa del cambio. Humedad, manejo, speckle y geometría pueden producir candidatos.',
        'No se fusiona esto con NDVI para emitir una decisión. Contrastar candidatos con óptico y evidencia independiente.',
        'Los polígonos GeoJSON pueden cargarse en el SIG para inspección, sin publicarlos ni alterar proyectos guardados.']
    (destination/'INFORME.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(summary))


if __name__=='__main__': main()
