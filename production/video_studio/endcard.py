"""Cierre editorial calculado a partir de los mismos rásteres del video.

El cierre no usa una imagen externa: se dibuja con Pillow y conserva la zona
segura de la maqueta. Las cifras se calculan al recorrer las fechas exportadas
para que el MP4 y su recibo puedan auditarse juntos.

Layout: todas las coordenadas de ``compose_endcard`` están medidas sobre la
imagen de referencia (941 x 1672 px) y se escalan con ``K`` al ancho real del
lienzo, de modo que el cierre sale igual a la maqueta aprobada.
"""

import calendar
import datetime as dt
import math
from collections import defaultdict

import numpy as np
from PIL import Image, ImageColor, ImageDraw

from data import boundary, load_values, province_boundaries
from rasterio.features import bounds as geometry_bounds
from variables import endcard_copy, resolve_aggregation, section_2_title
from layout_engine import (begin_layout, finish_layout, scene_for, attach_layout,
                           place_layer, draw as layout_draw)
from maqueta import (
    DESIGN_CROP,
    HEIGHT,
    SAFE_BOTTOM,
    SAFE_LEFT,
    SAFE_RIGHT,
    SAFE_TOP,
    WIDTH,
    build_mask_and_rings,
    compose_final,
    draw_database_icon,
    draw_instagram_icon,
    draw_line,
    draw_mountain_icon,
    draw_tiktok_icon,
    fit_text,
    gradient_text,
    make_font,
    outline_layer,
    text_bbox,
    text_width,
)


# Capitales provinciales kept only for older projects and compatibility with
# prior receipts. New cards rank the 24 provincial polygons, not these points.
CAPITALS = [
    ('Tena', -77.813, -0.994),
    ('Puyo', -77.983, -1.492),
    ('Nueva Loja', -76.886, -0.963),
    ('Quito', -78.468, -0.181),
    ('Guayaquil', -79.889, -2.170),
    ('Cuenca', -79.005, -2.900),
    ('Riobamba', -78.647, -1.663),
    ('Ibarra', -78.120, 0.351),
    ('Santo Domingo', -79.175, -0.254),
    ('Ambato', -78.624, -1.249),
    ('Latacunga', -78.616, -0.934),
    ('Tulcán', -77.723, 0.812),
    ('Babahoyo', -79.535, -1.802),
    ('Machala', -79.960, -3.258),
    ('Santa Elena', -80.858, -2.227),
    ('Azogues', -78.848, -2.740),
    ('Guaranda', -79.002, -1.593),
    ('Portoviejo', -80.454, -1.055),
    ('Loja', -79.204, -3.993),
    ('Esmeraldas', -79.652, 0.968),
    ('Zamora', -78.955, -4.067),
    ('Macas', -78.111, -2.309),
    ('Puerto Fco. de Orellana', -76.990, -0.462),
    ('Pto. Baquerizo Moreno', -89.617, -0.905),
]

MONTHS = ('ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN',
          'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC')
MONTH_NAMES = ('Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
               'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre',
               'Diciembre')

# --- Escala de la imagen de referencia -------------------------------------
REF_W = 941
# The endcard is authored in the 941 px reference system, then placed inside
# maqueta.DESIGN_CROP. Fit to the crop width so the lower credits remain inside
# the safe vertical video instead of being clipped by compose_final().
K = (DESIGN_CROP[2] - DESIGN_CROP[0]) / REF_W


def _s(value):
    """Coordenada de la referencia -> píxeles del lienzo."""
    return value * K


# Color (izquierda, derecha) de cada barra del ranking, medido de la imagen.
BAR_COLORS = [
    ('#ED3264', '#F73958'), ('#FD655C', '#FD694E'), ('#FC9A5D', '#FE9F60'),
    ('#FCCD68', '#FDCC64'), ('#C1EA92', '#E4ED86'), ('#A2E6A2', '#A9E8A3'),
    ('#63DCC3', '#3FD6D5'), ('#3AD1E2', '#30CFE9'), ('#2DBBF5', '#2BBEF5'),
    ('#29A7F9', '#28ADF8'), ('#289FF9', '#28A1FC'), ('#2C77DB', '#2E76D9'),
    ('#31C6DB', '#B3EA9D'), ('#35CBE8', '#93E6AD'), ('#2DC2F1', '#48DDD5'),
    ('#2BB9F4', '#37D0DC'), ('#28B5F5', '#33CDE2'), ('#2BABF7', '#2EC4ED'),
    ('#29A0F9', '#28B6F6'), ('#2995F6', '#26A3F7'), ('#2A8DF5', '#279CF7'),
    ('#2985EC', '#2988EA'), ('#2B79E1', '#2C7AE0'), ('#2E71DA', '#3175DF'),
]

# Geometría de cada sección (px de la referencia).
SECTIONS = {
    1: dict(panel=(22.5, 230, 918, 533), chip_y=248, div=(253, 285),
            title_ref=('2024 EN CIFRAS', 285), title_base=285,
            note_x=468, note_ref=('Así se comportó la lluvia', 220),
            note_base=(265.5, 287.5), line_y=268.5, line_end=889),
    2: dict(panel=(22.5, 549.5, 918, 1050), chip_y=567, div=(573, 605),
            title_ref=('¿DÓNDE LLOVIÓ MÁS?', 343), title_base=603,
            note_x=517, note_ref=('Capitales provinciales · Ranking 1–12', 324),
            note_base=(601,), line_y=594.5, line_end=898),
    3: dict(panel=(22.5, 1066.5, 918, 1538), chip_y=1082, div=(1088, 1119),
            title_ref=('CIUDADES 13–24', 273), title_base=1116,
            note_x=462, note_ref=('Continuación del ranking.', 228),
            note_base=(1114,), line_y=1107, line_end=889),
}

# Panel de ranking: primer centro de fila, paso, eje y columna de nombres.
RANK_PANELS = {
    2: dict(first_c=642.5, pitch=28.77, axis_y=981, name_x=104.5,
            grid_top=632),
    3: dict(first_c=1151.5, pitch=27.77, axis_y=1472, name_x=106,
            grid_top=1135),
}
AXIS_X0 = 287.5      # x del cero
# Leave a clear label gutter to the right of the last bar. Values are always
# drawn outside their bars, including the largest ranked city.
AXIS_W = 535.0       # ancho útil del eje (0 -> último tick)
AXIS_END = AXIS_X0 + AXIS_W


def _land_mask(geojson, box, shape):
    """Rasterize the selected boundary at the source-array resolution."""
    height, width = shape
    mask, _, _ = build_mask_and_rings(geojson, box, width, height, clip=True)
    return np.asarray(mask) > 64


class SummaryAccumulator:
    """Collect reproducible summary values while the video is rendered."""

    def __init__(self, project, boundary_geojson):
        self.project = project
        self.boundary = boundary_geojson
        self.box = tuple(float(v) for v in project['bbox'])
        self.daily = []
        self.monthly_values = defaultdict(list)
        self.monthly_dates = defaultdict(set)
        self.annual_values = defaultdict(list)
        self.region_sums = defaultdict(float)
        self.region_counts = defaultdict(int)
        self.n_observed = 0
        self.spatial_coverage = []
        self.rank_features = self._selected_provinces()
        # National native extremes are only meaningful when the frame is the
        # whole country (23 continental provinces + Galápagos polygon).
        self.national = len(self.rank_features) == 24
        self.rank_names = {
            feature.get('properties', {}).get('shapeName')
            for feature in self.rank_features
        }
        # Retained as a harmless compatibility attribute for callers of an
        # early editor build. Province polygons now supply Galápagos directly.
        self.out_of_frame_points = ()

    @staticmethod
    def _intersects(box, feature):
        left, bottom, right, top = geometry_bounds(feature['geometry'])
        return not (right < box[0] or left > box[2]
                    or top < box[1] or bottom > box[3])

    def _selected_provinces(self):
        """Provinces relevant to this map, with Galápagos on national cards.

        The standard continental frame intentionally leaves the Pacific gap
        out of the map. When it includes all 23 continental provinces, this
        method explicitly adds the Galápagos ADM1 polygon as province 24.
        A regional frame remains regional and never receives an unrelated
        island statistic.
        """
        try:
            features = province_boundaries()
        except (OSError, ValueError):
            return []
        mainland = [
            feature for feature in features
            if feature.get('properties', {}).get('shapeName') != 'Galápagos'
            and self._intersects(self.box, feature)
        ]
        galapagos = [
            feature for feature in features
            if feature.get('properties', {}).get('shapeName') == 'Galápagos'
        ]
        if len(mainland) == 23:
            return mainland + galapagos
        return [feature for feature in features if self._intersects(self.box, feature)]

    @property
    def aggregation(self):
        """Temporal operator selected for the physical meaning of the data."""
        return resolve_aggregation(self.project)[0]

    @property
    def profile(self):
        return resolve_aggregation(self.project)[1]

    def _area_weights(self, shape):
        """Cell-area proxy for the EPSG:4326 grid used by every render.

        The exporter reprojects local rasters to WGS84. Multiplying each row
        by cos(latitude) avoids treating a degree-wide cell near the northern
        edge as exactly the same physical area as one near the southern edge.
        """
        height, width = shape
        lat = self.box[3] - ((np.arange(height) + .5) / height
                             * (self.box[3] - self.box[1]))
        return np.broadcast_to(
            np.cos(np.deg2rad(lat))[:, np.newaxis], (height, width)
        )

    def observe(self, date, values, point_samples=None, province_samples=None,
                province_extremes=None, *, spatial_stats=None):
        self.n_observed += 1
        values = np.asarray(values, dtype='float32')
        # Values below zero are legitimate for temperature, anomalies and
        # spectral indices. CHIRPS invalid negatives are removed in data.py.
        valid = np.isfinite(values)
        domain_count = values.size
        if self.project.get('clip_ecuador', True):
            try:
                domain = _land_mask(self.boundary, self.box, values.shape)
                domain_count = int(domain.sum())
                valid &= domain
            except Exception:
                # A custom non-Ecuador bbox may not intersect the country polygon;
                # preserving the source values is safer than silently dropping all.
                pass

        coverage = (int(valid.sum()) / domain_count if domain_count else 0.0)
        if spatial_stats is not None:
            coverage = spatial_stats['coverage']
        self.spatial_coverage.append((date, coverage))

        if spatial_stats is not None and spatial_stats.get('mean') is None:
            return
        if spatial_stats is None and not valid.any():
            return

        if spatial_stats is not None:
            mean_value = spatial_stats['mean']
            max_value = spatial_stats['max']
            min_value = spatial_stats['min']
            extreme_source = 'native_source_pixels'
        else:
            # Compatibility for callers supplying arrays directly; explicitly
            # identified in the receipt. Normal preview/export supply native stats.
            land_values = values[valid]
            weights = self._area_weights(values.shape)[valid]
            mean_value = float(np.average(land_values, weights=weights))
            max_value = float(np.max(land_values))
            min_value = float(np.min(land_values))
            extreme_source = 'display_grid'
        # Extremes come from the native raster (zonal pass over the 23
        # continental provinces) whenever available: the display grid can
        # alias away a fine-resolution peak. Galápagos is left out so that
        # mean and extremes describe the same domain as the map frame.
        if spatial_stats is None and self.national and province_extremes:
            native = [ext for name, ext in province_extremes.items()
                      if name in self.rank_names and name != 'Galápagos']
            if len(native) == 23:
                min_value = float(min(e[0] for e in native))
                max_value = float(max(e[1] for e in native))
                extreme_source = 'native_source_pixels'
        day = dt.date.fromisoformat(date)
        self.daily.append({
            'date': date,
            'mean': mean_value,
            'maximum': max_value,
            'minimum': min_value,
            'extreme_source': extreme_source,
            'mean_source': 'native_source_pixels' if spatial_stats is not None else 'display_grid',
            'weighting': (spatial_stats['weighting'] if spatial_stats is not None
                          else 'cosine_latitude_area_approximation'),
        })
        # Keep the year in the key: a multi-year project must not merge every
        # January into a fictitious "wettest month".
        self.monthly_values[(day.year, day.month)].append(mean_value)
        self.monthly_dates[(day.year, day.month)].add(day)
        self.annual_values[day.year].append(mean_value)

        # Province statistics arrive from the native source raster (before
        # display resampling). Thus “Napo” means all valid source pixels inside
        # Napo's ADM1 polygon, not the pixel under Tena or a provincial capital.
        for name, sample in (province_samples or {}).items():
            if (name in self.rank_names and sample is not None
                    and np.isfinite(sample)):
                self.region_sums[name] += float(sample)
                self.region_counts[name] += 1

    def to_dict(self):
        days = sorted(self.daily, key=lambda row: row['date'])
        if not days:
            return {
                'days': 0,
                'year': None,
                'aggregation': self.aggregation,
                'cadence': self.project.get('cadence'),
                'units': self.project.get('units', ''),
                'aggregate_units': self.project.get('units', ''),
                'spatial_weighting': 'cosine latitude',
                'mean_daily': None,
                'wettest_day': None,
                'wettest_day_value': None,
                'rainiest_day': None,
                'rainiest_day_mean': None,
                'wettest_month': None,
                'wettest_month_number': None,
                'wettest_month_value': None,
                'wettest_month_mean': None,
                'city_rank': [],
                'scope': 'Sin datos válidos dentro del encuadre.',
            }

        # These names are retained for receipts created by earlier versions;
        # the editorial card below uses the generic peak_* fields.
        wettest_day = max(days, key=lambda row: row['maximum'])
        rainiest_day = max(days, key=lambda row: row['mean'])
        warnings = list(self.profile['warnings'])
        cadence = self.project.get('cadence', 'Diaria')
        valid_dates = len(days)
        if valid_dates < self.n_observed:
            warnings.append(
                f'{self.n_observed - valid_dates} observación(es) no tuvieron '
                'píxeles válidos en el encuadre; se excluyeron del resumen.'
            )
        lowest_coverage = min(self.spatial_coverage, key=lambda row: row[1],
                              default=None)
        if lowest_coverage and lowest_coverage[1] < 0.999:
            warnings.append(
                f'Cobertura espacial incompleta: el mínimo fue '
                f'{lowest_coverage[1]:.1%} el {lowest_coverage[0]}; '
                'los promedios usan solo píxeles válidos.'
            )

        def complete(key, n):
            # A partial calendar month must never compete with full ones:
            # with a constant 5 mm/day, a 31-day month beats a 29-day one and
            # the first/last month of a custom range would always lose.
            if cadence != 'Diaria':
                return True
            return n == calendar.monthrange(*key)[1]

        if cadence == 'Anual':
            candidates = self.annual_values
            period_metric = {
                year: (sum(values) if self.aggregation == 'sum'
                       else float(np.mean(values)))
                for year, values in candidates.items() if values
            }
            peak_year, month_value = max(period_metric.items(),
                                         key=lambda item: item[1])
            month_year, month_number = peak_year, None
            month_days = len(candidates[peak_year]) or 1
        else:
            candidates = {k: v for k, v in self.monthly_values.items()
                          if v and complete(k, len(self.monthly_dates[k]))}
            if not candidates:
                candidates = {k: v for k, v in self.monthly_values.items() if v}
                warnings.append('Ningún mes está completo: el mes destacado usa '
                                'datos parciales y no es comparable.')
            elif len(candidates) < len([v for v in self.monthly_values.values() if v]):
                warnings.append('Los meses incompletos se excluyen del mes destacado.')
            period_metric = {
                month: (sum(values) if self.aggregation == 'sum'
                        else float(np.mean(values)))
                for month, values in candidates.items()
            }
            (month_year, month_number), month_value = max(
                period_metric.items(), key=lambda item: item[1]
            )
            month_days = len(self.monthly_values[(month_year, month_number)]) or 1
        aggregate_units = (
            (self.project.get('endcard_accumulated_units', '').strip()
             or self.profile['accumulated_unit'])
            if self.aggregation == 'sum' else self.project.get('units', '').strip()
        )
        total_dates = max(1, self.n_observed)
        provinces = [
            {
                'name': name,
                'value': (total if self.aggregation == 'sum'
                          else total / self.region_counts[name]),
                'days': self.region_counts[name],
                'coverage': self.region_counts[name] / total_dates,
            }
            for name, total in self.region_sums.items()
            if self.region_counts[name]
        ]
        provinces.sort(key=lambda row: row['value'], reverse=True)
        partial = [r for r in provinces if r['coverage'] < 1.0]
        if partial and self.aggregation == 'sum':
            worst = min(partial, key=lambda r: r['coverage'])
            warnings.append(
                f'{len(partial)} provincia(s) con fechas sin dato; su '
                f'acumulado queda subestimado (peor caso: {worst["name"]}, '
                f'{worst["coverage"]:.0%} de cobertura).')
        elif partial:
            warnings.append(f'{len(partial)} provincia(s) con fechas sin dato; '
                            'su promedio usa solo las fechas válidas.')
        if self.national and len(provinces) < 24:
            warnings.append(f'Solo {len(provinces)} de 24 provincias tienen '
                            'datos válidos.')
        mean_period = float(np.mean([row['mean'] for row in days]))
        years = {dt.date.fromisoformat(row['date']).year for row in days}
        project_year = next(iter(years)) if len(years) == 1 else None
        period_name = (str(month_year) if cadence == 'Anual'
                       else MONTHS[month_number - 1])
        weightings = {row['weighting'] for row in days}
        weighting_label = (
            'promedio espacial de píxeles nativos en CRS proyectado, sin pesos '
            'geográficos (no presupone una proyección equivalente)'
            if weightings == {'native_pixel_mean_projected_crs'} else
            'promedio espacial ponderado por área aproximada (coseno de latitud)'
            if len(weightings) == 1 else 'promedio espacial con métodos de ponderación mixtos'
        )
        continental_domain = (self.box == (-81.5, -5.2, -75.0, 1.8)
                              and self.project.get('clip_ecuador', True))
        spatial_domain = ('ecuador_continental' if continental_domain else
                          'ecuador_land_within_bbox' if self.project.get('clip_ecuador', True)
                          else 'source_pixels_within_bbox')
        if self.national:
            domain_label = ('Ecuador continental del mapa principal' if continental_domain
                            else 'encuadre seleccionado del mapa principal')
            scope = (
                f'Promedio y extremos: {domain_label}; {weighting_label}. '
                'Ranking: 24 provincias, incluida Galápagos; cada '
                'valor es el promedio espacial de píxeles nativos válidos.'
            )
        else:
            scope = (
                f'Encuadre seleccionado: {weighting_label}; ranking: promedio espacial '
                'de la porción visible de cada provincia, usando píxeles nativos '
                'válidos dentro del encuadre.'
            )
        extreme_sources = {row['extreme_source'] for row in days}
        mean_sources = {row['mean_source'] for row in days}
        mean_method = next(iter(mean_sources)) if len(mean_sources) == 1 else 'mixed'
        extreme_method = (
            next(iter(extreme_sources)) if len(extreme_sources) == 1 else 'mixed'
        )
        if extreme_method == 'mixed':
            warnings.append(
                'Los máximos combinan píxeles fuente y la rejilla visual según '
                'la fecha; revisa la cobertura antes de interpretarlos.'
            )
        elif extreme_method == 'display_grid':
            warnings.append(
                'El máximo se obtuvo de la rejilla remuestreada para el mapa; '
                'puede suavizar extremos respecto al GeoTIFF fuente.'
            )
        return {
            'days': len(days),
            'observed_period': {'start': days[0]['date'], 'end': days[-1]['date']},
            'year': project_year,
            'aggregation': self.aggregation,
            'cadence': self.project.get('cadence'),
            'units': self.project.get('units', '').strip(),
            'aggregate_units': aggregate_units,
            'spatial_weighting': next(iter(weightings)) if len(weightings) == 1 else 'mixed',
            'mean_method': mean_method,
            'calculation_method_version': 2 if mean_method == 'native_source_pixels' else 1,
            'spatial_domain': spatial_domain,
            'ranking_spatial_domain': 'ecuador_24_provinces' if self.national else 'province_parts_within_bbox',
            'mean_period': mean_period,
            'peak_date': rainiest_day['date'],
            'peak_date_mean': rainiest_day['mean'],
            'peak_pixel_date': wettest_day['date'],
            'peak_pixel_value': wettest_day['maximum'],
            'minimum_pixel_value': min(row['minimum'] for row in days),
            'extreme_method': extreme_method,
            'peak_month': period_name,
            'peak_month_number': month_number,
            'peak_month_year': month_year,
            'peak_month_value': month_value,
            'peak_period_kind': 'year' if cadence == 'Anual' else 'month',
            'variable_kind': self.profile['kind'],
            'decimals': self.profile['decimals'],
            'signed': self.profile['signed'],
            'warnings': warnings,
            'city_rank_units': aggregate_units,
            'province_rank': provinces,
            'ranking_kind': 'provinces',
            'national_extent': self.national,
            # Backward-compatible aliases for older receipts and projects.
            'mean_daily': mean_period,
            'wettest_day': wettest_day['date'],
            'wettest_day_value': wettest_day['maximum'],
            'rainiest_day': rainiest_day['date'],
            'rainiest_day_mean': rainiest_day['mean'],
            'wettest_month': period_name,
            'wettest_month_number': month_number,
            'wettest_month_value': month_value,
            'wettest_month_mean': (month_value if cadence == 'Anual'
                                   else month_value / month_days),
            # city_rank remains for receipt compatibility with the first
            # release; it now contains provincial, not capital, statistics.
            'city_rank': provinces,
            'scope': scope,
        }


def summary_for_project(project, rows, boundary_geojson=None, *, progress=None, cancelled=None):
    """Build an end-card summary for preview or a reproducible export."""
    accumulator = SummaryAccumulator(project, boundary_geojson or boundary())
    for index, row in enumerate(rows):
        if cancelled and cancelled():
            raise InterruptedError('Preparación científica cancelada.')
        values, metadata = load_values(
            project, row, province_features=accumulator.rank_features
        )
        accumulator.observe(
            row['date'], values,
            metadata.get('point_samples'), metadata.get('province_samples'),
            metadata.get('province_extremes'),
            spatial_stats=metadata.get('spatial_stats')
        )
        if progress:
            progress(index + 1, len(rows), row['date'])
    if cancelled and cancelled():
        raise InterruptedError('Preparación científica cancelada.')
    return accumulator.to_dict()


def _fmt(value, unit='', decimals=1):
    if value is None:
        return 'N/D'
    return (f'{value:.{decimals}f}'
            + (f' {unit.strip()}' if unit and unit.strip() else ''))


def _date_label(value, year=False):
    if not value:
        return 'N/D'
    day = dt.date.fromisoformat(value)
    if year:
        return str(day.year)
    return f'{day.day:02d} {MONTHS[day.month - 1].lower()}'


def _period_label(value, cadence='Diaria', include_year=False):
    if not value:
        return 'N/D'
    day = dt.date.fromisoformat(value)
    if cadence == 'Anual':
        return str(day.year)
    if cadence == 'Mensual':
        return f'{MONTH_NAMES[day.month - 1]} {day.year}'
    if cadence == 'Por observación':
        return f'{day.day:02d} {MONTHS[day.month - 1].lower()} {day.year}'
    if include_year and cadence == 'Diaria':
        return f'{day.day:02d} {MONTHS[day.month - 1].lower()} {day.year}'
    return _date_label(value)


def _month_name(summary):
    if summary.get('peak_period_kind') == 'year':
        return str(summary.get('peak_month_year', 'N/D'))
    number = summary.get('peak_month_number', summary.get('wettest_month_number'))
    month = summary.get('peak_month', summary.get('wettest_month'))
    if not number and month in MONTHS:
        number = MONTHS.index(month) + 1
    if not number:
        return 'N/D'
    label = MONTH_NAMES[number - 1]
    peak_year = summary.get('peak_month_year')
    return f'{label} {peak_year}' if peak_year and summary.get('year') is None else label


# --- Helpers de texto -------------------------------------------------------

_SIZE_CACHE = {}


def _size_for(kind, ref_text, ref_w):
    """Tamaño de fuente con el que ``ref_text`` mide ``ref_w`` px de la
    referencia usando la fuente real del proyecto (así el ancho coincide con
    la imagen aunque cambie la familia tipográfica)."""
    key = (kind, ref_text, ref_w)
    if key not in _SIZE_CACHE:
        target = ref_w * K
        lo, hi = 6, 400
        while lo < hi:
            mid = (lo + hi + 1) // 2
            left, _, right, _ = text_bbox(make_font(kind, mid), ref_text)
            if right - left <= target:
                lo = mid
            else:
                hi = mid - 1
        _SIZE_CACHE[key] = lo
    return _SIZE_CACHE[key]


def _fit(kind, ref, text, max_w=None):
    """Fuente calibrada con ``ref=(texto, ancho_ref)``; se encoge si ``text``
    no cabe en ``max_w`` (px de la referencia)."""
    size = _size_for(kind, ref[0], ref[1])
    limit = _s(max_w) if max_w else WIDTH
    return fit_text(kind, size, int(limit), text)


def _ink(draw, x, y, text, font, fill):
    """Texto con la tinta empezando en x (baseline en y)."""
    left, _, _, _ = text_bbox(font, text)
    draw.text((x - left, y), text, font=font, fill=fill, anchor='ls')


def _ink_width(font, text):
    left, _, right, _ = text_bbox(font, text)
    return right - left


def _center(draw, x, y, text, font, fill):
    draw.text((x, y), text, font=font, fill=fill, anchor='ms')


def _parts(draw, x, y, parts, font):
    """Varios tramos de color en una misma línea."""
    left, _, _, _ = text_bbox(font, parts[0][0])
    x -= left
    for text, color in parts:
        draw.text((x, y), text, font=font, fill=color, anchor='ls')
        x += draw.textlength(text, font=font)


def _wrap(text, font, max_px):
    """Corta en dos líneas como mucho (la segunda toma el resto)."""
    words = text.split()
    line = ''
    for i, word in enumerate(words):
        trial = f'{line} {word}'.strip()
        if line and _ink_width(font, trial) > max_px:
            return [line, ' '.join(words[i:])]
        line = trial
    return [line]


# --- Helpers gráficos -------------------------------------------------------

def _gradient_bar(design, x0, y0, x1, y1, left, right, radius):
    """Barra con degradado horizontal, borde izquierdo recto y derecho
    redondeado."""
    w = max(2, int(round(x1 - x0)))
    h = max(2, int(round(y1 - y0)))
    ss = 4
    mask = Image.new('L', (w * ss, h * ss), 0)
    md = ImageDraw.Draw(mask)
    r = int(radius * ss)
    md.rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), radius=r, fill=255)
    md.rectangle((0, 0, min(r, w * ss - 1), h * ss - 1), fill=255)
    mask = mask.resize((w, h), Image.Resampling.LANCZOS)
    c1 = np.array(ImageColor.getrgb(left), dtype='float32')
    c2 = np.array(ImageColor.getrgb(right), dtype='float32')
    t = np.linspace(0, 1, w, dtype='float32')[None, :, None]
    row = c1[None, None, :] * (1 - t) + c2[None, None, :] * t
    arr = np.repeat(row, h, axis=0).astype('uint8')
    bar = Image.fromarray(arr, 'RGB').convert('RGBA')
    bar.putalpha(mask)
    place_layer(design, bar, (int(round(x0)), int(round(y0))), kind='data', editable=False, label='Barra calculada')


def _dashed_v(draw, x, y0, y1, color, dash=3, gap=4):
    y = y0
    while y < y1:
        draw.line((x, y, x, min(y + dash, y1)), fill=color, width=1)
        y += dash + gap


def _stamp_icon(design, painter, box, color):
    """Dibuja un icono de maqueta (``painter(draw, x, y, color)``) en una capa
    aparte y lo escala para que ocupe ``box`` (px de la referencia)."""
    x0, y0, x1, y1 = (_s(v) for v in box)
    scene = scene_for(design)
    key = scene.key('stamp_icon') if scene else None
    if scene and scene.overrides.get(key, {}).get('icon'):
        from editorial import stamp_icon
        diameter = max(1, round(min(x1-x0, y1-y0)))
        tile = Image.new('RGBA', (diameter, diameter))
        stamp_icon(tile, diameter/2, diameter/2, scene.overrides[key]['icon'], diameter=diameter)
        place_layer(design, tile, (round((x0+x1-diameter)/2), round((y0+y1-diameter)/2)),
                    key=key, kind='icon', label='Icono', icon=scene.overrides[key]['icon'])
        return
    origin = 200
    layer = Image.new('RGBA', (900, 900), (0, 0, 0, 0))
    painter(ImageDraw.Draw(layer), origin, origin, color)
    bbox = layer.getchannel('A').getbbox()
    if bbox is None:
        return
    icon = layer.crop(bbox)
    scale = min((x1 - x0) / icon.width, (y1 - y0) / icon.height)
    size = (max(1, round(icon.width * scale)), max(1, round(icon.height * scale)))
    icon = icon.resize(size, Image.Resampling.LANCZOS)
    place_layer(design, icon, (round((x0 + x1) / 2 - size[0] / 2),
                              round((y0 + y1) / 2 - size[1] / 2)), key=key, kind='icon', label=painter.__name__)


def _icon_circle(design, cx, cy, painter):
    """Círculo oscuro de 78 px (ref) con un icono vectorial dentro,
    suavizado con supersampling."""
    scene = scene_for(design)
    key = scene.key('icon') if scene else None
    if scene and scene.overrides.get(key, {}).get('icon'):
        from editorial import stamp_icon
        tile = Image.new('RGBA', (round(80*K), round(80*K)))
        stamp_icon(tile, tile.width/2, tile.height/2, scene.overrides[key]['icon'], diameter=tile.width)
        place_layer(design, tile, (round(_s(cx)-tile.width/2), round(_s(cy)-tile.height/2)),
                    key=key, kind='icon', label='Icono de métrica', icon=scene.overrides[key]['icon'])
        return
    ss = 4
    side = int(round(80 * K * ss))
    u = K * ss
    mid = side / 2

    def p(x, y):
        return (mid + x * u, mid + y * u)

    layer = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse((*p(-39, -39), *p(39, 39)), fill='#172F3F')
    painter(d, p, u)
    out = int(round(80 * K))
    layer = layer.resize((out, out), Image.Resampling.LANCZOS)
    place_layer(design, layer, (round(_s(cx) - out / 2), round(_s(cy) - out / 2)),
                key=key, kind='icon', label='Icono de métrica')


def _paint_cloud(d, p, u):
    gray = '#DADFE7'
    d.rounded_rectangle((*p(-24, -11), *p(25, 4)), radius=7 * u, fill=gray)
    d.ellipse((*p(-15.5, -26.5), *p(13.5, 2.5)), fill=gray)
    d.ellipse((*p(-21, -15), *p(-5, 1)), fill=gray)
    d.ellipse((*p(2, -15), *p(20, 3)), fill=gray)
    blue = '#38A8F0'
    drops = [(-16, 14.8, 1.0), (0, 13, 1.0), (15.4, 14.8, 1.0),
             (-7.3, 22.9, 0.85), (6.4, 23.3, 0.85)]
    for x, y, s in drops:
        r = 2.7 * s
        d.ellipse((*p(x - r, y + 1.5 * s - r), *p(x + r, y + 1.5 * s + r)),
                  fill=blue)
        d.polygon([p(x, y - 5.2 * s), p(x - r * 0.95, y + 0.6 * s),
                   p(x + r * 0.95, y + 0.6 * s)], fill=blue)


def _paint_calendar(d, p, u):
    white = '#F2F6F9'
    d.rounded_rectangle((*p(-22.5, -21.5), *p(22.5, 24.5)), radius=3 * u,
                        fill=white)
    d.rounded_rectangle((*p(-22.5, -21.5), *p(22.5, -6)), radius=3 * u,
                        fill='#3DA9F0')
    d.rectangle((*p(-22.5, -9), *p(22.5, -6)), fill=white)
    d.rectangle((*p(-17.5, -5.5), *p(17.5, 19.5)), fill='#17364F')
    for x in (-10.0, -3.4, 3.2, 9.8):
        for y in (3.8, 11.4):
            d.rounded_rectangle((*p(x - 2.1, y - 2.5), *p(x + 2.1, y + 2.5)),
                                radius=0.8 * u, fill='#2F90E8')
    for x in (-10.8, 10.3):
        d.rounded_rectangle((*p(x - 1.6, -25.6), *p(x + 1.6, -17.5)),
                            radius=1.4 * u, fill=white)


def _paint_bars(d, p, u):
    blue = '#3DB0F5'
    for x0, x1, y0, color in ((-22, -10, 2.6, blue),
                              (-6.7, 5.3, -10, '#F4F7F9'),
                              (9, 21, -24.2, blue)):
        d.rounded_rectangle((*p(x0, y0), *p(x1, 24)), radius=2.5 * u,
                            fill=color)


def _paint_mountain(d, p, u):
    apex, left, right = (-0.7, -27.2), (-28.2, 22.2), (28.5, 22.2)
    d.polygon([p(*apex), p(*left), p(*right)], fill='#142C42')
    snow = [apex, (-14.7, -1.95), (-9.9, -4.9), (-5.3, -1.95), (-0.2, -0.3),
            (5.1, -3.1), (9.6, -1.95), (13.3, -1.95)]
    d.polygon([p(*pt) for pt in snow], fill='#C9D6E1')
    pts = [p(*apex), p(*left), p(*right), p(*apex)]
    d.line(pts, fill='#F2F5F7', width=int(2.9 * u), joint='curve')
    for pt in pts[:3]:
        r = 1.45 * u
        d.ellipse((pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r),
                  fill='#F2F5F7')


def _paint_thermometer(d, p, u):
    white, hot = '#F2F6F9', '#FF775E'
    d.rounded_rectangle((*p(-7, -28), *p(7, 16)), radius=6 * u,
                        outline=white, width=max(2, int(3 * u)))
    d.ellipse((*p(-13, 10), *p(13, 36)), fill=hot, outline=white,
              width=max(2, int(3 * u)))
    d.rounded_rectangle((*p(-3, -4), *p(3, 21)), radius=2 * u, fill=hot)
    for y in (-15, -6, 3):
        d.line([p(8, y), p(16, y)], fill=white, width=max(1, int(2 * u)))


def _paint_wind(d, p, u):
    color = '#E8F2F6'
    for points in (
        [(-27, -13), (1, -13), (15, -8), (7, -2)],
        [(-32, 0), (14, 0), (27, 5), (18, 12)],
        [(-23, 14), (-2, 14), (7, 20)],
    ):
        d.line([p(x, y) for x, y in points], fill=color,
               width=max(2, int(3 * u)), joint='curve')


def _paint_index(d, p, u):
    colors = ('#55E6D1', '#6FB7FF', '#F4D276')
    for i, color in enumerate(colors):
        y = -12 + i * 12
        d.arc((*p(-25 + i * 2, y - 10), *p(25 - i * 2, y + 10)),
              start=205, end=335, fill=color, width=max(2, int(3 * u)))


def _paint_pin(d, p, u):
    """Location icon for geographic records, not a rainfall-cloud default."""
    color = '#55E6D1'
    d.ellipse((*p(-20, -25), *p(20, 15)), fill=color)
    d.polygon([p(-16, 6), p(0, 30), p(16, 6)], fill=color)
    d.ellipse((*p(-8, -14), *p(8, 2)), fill='#102b36')


def _icon_for_profile(kind):
    return {
        'temperature': _paint_thermometer,
        'wind_speed': _paint_wind,
        'index': _paint_index,
    }.get(kind, _paint_cloud)


def _nice_step(max_value, intervals=8, fill=0.92):
    """Paso 'redondo' del eje para que la barra mayor quede en ~90 %."""
    if not max_value or max_value <= 0:
        return 1.0
    raw = max_value / fill / intervals
    mag = 10 ** math.floor(math.log10(raw))
    # Finer multipliers keep the longest bar near 90 % of the axis (with
    # 1/2/2.5/5/10 a 4 096 mm maximum used only 51 % of the width).
    for mult in (1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if mult * mag >= raw:
            return round(mult * mag, 10)
    return 10 * mag


# --- Paneles ----------------------------------------------------------------

def _section_header(draw, index, title, note, accent, white, muted):
    sec = SECTIONS[index]
    x0, y0, x1, y1 = sec['panel']
    draw.rounded_rectangle((_s(x0), _s(y0), _s(x1), _s(y1)), radius=_s(20),
                           outline='#285C78', width=2)
    chip_y = sec['chip_y']
    draw.rounded_rectangle((_s(46), _s(chip_y), _s(90), _s(chip_y + 42)),
                           radius=_s(8), fill=accent)
    chip_font = _fit('bold', ('01', 25), f'{index:02d}', 40)
    _center(draw, _s(68), _s(chip_y + 29), f'{index:02d}', chip_font,
            '#06131C')
    dx = 118.5 if index < 3 else 117
    draw.line((_s(dx), _s(sec['div'][0]), _s(dx), _s(sec['div'][1])),
              fill='#6F8793', width=2)

    # Título (en 2 y 3 la última palabra va en acento).
    title = title.strip().upper()
    tfont = _fit('display', sec['title_ref'], title, 330 if index == 1 else 340)
    base = _s(sec['title_base'])
    if index == 1:
        parts = [(title, '#CFF3EF')]
    else:
        head, _, tail = title.rpartition(' ')
        core = tail.rstrip('?!.')
        parts = [(f'{head} ', white)] if head else []
        parts.append((core, accent))
        if tail[len(core):]:
            parts.append((tail[len(core):], white))
    _parts(draw, _s(150), base, parts, tfont)
    title_end = _s(150) + _ink_width(tfont, title)

    # Nota a la derecha del título.
    note_x = max(_s(sec['note_x']), title_end + _s(24))
    # Keep the annotation inside the rounded panel even when the user edits
    # its wording in the Streamlit editor.
    note_max = max(120, sec['line_end'] - sec['note_x'] - 24)
    nfont = _fit('regular', sec['note_ref'], note, note_max)
    if len(sec['note_base']) == 2:
        lines = _wrap(note, nfont, _s(236))
    else:
        lines = [note]
    note_end = note_x
    for text, bl in zip(lines, sec['note_base']):
        _ink(draw, note_x, _s(bl), text, nfont, '#E4EEF3')
        note_end = max(note_end, note_x + _ink_width(nfont, text))
    line_x0 = note_end + _s(20)
    line_x1 = _s(sec['line_end'])
    if line_x1 - line_x0 > _s(12):
        draw.line((line_x0, _s(sec['line_y']), line_x1, _s(sec['line_y'])),
                  fill='#8FA4AF', width=2)


def _ranking_panel(draw, design, project, index, first_rank, entries,
                   axis_max, step, label, unit, white, axis_min=0.0,
                   decimals=1, spread_rows=False):
    geo = RANK_PANELS[index]
    axis_y = geo['axis_y']
    muted = '#C3D0D8'
    # Rejilla vertical punteada y eje.
    for i in range(1, 9):
        x = AXIS_X0 + i * AXIS_W / 8
        _dashed_v(draw, round(_s(x)), round(_s(geo['grid_top'])),
                  round(_s(axis_y)), '#17394A')
    draw.line((_s(AXIS_X0), _s(geo['grid_top']), _s(AXIS_X0), _s(axis_y)),
              fill='#34464F', width=1)
    zero_x = (AXIS_X0 + AXIS_W * (0 - axis_min) / (axis_max - axis_min)
              if axis_min < 0 else AXIS_X0)
    draw.line((_s(zero_x), _s(geo['grid_top']), _s(zero_x), _s(axis_y)),
              fill='#667986', width=2)
    draw.line((_s(AXIS_X0), _s(axis_y), _s(AXIS_END), _s(axis_y)),
              fill='#667986', width=2)
    tick_font = _fit('regular', ('160', 23), '160')
    for i in range(9):
        x = AXIS_X0 + i * AXIS_W / 8
        draw.line((_s(x), _s(axis_y), _s(x), _s(axis_y + 5)), fill='#667986',
                  width=1)
        _center(draw, _s(x), _s(axis_y + 27.5),
                f'{round(axis_min + i * step, 6):g}', tick_font, muted)
    lab_font = _fit('regular', ('Acumulado en 2024 (mm)', 234), label,
                    420)
    _center(draw, _s(586), _s(axis_y + 55), label, lab_font, muted)

    if not entries:
        text = 'No hay provincias con datos dentro del encuadre.'
        _ink(draw, _s(104), _s(axis_y - 170), text,
             _fit('regular', ('Continuación del ranking.', 228), text, 700),
             muted)
        return

    colors = project.get('rank_bar_colors') or BAR_COLORS
    chip_font = _fit('bold', ('12', 17), '12')
    name_ref = ('Pto. Fco. de Orellana', 164.5)
    val_ref = ('142.6 mm', 72)
    for idx, row in enumerate(entries[:12]):
        c = (geo['grid_top'] + (axis_y - geo['grid_top']) * (idx + .5) / len(entries)
             if spread_rows and len(entries) <= 6 else geo['first_c'] + idx * geo['pitch'])
        rank = first_rank + idx
        # Chip del puesto.
        draw.rounded_rectangle((_s(48), _s(c - 9), _s(88), _s(c + 13)),
                               radius=_s(5), fill='#173042')
        _center(draw, _s(68), _s(c + 7), str(rank), chip_font, white)
        # Nombre.
        nfont = _fit('regular', name_ref, row['name'], 175)
        _ink(draw, _s(geo['name_x']), _s(c + 7), row['name'], nfont, white)
        # Barra.
        # The axis may start below zero (anomalies, sub-zero temperatures);
        # a bar is always the distance from the axis start to the value, so a
        # negative value is never drawn as a fake 6 px stub.
        value_x = (AXIS_X0 + AXIS_W * (row['value'] - axis_min)
                   / (axis_max - axis_min))
        left, right = colors[min(rank - 1, len(colors) - 1)]
        bar_start, bar_end = sorted((zero_x, value_x))
        # Keep the zero crossing exact for negative values. Extending a bar to
        # an arbitrary minimum width can make a tiny anomaly look larger and
        # cross the zero line, which is scientifically misleading.
        if abs(bar_end - bar_start) < 1:
            bar_end = bar_start + 1
        _gradient_bar(design, _s(bar_start), _s(c - 9.75), _s(bar_end), _s(c + 9.75),
                      left, right, _s(4))
        # Valor.
        value = _fmt(row['value'], unit, decimals)
        vfont = _fit('bold', val_ref, value)
        # The gutter created by AXIS_W keeps this label outside the coloured
        # bar for every value, including the maximum.
        if row['value'] < 0:
            # Put negative labels just to the right of zero, outside the bar.
            # Left-aligned labels can collide with long province names.
            _ink(draw, _s(zero_x + 11), _s(c + 7.5), value, vfont, white)
        else:
            _ink(draw, _s(bar_end + 11), _s(c + 7.5), value, vfont, white)


def compose_endcard(project, summary):
    """Render the editable closing card at the project's output size."""
    if summary.get('findings') and summary.get('period_values'):
        from editorial import compose_temporal_closing
        return compose_temporal_closing(project, summary)
    bg = project['background']
    white = project['text']
    accent = project['accent']
    muted = '#BCD0D8'
    profile = resolve_aggregation(project)[1]
    copy = endcard_copy(project, summary, profile)
    if summary.get('comparison_copy'):
        copy.update(summary['comparison_copy'])
    design = begin_layout(Image.new('RGBA', (WIDTH, HEIGHT), bg), project, 'endcard')
    draw = layout_draw(design)

    # Marca + filete.
    brand = project['brand'].upper()
    bfont = _fit('bold', ('ECUADOR VIVO / ANDES PULSO', 363), brand, 372)
    _ink(draw, _s(64), _s(47.5), brand, bfont, accent)
    end = _s(64) + _ink_width(bfont, brand)
    draw.line((end + _s(22), _s(36.5), end + _s(66), _s(36.5)),
              fill='#8E9BA5', width=2)

    # Título: primera palabra en blanco, el resto con degradado.
    title = project['endcard_title'].strip().upper()
    first, *rest = title.split()
    rest = ' '.join(rest)
    tsize = _size_for('display', 'MÉTRICAS FINALES', 746)
    title_font = fit_text('display', tsize, 970, title)
    gap = round(_s(20) * title_font.size / tsize)
    x = _s(65)
    # The reference font has a taller ascender than the original mock-up. Move
    # the title down a little so it cannot collide with the brand line.
    base = _s(198)
    left, _, right, _ = text_bbox(title_font, first)
    draw.text((x - left, base), first, font=title_font, fill=white,
              anchor='ls')
    x += right - left + gap
    if rest:
        left, _, _, _ = text_bbox(title_font, rest)
        gradient_text(design, x - left, base, rest, title_font,
                      project['title_gradient_1'], project['title_gradient_2'])

    # The rest of the editorial card is rendered on a transparent layer and
    # shifted down together. This keeps the title/brand relationship clean
    # without changing the reference geometry of the panels.
    body = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    body_shift = round(_s(50))
    attach_layout(body, design, (0, body_shift))
    draw = layout_draw(body)

    # Subtítulo.
    draw.rounded_rectangle((_s(60), _s(158), _s(817), _s(211)),
                           radius=_s(18), fill='#0E2232')
    sub = copy['subtitle'] if project.get('endcard_auto_text', True) else project['endcard_subtitle']
    sfont = _fit('regular', ('Concepto para el cierre del video de lluvia 2024.',
                             650), sub, 709)
    _ink(draw, _s(84), _s(196), sub, sfont, '#DDEBF3')

    # 01 · Cifras.
    _section_header(draw, 1, copy['section_1'], copy['section_1_note'],
                    accent, white, muted)
    for dx in (254.5, 486.5, 705):
        draw.line((_s(dx), _s(324), _s(dx), _s(508)), fill='#2B4757', width=2)

    aggregation = summary.get('aggregation',
                              project.get('endcard_aggregation', 'sum'))
    unit = summary.get('units', project.get('units', ''))
    aggregate_unit = summary.get(
        'aggregate_units',
        project.get('endcard_accumulated_units', unit) if aggregation == 'sum'
        else unit,
    )
    peak_date = summary.get('peak_date', summary.get('rainiest_day'))
    peak_date_mean = summary.get('peak_date_mean',
                                 summary.get('rainiest_day_mean'))
    peak_pixel_date = summary.get('peak_pixel_date',
                                  summary.get('wettest_day'))
    peak_pixel_value = summary.get('peak_pixel_value',
                                   summary.get('wettest_day_value'))
    period_mean = summary.get('mean_period', summary.get('mean_daily'))
    month_value = summary.get('peak_month_value',
                              summary.get('wettest_month_value'))
    decimals = summary.get('decimals', 1)
    month_labels = [(copy['period_label'], 205, 457)]
    rank_axis_label = copy['rank_axis_label']
    label_color = '#E8EFF3'
    # (cx_círculo, icono, cx_texto, ancho_max, valor, ref_valor, base_valor,
    #  líneas de etiqueta [(texto, ref_ancho, base)], regla, sub)
    date_label = copy['date_label']
    cadence = summary.get('cadence', project.get('cadence', 'Diaria'))
    date_value = _period_label(peak_date, cadence)
    max_date = _period_label(peak_pixel_date, cadence, include_year=True)
    period_display = _month_name(summary)
    period_metric = _fmt(month_value, aggregate_unit, decimals)
    if cadence == 'Por observación':
        period_display = f'{summary.get("days", 0):,}'
        period_metric = f'{summary.get("days", 0):,} observaciones'
    cards = [
        (141, _icon_for_profile(profile['kind']), 141.5, 200,
         date_value, ('14 ene', 116), 430.5,
         [(date_label, 205, 457)], (66, 215),
         (_fmt(peak_date_mean, unit, decimals), ('87.3 mm', 99), 505, 'display')),
        (372, _paint_calendar, 371.5, 215,
         period_display, ('Marzo', 90), 428.5,
         month_labels, (283, 459),
         (period_metric,
          ('12.6 mm/día', 131), 506, 'display')),
        (593, _paint_bars, 595.5, 205,
         _fmt(period_mean, unit, decimals), ('5.8 mm/día', 150), 433,
         [(copy['average_labels'][0], 146, 465),
          (copy['average_labels'][1], 100, 490)], None, None),
        (807, _paint_mountain, 813, 190,
         _fmt(peak_pixel_value, unit, decimals), ('142.6 mm', 143),
         429.5,
         [(copy['maximum_labels'][0], 140, 458),
          (copy['maximum_labels'][1], 92, 483)], None,
         (max_date,
          ('02 abr 2024', 102), 514, 'bold')),
    ]
    if summary.get('comparison_cards'):
        painters = [_icon_for_profile(profile['kind']), _paint_calendar, _paint_bars, _paint_index]
        if summary.get('geographic_records'):
            painters[0] = _paint_pin
        cards = [
            (cx, painters[index], cx, 185,
             item['value'], ('142.6 mm', 143), 430,
             [(item['label'], 200, 462)], (cx - 75, cx + 75),
             (item.get('sub', ''), ('02 abr 2024', 102), 505, 'bold'))
            for index, (cx, item) in enumerate(zip((141, 372, 593, 807), summary['comparison_cards']))
        ]
    for (cx, painter, tx, vmax, value, vref, vbase, labels, rule,
         sub_item) in cards:
        _icon_circle(body, cx, 349.5, painter)
        vfont = _fit('display', vref, value, vmax)
        _center(draw, _s(tx), _s(vbase), value, vfont, white)
        for text, ref_w, bl in labels:
            lfont = _fit('regular', (text, ref_w), text, vmax)
            _center(draw, _s(tx), _s(bl), text, lfont, label_color)
        if rule:
            draw.line((_s(rule[0]), _s(472), _s(rule[1]), _s(472)),
                      fill='#8DA0A9', width=1)
        if sub_item:
            text, sref, bl, kind = sub_item
            sfont2 = _fit(kind, sref, text, vmax)
            _center(draw, _s(tx), _s(bl), text, sfont2, accent)

    # 02 y 03 · Ranking provincial.
    ranking = summary.get('city_rank', [])
    max_value = max((row['value'] for row in ranking), default=0)
    min_value = min((row['value'] for row in ranking), default=0)
    if min_value < 0:
        step = _nice_step(max(max_value, 0) - min_value)
        axis_min = math.floor(min_value / step) * step
    else:
        step = _nice_step(max_value)
        axis_min = 0.0
    axis_max = axis_min + step * 8
    _section_header(draw, 2, copy['section_2'], copy['section_2_note'],
                    accent, white, muted)
    _ranking_panel(draw, body, project, 2, 1, ranking[:12], axis_max, step,
                   rank_axis_label, aggregate_unit, white, axis_min, decimals,
                   spread_rows=bool(summary.get('comparison_cards')))
    section_3 = copy['section_3'] if project.get('endcard_auto_text', True) else project['endcard_section_3']
    # Do not promise a 24th province when a regional/local raster lacks a
    # complete province. Custom user wording is always preserved.
    canonical_third = section_3.upper().replace('–', '-').strip()
    if canonical_third in ('CIUDADES 13-24', 'PROVINCIAS 13-24') and len(ranking) < 24:
        prefix = 'PROVINCIAS' if 'PROVINCIAS' in canonical_third else 'CIUDADES'
        section_3 = f'{prefix} 13–{max(13, len(ranking))}'
    section_3_note = copy['section_3_note'] if project.get('endcard_auto_text', True) else project['endcard_section_3_note']
    _section_header(draw, 3, section_3, section_3_note, accent, white, muted)
    if summary.get('comparison_notes'):
        for idx, note in enumerate(summary['comparison_notes']):
            note_font = _fit('regular', ('Ventana temporal comparable', 340), note, 810)
            _ink(draw, _s(54), _s(1175 + idx * 62), note, note_font, muted)
    else:
        _ranking_panel(draw, body, project, 3, 13, ranking[12:24], axis_max,
                       step, rank_axis_label, aggregate_unit, white, axis_min,
                       decimals)

    # Pie.
    draw.line((_s(33), _s(1556), _s(907), _s(1556)), fill='#627783', width=2)
    draw.line((_s(510.5), _s(1575), _s(510.5), _s(1648)), fill='#506574',
              width=2)
    _stamp_icon(body, draw_database_icon, (46, 1577, 89, 1627), '#E4EFEA')
    n_provinces = len(ranking) or len(getattr(summary, 'rank_features', []))
    province_label = summary.get('rank_label') or (f'{n_provinces} provincias del Ecuador'
                      if n_provinces == 24
                      else f'{n_provinces} provincias incluidas')
    foot = [
        (province_label, 'bold',
         ('24 provincias del Ecuador', 312), 118, 1593, white),
        ((copy['footer'] if project.get('endcard_auto_text', True)
          else project.get('endcard_footer', 'Fuente de datos')), 'regular',
         ('CHIRPS v2 · resolución nativa ≈ 5,6 km', 286), 118, 1619.5,
         '#B9C9D3'),
        ((copy['footer_2'] if project.get('endcard_auto_text', True)
          else project.get('endcard_footer_2', 'Encuadre seleccionado')),
         'regular',
         ('Ecuador continental + Galápagos · límites: geoBoundaries', 390),
         119, 1644,
         '#B9C9D3'),
    ]
    for text, kind, ref, fx, fy, color in foot:
        _ink(draw, _s(fx), _s(fy), text, _fit(kind, ref, text, 385), color)

    _stamp_icon(body, draw_mountain_icon, (541, 1577, 599, 1611), '#E4EFEA')
    author = project['author']
    _ink(draw, _s(622), _s(1589.5), author,
         _fit('bold', ('Henry P. Conteron Moreta', 222), author, 283), white)
    credits = project['credits']
    _ink(draw, _s(622), _s(1613), credits,
         _fit('regular', ('Ing. Geociencias', 131), credits, 283), '#B9C8D2')
    _stamp_icon(body, draw_tiktok_icon, (621, 1626, 640, 1649), white)
    _stamp_icon(body, draw_instagram_icon, (656, 1626, 679, 1649), white)
    handles = ' · '.join(h for h in (project.get('tiktok', ''),
                                     project.get('instagram', '')) if h)
    _ink(draw, _s(688), _s(1641.5), handles,
         _fit('regular', ('@elgeocientifico · @henry_conteron', 224), handles,
              227), '#C9D6DE')

    design.alpha_composite(body, (0, body_shift))
    design = finish_layout(design)
    custom = project.get('_layout_capture') or project.get('visual_layout', {}).get('full_canvas')
    result = design.convert('RGB') if custom else compose_final(design.convert('RGB'))
    if project['width'] != WIDTH:
        result = result.resize((project['width'], project['width'] * 16 // 9),
                               Image.Resampling.LANCZOS)
    return result
