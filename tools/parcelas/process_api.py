"""Fixed, bounded Ghana reference experiment; no credentials or network access."""
import argparse
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
import tarfile

import numpy as np
import rasterio
from rasterio.io import MemoryFile
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / '_local/parcelas/piloto-352'
DATES = ('2020-12-23', '2021-01-04', '2025-03-08', '2025-03-20')
# Fixed context containing the approved public polygon; UTM 30N, exact 20 m grid.
BBOX = [528200, 754180, 529640, 755420]
EVALSCRIPT = '''//VERSION=3
function setup() {
  return {input: [{bands: ["VV", "VH", "dataMask", "shadowMask", "localIncidenceAngle"]}],
    mosaicking: "ORBIT", output: {id: "default", bands: 5, sampleType: "FLOAT32"}};
}
function evaluatePixel(samples) {
  for (let i=0; i<samples.length; i++) {
    let s=samples[i];
    if (s.dataMask) return [s.VV, s.VH, s.dataMask, s.shadowMask, s.localIncidenceAngle];
  }
  return [0,0,0,0,0];
}
function updateOutputMetadata(scenes, inputMetadata, outputMetadata) {
  outputMetadata.userData = {orbits: scenes.orbits, inputMetadata: inputMetadata,
    selection: "first available orbit sample; no temporal averaging",
    bands: ["VV", "VH", "dataMask", "shadowMask", "localIncidenceAngle"]};
}
'''


def build_request(day, allowed_dates=DATES):
    if day not in allowed_dates:
        raise ValueError('Date outside approved four-date experiment')
    next_day = (date.fromisoformat(day) + timedelta(days=1)).isoformat()
    return {'input': {'bounds': {'bbox': BBOX,
                'properties': {'crs': 'http://www.opengis.net/def/crs/EPSG/0/32630'}},
            'data': [{'type': 'sentinel-1-grd', 'dataFilter': {
                'timeRange': {'from': day+'T00:00:00Z', 'to': next_day+'T00:00:00Z'},
                'acquisitionMode': 'IW', 'polarization': 'DV',
                'orbitDirection': 'ASCENDING', 'resolution': 'HIGH'},
                'processing': {'backCoeff': 'GAMMA0_TERRAIN', 'orthorectify': True,
                    'demInstance': 'COPERNICUS_30', 'speckleFilter': {'type': 'NONE'},
                    'upsampling': 'NEAREST', 'downsampling': 'NEAREST'}}]},
            'output': {'width': 72, 'height': 62, 'responses': [
                {'identifier': 'default', 'format': {'type': 'image/tiff'}},
                {'identifier': 'userdata', 'format': {'type': 'application/json'}}]},
            'evalscript': EVALSCRIPT}


def output_folder(day):
    if day not in DATES:
        raise ValueError('Unplanned date')
    return PILOT / ('api-rtc-'+day.replace('-', '') + ('-trazable' if day == '2025-03-20' else ''))


def source_product(metadata):
    identifiers = {tile['sentinel1ProductId'].removesuffix('.SAFE')
                   for orbit in metadata.get('orbits', []) for tile in orbit.get('tiles', [])
                   if tile.get('sentinel1ProductId')}
    if len(identifiers) != 1:
        raise ValueError('Exactly one service source product required')
    return identifiers.pop()


def inspect(day, write=True, folder=None):
    folder = output_folder(day) if folder is None else Path(folder)
    archive = folder / 'response.tar'
    if archive.stat().st_size > 5_000_000:
        raise ValueError('Response exceeds limit')
    with tarfile.open(archive) as tar:
        members = tar.getmembers()
        if len(members) != 2 or {m.name for m in members} != {'default.tif', 'userdata.json'}:
            raise ValueError('Unexpected response members; no filesystem extraction')
        if any(not m.isfile() or m.size > 5_000_000 for m in members):
            raise ValueError('Invalid response member')
        metadata = json.load(tar.extractfile('userdata.json'))
        with MemoryFile(tar.extractfile('default.tif').read()) as mem, mem.open() as src:
            if src.count != 5 or src.crs.to_epsg() != 32630 or src.shape != (62, 72):
                raise ValueError('Unexpected raster contract')
            if tuple(src.bounds) != tuple(BBOX) or src.res != (20, 20):
                raise ValueError('Unexpected grid')
            data = src.read()
            if not np.isin(data[2:4], [0, 1]).all():
                raise ValueError('Unexpected mask values')
            parcel = json.loads((ROOT/'_local/parcelas/referencias/cersgis-16579443/parcela-piloto.geojson').read_text())
            geom = transform_geom('EPSG:4326', src.crs, parcel['features'][0]['geometry'])
            inside = geometry_mask([geom], src.shape, src.transform, invert=True)
            valid = inside & (data[2] == 1) & (data[3] == 0)
            valid &= np.isfinite(data).all(axis=0) & (data[0] > 0) & (data[1] > 0)
            report = {'date': day, 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
                'crs': str(src.crs), 'transform': list(src.transform)[:6],
                'shape': list(src.shape), 'bands': metadata.get('bands'),
                'parcel_centres': int(inside.sum()), 'usable_centres': int(valid.sum()),
                'shadow_centres': int((inside & (data[3] == 1)).sum()),
                'incidence_range_degrees': [float(data[4][valid].min()), float(data[4][valid].max())] if valid.any() else None,
                'metadata': metadata,
                'source_product_ids': [tile['sentinel1ProductId']
                    for orbit in metadata.get('orbits', []) for tile in orbit.get('tiles', [])
                    if tile.get('sentinel1ProductId')],
                'warning': 'Diagnostic only. shadowMask is not a complete layover/terrain QA or deforestation detector.'}
    if write:
        output = folder / 'inspection.json'
        with output.open('x', encoding='utf-8') as stream:
            json.dump(report, stream, indent=2, allow_nan=False)
        print(json.dumps({k:v for k,v in report.items() if k != 'metadata'}, indent=2))
    return report, data, valid


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'inspect'])
    parser.add_argument('day', choices=DATES)
    args = parser.parse_args()
    if args.mode == 'inspect':
        inspect(args.day)
    else:
        folder = output_folder(args.day)
        folder.mkdir(exist_ok=False)
        (folder/'request.json').write_text(json.dumps(build_request(args.day), indent=2), encoding='utf-8')
        print('Prepared bounded request; no remote processing executed.')
