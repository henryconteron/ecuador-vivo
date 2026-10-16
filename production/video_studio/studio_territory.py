"""Export geography, independent of the interactive SIG view and layer visibility.

Only presentation is resampled. All analysis continues to use authorized native
GeoTIFFs through studio_sig_raster. Existing maqueta masks/lines/colorizer are shared.
"""
import copy
import hashlib
import json
import re
from pathlib import Path
from functools import lru_cache

DEFAULT = {'territory': 'ecuador', 'resampling': 'bilinear', 'borders': True, 'provinces': True}
LEGACY = {'territory': 'view', 'resampling': 'nearest', 'borders': False, 'provinces': False}
NOTE = 'Suavizado visual; resolución original conservada'


def validate(options):
    if (not isinstance(options, dict) or set(options) != set(DEFAULT) | ({'province'} if options.get('territory')=='province' else set())
            or options['territory'] not in ('ecuador', 'continent', 'galapagos', 'province', 'view')
            or options['resampling'] not in ('nearest', 'bilinear')
            or any(type(options[k]) is not bool for k in ('borders', 'provinces'))):
        raise ValueError('Configuración territorial o de presentación inválida.')
    if options['territory']=='province' and options['province'] not in province_names():
        raise ValueError('Selecciona una de las 24 provincias disponibles.')
    return options


def options_for(project):
    time = project['studio'].get('geography', {}).get('map_workspace', {}).get('raster_time', {})
    return copy.deepcopy(validate(time.get('presentation', DEFAULT if project.get('clip_ecuador') else LEGACY)))


def boundaries():
    """Pinned, attributed project inputs. Transform declared CRS, never guess it."""
    from data import ROOT
    from studio_validation_cache import file_revision
    paths=[ROOT/'data'/'raw'/'catalog-inputs'/f'geoBoundaries-ECU-{level}.geojson' for level in ('ADM0','ADM1')]
    tokens=[]
    for path in paths:
        stat=path.stat()
        tokens.append((str(path.resolve()),stat.st_dev,stat.st_ino,stat.st_size,stat.st_mtime_ns,file_revision(path)))
    # Cached transformed geometry, NOT a cached authorization decision. NTFS
    # change time catches changed bytes even when mtime/length are restored.
    payload,records=_boundaries(tuple(tokens))
    return json.loads(payload),json.loads(records)


@lru_cache(maxsize=4)
def _boundaries(tokens):
    from data import ROOT, BOUNDARY_URL, PROVINCES_URL, sha256
    from pyproj import CRS, Transformer
    from shapely.geometry import shape, mapping
    from shapely.ops import transform
    payloads = {}; records = []
    for level, url in (('ADM0', BOUNDARY_URL), ('ADM1', PROVINCES_URL)):
        path = ROOT / 'data' / 'raw' / 'catalog-inputs' / f'geoBoundaries-ECU-{level}.geojson'
        payload = json.loads(path.read_text(encoding='utf-8'))
        name = payload.get('crs', {}).get('properties', {}).get('name')
        if not name:
            raise ValueError('Límites territoriales sin CRS declarado.')
        crs = CRS.from_user_input(name)
        transformer = Transformer.from_crs(crs, 'OGC:CRS84', always_xy=True)
        for feature in payload['features']:
            geometry = shape(feature['geometry'])
            if geometry.geom_type not in ('Polygon', 'MultiPolygon') or geometry.is_empty or not geometry.is_valid:
                raise ValueError('Polígono territorial inválido.')
            feature['geometry'] = mapping(transform(transformer.transform, geometry))
        payloads[level] = payload
        records.append({'level': level, 'path': str(path.resolve()), 'sha256': sha256(path),
                        'native_crs': name, 'display_crs': 'OGC:CRS84', 'url': url,
                        'citation': 'geoBoundaries gbOpen; Runfola et al. (2020), William & Mary',
                        'license': 'CC BY 4.0; referencia, no límite oficial ecuatoriano'})
    return json.dumps(payloads),json.dumps(records)


def geometry(box, size, options):
    from PIL import Image
    from maqueta import build_mask_and_rings, extract_outline_rings
    if options['territory'] == 'view':
        return Image.new('L', size, 255), [], []
    payloads, _ = boundaries()
    mask, rings, _ = build_mask_and_rings(territory_payload(options), box, *size)
    provinces = extract_outline_rings(payloads['ADM1'], box, *size) if options['provinces'] else []
    return mask, rings if options['borders'] else [], provinces


def province_names():
    return sorted(f['properties']['shapeName'] for f in boundaries()[0]['ADM1']['features'])


def territory_label(options):
    return options.get('province') if options['territory']=='province' else {
        'ecuador':'Ecuador continental + Galápagos','continent':'Ecuador continental',
        'galapagos':'Galápagos','view':'Región de la vista SIG'}[options['territory']]


def territory_payload(options):
    from shapely.geometry import shape,mapping,box
    from shapely.ops import unary_union
    payloads,_=boundaries();territory=options['territory']
    if territory=='ecuador':return payloads['ADM0']
    if territory=='view':raise ValueError('La vista libre no tiene polígono territorial.')
    if territory=='continent':
        from maqueta import MAIN_BOX
        selected=unary_union([shape(f['geometry']) for f in payloads['ADM0']['features']]).intersection(box(*MAIN_BOX))
    else:
        name='Galápagos' if territory=='galapagos' else options['province']
        selected=unary_union([shape(f['geometry']) for f in payloads['ADM1']['features'] if f['properties']['shapeName']==name])
    return {'type':'FeatureCollection','features':[{'type':'Feature','properties':{},'geometry':mapping(selected)}]}


def territory_bbox(options):
    if options['territory']=='ecuador':
        from maqueta import MAIN_BOX
        return list(MAIN_BOX)
    from shapely.geometry import shape
    from shapely.ops import unary_union
    bounds=unary_union([shape(f['geometry']) for f in territory_payload(options)['features']]).bounds
    dx=(bounds[2]-bounds[0])*.03;dy=(bounds[3]-bounds[1])*.03
    return [bounds[0]-dx,bounds[1]-dy,bounds[2]+dx,bounds[3]+dy]


def recover_insets(project, sources):
    """Recover ONLY a native Galápagos window from locally cached SAME CHIRPS v2.

    No continent substitution, downloads, inferred product, date interpolation,
    or mutations of the author's document. Missing evidence stays no_coverage.
    Supplemental originals are content-addressed and sealed in the binding.
    """
    import rasterio
    import numpy as np
    from rasterio.io import MemoryFile
    from rasterio.windows import from_bounds
    from data import rain_path, sha256
    from maqueta import GALAPAGOS_BOX
    from studio_sig_raster import add_raster
    from studio_sig_layers import workspace_for
    result = []; warnings = []
    for source in sources:
        box = source['raster']['bbox']
        if box[0] <= GALAPAGOS_BOX[0] and box[2] >= GALAPAGOS_BOX[2] and box[1] <= GALAPAGOS_BOX[1] and box[3] >= GALAPAGOS_BOX[3]:
            result.append(copy.deepcopy(source)); continue
        provenance = source['provenance']
        match = re.search(r'original gzip SHA256 ([0-9a-f]{64})', provenance['citation'])
        date = source['date']
        expected_url = f'https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/{date[:4]}/chirps-v2.0.{date.replace("-", ".")}.tif.gz'
        if source['semantics'] != 'precipitation' or provenance.get('url') != expected_url or not match:
            result.append(None); warnings.append(f'{date}: Galápagos sin original del mismo producto verificable.'); continue
        try:
            path, url = rain_path(date, allow_download=False)
        except FileNotFoundError:
            result.append(None); warnings.append(f'{date}: falta cobertura local de Galápagos; recupera la ventana nativa del mismo CHIRPS v2.'); continue
        original_hash = sha256(path)
        if original_hash != match[1]:
            raise ValueError('El original CHIRPS global difiere del declarado para el continente.')
        with rasterio.open('/vsigzip/' + path.resolve().as_posix()) as ds:
            if ds.crs != rasterio.crs.CRS.from_epsg(4326):
                raise ValueError('El original CHIRPS global requiere el CRS WGS84 declarado.')
            window = from_bounds(*GALAPAGOS_BOX, ds.transform).round_offsets().round_lengths()
            values = ds.read(1, window=window, masked=True)
            # These CHIRPS v2 originals omit the nodata tag; the product declares -9999.
            values = np.where(np.ma.getmaskarray(values) | (values.data == -9999), -9999, values.data)
            profile = ds.profile.copy()
            profile.update(width=values.shape[1], height=values.shape[0], count=1,
                           transform=ds.window_transform(window), nodata=-9999, compress='deflate')
            with MemoryFile() as memory:
                with memory.open(**profile) as out:
                    out.write(values, 1)
                    out.update_tags(original_gzip_sha256=original_hash, window=json.dumps(list(window.flatten())),
                                    product='CHIRPS-2.0', observed_date=date, source_url=url)
                content = memory.read()
        candidate, lid = add_raster(project, content, 'CHIRPS v2 · Galápagos · '+date+'.tif',
            {**provenance, 'citation': provenance['citation']+' · ventana nativa Galápagos, sin remuestreo'},
            observed_date=date, variable=source['variable'], units=source['units'], semantics=source['semantics'])
        result.append(candidate['studio']['geography']['sources'][workspace_for(candidate)['layers'][lid]['source_id']])
    return result, warnings


def method(options, *, revision=3):
    suffix='RGBA v2' if revision==2 else 'RGBA v3 (province ink 90,125,142,200; outlines preserve support alpha)'
    return 'GDAL '+options['resampling']+', nearest finite native support, territorial mask after resampling, '+suffix


def composition_regions(profile):
    """Quiet editorial slots shared by the export frame and editable elements."""
    from output_profiles import adaptive_regions
    regions=adaptive_regions(profile)
    if profile.height>profile.width:
        margin=profile.margin;w=profile.width-2*margin
        regions['map']={'x':margin,'y':profile.height*.12,'width':w,'height':profile.height*.66}
        regions['metric']={'x':margin,'y':profile.height*.79,'width':w,'height':profile.height*.105}
    return regions


def element_regions(profile, layers):
    """Shared initial placement and explicit format adaptation for territorial maps."""
    from output_profiles import contain_bounds
    regions=composition_regions(profile);main=regions['map'];side=regions['metric']
    gap=max(2,min(profile.width,profile.height)*.015)
    if profile.width>profile.height:
        side={**side,'y':profile.height*.28,'height':profile.height*.22}
        inset={'x':side['x'],'y':profile.height*.56,'width':side['width']*.65,'height':profile.height*.25}
    else:
        inset={'x':main['x']+main['width']*.015,'y':main['y']+main['height']*.69,
               'width':main['width']*.26,'height':main['height']*.28}
    date={**side,'height':min(60,side['height']*.4)}
    legend={**side,'y':side['y']+date['height']+gap,'height':max(1,side['height']-date['height']-gap)}
    return {'continent':contain_bounds(layers['continent']['size'],main),
            'galapagos':contain_bounds(layers['galapagos']['size'],inset),
            'date':date,'legend_static':legend,'legend_background':legend,
            'title':regions['title'],'source':regions['source']}


def reflow_scene(scene, studio, profile):
    """Reflow only sealed Ecuador resources on an explicit format change."""
    placements={}
    for iid,instance in scene.get('map_instances',{}).items():
        record=studio['media'][instance['asset_id']]
        if record.get('geographic_presentation',{}).get('presentation',{}).get('territory')=='ecuador':
            placements[iid]=element_regions(profile,record['layers'])
    if not placements:return set()
    changed=set();slots=next(iter(placements.values()))
    for element in scene['elements']:
        binding=element.get('temporal_binding',{})
        box=placements.get(binding.get('instance_id'),{}).get(binding.get('channel'))
        role=None
        if element['type']=='source':role='source'
        elif element['name']=='Variable y unidades':role='title'
        elif element['name']=='Fondo de leyenda':role='legend_background'
        if box is None and role:box=slots[role]
        if box is not None:
            element['transform'].update(box);changed.add(element['id'])
    return changed
