"""Prepare real field plots, measure spatial support, discover bounded acquisitions."""
import json
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import math
import numpy as np
from pyproj import Transformer
from shapely.geometry import shape,box
from shapely.ops import transform
from affine import Affine
from rasterio.features import geometry_mask
from tools.parcelas.process_api import ROOT
from tools.parcelas.catalog import validate_parcel,discover,summarize_items


def eligible_plot(properties):
    return properties.get('topological_repair_applied') is False and properties.get('geometry_review')=='original_2D_geometry_valid'


def main():
    source=ROOT/'_local/parcelas/referencias/reforestree-6813783/parcelas-estudio.geojson'
    document=json.loads(source.read_text())
    base=ROOT/'_local/parcelas/parcelas-campo-ecuador'
    base.mkdir(exist_ok=True)
    reports=[]
    for feature in document['features']:
        p=feature['properties']
        if not eligible_plot(p): continue
        info=validate_parcel({'type':'FeatureCollection','features':[feature]})
        folder=base/p['plot_id']; folder.mkdir(exist_ok=True)
        parcel_path=folder/'parcela.geojson'
        if not parcel_path.exists(): parcel_path.write_text(json.dumps({'type':'FeatureCollection','features':[feature]},indent=2),encoding='utf-8')
        geometry=shape(feature['geometry'])
        center=geometry.centroid
        zone=int((center.x+180)//6)+1; epsg=(32700 if center.y<0 else 32600)+zone
        projected=transform(Transformer.from_crs(4326,epsg,always_xy=True).transform,geometry)
        support={}
        for step in (10,20):
            west,south,east,north=projected.bounds
            west=math.floor(west/step)*step; north=math.ceil(north/step)*step
            width=math.ceil((east-west)/step); height=math.ceil((north-south)/step)
            grid=Affine(step,0,west,0,-step,north)
            inside=geometry_mask([projected.__geo_interface__],(height,width),grid,invert=True)
            full=sum(projected.covers(box(west+c*step,north-(r+1)*step,west+(c+1)*step,north-r*step)) for r,c in np.argwhere(inside))
            support[str(step)]={'pixel_spacing_m':step,'epsg':epsg,'transform':list(grid)[:6],
                'shape':[height,width],'centres_inside':int(inside.sum()),'fully_contained_cells':int(full),
                'warning':'Grid-dependent geometric support, not count of independent observations or effective spatial accuracy'}
        inventories=[]
        for start,end in [('2020-10-01','2021-01-01'),('2025-10-01','2026-01-01')]:
            cache=folder/f'catalog-{start[:4]}.json'
            if cache.exists(): batch=json.loads(cache.read_text())
            else:
                items=[]; completion={}
                for collection in ('sentinel-1-grd','sentinel-2-l2a'):
                    selected,complete=discover(collection,info['bbox'],start,end)
                    items.extend(selected); completion[collection]=complete
                batch={'features':items,'pagination_complete':completion,'start':start,'end_exclusive':end,
                    'queried_utc':datetime.now(timezone.utc).isoformat()}
                cache.write_text(json.dumps(batch),encoding='utf-8')
            covering=[item for item in batch['features'] if shape(item['geometry']).covers(geometry)]
            summary=summarize_items(covering)
            inventories.append({'start':start,'end_exclusive':end,'covering_counts':{
                collection:sum(i.get('collection')==collection for i in covering) for collection in ('sentinel-1-grd','sentinel-2-l2a')},
                'radar_groups':summary['radar_groups'],'pagination_complete':batch['pagination_complete']})
            print(p['plot_id'],start, inventories[-1]['covering_counts'],flush=True)
        report={'plot_id':p['plot_id'],'source_name':p['source_name'],'area_ha':info['area_ha'],
            'source_geometry_sha256':hashlib.sha256(json.dumps(feature['geometry'],sort_keys=True).encode()).hexdigest(),
            'support':support,'inventories':inventories,'status':'ready_for_bounded_pixel_processing_not_deforestation_validation',
            'reference_year':2020,'inventory_planting_years':p['planting_years_in_inventory'],
            'boundary_type':'original valid field study polygon, not cadastral ownership',
            'drone_alignment_review':'required before treating high-resolution imagery as georeferenced ground truth',
            'event_date':'unknown','forest_before_crop':'unknown'}
        (folder/'preparacion.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        reports.append(report)
    lines=['# Ecuador Vivo · dos parcelas reales preparadas','',
        'Se excluyeron las cuatro geometrías reparadas. Se usan exclusivamente las dos geometrías originalmente válidas.',
        'Referencia ReforesTree CC BY 4.0, DOI 10.5281/zenodo.6813783. Inventario y dron reportados para 2020; revisión de alineación pendiente.', '',
        '| Parcela | Área ha | Centros 10 m / celdas completas | Centros 20 m / celdas completas |', '|---|---:|---:|---:|']
    for r in reports:
        a,b=r['support']['10'],r['support']['20']
        lines.append(f'| {r["plot_id"]} · {r["source_name"]} | {r["area_ha"]:.4f} | {a["centres_inside"]} / {a["fully_contained_cells"]} | {b["centres_inside"]} / {b["fully_contained_cells"]} |')
    lines+=['', '## Siguiente ejecución', '',
        'Usar el GeoJSON individual y sus catálogos guardados para seleccionar óptico despejado dentro de la parcela y radar de un mismo grupo entre 2020 y 2025.',
        'No reutilizar la órbita120, UTM18S ni el cuadrado de 1km del caso2435: estas son otras parcelas y su CRS/grilla están en preparacion.json.',
        'Conservar celdas de borde y soporte efectivo: las parcelas tienen pocos píxeles radar y no justifican precisión catastral ni detección de cada árbol.',
        'No se descargaron nuevas imágenes ni se consumió cuota Process API. No se validó una fecha de tala ni una historia de bosque inicial.',
        'Los catálogos indican truncamiento si existe; no interpretarlos como lista completa sin comprobar esos campos.']
    (base/'CONTINUAR-AQUI.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Prepared real field plots:',len(reports))


if __name__=='__main__': main()
