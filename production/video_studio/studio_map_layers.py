"""Private RGBA observations from maqueta; no project schema, jobs or new clock."""
import copy
import math
from pathlib import Path

import numpy as np
from PIL import Image
from rasterio.transform import from_bounds

import data
import maqueta
from model import validate
from studio_preparation import verify_sources
from studio_project import source_projection
from studio_science import restored_snapshot, _hash


def _resolution(size, box):
    if (not isinstance(size, (tuple, list)) or len(size) != 2
            or any(type(n) is not int or n < 1 for n in size)
            or math.prod(size) > 40_000_000):
        raise ValueError('Cada tile requiere dimensiones enteras positivas y como máximo 40 MP.')
    w, h = size
    ratio = (box[2] - box[0]) / (box[3] - box[1])
    if abs(h - round(w / ratio)) > 1 and abs(w - round(h * ratio)) > 1:
        raise ValueError('La resolución del tile debe conservar la proporción geográfica.')
    return w, h


class MapLayerPainter:
    """Freeze geography/settings; resolve both visual identities from one index.

    render_observation never accepts a separate date/band/trim for a layer.
    Its output is private preparation data, not a new Studio media record.
    Timeline clocks, storage and publication are subsequent subincrements.
    """

    def __init__(self, project, *, continent_size=None, galapagos_size=None):
        self._snapshot = restored_snapshot(project)
        if self._snapshot is None:
            raise ValueError('Prepara una revisión científica antes de generar capas.')
        self._source = source_projection(project)
        self._rows = validate(self._source)
        self._records = self._snapshot['source_records']
        if len(self._rows) != len(self._records) or any(
                row['date'] != record['date'] or row.get('band', 1) != record['band']
                or (self._source['source'] == 'local'
                    and Path(row['path']).resolve() != Path(record['file']).resolve())
                for row, record in zip(self._rows, self._records)):
            raise ValueError('Fechas, bandas o archivos distintos de la revisión científica.')
        verify_sources(project, self._snapshot)
        self._revision = project['project_meta']['scientific_revision']
        self._shape = copy.deepcopy(data.boundary())
        self._shape_hash = _hash(self._shape)
        self._warnings = []
        main_box, gal_box = tuple(self._source['bbox']), maqueta.GALAPAGOS_BOX
        main_size = _resolution(maqueta.main_map_size(main_box) if continent_size is None else continent_size, main_box)
        gal_size = _resolution((maqueta.GAL_W_MAX, round(maqueta.GAL_W_MAX * maqueta.GAL_ASPECT))
                               if galapagos_size is None else galapagos_size, gal_box)
        if math.prod(main_size) + math.prod(gal_size) > 80_000_000:
            raise ValueError('Las capas superan el presupuesto combinado de 80 MP.')
        self._geography = {}
        self._specs = {}
        for identifier, box, size, clip, minimum, border in (
                ('continent', main_box, main_size, self._source['clip_ecuador'], 0., 2.2),
                ('galapagos', gal_box, gal_size, True, maqueta.GAL_MIN_AREA_DEG2, 1.4)):
            mask, rings, _ = maqueta.build_mask_and_rings(self._shape, box, *size, clip=clip, min_outer_area=minimum)
            self._geography[identifier] = (mask, rings, [])
            self._specs[identifier] = {
                'id': identifier, 'bbox': list(box), 'crs': 'EPSG:4326', 'size': list(size),
                'transform': list(from_bounds(*box, *size)), 'boundary_sha256': self._shape_hash,
                'clip': clip, 'min_outer_area_deg2': minimum, 'border_width': border,
                'province_geometry_sha256': None,
                'name': ('Galápagos · inset editorial' if identifier == 'galapagos' else
                         'Ecuador continental' if main_box == maqueta.MAIN_BOX else 'Región principal · bbox seleccionado')}
        if self._source.get('show_provinces', True) and self._source['clip_ecuador']:
            try:
                provinces = copy.deepcopy(maqueta.adm1_boundary())
                rings = maqueta.extract_outline_rings(provinces, main_box, *main_size)
                self._geography['continent'][2].extend(rings)
                if rings:
                    self._specs['continent']['province_geometry_sha256'] = _hash(provinces)
            except Exception:
                self._warnings.append('No se pintaron límites provinciales: geometría no disponible.')

    @property
    def layer_specs(self):
        return copy.deepcopy(self._specs)

    @property
    def cartographic_settings(self):
        return copy.deepcopy(self._source)

    def _tile(self, identifier, values, *, disabled=False):
        grid = self._specs[identifier]
        mask, rings, provinces = self._geography[identifier]
        if self._source['kind'] == 'categorical':
            unknown = set(np.unique(values[np.isfinite(values)])) - {c['value'] for c in self._source['classes']}
            if unknown:
                raise ValueError('Faltan clases en la leyenda cartográfica de ' + identifier + '.')
        image = maqueta.paint_raster_layer(values, self._source, mask)
        count = int(np.count_nonzero(np.asarray(image.getchannel('A'))))
        if count:
            image.alpha_composite(maqueta.paint_map_outline(image.size, rings, provinces, border_width=grid['border_width']))
        else:
            image.close()
            image = Image.new('RGBA', tuple(grid['size']))
        return {'grid': copy.deepcopy(grid), 'image': image, 'data_pixels': count,
                'borders_painted': bool(count and rings), 'provinces_painted': bool(count and provinces),
                'state': 'disabled' if disabled else 'covered' if count else 'no_coverage'}

    def render_observation(self, source_index):
        if type(source_index) is not int or not 0 <= source_index < len(self._rows):
            raise ValueError('Índice de observación fuera de la revisión científica.')
        row, record = self._rows[source_index], self._records[source_index]
        if data.sha256(record['file']) != record['sha256']:
            raise ValueError('Cambió el archivo de origen de la observación.')
        # The existing inset loader uses this ADM0; reject a changed geometry
        # rather than mixing a new mask with the frozen output grid.
        if _hash(maqueta.boundary()) != self._shape_hash:
            raise ValueError('Cambió la geometría de límites durante la preparación.')
        values, metadata = data.load_values(self._source, row)
        if (Path(metadata['path']).resolve() != Path(record['file']).resolve()
                or metadata['band'] != record['band']):
            raise ValueError('Los datos de la observación no coinciden con la revisión.')
        main_size = self._specs['continent']['size']
        main = maqueta.resize_values(values, *main_size, self._source['kind'])
        gal_size = self._specs['galapagos']['size']
        enabled = self._source.get('show_galapagos', True)
        scene = maqueta.load_galapagos_scene(self._source, row['date'], *gal_size) if enabled else None
        if enabled and scene is None:
            raise ValueError('No se pudo cargar la observación de Galápagos; no se sustituye por cero.')
        gal = scene['values'] if scene is not None else np.full((gal_size[1], gal_size[0]), np.nan, dtype='float32')
        if data.sha256(record['file']) != record['sha256'] or _hash(maqueta.boundary()) != self._shape_hash:
            raise ValueError('La fuente o los límites cambiaron mientras se cargaban las capas.')
        return {'observation': {'source_index': source_index, 'date': row['date'],
                    'source': copy.deepcopy(record), 'scientific_revision': self._revision,
                    'scientific_identity': self._snapshot['scientific_identity'],
                    'native_crs': metadata.get('native_crs')},
                'layers': {'continent': self._tile('continent', main),
                           'galapagos': self._tile('galapagos', gal, disabled=not enabled)},
                'warnings': list(self._warnings),
                'rules': {'alpha': 'geographic_mask AND finite display support',
                          'main_resize': 'existing resize_values: nearest support; bounded bicubic continuous / nearest categorical',
                          'inset_reprojection': 'existing load_galapagos_scene', 'glow': False,
                          'inset_resampling': 'bilinear continuous / nearest categorical; existing loader support',
                          'local_inset_mask_threshold': 'geographic mask >64; existing loader policy',
                          'borders': 'geographic decoration, not data support', 'overlays': False,
                          'statistics_domain': 'primary bbox unchanged; inset is editorial',
                          'temporal_interpolation': False}}
