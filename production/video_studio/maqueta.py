"""Maqueta oficial Ecuador Vivo / Andes Pulso.

Esta plantilla reproduce la composición aprobada para videos verticales 1080x1920.
La vista previa y la exportación usan exactamente esta misma función.

El editor puede cambiar:
- título y subtítulo
- marca
- paleta y escala
- fondo, texto y acento
- fuente de datos, autor y redes
- ciudades
- Galápagos, provincias y botón decorativo
"""

import copy
import datetime as dt
import gzip
import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageColor
from rasterio.io import MemoryFile
from rasterio.windows import Window, from_bounds
from rasterio.enums import Resampling
from rasterio.transform import from_bounds as grid_from_bounds
from rasterio.warp import reproject

from data import boundary, fetch, rain_path
from model import ROOT, STORE


# =============================================================================
# LIENZO / ZONA SEGURA
# =============================================================================

WIDTH = 1080
HEIGHT = 1920

SAFE_LEFT = 60
SAFE_RIGHT = 120
SAFE_TOP = 190
SAFE_BOTTOM = 400

DESIGN_CROP = (45, 20, 1050, 1842)

# El diseño se construye primero a tamaño completo y luego se mete en la zona
# segura. Esto reproduce la maqueta final que ya aprobaste.
MAIN_BOX = (-81.5, -5.2, -75.0, 1.8)
GALAPAGOS_BOX = (-92.2, -1.8, -88.8, 1.9)

MAIN_X, MAIN_Y, MAIN_W, MAIN_H = 93, 468, 946, 1019

# Galápagos es un recuadro (inset). Su posición se calcula en cada frame con
# place_galapagos(): primero arriba a la izquierda (lugar original), y si toca
# el mapa continental lo achica o lo pasa abajo a la izquierda.
# Se mantiene la proporción geográfica para que las islas no se deformen.
GAL_ASPECT = (GALAPAGOS_BOX[3] - GALAPAGOS_BOX[1]) / (GALAPAGOS_BOX[2] - GALAPAGOS_BOX[0])
GAL_W_MAX, GAL_W_MIN = 235, 150
# CHIRPS cells are about 0.05° (~5.6 km). Keep only islands whose vector
# footprint is large enough to contain several native cells; tiny islets remain
# outside the rainfall inset because their colour would imply false precision.
GAL_MIN_AREA_DEG2 = 0.02

SS = 3
FILL_ITERATIONS = 8

MAP_BORDER = (244, 248, 246, 255)
PROVINCE_BORDER = (190, 210, 216, 150)

MONTHS = (
    'ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN',
    'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC',
)

CITIES = [
    ('Quito', -78.4678, -0.1807),
    ('Guayaquil', -79.889, -2.17),
    ('Cuenca', -79.005, -2.9),
    ('Tena', -77.813, -0.994),
    ('Archidona', -77.808, -0.909),
]


# =============================================================================
# FUENTES
# =============================================================================

FONT_DIRS = [
    Path('C:/Windows/Fonts'),
    Path('/usr/share/fonts'),
    Path('/usr/local/share/fonts'),
    Path('/System/Library/Fonts'),
    Path('/System/Library/Fonts/Supplemental'),
    Path('/Library/Fonts'),
    Path.home() / 'Library' / 'Fonts',
    Path.home() / '.fonts',
]

FONT_SPECS = {
    'display': {
        'weight': 700,
        'width': 75,
        'static': [
            'arialnb.ttf',
            'DejaVuSansCondensed-Bold.ttf',
            'Inter-ExtraBold.otf',
            'arialbd.ttf',
            'segoeuib.ttf',
        ],
    },
    'bold': {
        'weight': 600,
        'width': 82,
        'static': [
            'segoeuib.ttf',
            'Inter-Bold.otf',
            'DejaVuSansCondensed-Bold.ttf',
            'arialbd.ttf',
        ],
    },
    'regular': {
        'weight': 400,
        'width': 82,
        'static': [
            'segoeui.ttf',
            'Inter-Regular.otf',
            'DejaVuSansCondensed.ttf',
            'arial.ttf',
        ],
    },
    'label': {
        'weight': 400,
        'width': 75,
        'static': [
            'arialn.ttf',
            'Inter-Regular.otf',
            'DejaVuSansCondensed.ttf',
            'segoeui.ttf',
            'arial.ttf',
        ],
    },
}


@lru_cache(maxsize=None)
def font_index():
    index = {}
    for directory in FONT_DIRS:
        if not directory.exists():
            continue
        try:
            for path in directory.rglob('*'):
                if path.suffix.lower() in ('.ttf', '.otf', '.ttc'):
                    index.setdefault(path.name.lower(), path)
        except OSError:
            continue
    return index


def find_font(*names):
    index = font_index()
    for name in names:
        path = index.get(name.lower())
        if path:
            return path
    return None


@lru_cache(maxsize=None)
def make_font(kind, size, width=None):
    spec = FONT_SPECS[kind]
    width = spec['width'] if width is None else width

    variable = find_font('bahnschrift.ttf')
    if variable:
        try:
            result = ImageFont.truetype(str(variable), size)
            values = []
            for axis in result.get_variation_axes():
                name = axis['name']
                if isinstance(name, bytes):
                    name = name.decode('utf-8', 'ignore')
                name = str(name).lower()
                if 'weight' in name:
                    value = spec['weight']
                elif 'width' in name:
                    value = width
                else:
                    value = axis['default']
                values.append(min(max(value, axis['minimum']), axis['maximum']))
            result.set_variation_by_axes(values)
            return result
        except Exception:
            pass

    static = find_font(*spec['static'])
    if static:
        return ImageFont.truetype(str(static), size)

    return ImageFont.load_default(size=size)


def text_bbox(font_obj, text):
    return font_obj.getbbox(text, anchor='ls')


def text_width(font_obj, text):
    left, _, right, _ = text_bbox(font_obj, text)
    return right - left


def size_for_cap(kind, cap):
    for size in range(8, 420):
        top = make_font(kind, size).getbbox('H', anchor='ls')[1]
        if -top >= cap:
            return size
    return 420


def fit_text(kind, cap, target_width, text):
    size = size_for_cap(kind, cap)
    base_width = FONT_SPECS[kind]['width']

    while size > 8 and text_width(make_font(kind, size, base_width), text) > target_width:
        size -= 1

    low, high, best = base_width, 100, base_width
    while low <= high:
        mid = (low + high) // 2
        candidate = make_font(kind, size, mid)
        if text_width(candidate, text) <= target_width:
            best = mid
            low = mid + 1
        else:
            high = mid - 1

    return make_font(kind, size, best)


def draw_line(draw, x, baseline, text, kind, cap, target_width, fill):
    font_obj = fit_text(kind, cap, target_width, text)
    left = text_bbox(font_obj, text)[0]
    draw.text(
        (x - left, baseline),
        text,
        font=font_obj,
        fill=fill,
        anchor='ls'
    )
    return font_obj


def draw_tracked(draw, x, baseline, text, kind, cap, target_width, fill):
    size = size_for_cap(kind, cap)

    while size > 12:
        font_obj = make_font(kind, size)
        widths = [font_obj.getlength(ch) for ch in text]
        tracking = (
            (target_width - sum(widths)) / max(1, len(text) - 1)
        )
        if tracking >= 0.8:
            break
        size -= 1

    for ch, width in zip(text, widths):
        draw.text((x, baseline), ch, font=font_obj, fill=fill, anchor='ls')
        x += width + tracking


# =============================================================================
# COLORES / DEGRADADOS
# =============================================================================

def hex_to_rgb(value):
    return ImageColor.getrgb(value)


def colorize(values, project):
    if project['kind'] == 'categorical':
        rgb = np.zeros((*values.shape, 3), dtype='uint8')
        for row in project['classes']:
            rgb[values == row['value']] = ImageColor.getrgb(row['color'])
        return rgb

    colors = np.array(
        [ImageColor.getrgb(c) for c in project['palette']],
        dtype=float
    )
    safe = np.nan_to_num(values, nan=project['stops'][0])
    return np.stack(
        [
            np.interp(safe, project['stops'], colors[:, channel])
            for channel in range(3)
        ],
        axis=-1
    ).astype('uint8')


def gradient_text(image, x, baseline, text, font_obj, color_left, color_right):
    mask = Image.new('L', image.size, 0)
    ImageDraw.Draw(mask).text(
        (x, baseline),
        text,
        font=font_obj,
        fill=255,
        anchor='ls'
    )

    bbox = mask.getbbox()
    if bbox is None:
        return

    x0, y0, x1, y1 = bbox
    width = x1 - x0
    height = y1 - y0

    t = np.linspace(0, 1, width)[None, :, None]
    left = np.array(hex_to_rgb(color_left), dtype=float)[None, None, :]
    right = np.array(hex_to_rgb(color_right), dtype=float)[None, None, :]
    gradient = np.repeat(left * (1 - t) + right * t, height, axis=0).astype('uint8')

    image.paste(
        Image.fromarray(gradient, 'RGB'),
        (x0, y0),
        mask.crop(bbox)
    )


# =============================================================================
# ICONOS
# =============================================================================

def draw_calendar_icon(draw, x, y, color, s=1.25):
    body = 44 * s
    stroke = round(3 * s)
    draw.rounded_rectangle(
        (x, y, x + body, y + body),
        radius=5 * s,
        outline=color,
        width=stroke
    )
    draw.line(
        (x, y + 13 * s, x + body, y + 13 * s),
        fill=color,
        width=stroke
    )
    for px in (11, 33):
        draw.line(
            (x + px * s, y - 5 * s, x + px * s, y + 7 * s),
            fill=color,
            width=round(4 * s)
        )


def draw_play_button(draw, box, color):
    x0, y0, x1, y1 = box
    draw.ellipse(box, fill='#1C2B37')
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    draw.polygon(
        [(cx - 10, cy - 17), (cx - 10, cy + 17), (cx + 18, cy)],
        fill=color
    )


def draw_database_icon(draw, x, y, color, w=58, h=74):
    e = round(w * 0.28)
    draw.ellipse((x, y, x + w, y + e), outline=color, width=3)
    draw.line((x, y + e / 2, x, y + h - e / 2), fill=color, width=3)
    draw.line((x + w, y + e / 2, x + w, y + h - e / 2), fill=color, width=3)
    for k in (1, 2, 3):
        yk = y + e / 2 + k * (h - e) / 3
        draw.arc((x, yk - e / 2, x + w, yk + e / 2), 0, 180, fill=color, width=3)


def draw_mountain_icon(draw, x, y, color):
    draw.line((x, y + 43, x + 26, y + 3, x + 49, y + 43), fill=color, width=3)
    draw.line((x + 32, y + 43, x + 48, y + 17, x + 70, y + 43), fill=color, width=3)


def draw_instagram_icon(draw, x, y, color):
    draw.rounded_rectangle((x, y, x + 32, y + 32), radius=9, outline=color, width=3)
    draw.ellipse((x + 8, y + 8, x + 24, y + 24), outline=color, width=3)
    draw.ellipse((x + 23, y + 5, x + 27, y + 9), fill=color)


def draw_tiktok_icon(draw, x, y, color):
    draw.line((x + 18, y + 3, x + 18, y + 26), fill=color, width=5)
    draw.line((x + 18, y + 4, x + 30, y + 11), fill=color, width=5)
    draw.ellipse((x + 3, y + 21, x + 20, y + 37), fill=color)


# =============================================================================
# GEOMETRÍA
# =============================================================================

def box_intersects_ring(ring, box):
    lons = [point[0] for point in ring]
    lats = [point[1] for point in ring]
    return not (
        max(lons) < box[0]
        or min(lons) > box[2]
        or max(lats) < box[1]
        or min(lats) > box[3]
    )


def projector(box, width, height):
    def xy(lon, lat):
        x = (lon - box[0]) / (box[2] - box[0]) * width
        y = (box[3] - lat) / (box[3] - box[1]) * height
        return x, y
    return xy


def iter_polygons(geojson):
    for feature in geojson['features']:
        geometry = feature.get('geometry')
        if geometry is None:
            continue
        if geometry['type'] == 'MultiPolygon':
            yield from geometry['coordinates']
        elif geometry['type'] == 'Polygon':
            yield geometry['coordinates']


def ring_area(ring):
    """Shoelace area in geographic degrees for an outer polygon ring."""
    if len(ring) < 4:
        return 0.0
    return abs(sum(
        x1 * y2 - x2 * y1
        for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1])
    )) / 2.0


def build_mask_and_rings(geojson, box, width, height, clip=True,
                         min_outer_area=0.0):
    xy = projector(box, width, height)
    base = 0 if clip else 255
    big = Image.new('L', (width * SS, height * SS), base)
    draw = ImageDraw.Draw(big)
    rings = []

    for polygon in iter_polygons(geojson):
        if min_outer_area and (not polygon or
                               ring_area(polygon[0]) < min_outer_area):
            continue
        for index, ring in enumerate(polygon):
            if not box_intersects_ring(ring, box):
                continue
            points = [xy(lon, lat) for lon, lat in ring]
            if clip:
                draw.polygon(
                    [(x * SS, y * SS) for x, y in points],
                    fill=255 if index == 0 else 0
                )
            rings.append(points)

    mask = big.resize((width, height), Image.Resampling.BOX)
    return mask, rings, xy


def extract_outline_rings(geojson, box, width, height):
    xy = projector(box, width, height)
    output = []
    for polygon in iter_polygons(geojson):
        if not polygon:
            continue
        ring = polygon[0]
        if box_intersects_ring(ring, box):
            output.append([xy(lon, lat) for lon, lat in ring])
    return output


def outline_layer(size, groups):
    width, height = size
    layer = Image.new('RGBA', (width * SS, height * SS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    for rings, color, line_width in groups:
        for ring in rings:
            draw.line(
                [(x * SS, y * SS) for x, y in ring],
                fill=color,
                width=max(1, round(line_width * SS)),
                joint='curve'
            )

    return layer.resize((width, height), Image.Resampling.LANCZOS)


@lru_cache(maxsize=1)
def adm1_boundary():
    base = (
        'https://github.com/wmgeolab/geoBoundaries/raw/9469f09/'
        'releaseData/gbOpen/ECU/ADM1/geoBoundaries-ECU-ADM1.geojson'
    )
    path = fetch(base, STORE / 'cache' / 'ecuador-adm1.geojson')
    return json.loads(path.read_text(encoding='utf-8'))


# =============================================================================
# RÁSTER
# =============================================================================

def fill_missing(values, valid, iterations=FILL_ITERATIONS):
    vals = np.where(valid, values, 0.0).astype('float32')
    weight = valid.astype('float32')
    rows, cols = vals.shape

    for _ in range(iterations):
        if weight.all():
            break

        padded_v = np.pad(vals * weight, 1)
        padded_w = np.pad(weight, 1)
        total = np.zeros_like(vals)
        count = np.zeros_like(vals)

        for dy in (0, 1, 2):
            for dx in (0, 1, 2):
                if dy == 1 and dx == 1:
                    continue
                total += padded_v[dy:dy + rows, dx:dx + cols]
                count += padded_w[dy:dy + rows, dx:dx + cols]

        new = (weight == 0) & (count > 0)
        vals = np.where(new, total / np.maximum(count, 1e-6), vals)
        weight = np.where(new, 1.0, weight).astype('float32')

    return vals


def resize_values(values, width, height, kind):
    values = np.asarray(values, dtype='float32')
    valid = np.isfinite(values)

    if kind == 'categorical':
        clean = np.where(valid, values, 0).astype('float32')
        return np.asarray(
            Image.fromarray(clean).resize(
                (width, height),
                Image.Resampling.NEAREST
            )
        )

    filled = fill_missing(np.nan_to_num(values, nan=0.0), valid)
    smooth = np.asarray(
        Image.fromarray(filled).resize(
            (width, height),
            Image.Resampling.BICUBIC
        )
    )
    return np.clip(smooth, 0, None)


def load_galapagos_scene(project, date, gal_w, gal_h):
    """Native island statistics and a georeferenced display, preserving NoData.

    Some CHIRPS TIFFs contain -9999 without a declared nodata value. Ocean
    cells must be removed explicitly before interpolation or statistics.
    gal_w / gal_h son el tamaño del recuadro calculado por place_galapagos().
    """
    if not project.get('show_galapagos', True):
        return None

    # Imported global/regional rasters use the same inset only when the file
    # actually reaches Galápagos. Missing coverage stays transparent and the
    # caller hides the empty inset instead of drawing a misleading zero map.
    if project['source'] == 'local':
        entry = next((item for item in project.get('entries', [])
                      if item.get('date') == date), None)
        if not entry:
            return None
        path = Path(entry['path'])
        if not path.is_file():
            return None
        with rasterio.open(path) as src:
            if not src.crs or entry.get('band', 1) > src.count:
                return None
            data = np.full((gal_h, gal_w), np.nan, dtype='float32')
            nodata = (project['nodata'] if project.get('nodata') is not None
                      else src.nodata)
            method = (Resampling.nearest if project.get('kind') == 'categorical'
                      else Resampling.bilinear)
            reproject(
                source=rasterio.band(src, entry.get('band', 1)),
                destination=data, src_nodata=nodata, dst_nodata=np.nan,
                src_crs=src.crs,
                dst_crs='EPSG:4326',
                dst_transform=grid_from_bounds(*GALAPAGOS_BOX, gal_w, gal_h),
                resampling=method,
            )
        data = data * project.get('scale', 1.0) + project.get('offset', 0.0)
        island_mask, _, _ = build_mask_and_rings(
            boundary(), GALAPAGOS_BOX, gal_w, gal_h, clip=True,
            min_outer_area=GAL_MIN_AREA_DEG2
        )
        valid = np.isfinite(data) & (np.asarray(island_mask) > 64)
        data[~valid] = np.nan
        return {'values': data, 'valid_pixels': int(valid.sum()),
                'mean': float(data[valid].mean()) if valid.any() else None,
                'max': float(data[valid].max()) if valid.any() else None}

    if project['source'] != 'chirps':
        return None

    path, _ = rain_path(date)

    with MemoryFile(gzip.decompress(path.read_bytes())) as mem:
        with mem.open() as src:
            window = from_bounds(*GALAPAGOS_BOX, transform=src.transform)

            c0 = max(int(np.floor(window.col_off)) - 2, 0)
            r0 = max(int(np.floor(window.row_off)) - 2, 0)
            c1 = min(int(np.ceil(window.col_off + window.width)) + 2, src.width)
            r1 = min(int(np.ceil(window.row_off + window.height)) + 2, src.height)

            data = src.read(
                1,
                window=Window(c0, r0, c1 - c0, r1 - r0),
                masked=True
            ).filled(np.nan).astype('float32')

            valid = np.isfinite(data) & (data >= 0)
            data[~valid] = np.nan
            native_transform = src.window_transform(Window(c0, r0, c1-c0, r1-r0))
            target_transform = grid_from_bounds(*GALAPAGOS_BOX, gal_w, gal_h)
            smooth = np.full((gal_h, gal_w), np.nan, dtype='float32')
            support = np.zeros((gal_h, gal_w), dtype='uint8')
            reprojection = dict(src_transform=native_transform,
                                src_crs=src.crs or 'EPSG:4326',
                                dst_transform=target_transform, dst_crs='EPSG:4326')
            reproject(data, smooth, src_nodata=np.nan, dst_nodata=np.nan,
                      resampling=Resampling.bilinear, **reprojection)
            reproject(valid.astype('uint8'), support,
                      resampling=Resampling.nearest, **reprojection)
            smooth[support == 0] = np.nan

            # Statistics use original pixel centers in the inset, never ocean
            # fill or the resampled image. Each CHIRPS land pixel counts once.
            rows, cols = np.indices(data.shape)
            lon = native_transform.c + (cols + .5) * native_transform.a
            lat = native_transform.f + (rows + .5) * native_transform.e
            inside = ((lon >= GALAPAGOS_BOX[0]) & (lon <= GALAPAGOS_BOX[2]) &
                      (lat >= GALAPAGOS_BOX[1]) & (lat <= GALAPAGOS_BOX[3]))
            samples = data[valid & inside]

    return {'values': smooth, 'valid_pixels': int(samples.size),
            'mean': float(samples.mean()) if samples.size else None,
            'max': float(samples.max()) if samples.size else None}


def load_galapagos_values(project, date, gal_w=GAL_W_MAX,
                          gal_h=round(GAL_W_MAX * GAL_ASPECT)):
    """Compatibility helper; missing coverage remains NaN, never zero."""
    scene = load_galapagos_scene(project, date, gal_w, gal_h)
    return scene['values'] if scene is not None else None


# =============================================================================
# DISEÑO
# =============================================================================

def make_glow(mask, accent, strength=0.16):
    rgb = ImageColor.getrgb(accent)
    alpha = mask.filter(ImageFilter.GaussianBlur(18)).point(
        lambda value: int(value * strength)
    )
    glow = Image.new('RGBA', mask.size, (*rgb, 0))
    glow.putalpha(alpha)
    return glow


def place_galapagos(main_mask, map_x, map_y):
    """Recuadro de Galápagos más grande posible que no toque el mapa continental.

    Coloca el recuadro arriba a la izquierda, achicando de GAL_W_MAX a
    GAL_W_MIN si hace falta. Esta es una ampliación cartográfica, por lo que
    puede convivir sobre el borde occidental del mapa continental.
    """
    occ = Image.new('L', (WIDTH, HEIGHT), 0)
    occ.paste(main_mask.filter(ImageFilter.MaxFilter(15)), (map_x, map_y))
    occ = np.asarray(occ) > 0

    for gw in range(GAL_W_MAX, GAL_W_MIN - 1, -5):
        gh = round(gw * GAL_ASPECT)
        pw, ph = gw + 35, gh + 70
        py = 560
        return {'panel': (48, py, 48 + pw, py + ph),
                'x': 65, 'y': py + 46, 'w': gw, 'h': gh}
    return None


def build_safe_layout():
    left, top, right, bottom = DESIGN_CROP
    crop_w = right - left
    crop_h = bottom - top

    box_w = WIDTH - SAFE_LEFT - SAFE_RIGHT
    box_h = HEIGHT - SAFE_TOP - SAFE_BOTTOM

    scale = min(box_w / crop_w, box_h / crop_h, 1.0)
    new_w = round(crop_w * scale)
    new_h = round(crop_h * scale)

    x = SAFE_LEFT + (box_w - new_w) // 2
    y = SAFE_TOP + (box_h - new_h) // 2

    return {
        'crop': DESIGN_CROP,
        'size': (new_w, new_h),
        'pos': (x, y),
        'scale': scale,
    }


SAFE_LAYOUT = build_safe_layout()


def compose_final(design):
    canvas = Image.new('RGB', (WIDTH, HEIGHT), design.getpixel((0, 0)))
    piece = design.crop(SAFE_LAYOUT['crop']).resize(
        SAFE_LAYOUT['size'],
        Image.Resampling.LANCZOS
    )
    canvas.paste(piece, SAFE_LAYOUT['pos'])
    return canvas


def split_source(citation):
    chunks = [part.strip() for part in citation.replace('/', ' / ').split('·') if part.strip()]
    if not chunks:
        return 'Fuente de datos', ''
    if len(chunks) == 1:
        return chunks[0], ''
    return chunks[0], ' · '.join(chunks[1:])


def period_word(cadence, count):
    if cadence == 'Diaria':
        return 'DÍA' if count == 1 else 'DÍAS'
    if cadence == 'Mensual':
        return 'MES' if count == 1 else 'MESES'
    if cadence == 'Anual':
        return 'AÑO' if count == 1 else 'AÑOS'
    return 'FECHA' if count == 1 else 'FECHAS'


def counter_word(project):
    return project['counter_label'] or {
        'Diaria': 'DÍA',
        'Mensual': 'MES',
        'Anual': 'AÑO',
        'Por observación': 'OBS.',
    }[project['cadence']]


def title_parts(project):
    title = project['title'].strip().upper()
    words = title.split()
    if not words:
        return '', ''
    return words[0], ' '.join(words[1:])


def compose_maqueta(project, values, boundary, date, index, count):
    """Return one frame using the approved Ecuador Vivo template."""

    bg = project['background']
    white = project['text']
    accent = project['accent']
    muted = '#B5C5CB'
    line_color = '#5E7F90'
    vline_color = '#4E6876'
    panel = '#172835'

    box = tuple(float(v) for v in project['bbox'])

    # Main map dimensions keep the geographic aspect ratio inside the approved box.
    ratio = (box[2] - box[0]) / (box[3] - box[1])
    target_ratio = MAIN_W / MAIN_H

    if ratio < target_ratio:
        map_h = MAIN_H
        map_w = max(1, round(MAIN_H * ratio))
    else:
        map_w = MAIN_W
        map_h = max(1, round(MAIN_W / ratio))

    map_x = MAIN_X + (MAIN_W - map_w) // 2
    map_y = MAIN_Y + (MAIN_H - map_h) // 2

    main_mask, main_rings, main_xy = build_mask_and_rings(
        boundary,
        box,
        map_w,
        map_h,
        clip=project['clip_ecuador']
    )

    main_provinces = []
    if project.get('show_provinces', True) and project['clip_ecuador']:
        try:
            main_provinces = extract_outline_rings(
                adm1_boundary(),
                box,
                map_w,
                map_h
            )
        except Exception:
            main_provinces = []

    # The template makes geographic sense for any Ecuador-wide layer. An empty
    # local coverage is detected below and simply does not draw an inset.
    show_gal = (
        project.get('show_galapagos', True)
        and project['clip_ecuador']
        and abs(box[0] - MAIN_BOX[0]) < 0.3
        and abs(box[1] - MAIN_BOX[1]) < 0.3
        and abs(box[2] - MAIN_BOX[2]) < 0.3
        and abs(box[3] - MAIN_BOX[3]) < 0.3
    )

    # El recuadro se coloca solo, sin tocar el mapa continental.
    gal = place_galapagos(main_mask, map_x, map_y) if show_gal else None
    show_gal = gal is not None

    gal_mask = None
    gal_rings = []
    gal_values = None

    if show_gal:
        gal_mask, gal_rings, _ = build_mask_and_rings(
            boundary,
            GALAPAGOS_BOX,
            gal['w'],
            gal['h'],
            clip=True,
            min_outer_area=GAL_MIN_AREA_DEG2
        )
        # Do not show an empty box when an imported scene ends at the mainland.
        gal_scene = load_galapagos_scene(project, date, gal['w'], gal['h'])
        if gal_scene is None or not np.isfinite(gal_scene['values']).any():
            show_gal = False
            gal = None
            gal_mask = None
            gal_rings = []
        else:
            gal_values = gal_scene['values']

    # -------------------------------------------------------------------------
    # Base
    # -------------------------------------------------------------------------
    design = Image.new('RGBA', (WIDTH, HEIGHT), bg)
    draw = ImageDraw.Draw(design)

    # -------------------------------------------------------------------------
    # Title line 1
    # -------------------------------------------------------------------------
    line1 = f'{count} {period_word(project["cadence"], count)} DE'
    line1_font = fit_text('display', 100, 970, line1)
    baseline1 = 216

    words = line1.split()
    first = words[0]
    rest = ' '.join(words[1:])
    gap = round(line1_font.size * 0.17)

    first_left, _, first_right, _ = text_bbox(line1_font, first)
    x = 59

    gradient_text(
        design,
        x - first_left,
        baseline1,
        first,
        line1_font,
        '#6AF0D0',
        '#54DCC5'
    )
    x += (first_right - first_left) + gap

    rest_left, _, _, _ = text_bbox(line1_font, rest)
    draw.text(
        (x - rest_left, baseline1),
        rest,
        font=line1_font,
        fill=white,
        anchor='ls'
    )

    # -------------------------------------------------------------------------
    # Brand above the accent mark
    # -------------------------------------------------------------------------
    ink_top = baseline1 + min(text_bbox(line1_font, word)[1] for word in words)
    brand_base = max(50, min(86, ink_top - 22))
    brand = project['brand'].upper()

    draw_tracked(
        draw,
        61,
        brand_base,
        brand,
        'bold',
        27,
        512,
        accent
    )

    draw.line(
        (599, brand_base - 13, 683, brand_base - 13),
        fill='#7C969E',
        width=2
    )

    # -------------------------------------------------------------------------
    # Title line 2
    # -------------------------------------------------------------------------
    baseline2 = 322
    title = project['title'].strip().upper()
    title_font = fit_text('display', 100, 971, title)

    first_word, rest_title = title_parts(project)
    x = 59

    if first_word:
        left, _, right, _ = text_bbox(title_font, first_word)
        gradient_text(
            design,
            x - left,
            baseline2,
            first_word,
            title_font,
            project['title_gradient_1'],
            project['title_gradient_2']
        )
        x += (right - left) + round(title_font.size * 0.17)

    if rest_title:
        left, _, _, _ = text_bbox(title_font, rest_title)
        draw.text(
            (x - left, baseline2),
            rest_title,
            font=title_font,
            fill=white,
            anchor='ls'
        )

    # -------------------------------------------------------------------------
    # Subtitle
    # -------------------------------------------------------------------------
    draw.rounded_rectangle((56, 335, 1027, 402), radius=18, fill=panel)
    draw_line(
        draw,
        78,
        383,
        project['description'],
        'regular',
        29,
        892,
        '#F2F5F6'
    )

    # -------------------------------------------------------------------------
    # Date / counter
    # -------------------------------------------------------------------------
    day = dt.date.fromisoformat(date)

    if project['cadence'] == 'Mensual':
        date_text = f'{MONTHS[day.month - 1]} {day.year}'
    elif project['cadence'] == 'Anual':
        date_text = str(day.year)
    else:
        if project['date_format'] == 'AAAA-MM-DD':
            date_text = day.strftime('%Y-%m-%d')
        elif project['date_format'] == 'MM / DD / AAAA':
            date_text = day.strftime('%m / %d / %Y')
        else:
            date_text = f'{day.day:02d} {MONTHS[day.month - 1]} {day.year}'

    draw_calendar_icon(draw, 56, 438, white)

    date_font = fit_text('display', 42, 304, date_text)
    left = text_bbox(date_font, date_text)[0]
    draw.text(
        (151 - left, 485),
        date_text,
        font=date_font,
        fill=white,
        anchor='ls'
    )

    draw.line((543, 431, 543, 498), fill='#59737C', width=3)

    if project.get('show_play_button', True):
        draw_play_button(draw, (631, 431, 706, 507), white)

    draw.rounded_rectangle(
        (728, 428, 1041, 510),
        radius=40,
        outline='#7D8F9A',
        width=3
    )

    prefix = counter_word(project)
    number = index + 1
    total = count

    counter_full = f'{prefix} {number:02d} / {total}'
    counter_font = fit_text('display', 38, 260, counter_full)

    # Draw as pieces so the number keeps the accent color.
    total_text = str(total)
    right = 1012
    base = 490
    slash_gap = 16

    total_w = text_width(counter_font, total_text)
    draw.text((right, base), total_text, font=counter_font, fill=white, anchor='rs')
    right -= total_w + slash_gap

    slash_w = text_width(counter_font, '/')
    draw.text((right, base), '/', font=counter_font, fill='#9DAFCA', anchor='rs')
    right -= slash_w + slash_gap

    number_text = f'{number:02d}'
    num_w = text_width(counter_font, number_text)
    draw.text((right, base), number_text, font=counter_font, fill=accent, anchor='rs')
    right -= num_w + slash_gap

    draw.text((right, base), prefix, font=counter_font, fill=white, anchor='rs')

    # -------------------------------------------------------------------------
    # Map glow
    # -------------------------------------------------------------------------
    design.alpha_composite(
        make_glow(main_mask, accent),
        (map_x, map_y)
    )

    if show_gal and gal_mask is not None:
        design.alpha_composite(
            make_glow(gal_mask, accent),
            (gal['x'], gal['y'])
        )

    # -------------------------------------------------------------------------
    # Main raster
    # -------------------------------------------------------------------------
    resized = resize_values(values, map_w, map_h, project['kind'])
    main_rgb = Image.fromarray(colorize(resized, project))

    if project['clip_ecuador']:
        design.paste(main_rgb, (map_x, map_y), main_mask)
    else:
        design.paste(main_rgb, (map_x, map_y))

    # -------------------------------------------------------------------------
    # Galápagos raster
    # -------------------------------------------------------------------------
    if show_gal and gal_mask is not None and gal_values is not None:
        gal_rgb = Image.fromarray(colorize(gal_values, project))
        covered = Image.fromarray(np.where(np.isfinite(gal_values),
                                          np.asarray(gal_mask), 0).astype('uint8'))
        design.paste(gal_rgb, (gal['x'], gal['y']), covered)

    # -------------------------------------------------------------------------
    # Outlines
    # -------------------------------------------------------------------------
    top = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))

    groups = []
    if main_provinces:
        groups.append((main_provinces, PROVINCE_BORDER, 1.2))
    groups.append((main_rings, MAP_BORDER, 2.2))

    main_lines = outline_layer((map_w, map_h), groups)
    top.alpha_composite(main_lines, (map_x, map_y))

    if show_gal and gal_mask is not None:
        gal_lines = outline_layer(
            (gal['w'], gal['h']),
            [(gal_rings, MAP_BORDER, 1.4)]
        )
        top.alpha_composite(gal_lines, (gal['x'], gal['y']))

    top_draw = ImageDraw.Draw(top)

    # -------------------------------------------------------------------------
    # Cities
    # -------------------------------------------------------------------------
    city_font = fit_text('bold', 24, 105, 'Guayaquil')

    for name, lon, lat in CITIES:
        if name not in project['cities']:
            continue
        if not (box[0] <= lon <= box[2] and box[1] <= lat <= box[3]):
            continue

        cx, cy = main_xy(lon, lat)
        cx += map_x
        cy += map_y

        # Marcadores de alto contraste: el relleno casi blanco destaca sobre
        # cualquier valor del ráster y el borde oscuro evita que se pierdan
        # sobre las provincias o los colores cálidos de la escala.
        top_draw.ellipse(
            (cx - 9, cy - 9, cx + 9, cy + 9),
            fill='#F8FBFF',
            outline='#06131C',
            width=4,
        )

        label = project['city_labels'].get(name, name)
        if not label:
            continue

        top_draw.text(
            (cx + 16, cy - 16),
            label,
            font=city_font,
            fill='white',
            anchor='lm',
            stroke_width=3,
            stroke_fill='#06131C'
        )

    design.alpha_composite(top)

    # -------------------------------------------------------------------------
    # Legend
    # -------------------------------------------------------------------------
    legend = project['legend']
    if project['units']:
        legend += f' · {project["units"]}'

    draw = ImageDraw.Draw(design)
    draw_line(
        draw,
        55,
        1520,
        legend,
        'bold',
        27,
        700,
        white
    )

    if project['kind'] == 'continuous':
        bar_x0, bar_x1, bar_y0, bar_y1 = 75, 1008, 1541, 1578
        bar_w = bar_x1 - bar_x0
        stops = project['stops']

        gradient_values = np.interp(
            np.linspace(0, len(stops) - 1, bar_w),
            np.arange(len(stops)),
            stops
        )

        bar = Image.fromarray(
            np.repeat(
                colorize(gradient_values[None, :], project),
                bar_y1 - bar_y0,
                axis=0
            )
        )

        bar_mask = Image.new('L', (bar_w * SS, (bar_y1 - bar_y0) * SS), 0)
        ImageDraw.Draw(bar_mask).rounded_rectangle(
            (0, 0, bar_w * SS - 1, (bar_y1 - bar_y0) * SS - 1),
            radius=4 * SS,
            fill=255
        )
        bar_mask = bar_mask.resize(
            (bar_w, bar_y1 - bar_y0),
            Image.Resampling.LANCZOS
        )

        design.paste(bar, (bar_x0, bar_y0), bar_mask)

        label_font = fit_text('label', 27, 66, '120+')

        for position, value in enumerate(stops):
            tick_x = bar_x0 + position * bar_w / (len(stops) - 1)
            draw.line(
                (tick_x, bar_y1 + 2, tick_x, bar_y1 + 21),
                fill='#DFE6EA',
                width=2
            )
            label = f'{value:g}' + ('+' if position == len(stops) - 1 else '')
            draw.text(
                (tick_x, 1635),
                label,
                font=label_font,
                fill='#DADCDF',
                anchor='ms'
            )
    else:
        x0 = 75
        y0 = 1544
        for idx, row in enumerate(project['classes'][:8]):
            col = idx % 4
            row_i = idx // 4
            x = x0 + col * 230
            y = y0 + row_i * 55
            draw.rounded_rectangle(
                (x, y, x + 28, y + 28),
                radius=5,
                fill=row['color']
            )
            draw_line(
                draw,
                x + 40,
                y + 24,
                row['label'],
                'regular',
                19,
                175,
                white
            )

    # -------------------------------------------------------------------------
    # Footer
    # -------------------------------------------------------------------------
    draw.line((56, 1689, 1025, 1689), fill=line_color, width=2)
    draw.line((587, 1716, 587, 1836), fill=vline_color, width=2)

    icon_color = '#E4EFEA'
    draw_database_icon(draw, 57, 1722, icon_color)

    source_main, source_detail = split_source(project['citation'])

    draw_line(draw, 146, 1753, 'Fuente:', 'bold', 24, 90, white)
    draw_line(draw, 238, 1753, source_main, 'regular', 24, 260, '#E9E6F7')

    if source_detail:
        draw_line(draw, 148, 1788, source_detail, 'regular', 20, 390, '#EEF1F2')

    boundary_caption = project['boundary_note']
    if not boundary_caption:
        if project['clip_ecuador'] and show_gal:
            boundary_caption = 'Ecuador continental + Galápagos · Límites: geoBoundaries'
        elif project['clip_ecuador']:
            boundary_caption = 'Ecuador continental · Límites: geoBoundaries'
        else:
            boundary_caption = 'Ventana geográfica · Límites: geoBoundaries'
    draw_line(
        draw,
        148,
        1819,
        boundary_caption,
        'regular',
        17,
        416,
        '#C2D5E3'
    )

    draw_mountain_icon(draw, 614, 1720, icon_color)

    draw_line(
        draw,
        708,
        1738,
        project['author'],
        'bold',
        22,
        309,
        white
    )
    draw_line(
        draw,
        709,
        1772,
        project['credits'],
        'regular',
        19,
        240,
        '#EBEEF0'
    )

    # Redes sociales en una sola línea (ambas se mantienen porque el mismo
    # MP4 circula en distintas plataformas).
    tk = project.get('tiktok', '@elgeocientifico')
    ig = project.get('instagram', '@henry_conteron')
    social_text = f'{tk} · {ig}'
    social_font = fit_text('bold', 16, 225, social_text)

    draw_tiktok_icon(draw, 709, 1796, white)
    draw_instagram_icon(draw, 752, 1799, white)
    draw.text(
        (800, 1823),
        social_text,
        font=social_font,
        fill=accent,
        anchor='ls'
    )

    # -------------------------------------------------------------------------
    # Safe-area composition
    # -------------------------------------------------------------------------
    result = compose_final(design.convert('RGB'))

    if project['width'] != 1080:
        result = result.resize(
            (project['width'], project['width'] * 16 // 9),
            Image.Resampling.LANCZOS
        )

    return result
