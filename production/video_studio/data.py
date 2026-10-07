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
from rasterio.mask import mask as mask_raster
from rasterio.io import MemoryFile
from rasterio.transform import from_bounds as grid_from_bounds
from rasterio.windows import Window, from_bounds
from rasterio.warp import reproject, transform_geom
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


def _polygon_means(src, band, features, *, scale=1.0, offset=0.0,
                   reject_negative=False, source_nodata=None):
    """Mean of each supplied WGS84 polygon on its native source raster.

    This deliberately happens *before* visual resampling.  Therefore the
    provincial ranking is a zonal statistic over actual source pixels, not a
    value sampled at the provincial capital nor an average of display colours.
    ``features`` must be geoJSON ADM1 features in EPSG:4326.
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
            sampled, _ = mask_raster(
                src, [native_geometry], indexes=band, crop=True, filled=False
            )
        except (ValueError, rasterio.errors.RasterioError):
            # A regional raster may not intersect an ADM1 polygon.  Missing
            # coverage remains absent; it is never converted to zero.
            continue
        values = np.ma.asarray(sampled).filled(np.nan).astype('float64')
        valid = np.isfinite(values)
        if source_nodata is not None and np.isfinite(source_nodata):
            valid &= ~np.isclose(values, source_nodata)
        if reject_negative:
            valid &= values >= 0
        if not valid.any():
            continue
        result[str(name)] = float(np.mean(values[valid] * scale + offset))
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
                samples = _chirps_point_means(src, point_samples)
                province_samples = _polygon_means(
                    src, 1, province_features, reject_negative=True
                )
        raw = values.filled(np.nan).astype('float32')
        raw[(raw < 0) | ~np.isfinite(raw)] = np.nan
        return raw, {'path': str(path), 'source_url': url, 'band': 1,
                     'point_samples': samples,
                     'province_samples': province_samples}
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
        province_samples = _polygon_means(
            src, row['band'], province_features,
            scale=project['scale'], offset=project['offset'],
            source_nodata=source_nodata,
        )
        metadata = {'path': str(path), 'band': row['band'], 'source_url': project.get('source_url', ''),
                    'native_crs': str(src.crs), 'native_transform': list(src.transform),
                    'embedded_scale': src.scales[row['band'] - 1], 'embedded_offset': src.offsets[row['band'] - 1],
                    'point_samples': {}, 'province_samples': province_samples}
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
    target = STORE / 'imports' / (digest + '.tif')
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
