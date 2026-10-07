"""Geographic video scenes. Never infer a surface from a national average.

Monthly fields come from original daily rasters; CSV locations remain points,
and provincial CSV values are joined to actual ADM1 geometries. Screen
resampling is separate from the native-grid calculations used by the endcard.
"""
from __future__ import annotations

import calendar
import datetime as dt
import json
import math
import unicodedata
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import Resampling
from rasterio.features import bounds as geometry_bounds, geometry_mask
from rasterio.transform import from_bounds
from rasterio.warp import reproject, transform_geom
from PIL import Image, ImageColor, ImageDraw
from layout_engine import draw as layout_draw, full_layer, place_layer

from climate_comparison import _monthly_grid, _raster_dates
from data import boundary, province_boundaries
from maqueta import (MAIN_BOX, GALAPAGOS_BOX, build_mask_and_rings,
                     extract_outline_rings, outline_layer, projector)
from render import font, fitted

MONTHS = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN',
          'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']


def normalized(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', str(value).strip().lower())
                   if not unicodedata.combining(c))


@lru_cache(maxsize=1)
def geometries():
    return boundary(), {'type': 'FeatureCollection', 'features': province_boundaries()}


def source_signature(output):
    """Cache invalidates when a source file is replaced, not just its path."""
    files = []
    for receipt in output.get('receipts', []):
        paths = ([receipt['tiff_path']] if receipt.get('tiff_path') else
                 [item['path'] for item in receipt.get('entries', [])])
        for path in paths:
            target = Path(path)
            if not target.is_file():
                raise ValueError('Falta un archivo fuente del mapa. Reabre o vuelve a obtener los datos originales.')
            stat = target.stat()
            files.append((str(target), stat.st_size, stat.st_mtime_ns))
    if not files:
        raise ValueError('Esta consulta solo conserva promedios. Para dibujar mapas necesitas los GeoTIFF originales, no la tabla de promedios.')
    return tuple(files)


def _complete_indexes(dates, year, month):
    selected = [(i + 1, day) for i, day in enumerate(dates)
                if day and day.year == year and day.month == month]
    expected = {dt.date(year, month, day) for day in
                range(1, calendar.monthrange(year, month)[1] + 1)}
    if len(selected) != len(expected) or {day for _, day in selected} != expected:
        raise ValueError(f'{MONTHS[month-1]} {year}: faltan días o hay fechas duplicadas. No se dibujará un mes incompleto.')
    return [index for index, _ in selected]


@lru_cache(maxsize=4)
def _load_fields(receipts_json, parameter, years, months, signature):
    fields = {}
    for receipt in json.loads(receipts_json):
        if receipt.get('tiff_path'):
            with rasterio.open(receipt['tiff_path']) as source:
                if not source.crs:
                    raise ValueError('El ráster no tiene SRC; no se puede ubicar en el mapa.')
                dates = _raster_dates(source)
                receipt_years = {day.year for day in dates if day}
                for year in years:
                    if year not in receipt_years:
                        continue
                    for month in months:
                        key = (year, month)
                        if key in fields:
                            raise ValueError(f'Fuente mensual duplicada: {key}.')
                        indexes = _complete_indexes(dates, year, month)
                        fields[key] = (_monthly_grid(source, indexes, parameter),
                                       source.transform, str(source.crs))
        else:
            entries = receipt.get('entries', [])
            for year in years:
                for month in months:
                    selected = [row for row in entries if str(row['date']).startswith(f'{year}-{month:02d}-')]
                    if not selected:
                        continue
                    _complete_indexes([dt.date.fromisoformat(row['date']) for row in selected], year, month)
                    total, count, reference = None, None, None
                    for row in selected:
                        with rasterio.open(row['path']) as src:
                            if not src.crs:
                                raise ValueError('El ráster diario no tiene SRC.')
                            grid = src.read(1, masked=True).astype('float64').filled(np.nan)
                            grid[~np.isfinite(grid) | (grid <= -900)] = np.nan
                            if parameter in ('PRECTOTCORR', 'CHIRPS_PRECTOT'):
                                grid[grid < 0] = np.nan
                            identity = (grid.shape, src.transform, str(src.crs))
                            if reference is None:
                                reference = identity
                                total, count = np.zeros(grid.shape), np.zeros(grid.shape, dtype='uint16')
                            if identity != reference:
                                raise ValueError('Los rásteres diarios no comparten la misma grilla.')
                            total += np.nan_to_num(grid, nan=0)
                            count += np.isfinite(grid)
                    if parameter not in ('PRECTOTCORR', 'CHIRPS_PRECTOT'):
                        total /= len(selected)
                    total[count != len(selected)] = np.nan
                    if (year, month) in fields:
                        raise ValueError('Fuente mensual duplicada.')
                    fields[(year, month)] = (total.astype('float32'), reference[1], reference[2])
    missing = [(year, month) for year in years for month in months if (year, month) not in fields]
    if missing:
        raise ValueError(f'Faltan rásteres originales para {missing}; no se inventará su distribución espacial.')
    return fields


def native_fields(output):
    years = tuple(sorted(set(int(y) for y in output['years'])))
    months = tuple(range(int(output['first_month']), int(output['last_month']) + 1))
    return _load_fields(json.dumps(output.get('receipts', []), sort_keys=True),
                        output['parameter'], years, months, source_signature(output))


def map_steps(output, config):
    """Same month on both maps; three years cycle baseline vs each later year."""
    if output.get('map_kind') in ('points', 'polygons'):
        return [((str(period), 0),) for period in output['periods']]
    years = sorted(set(int(y) for y in output['years']))
    months = range(int(output['first_month']), int(output['last_month']) + 1)
    if config.get('map_layout', 'Dos mapas') == 'Dos mapas' and len(years) >= 2:
        return [((years[0], month), (year, month)) for year in years[1:] for month in months]
    return [((year, month),) for year in years for month in months]


def _scope(output):
    country, provinces = geometries()
    if output.get('mode') == 'provincia':
        feature = next((f for f in provinces['features']
                        if normalized(f['properties'].get('shapeName', f['properties'].get('name'))) == normalized(output['area'])), None)
        if not feature:
            raise ValueError('Provincia sin geometría reconocida.')
        west, south, east, north = geometry_bounds(feature['geometry'])
        pad = max(east - west, north - south) * .08
        return {'type': 'FeatureCollection', 'features': [feature]}, (west - pad, south - pad, east + pad, north + pad), False
    return country, MAIN_BOX, True


def _fit_box(box, width, height):
    west, south, east, north = box
    native_aspect = (east - west) / (north - south)
    if width / height > native_aspect:
        pad = ((north - south) * width / height - (east - west)) / 2
        west, east = west - pad, east + pad
    else:
        pad = ((east - west) * height / width - (north - south)) / 2
        south, north = south - pad, north + pad
    return west, south, east, north


def display_grid(field, box, width, height, *, smooth=True):
    values, transform, crs = field
    result = np.full((height, width), np.nan, dtype='float32')
    destination = from_bounds(*box, width, height)
    reproject(values, result, src_transform=transform, src_crs=crs,
              src_nodata=np.nan, dst_transform=destination, dst_crs='EPSG:4326',
              dst_nodata=np.nan, resampling=Resampling.bilinear if smooth else Resampling.nearest)
    # Screen smoothing must not fill an original NoData cell or extrapolate coast/ocean.
    valid = np.zeros((height, width), dtype='uint8')
    reproject(np.isfinite(values).astype('uint8'), valid, src_transform=transform,
              src_crs=crs, dst_transform=destination, dst_crs='EPSG:4326',
              resampling=Resampling.nearest)
    result[valid == 0] = np.nan
    return result


def _colors(values, limits, palette):
    colors = np.asarray([ImageColor.getrgb(c) for c in palette], dtype=float)
    stops = np.linspace(*limits, len(colors))
    return np.stack([np.interp(np.nan_to_num(values, nan=limits[0]), stops, colors[:, channel])
                     for channel in range(3)], axis=-1).astype('uint8')


def scale_limits(output, config, fields=None):
    if config.get('scale_min') is not None and config.get('scale_max') is not None:
        limits = float(config['scale_min']), float(config['scale_max'])
        if not all(np.isfinite(limits)) or limits[0] >= limits[1]:
            raise ValueError('El mínimo de escala debe ser menor que el máximo.')
        return limits
    if output.get('map_kind') == 'polygons':
        values = np.asarray([row['value'] for row in output['records']], dtype=float)
    elif output.get('map_kind') == 'points':
        return 0., 1.
    else:
        geojson, _, _ = _scope(output)
        samples = []
        features = geojson.get('features', [geojson])
        # Exact extrema of native cells intersecting the scope, across ALL
        # periods. No percentiles, preview downsampling or ocean in the limits.
        for grid, transform, crs in (fields or native_fields(output)).values():
            shapes = [transform_geom('EPSG:4326', crs, f['geometry']) for f in features]
            mask = geometry_mask(shapes, grid.shape, transform, invert=True, all_touched=True)
            samples.append(grid[mask & np.isfinite(grid)])
        values = np.concatenate(samples)
    values = values[np.isfinite(values)]
    if not len(values):
        raise ValueError('No hay datos válidos dentro del encuadre geográfico.')
    low, high = float(values.min()), float(values.max())
    if low == high:
        pad = max(abs(low) * .02, .5)
        low, high = low - pad, high + pad
    return low, high


def _map_layer(output, field, period, box, width, height, limits, palette, *, smooth=True):
    geojson, _, _ = _scope(output)
    country, provinces = geometries()
    mask, rings, xy = build_mask_and_rings(geojson, box, width, height)
    layer = Image.new('RGBA', (width, height), '#0a2533')
    alpha = np.asarray(mask)
    kind = output.get('map_kind', 'raster')
    if kind == 'raster':
        grid = display_grid(field, box, width, height, smooth=smooth)
        rgb = _colors(grid, limits, palette)
        rgba = np.dstack((rgb, np.where(np.isfinite(grid), alpha, 0).astype('uint8')))
        layer.alpha_composite(Image.fromarray(rgba))
    elif kind == 'polygons':
        rows = {normalized(row['area']): row['value'] for row in output['records'] if str(row['period']) == str(period)}
        for feature in provinces['features']:
            name = normalized(feature['properties'].get('shapeName'))
            value = rows.get(name)
            if value is None or not np.isfinite(value):
                continue
            feature_mask, _, _ = build_mask_and_rings({'type': 'FeatureCollection', 'features': [feature]}, box, width, height)
            color = tuple(_colors(np.array([[value]]), limits, palette)[0, 0])
            layer.paste(Image.new('RGBA', (width, height), color + (255,)), (0, 0), feature_mask)
    layer.putalpha(mask)
    province_rings = extract_outline_rings(provinces, box, width, height)
    layer.alpha_composite(outline_layer((width, height), [
        (province_rings, (159, 190, 205, 140), .7), (rings, (236, 251, 255, 255), 1.6)]))
    draw = ImageDraw.Draw(layer)
    if kind == 'points':
        for row in output['records']:
            if str(row['period']) != str(period):
                continue
            x, y = xy(row['lon'], row['lat'])
            if not 0 <= x < width or not 0 <= y < height:
                continue
            color = output['category_colors'][str(row['category'])]
            radius = int(output.get('point_size', 6))
            draw.ellipse((x-radius-2, y-radius-2, x+radius+2, y+radius+2), fill='#020d16')
            draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color, outline='#ffffff', width=1)
    if output.get('mode') == 'ciudad':
        from climate_comparison import _city_coordinates
        lon, lat = _city_coordinates(output['area'])
        x, y = xy(lon, lat)
        if 0 <= x < width and 0 <= y < height:
            draw.ellipse((x-6, y-6, x+6, y+6), fill='#ffffff', outline='#000000', width=3)
            draw.text((x+10, y-12), output['area'], font=font(20, True), fill='white', stroke_width=2, stroke_fill='black')
    return layer


def draw_geographic_scene(image, output, config, palette, *, progress=1.0):
    from editorial import text_box, panel as draw_panel, stamp_icon, editorial_font
    steps = map_steps(output, config)
    step = steps[min(len(steps)-1, int(min(.999999, max(0., progress)) * len(steps)))]
    fields = None if output.get('map_kind') else native_fields(output)
    limits = scale_limits(output, config, fields)
    draw = layout_draw(image)
    foreground = config.get('text', '#f4f8fb')
    accent = config.get('accent', '#55e2cb')
    muted = '#a6bdc7'
    geojson, box, inset = _scope(output)
    double = len(step) == 2
    panels = [(96, 477, 984, 911), (96, 931, 984, 1365)] if double else [(96, 477, 984, 1365)]
    for map_index, ((year, month), panel) in enumerate(zip(step, panels)):
        x0, y0, x1, y1 = panel
        draw_panel(image, panel)
        label = str(year) if not month else f'{MONTHS[month-1]} · {year}'
        draw.rounded_rectangle((x0+23, y0+18, x0+247, y0+78), radius=12, fill='#103e50', outline='#287287', width=2)
        text_box(image, label, (x0+40, y0+29, x0+237, y0+70), size=39, bold=True, color=foreground, lines=1)
        area = str(output.get('area', 'Ecuador'))
        draw.line((x0+264, y0+26, x0+264, y0+73), fill='#648fa3', width=2)
        text_box(image, area.upper(), (x0+284, y0+32, x0+462, y0+75), size=34, bold=True, color=muted, lines=1)
        # Equal geometry and dimensions in every comparison panel; islands re-located as inset.
        map_h = y1-y0-(34 if double and inset else 122)
        map_w = 550 if double and inset else min(750, round(map_h * (box[2]-box[0]) / (box[3]-box[1])))
        map_x = x0+303 if double and inset else x0+(x1-x0-map_w)//2+(60 if inset else 0)
        map_y = y0+17 if double and inset else y0+102
        target_box = _fit_box(box, map_w, map_h)
        field = fields[(year, month)] if fields is not None else None
        layer = _map_layer(output, field, year, target_box, map_w, map_h, limits, palette,
                           smooth=config.get('map_smooth', True))
        map_group = Image.new('RGBA', image.size)
        map_group.paste(layer, (map_x, map_y), layer)
        if inset:
            gal_w = 215
            gal_h = round(gal_w * (GALAPAGOS_BOX[3]-GALAPAGOS_BOX[1]) / (GALAPAGOS_BOX[2]-GALAPAGOS_BOX[0]))
            gal = _map_layer(output, field, year, GALAPAGOS_BOX, gal_w, gal_h, limits, palette,
                             smooth=config.get('map_smooth', True))
            gx, gy = x0+37, y0+137 if double else map_y+map_h//3
            gal_group = Image.new('RGBA', image.size)
            gal_group.paste(gal, (gx, gy), gal)
            gal_draw = ImageDraw.Draw(gal_group)
            # Dashed locator from the requested reference; different inset scale.
            for xx in range(gx-8, gx+gal_w+9, 17):
                gal_draw.line((xx, gy-5, min(xx+5, gx+gal_w+8), gy-5), fill='#4a8297', width=2)
                gal_draw.line((xx, gy+gal_h+5, min(xx+5, gx+gal_w+8), gy+gal_h+5), fill='#4a8297', width=2)
            for yy in range(gy-5, gy+gal_h+6, 17):
                gal_draw.line((gx-8, yy, gx-8, min(yy+5, gy+gal_h+5)), fill='#4a8297', width=2)
                gal_draw.line((gx+gal_w+8, yy, gx+gal_w+8, min(yy+5, gy+gal_h+5)), fill='#4a8297', width=2)
            text_box(gal_group, 'GALÁPAGOS', (gx, gy+gal_h+16, gx+gal_w, gy+gal_h+46), size=24, color=muted, lines=1, align='center')
            full_layer(image, gal_group, key=f'map.{map_index}.galapagos', label=f'Galápagos · mapa {map_index+1}', kind='map')
            for yy in range(y0+110, y1-25, 11):
                draw.line((x0+307, yy, x0+307, min(yy+4, y1-25)), fill='#427087', width=1)
        # North-up WGS84 display. Distance is calculated for the actual map,
        # not an arbitrary copied "200 km" graphic (the inset has its own scale).
        nx, ny = x1-31, y0+34
        map_draw = ImageDraw.Draw(map_group)
        map_draw.line((nx, ny+18, nx, ny), fill=muted, width=2)
        map_draw.line((nx-5, ny+6, nx, ny, nx+5, ny+6), fill=muted, width=2)
        map_draw.text((nx, ny+24), 'N', font=editorial_font(24), fill=muted, anchor='mt')
        if inset and double:
            lon_span = target_box[2]-target_box[0]
            latitude = (target_box[1]+target_box[3])/2
            km_per_px = lon_span*111.32*math.cos(math.radians(latitude))/map_w
            desired_km = km_per_px*130
            power = 10**math.floor(math.log10(max(.001, desired_km)))
            km = max(v*power for v in (.1, .2, .5, 1, 2, 5, 10) if v*power <= desired_km)
            pixels = km/km_per_px
            sx, sy = x1-180, y1-23
            map_draw.line((sx, sy, sx+pixels, sy), fill=muted, width=2)
            for xx in (sx, sx+pixels/2, sx+pixels):
                map_draw.line((xx, sy-4, xx, sy+4), fill=muted, width=2)
            map_draw.text((sx, sy-7), f'0     {km:g} km', font=editorial_font(24), fill=muted, anchor='lb')
        full_layer(image, map_group, key=f'map.{map_index}.main', label=f'Mapa {map_index+1} · continente, norte y distancia', kind='map')
    canvas = image
    image = Image.new('RGBA', canvas.size)
    draw = ImageDraw.Draw(image)
    if output.get('map_kind') == 'points':
        labels = list(output['category_colors'].items())
        for i, (label, color) in enumerate(labels[:6]):
            x, y = 119 + (i % 2)*410, 1395 + (i//2)*38
            draw.ellipse((x, y+4, x+14, y+18), fill=color, outline='white')
            text_box(image, label, (x+24, y, x+390, y+34), size=31, color=foreground, lines=1)
    else:
        units = config.get('units', '')
        draw_panel(image, (96, 1385, 984, 1528))
        text_box(image, f'ESCALA COMPARTIDA · {units}', (127, 1400, 953, 1440), size=32, bold=True, color=foreground, lines=1)
        gradient = _colors(np.linspace(*limits, 814)[None, :], limits, palette)
        bar = Image.fromarray(np.repeat(gradient, 25, axis=0)).convert('RGBA')
        image.alpha_composite(bar, (133, 1445))
        draw = ImageDraw.Draw(image)
        for i, value in enumerate(np.linspace(*limits, 5)):
            x = 133 + i * 814 / 4
            draw.line((x, 1472, x, 1482), fill=muted, width=2)
            draw.text((x, 1488), f'{value:.1f}', font=editorial_font(29), fill=foreground, anchor='mt')
    full_layer(canvas, image, key='legend.shared', kind='map', label='Leyenda y escala compartida')
    image = canvas
    draw = layout_draw(image)
    if output.get('map_kind') == 'points':
        chips = [('pin', 'UBICACIONES REALES', 'Coordenadas del CSV.'), ('bars', 'REGISTROS', 'No equivalen a individuos.'), ('index', 'COBERTURA', 'Ausencia no prueba extinción.')]
    else:
        chips = [('bars', 'MISMA ESCALA', 'Comparación directa entre años.'), ('calendar', 'SIN INTERPOLAR FECHAS', 'Solo meses completos.'), ('pin', 'ISLAS REUBICADAS' if inset else 'LÍMITES REALES', 'Para facilitar la lectura.')]
    draw_panel(image, (96, 1548, 984, 1688))
    for i, (icon, label, note) in enumerate(chips):
        x = 108+i*291
        if i:
            draw.line((x-4, 1574, x-4, 1668), fill='#456b7d', width=2)
        stamp_icon(image, x+44, 1618, icon, diameter=72)
        text_box(image, label, (x+95, 1572, x+277, 1629), size=23, display=True, color=accent, lines=2)
        text_box(image, note, (x+95, 1636, x+277, 1682), size=24, lines=2)
    index = steps.index(step)
    # Discreet timeline integrated into the bottom card border.
    draw.line((120, 1688, 120+840*(index+1)/len(steps), 1688), fill=accent, width=2)
    return {'layout': config.get('map_layout', 'Dos mapas'), 'scale': list(limits),
            'step': step, 'steps': len(steps), 'representation': output.get('map_kind', 'raster')}
