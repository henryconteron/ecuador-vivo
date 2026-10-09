"""Raster access, cache reuse, and explicit date/band imports."""
import datetime as dt
import gzip
import hashlib
import json
import re
import urllib.request
import uuid
from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.mask import mask as mask_raster
from rasterio.io import MemoryFile
from rasterio.transform import from_bounds as grid_from_bounds
from rasterio.windows import Window, from_bounds
from rasterio.warp import reproject, transform_geom, transform as warp_transform
from rasterio.enums import Resampling

from model import ROOT, STORE

BOUNDARY_URL = 'https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/ECU/ADM0/geoBoundaries-ECU-ADM0.geojson'
PROVINCES_URL = 'https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/ECU/ADM1/geoBoundaries-ECU-ADM1.geojson'
PROVINCES_LOCAL = ROOT / 'data' / 'raw' / 'catalog-inputs' / 'geoBoundaries-ECU-ADM1.geojson'


def sha256(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def fetch(url, target):
    target = Path(target)
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=60) as response:
            payload = response.read()
        if target.name.endswith('.gz'):
            gzip.decompress(payload)
        else:
            json.loads(payload)
        temp = target.with_name(target.name + '.' + uuid.uuid4().hex + '.part')
        temp.write_bytes(payload)
        temp.replace(target)
    return target


def boundary():
    cached = list((ROOT / '_local' / 'climate-studio').glob('*/ecuador.geojson'))
    path = cached[0] if cached else fetch(BOUNDARY_URL, STORE / 'cache' / 'ecuador.geojson')
    return json.loads(path.read_text(encoding='utf-8'))


def province_boundaries():
    """Return the 24 ADM1 polygons used for provincial statistics.

    The repository keeps the exact geoBoundaries input used by the atlas, so
    the video studio can work offline and every receipt can name a stable
    boundary source.  The network copy is only a fallback for a standalone
    installation that does not include the catalog input.
    """
    path = PROVINCES_LOCAL
    if not path.exists():
        path = fetch(PROVINCES_URL, STORE / 'cache' / 'ecuador-adm1.geojson')
    payload = json.loads(path.read_text(encoding='utf-8'))
    features = payload.get('features', [])
    if len(features) != 24:
        raise ValueError('El límite ADM1 de Ecuador debe contener 24 provincias.')
    return features


def rain_path(date, allow_download=True):
    day = dt.date.fromisoformat(date)
    filename = f'chirps-v2.0.{day:%Y.%m.%d}.tif.gz'
    existing = list((ROOT / '_local' / 'climate-studio').glob('*/' + filename))
    url = f'https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/{day.year}/{filename}'
    target = existing[0] if existing else STORE / 'cache' / 'chirps-v2' / filename
    if not target.exists() and not allow_download:
        raise FileNotFoundError(f'{date}: todavía no está descargado.')
    return fetch(url, target), url


def scientific_file_versions(project):
    """Cheap cache invalidation for actual sources; never download on styling."""
    from model import timeline
    versions=[]
    rows=timeline(project) if project.get('source')=='chirps' else project.get('entries',[])
    for row in rows:
        try:
            path=(rain_path(row['date'],allow_download=False)[0]
                  if project.get('source')=='chirps' else Path(row['path']))
            stat=path.stat()
            versions.append((row['date'],str(path),stat.st_mtime_ns,stat.st_size))
        except FileNotFoundError:
            versions.append((row['date'],None,None,None))
    return tuple(versions)


def map_dimensions(box):
    ratio = (box[2] - box[0]) / (box[3] - box[1])
    w, h = 960, 1034
    if abs(ratio - w / h) > 0.002:
        if ratio < w / h:
            w = max(1, round(h * ratio))
        else:
            h = max(1, round(w / ratio))
    return w, h


def _chirps_point_means(src, points):
    """Return native CHIRPS neighbourhood means for named lon/lat points.

    This is intentionally sampled from the source grid rather than from the
    resampled visual map. It lets an Ecuador-wide render include Puerto
    Baquerizo Moreno (Galápagos) in its capital ranking without inventing a
    value from the continental window.
    """
    values = {}
    for name, lon, lat in points:
        try:
            row, col = src.index(lon, lat)
        except (ValueError, TypeError):
            continue
        r0, r1 = max(0, row - 1), min(src.height, row + 2)
        c0, c1 = max(0, col - 1), min(src.width, col + 2)
        if r0 >= r1 or c0 >= c1:
            continue
        sample = src.read(1, window=Window(c0, r0, c1 - c0, r1 - r0),
                          masked=True).filled(np.nan).astype('float32')
        sample = sample[np.isfinite(sample) & (sample >= 0)]
        if sample.size:
            values[name] = float(np.mean(sample))
    return values


def _polygon_stats(src, band, features, *, scale=1.0, offset=0.0,
                   reject_negative=False, source_nodata=None,
                   clip_bounds=None, include_empty=False, counts_only=False):
    """Mean, max and min of each WGS84 polygon on the *native* source raster.

    This deliberately happens before visual resampling. The provincial ranking
    is a zonal statistic over actual source pixels, not a value sampled at the
    provincial capital nor an average of display colours. The extremes are also
    native: a bilinear display grid can hide a hot pixel (a 45 °C pixel became
    25 °C in a synthetic 110 m raster), so national maxima must not be read
    from it. ``features`` must be geoJSON ADM1 features in EPSG:4326.
    """
    result = {}
    if not features or not src.crs:
        return result
    for feature in features:
        properties = feature.get('properties', {})
        name = properties.get('shapeName') or properties.get('name')
        geometry = feature.get('geometry')
        if not name or not geometry:
            continue
        try:
            native_geometry = transform_geom('EPSG:4326', src.crs, geometry,
                                             precision=9)
            sampled, out_transform = mask_raster(
                src, [native_geometry], indexes=band, crop=True, filled=False
            )
        except (ValueError, rasterio.errors.RasterioError):
            # A regional raster may not intersect an ADM1 polygon. Missing
            # coverage remains absent; it is never converted to zero.
            continue
        # Cast before filling: integer source masks cannot represent NaN.
        # https://rasterio.readthedocs.io/en/stable/topics/masks.html
        values = np.ma.asarray(sampled).astype('float64').filled(np.nan)
        domain = geometry_mask([native_geometry], out_shape=values.shape,
                               transform=out_transform, invert=True,
                               all_touched=False)
        valid = np.isfinite(values)
        if clip_bounds is not None:
            west, south, east, north = clip_bounds
            clip_geometry = {
                'type': 'Polygon',
                'coordinates': [[
                    [west, south], [east, south], [east, north],
                    [west, north], [west, south]
                ]],
            }
            native_clip = transform_geom('EPSG:4326', src.crs,
                                         clip_geometry, precision=9)
            within_frame = geometry_mask(
                [native_clip], out_shape=values.shape,
                transform=out_transform, invert=True, all_touched=False,
            )
            valid &= within_frame
            domain &= within_frame
        if source_nodata is not None and np.isfinite(source_nodata):
            valid &= values != source_nodata
        if reject_negative:
            valid &= values >= 0
        if not valid.any():
            if include_empty:
                result[str(name)] = {
                    'mean': None, 'max': None, 'min': None,
                    'valid_pixels': 0, 'total_pixels': int(domain.sum()),
                    'coverage': 0.0,
                    'weighting': (None if counts_only else 'cosine_latitude_area_approximation'
                                  if src.crs.is_geographic else 'native_pixel_mean_projected_crs'),
                }
            continue
        if counts_only:
            result[str(name)] = {
                'mean': None, 'max': None, 'min': None,
                'valid_pixels': int(valid.sum()), 'total_pixels': int(domain.sum()),
                'coverage': float(valid.sum()/domain.sum()) if domain.any() else 0.0,
                'weighting': None,
            }
            continue
        physical = values[valid] * scale + offset
        # Geographic raster cells shrink with latitude. Weight native pixels
        # by cos(latitude) so a zonal mean approximates an area mean instead
        # of over-weighting the smaller high-latitude cells. In projected
        # rasters this falls back to an ordinary pixel mean; the input CRS is
        # retained in the receipt so that choice remains auditable.
        if src.crs.is_geographic:
            rows, cols = values.shape[-2:]
            center_col = cols // 2
            xs, ys = rasterio.transform.xy(
                out_transform, np.arange(rows), np.full(rows, center_col),
                offset='center'
            )
            _, latitudes = warp_transform(src.crs, 'EPSG:4326', xs, ys)
            row_weights = np.cos(np.deg2rad(np.asarray(latitudes, dtype='float64')))
            area_weights = np.broadcast_to(
                row_weights[:, np.newaxis], values.shape[-2:]
            )
            mean_value = float(np.average(values[valid] * scale + offset,
                                          weights=area_weights[valid]))
        else:
            mean_value = float(np.mean(physical))
        result[str(name)] = {
            'mean': mean_value,
            'max': float(np.max(physical)),
            'min': float(np.min(physical)),
            'valid_pixels': int(valid.sum()),
            'total_pixels': int(domain.sum()),
            'coverage': float(valid.sum() / domain.sum()) if domain.any() else 0.0,
            'weighting': ('cosine_latitude_area_approximation'
                          if src.crs.is_geographic else 'native_pixel_mean_projected_crs'),
        }
    return result


def _polygon_means(src, band, features, **kwargs):
    """Backward-compatible view of ``_polygon_stats``: name → mean."""
    return {name: row['mean']
            for name, row in _polygon_stats(src, band, features, **kwargs).items()}


def native_domain_stats(src, band, project, *, reject_negative=False):
    """Scientific source pixels within the frame, independent of display size.

    The bbox defines the domain; clipping adds all ADM0 polygon parts, including
    holes. No geographic statistics are read from a resampled display raster.
    """
    west, south, east, north = project['bbox']
    geometry = {'type': 'Polygon', 'coordinates': [[
        [west, south], [east, south], [east, north],
        [west, north], [west, south]]]}
    if project.get('clip_ecuador', True):
        polygons = []
        for feature in boundary()['features']:
            part = feature['geometry']
            if part['type'] == 'Polygon':
                polygons.append(part['coordinates'])
            elif part['type'] == 'MultiPolygon':
                polygons.extend(part['coordinates'])
            else:
                raise ValueError('El dominio científico requiere límites poligonales.')
        geometry = {'type': 'MultiPolygon', 'coordinates': polygons}
    feature = {'type': 'Feature', 'properties': {'name': 'domain'}, 'geometry': geometry}
    categorical = project.get('kind') == 'categorical'
    stats = _polygon_stats(src, band, [feature], scale=project.get('scale', 1),
                           offset=project.get('offset', 0),
                           source_nodata=project.get('nodata'),
                           reject_negative=reject_negative,
                           clip_bounds=project['bbox'], include_empty=True,
                           counts_only=categorical).get('domain')
    result = stats or {'mean': None, 'min': None, 'max': None,
                      'valid_pixels': 0, 'total_pixels': 0, 'coverage': 0.0,
                      'weighting': (None if categorical else 'cosine_latitude_area_approximation'
                                    if src.crs.is_geographic else 'native_pixel_mean_projected_crs')}
    result.update(method='native_categorical_support' if categorical else 'native_source_pixels', calculation_method_version=2,
                  spatial_domain=('ecuador_land_within_bbox' if project.get('clip_ecuador', True)
                                  else 'source_pixels_within_bbox'),
                  bbox=list(project['bbox']), source_crs=str(src.crs))
    return result


def load_values(project, row, point_samples=(), province_features=()):
    box = project['bbox']
    if project['source'] == 'chirps':
        path, url = rain_path(row['date'])
        with MemoryFile(gzip.decompress(path.read_bytes())) as mem:
            with mem.open() as src:
                window = from_bounds(*box, transform=src.transform).round_offsets().round_lengths()
                # Read only the requested window, not the global image.
                values = src.read(1, window=window, masked=True)
                spatial_stats = native_domain_stats(src, 1, project, reject_negative=True)
                samples = _chirps_point_means(src, point_samples)
                stats = _polygon_stats(
                    src, 1, province_features, reject_negative=True,
                    clip_bounds=(None if len(province_features) == 24 else box),
                )
        province_samples = {n: r['mean'] for n, r in stats.items()}
        raw = values.astype('float32').filled(np.nan)
        raw[(raw < 0) | ~np.isfinite(raw)] = np.nan
        return raw, {'path': str(path), 'source_url': url, 'band': 1,
                     'spatial_stats': spatial_stats,
                     'point_samples': samples,
                     'province_mean_method': 'cosine_latitude_area_approximation',
                     'province_samples': province_samples,
                     'province_extremes': {n: (r['min'], r['max'])
                                           for n, r in stats.items()}}
    path = Path(row['path'])
    w, h = map_dimensions(box)
    with rasterio.open(path) as src:
        if not src.crs:
            raise ValueError(f'{path.name}: el TIFF no tiene un sistema de coordenadas.')
        if row['band'] > src.count:
            raise ValueError(f'{path.name}: no existe la banda {row["band"]}.')
        method = Resampling.nearest if project['kind'] == 'categorical' else Resampling.bilinear
        # Warp the selected band independently: multiband unified NoData can
        # incorrectly retain a missing date when a different band has valid data.
        raw = np.full((h, w), np.nan, dtype='float32')
        source_nodata = (project['nodata'] if project['nodata'] is not None
                         else src.nodata)
        reproject(source=rasterio.band(src, row['band']), destination=raw,
                  src_nodata=source_nodata,
                  dst_crs='EPSG:4326', dst_transform=grid_from_bounds(*box, w, h),
                  dst_nodata=float('nan'), resampling=method)
        continuous = project['kind'] == 'continuous'
        spatial_stats = native_domain_stats(src, row['band'], project) if continuous else None
        stats = _polygon_stats(
            src, row['band'], province_features,
            scale=project['scale'], offset=project['offset'],
            source_nodata=source_nodata,
            clip_bounds=(None if len(province_features) == 24 else box),
        ) if continuous else {}
        province_samples = {n: r['mean'] for n, r in stats.items()}
        metadata = {'path': str(path), 'band': row['band'],
                    'spatial_stats': spatial_stats,
                    'source_url': project.get('source_url', ''),
                    'provider_source_url': row.get('source_url', ''),
                    'provider_artifact_sha256': row.get('artifact_sha256', ''),
                    'native_crs': str(src.crs), 'native_transform': list(src.transform),
                    'embedded_scale': src.scales[row['band'] - 1], 'embedded_offset': src.offsets[row['band'] - 1],
                    'province_mean_method': (
                        None if not continuous else 'cosine_latitude_area_approximation'
                        if src.crs.is_geographic else 'native_pixel_mean_projected_crs'
                    ),
                    'point_samples': {}, 'province_samples': province_samples,
                    'province_extremes': {n: (r['min'], r['max'])
                                          for n, r in stats.items()}}
    raw = raw * project['scale'] + project['offset']
    if not np.isfinite(raw).any():
        raise ValueError(f'{row["date"]}: no hay datos válidos dentro del encuadre.')
    if project['kind'] == 'categorical':
        unknown = set(np.unique(raw[np.isfinite(raw)]).tolist()) - {c['value'] for c in project['classes']}
        if unknown:
            raise ValueError(f'Faltan clases en la leyenda: {sorted(unknown)[:15]}. Añádelas o define su NoData.')
    return raw, metadata


def store_upload(name, payload):
    # The supplied filename never determines a filesystem path.
    digest = hashlib.sha256(payload).hexdigest()
    extension = '.csv' if Path(name).suffix.lower() == '.csv' else '.tif'
    target = STORE / 'imports' / (digest + extension)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_bytes(payload)
    return target


def infer_date(text):
    match = re.search(r'(?<!\d)((?:19|20)\d{2})[-_.]?(0[1-9]|1[0-2])[-_.]?([0-2]\d|3[01])(?!\d)', text)
    if match:
        try:
            return str(dt.date(*(int(v) for v in match.groups())))
        except ValueError:
            pass
    return ''


def inspect_file(path, original_name):
    rows = []
    with rasterio.open(path) as src:
        if not src.crs:
            raise ValueError(f'{original_name}: falta georreferenciación.')
        if src.count > 366:
            raise ValueError('Importa como máximo 366 bandas por archivo.')
        for band in range(1, src.count + 1):
            description = src.descriptions[band - 1] or ''
            date = infer_date(description) or (infer_date(original_name) if src.count == 1 else '')
            rows.append({'usar': not any(t in description.lower() for t in ('valid_days', 'count', 'quality', 'qc_', 'qa_')),
                         'fecha': date, 'archivo': original_name, 'banda': band,
                         'nombre_banda': description, 'path': str(path)})
    return rows
