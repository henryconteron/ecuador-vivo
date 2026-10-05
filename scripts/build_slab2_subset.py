"""Reproducible native-grid Slab2 crop; requires numpy and h5py (offline after download)."""
import argparse
import hashlib
import json
from pathlib import Path

import h5py
import numpy as np

BASE = 'https://apps.usgs.gov/shakemap_geodata/slabs/'
NAMES = ['sam_slab2_dep_02.23.18.grd', 'sam_slab2_unc_02.23.18.grd']
HASHES = ['0e09dc45baaf402204bdecbe3254b637e3a8f4818ff23903bf61254de3525257',
          '38b27b519c368631e52598708b24012cb0911cecbe0144b593003fb0d45c1dc0']


def build(source, destination):
    for name, expected in zip(NAMES, HASHES):
        if hashlib.sha256((source / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Source checksum mismatch: ' + name)
    with h5py.File(source / NAMES[0]) as dep, h5py.File(source / NAMES[1]) as unc:
        assert np.array_equal(dep['x'][:], unc['x'][:])
        assert np.array_equal(dep['y'][:], unc['y'][:])
        x = dep['x'][:] - 360
        y = dep['y'][:]
        ix = np.flatnonzero((x >= -83 - 1e-8) & (x <= -74.5 + 1e-8))
        iy = np.flatnonzero((y >= -5.5 - 1e-8) & (y <= 2.5 + 1e-8))
        depths = -dep['z'][:][np.ix_(iy, ix)]
        uncertainties = unc['z'][:][np.ix_(iy, ix)]
        assert np.all(depths[np.isfinite(depths)] >= 0)
        assert np.all(uncertainties[np.isfinite(uncertainties)] >= 0)
        encode = lambda a: [[round(float(v), 3) if np.isfinite(v) else None for v in row] for row in a]
        data = dict(model='Slab2 South America 2018-02-23',
                    longitude=[round(float(v), 5) for v in x[ix]],
                    latitude=[round(float(v), 5) for v in y[iy]],
                    depth_km=encode(depths), uncertainty_km=encode(uncertainties))
    destination.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(data, separators=(',', ':'), allow_nan=False) + '\n').encode()
    (destination / 'ecuador.json').write_bytes(payload)
    manifest = dict(model=data['model'], citation='Hayes (2018), doi:10.5066/F7PV6JNV',
                    article='https://doi.org/10.1126/science.aat4723', license='CC0-1.0',
                    retrieved_date='2026-10-04', source_distribution=BASE,
                    inputs=[dict(url=BASE+n, sha256=hashlib.sha256((source/n).read_bytes()).hexdigest()) for n in NAMES],
                    output=dict(path='ecuador.json', sha256=hashlib.sha256(payload).hexdigest(), bytes=len(payload)),
                    grid_spacing_degrees=0.05, rows=len(iy), columns=len(ix),
                    finite_depth_nodes=int(np.isfinite(depths).sum()),
                    method='Native grid crop; longitude minus 360; negate depth; round km to 0.001; preserve NaN as null. No interpolation or extrapolation.',
                    limits='Regional model, not direct observation or a complete plate volume. Grid spacing and decimal precision are not accuracy. Uncertainty is the supplied unc grid, not an asserted 95% interval.')
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('data/slab2'))
    args = parser.parse_args()
    build(args.source, args.output)
