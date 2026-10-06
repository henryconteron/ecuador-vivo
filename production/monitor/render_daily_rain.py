"""Render real daily CHIRPS data as a vertical, dated video.

Formato:
    1080 x 1920  (TikTok / Instagram Reels / Shorts)

Cada frame representa un día real de CHIRPS v2.
No se realiza interpolación temporal entre días.

Uso:
    python production/monitor/render_daily_rain.py --days 1
    python production/monitor/render_daily_rain.py --days 7
    python production/monitor/render_daily_rain.py --days 366

Opciones de formato:
    --guides     pinta las bandas que tapan las apps (solo para revisar, no
                 para publicar). El archivo sale con sufijo -guides.
    --no-safe    desactiva la zona segura y usa el diseño a pantalla completa
                 (como era antes).

Diseño: calibrado píxel a píxel sobre la maqueta aprobada (títulos, botón de
reproducción, contador, escala de color con marcas, Galápagos con datos y pie
de página). Todo lo que no cambia entre días se dibuja una sola vez; cada frame
solo calcula el mapa, la fecha y el contador.

Zona segura: el diseño se dibuja en el lienzo de la maqueta (1080 x 1920) y al
final se recorta y se reduce para que quede dentro de la zona que NO tapan las
interfaces de TikTok / Instagram Reels (barra superior, descripción abajo y
columna de botones a la derecha). Los márgenes se cambian en SAFE_* más abajo.

Tipografía: usa Bahnschrift (Windows 10/11) en peso/ancho condensado. Si no
existe, cae a Arial Narrow / Segoe UI / Inter / DejaVu. Los textos se ajustan al
ancho de la maqueta, así que el diseño no se desarma con otra fuente.
"""

import argparse
import calendar
import datetime as dt
import gzip
import hashlib
import json
import time
import urllib.request
from functools import lru_cache
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from rasterio.io import MemoryFile
from rasterio.windows import Window, from_bounds


# =============================================================================
# CONFIGURACIÓN
# =============================================================================

ROOT = Path(__file__).resolve().parents[2]

WIDTH = 1080
HEIGHT = 1920
FPS = 30

# Zona segura (px sobre el lienzo final de 1080 x 1920).
# Valores de compromiso entre TikTok, Instagram Reels y Shorts:
#   arriba   ~ barra de la app / pestañas
#   abajo    ~ usuario, descripción y sonido
#   derecha  ~ columna de botones (like, comentar, compartir)
# Si quieres ser más estricto con Reels (Meta pide 14 % arriba y 35 % abajo)
# sube SAFE_TOP a ~270 y SAFE_BOTTOM a ~670; el diseño se reduce solo.
SAFE_ZONE = True
SAFE_LEFT = 60
SAFE_RIGHT = 120
SAFE_TOP = 190
SAFE_BOTTOM = 400

# Parte del lienzo de diseño que se mete en la zona segura
# (izquierda, arriba, derecha, abajo). Deja un pequeño margen alrededor
# del contenido real: marca arriba, pie de página abajo.
DESIGN_CROP = (45, 20, 1050, 1842)

# Marca superior: se coloca sola por encima de la tilde de "DÍAS".
BRAND_BASELINE = 86       # posición original (si no hay choque)
BRAND_CLEARANCE = 22      # espacio libre entre marca y la tilde
BRAND_MIN_BASELINE = 50   # tope para que no se salga del recorte

# Supermuestreo para bordes y máscaras suaves (antialiasing).
SS = 3

# Extensiones geográficas (lon_min, lat_min, lon_max, lat_max)
MAIN_BOX = (-81.5, -5.2, -75.0, 1.8)
GALAPAGOS_BOX = (-92.2, -1.8, -88.8, 1.9)  # incluye Darwin y Wolf

# Mapa principal: 145,5 px por grado (igual que la maqueta).
MAIN_X, MAIN_Y, MAIN_W, MAIN_H = 93, 468, 946, 1019

# Inset de Galápagos: 60 px por grado.
GAL_X, GAL_Y, GAL_W, GAL_H = 9, 592, 204, 222

# Celdas CHIRPS (0,05°) sin dato en costa/islas se rellenan con el promedio de
# sus vecinas válidas, solo para el dibujo. Se registra en receipt.json.
FILL_ITERATIONS = 8

# Escala de precipitación (mm/día). Las 8 marcas de la leyenda están a igual
# distancia; el color se interpola entre marcas.
COLORS = [
    '052c44',
    '0a6194',
    '1da9d6',
    '42c9c7',
    'bcec98',
    'fed35c',
    'fd643b',
    'cf2a6a',
]
STOPS = np.array([0, 1, 5, 10, 20, 40, 70, 120], dtype=float)

# Identidad visual
BG = '#04141F'
WHITE = '#F8FAFB'
MUTED = '#B5C5CB'
AQUA = '#5DF2D8'
BRAND = '#6FF0D2'
SLASH = '#9DAFCA'
PANEL = '#172835'
LINE = '#5E7F90'
VLINE = '#4E6876'
MAP_BORDER = (244, 248, 246, 255)
PROVINCE_BORDER = (190, 210, 216, 150)

SOCIAL_HANDLE = '@elgeocientifico'


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

# kind -> (peso, ancho) para Bahnschrift + alternativas estáticas
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
            font = ImageFont.truetype(str(variable), size)
            values = []
            for axis in font.get_variation_axes():
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
                values.append(
                    min(max(value, axis['minimum']), axis['maximum'])
                )
            font.set_variation_by_axes(values)
            return font
        except Exception:
            pass

    static = find_font(*spec['static'])
    if static:
        return ImageFont.truetype(str(static), size)

    return ImageFont.load_default(size)


def text_bbox(font, text):
    """Caja de tinta relativa al origen en la línea base (anchor 'ls')."""
    return font.getbbox(text, anchor='ls')


def text_width(font, text):
    left, _, right, _ = text_bbox(font, text)
    return right - left


def size_for_cap(kind, cap):
    for size in range(8, 420):
        top = make_font(kind, size).getbbox('H', anchor='ls')[1]
        if -top >= cap:
            return size
    return 420


def word_gap(size):
    return round(size * 0.17)


def fit_cap_width(kind, cap, target, width_of):
    """Altura de mayúsculas fija (la de la maqueta) y ancho de texto = target.

    Con Bahnschrift se usa el eje de ancho (de condensado a normal) para
    llenar `target` sin cambiar la altura. Si ni siquiera el ancho mínimo cabe,
    se reduce el tamaño. Con fuentes sin eje de ancho solo actúa el tamaño.
    width_of(size, wdth) -> ancho en px.
    """
    base = FONT_SPECS[kind]['width']
    size = size_for_cap(kind, cap)
    while size > 8 and width_of(size, base) > target:
        size -= 1

    low, high, best = base, 100, base
    while low <= high:
        mid = (low + high) // 2
        if width_of(size, mid) <= target:
            best = mid
            low = mid + 1
        else:
            high = mid - 1
    return size, best


def parts_width(parts, size, width, gap_ratio=0.28):
    total = sum(
        text_width(make_font(kind, size, width), text)
        for text, kind, _ in parts
    )
    return total + round(size * gap_ratio) * (len(parts) - 1)


def draw_parts(draw, x, baseline, parts, size, width, gap_ratio=0.28):
    for text, kind, fill in parts:
        font = make_font(kind, size, width)
        left, _, right, _ = text_bbox(font, text)
        draw.text((x - left, baseline), text, font=font, fill=fill,
                  anchor='ls')
        x += (right - left) + round(size * gap_ratio)


def draw_line(draw, x, baseline, text, kind, cap, target_width, fill):
    """Dibuja `text` con altura de mayúsculas `cap` y ancho `target_width`."""
    size, width = fit_cap_width(
        kind, cap, target_width,
        lambda s, w: text_width(make_font(kind, s, w), text))
    font = make_font(kind, size, width)
    left = text_bbox(font, text)[0]
    draw.text((x - left, baseline), text, font=font, fill=fill, anchor='ls')
    return size


def draw_tracked(draw, x, baseline, text, kind, cap, target_width, fill):
    """Texto en mayúsculas con espaciado entre letras hasta `target_width`."""
    size = size_for_cap(kind, cap)
    while True:
        font = make_font(kind, size)
        widths = [font.getlength(ch) for ch in text]
        tracking = (target_width - sum(widths)) / (len(text) - 1)
        if tracking >= 0.8 or size <= 12:
            break
        size -= 1
    for ch, width in zip(text, widths):
        draw.text((x, baseline), ch, font=font, fill=fill, anchor='ls')
        x += width + tracking


# =============================================================================
# DESCARGAS / CACHÉ
# =============================================================================

def fetch(url, target, attempts=3):
    target.parent.mkdir(parents=True, exist_ok=True)

    if not target.exists():
        print('Downloading:', target.name, flush=True)

        for attempt in range(1, attempts + 1):
            try:
                with urllib.request.urlopen(url, timeout=120) as response:
                    payload = response.read()
                break
            except Exception as error:
                if attempt == attempts:
                    raise
                print(f'  retry {attempt}/{attempts - 1}: {error}',
                      flush=True)
                time.sleep(3 * attempt)

        partial = target.with_name(target.name + '.part')
        partial.write_bytes(payload)
        partial.replace(target)

    return target.read_bytes()


# =============================================================================
# COLOR
# =============================================================================

def hex_to_rgb(value):
    value = value.lstrip('#')
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


_RGB = np.array([hex_to_rgb(color) for color in COLORS], dtype=float)


def colorize(values):
    return np.stack(
        [
            np.interp(values, STOPS, _RGB[:, channel])
            for channel in range(3)
        ],
        axis=-1,
    ).astype('uint8')


def gradient_text(image, x, baseline, text, font, color_left, color_right):
    """Texto con degradado horizontal; (x, baseline) = esquina de tinta."""
    mask = Image.new('L', image.size, 0)
    ImageDraw.Draw(mask).text((x, baseline), text, font=font, fill=255,
                              anchor='ls')
    bbox = mask.getbbox()
    if bbox is None:
        return

    x0, y0, x1, y1 = bbox
    width, height = x1 - x0, y1 - y0
    t = np.linspace(0, 1, width)[None, :, None]
    left = np.array(hex_to_rgb(color_left), dtype=float)[None, None, :]
    right = np.array(hex_to_rgb(color_right), dtype=float)[None, None, :]
    row = left * (1 - t) + right * t
    gradient = np.repeat(row, height, axis=0).astype('uint8')

    image.paste(
        Image.fromarray(gradient, 'RGB'),
        (x0, y0),
        mask.crop(bbox),
    )


# =============================================================================
# ICONOS
# =============================================================================

def draw_calendar_icon(draw, x, y, s=1.25):
    c = WHITE
    body = 44 * s
    stroke = round(3 * s)
    draw.rounded_rectangle(
        (x, y, x + body, y + body),
        radius=5 * s,
        outline=c,
        width=stroke,
    )
    draw.line((x, y + 13 * s, x + body, y + 13 * s), fill=c, width=stroke)
    for px in (11, 33):
        draw.line(
            (x + px * s, y - 5 * s, x + px * s, y + 7 * s),
            fill=c,
            width=round(4 * s),
        )


def draw_play_button(draw, box):
    x0, y0, x1, y1 = box
    draw.ellipse(box, fill='#1C2B37')
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    draw.polygon(
        [(cx - 10, cy - 17), (cx - 10, cy + 17), (cx + 18, cy)],
        fill=WHITE,
    )


def draw_database_icon(draw, x, y, w=58, h=74):
    c = '#E4EFEA'
    e = round(w * 0.28)
    draw.ellipse((x, y, x + w, y + e), outline=c, width=3)
    draw.line((x, y + e / 2, x, y + h - e / 2), fill=c, width=3)
    draw.line((x + w, y + e / 2, x + w, y + h - e / 2), fill=c, width=3)
    for k in (1, 2, 3):
        yk = y + e / 2 + k * (h - e) / 3
        draw.arc((x, yk - e / 2, x + w, yk + e / 2), 0, 180, fill=c, width=3)


def draw_mountain_icon(draw, x, y):
    c = '#E4EFEA'
    draw.line((x, y + 43, x + 26, y + 3, x + 49, y + 43), fill=c, width=3)
    draw.line((x + 32, y + 43, x + 48, y + 17, x + 70, y + 43), fill=c,
              width=3)


def draw_instagram_icon(draw, x, y):
    c = WHITE
    draw.rounded_rectangle((x, y, x + 32, y + 32), radius=9, outline=c,
                           width=3)
    draw.ellipse((x + 8, y + 8, x + 24, y + 24), outline=c, width=3)
    draw.ellipse((x + 23, y + 5, x + 27, y + 9), fill=c)


def draw_tiktok_icon(draw, x, y):
    c = WHITE
    draw.line((x + 18, y + 3, x + 18, y + 26), fill=c, width=5)
    draw.line((x + 18, y + 4, x + 30, y + 11), fill=c, width=5)
    draw.ellipse((x + 3, y + 21, x + 20, y + 37), fill=c)


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
        return (x, y)

    return xy


def iter_polygons(geojson):
    for feature in geojson['features']:
        geometry = feature['geometry']
        if geometry is None:
            continue
        if geometry['type'] == 'MultiPolygon':
            yield from geometry['coordinates']
        elif geometry['type'] == 'Polygon':
            yield geometry['coordinates']


def build_mask_and_rings(geojson, box, width, height):
    """Máscara suavizada (supermuestreada), anillos y proyector."""
    xy = projector(box, width, height)
    big = Image.new('L', (width * SS, height * SS), 0)
    draw = ImageDraw.Draw(big)
    rings = []

    for polygon in iter_polygons(geojson):
        for index, ring in enumerate(polygon):
            if not box_intersects_ring(ring, box):
                continue
            points = [xy(lon, lat) for lon, lat in ring]
            draw.polygon(
                [(x * SS, y * SS) for x, y in points],
                fill=255 if index == 0 else 0,
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
    """Líneas suaves: groups = [(anillos, color RGBA, ancho en px), ...]."""
    width, height = size
    layer = Image.new('RGBA', (width * SS, height * SS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for rings, color, line_width in groups:
        for ring in rings:
            draw.line(
                [(x * SS, y * SS) for x, y in ring],
                fill=color,
                width=max(1, round(line_width * SS)),
                joint='curve',
            )
    return layer.resize((width, height), Image.Resampling.LANCZOS)


# =============================================================================
# RÁSTER CHIRPS
# =============================================================================

def fill_missing(values, valid, iterations):
    """Rellena celdas sin dato con el promedio de vecinas válidas (8-vecindad)."""
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


def render_chirps_region(src, box, width, height, mask_array):
    """Devuelve (imagen RGB, celdas válidas, celdas de tierra rellenadas)."""
    window = from_bounds(*box, transform=src.transform)

    c0 = max(int(np.floor(window.col_off)) - 2, 0)
    r0 = max(int(np.floor(window.row_off)) - 2, 0)
    c1 = min(int(np.ceil(window.col_off + window.width)) + 2, src.width)
    r1 = min(int(np.ceil(window.row_off + window.height)) + 2, src.height)

    data = src.read(
        1,
        window=Window(c0, r0, c1 - c0, r1 - r0),
        masked=True,
    ).filled(np.nan).astype('float32')

    valid = np.isfinite(data) & (data >= 0)
    filled = fill_missing(np.nan_to_num(data, nan=0.0), valid,
                          FILL_ITERATIONS)

    # Recorte exacto de la caja geográfica (sin redondear a celdas).
    crop = (
        window.col_off - c0,
        window.row_off - r0,
        window.col_off - c0 + window.width,
        window.row_off - r0 + window.height,
    )
    smooth = np.asarray(
        Image.fromarray(filled).resize(
            (width, height),
            Image.Resampling.BICUBIC,
            box=crop,
        )
    )
    smooth = np.clip(smooth, 0, None)

    # ¿Cuántas celdas de tierra no traían dato y se rellenaron?
    transform = src.transform
    lons = transform.c + (np.arange(c0, c1) + 0.5) * transform.a
    lats = transform.f + (np.arange(r0, r1) + 0.5) * transform.e
    px = np.floor((lons - box[0]) / (box[2] - box[0]) * width).astype(int)
    py = np.floor((box[3] - lats) / (box[3] - box[1]) * height).astype(int)
    inside = np.outer(
        (py >= 0) & (py < height),
        (px >= 0) & (px < width),
    )
    land = np.zeros(valid.shape, dtype=bool)
    ii, jj = np.where(inside)
    land[ii, jj] = mask_array[py[ii], px[jj]] > 127
    filled_land = int((land & ~valid).sum())

    return Image.fromarray(colorize(smooth)), valid, filled_land


# =============================================================================
# CAPA ESTÁTICA (se dibuja una sola vez)
# =============================================================================

def make_glow(mask, strength=0.16):
    alpha = mask.filter(ImageFilter.GaussianBlur(18)).point(
        lambda value: int(value * strength)
    )
    glow = Image.new('RGBA', mask.size, (44, 190, 197, 0))
    glow.putalpha(alpha)
    return glow


MONTHS = (
    'ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN',
    'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC',
)

CITIES = [
    ('Quito', -78.4678, -0.1807),
    ('Guayaquil', -79.889, -2.17),
    ('Cuenca', -79.005, -2.9),
    ('Tena', -77.813, -0.994),
]


def build_static(year, total_days, geometry):
    """Devuelve (fondo, capa superior, parámetros de texto dinámico)."""
    frame = Image.new('RGBA', (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(frame)

    # ---- título ------------------------------------------------------------
    # Se calcula antes que la marca: la tilde de la Í de "DÍAS" sube por
    # encima de las mayúsculas y la marca tiene que quedar por encima de ella.
    def title_width(size, width):
        font = make_font('display', size, width)
        return (
            sum(text_width(font, w) for w in ('LLUVIA', 'EN', 'ECUADOR'))
            + word_gap(size) * 2
        )

    title_size, title_wd = fit_cap_width('display', 100, 971, title_width)
    title_font = make_font('display', title_size, title_wd)
    gap = word_gap(title_size)

    line1_base, line2_base = 216, 322

    # ---- marca (encima de la tilde, nunca tapada por el título) ------------
    ink_top = line1_base + min(
        text_bbox(title_font, w)[1] for w in (str(total_days), 'DÍAS', 'DE')
    )
    brand_base = max(
        BRAND_MIN_BASELINE,
        min(BRAND_BASELINE, ink_top - BRAND_CLEARANCE),
    )
    draw_tracked(draw, 61, brand_base, 'ECUADOR VIVO / ANDES PULSO', 'bold',
                 27, 512, BRAND)
    draw.line((599, brand_base - 13, 683, brand_base - 13), fill='#7C969E',
              width=2)

    x = 59
    for word, kind in (('366', 'grad_aqua'), ('DÍAS', 'white'),
                       ('DE', 'white')):
        word = str(total_days) if kind == 'grad_aqua' else word
        left, _, right, _ = text_bbox(title_font, word)
        if kind == 'grad_aqua':
            gradient_text(frame, x - left, line1_base, word, title_font,
                          '#6AF0D0', '#54DCC5')
        else:
            draw.text((x - left, line1_base), word, font=title_font,
                      fill=WHITE, anchor='ls')
        x += (right - left) + gap

    x = 59
    for word, kind in (('LLUVIA', 'grad_blue'), ('EN', 'white'),
                       ('ECUADOR', 'white')):
        left, _, right, _ = text_bbox(title_font, word)
        if kind == 'grad_blue':
            gradient_text(frame, x - left, line2_base, word, title_font,
                          '#58B8F8', '#F3F2EE')
        else:
            draw.text((x - left, line2_base), word, font=title_font,
                      fill=WHITE, anchor='ls')
        x += (right - left) + gap

    # ---- subtítulo ---------------------------------------------------------
    draw.rounded_rectangle((56, 335, 1027, 402), radius=18, fill=PANEL)
    subtitle = f'Así cambió la precipitación día a día durante {year}.'
    draw_line(draw, 78, 383, subtitle, 'regular', 29, 892, '#F2F5F6')

    # ---- fila de fecha -----------------------------------------------------
    draw_calendar_icon(draw, 56, 438)

    date_size, date_wd = fit_cap_width(
        'display', 42, 304,
        lambda s, w: text_width(make_font('display', s, w), '01 ENE 2024'))

    draw.line((543, 431, 543, 498), fill='#59737C', width=3)
    draw_play_button(draw, (631, 431, 706, 507))
    draw.rounded_rectangle((728, 428, 1041, 510), radius=40,
                           outline='#7D8F9A', width=3)

    # contador: alturas de la maqueta; el ancho se ajusta al óvalo (cabe con 3 dígitos)
    caps = {'dia': 30, 'num': 44, 'tot': 36}
    sizes = {k: size_for_cap('display', v) for k, v in caps.items()}
    base_wd = FONT_SPECS['display']['width']

    def counter_fonts_for(scale, wd):
        return {
            k: make_font('display', max(8, round(v * scale)), wd)
            for k, v in sizes.items()
        }

    def counter_total(scale, wd):
        f = counter_fonts_for(scale, wd)
        return (
            text_width(f['dia'], 'DÍA') + text_width(f['num'], '000')
            + text_width(f['tot'], '/') + text_width(f['tot'], str(total_days))
            + 50
        )

    scale = 1.0
    while counter_total(scale, base_wd) > 263 and scale > 0.4:
        scale -= 0.02
    low, high, counter_wd = base_wd, 100, base_wd
    while low <= high:
        mid = (low + high) // 2
        if counter_total(scale, mid) <= 263:
            counter_wd = mid
            low = mid + 1
        else:
            high = mid - 1
    counter_fonts = counter_fonts_for(scale, counter_wd)

    # ---- mapa: brillo ------------------------------------------------------
    frame.alpha_composite(make_glow(geometry['main_mask']),
                          (MAIN_X, MAIN_Y))
    frame.alpha_composite(make_glow(geometry['gal_mask']),
                          (GAL_X, GAL_Y))

    # ---- leyenda -----------------------------------------------------------
    draw_line(draw, 55, 1520, 'LLUVIA ACUMULADA · mm/día', 'bold', 27, 528,
              WHITE)

    bar_x0, bar_x1, bar_y0, bar_y1 = 75, 1008, 1541, 1578
    bar_w = bar_x1 - bar_x0
    gradient_values = np.interp(
        np.linspace(0, 7, bar_w), np.arange(8), STOPS)
    bar = Image.fromarray(
        np.repeat(colorize(gradient_values[None, :]), bar_y1 - bar_y0,
                  axis=0)
    )
    bar_mask = Image.new('L', (bar_w * SS, (bar_y1 - bar_y0) * SS), 0)
    ImageDraw.Draw(bar_mask).rounded_rectangle(
        (0, 0, bar_w * SS - 1, (bar_y1 - bar_y0) * SS - 1),
        radius=4 * SS, fill=255)
    bar_mask = bar_mask.resize((bar_w, bar_y1 - bar_y0),
                               Image.Resampling.LANCZOS)
    frame.paste(bar, (bar_x0, bar_y0), bar_mask)

    label_size, label_wd = fit_cap_width(
        'label', 27, 64,
        lambda s, w: text_width(make_font('label', s, w), '120+'))
    label_font = make_font('label', label_size, label_wd)

    for index, value in enumerate(STOPS):
        tick_x = bar_x0 + index * bar_w / 7
        draw.line((tick_x, bar_y1 + 2, tick_x, bar_y1 + 21),
                  fill='#DFE6EA', width=2)
        label = str(int(value)) + ('+' if index == 7 else '')
        draw.text((tick_x, 1635), label, font=label_font, fill='#DADCDF',
                  anchor='ms')

    # ---- pie de página -----------------------------------------------------
    draw.line((56, 1689, 1025, 1689), fill=LINE, width=2)
    draw.line((587, 1716, 587, 1836), fill=VLINE, width=2)

    draw_database_icon(draw, 57, 1722)
    source_parts = [
        ('Fuente:', 'bold', WHITE),
        ('CHIRPS v2', 'regular', '#E9E6F7'),
    ]
    src_size, src_wd = fit_cap_width(
        'bold', 24, 225,
        lambda s, w: parts_width(source_parts, s, w))
    draw_parts(draw, 146, 1753, source_parts, src_size, src_wd)
    draw_line(draw, 148, 1788, 'UCSB Climate Hazards Center', 'regular',
              22, 329, '#EEF1F2')
    draw_line(draw, 148, 1819,
              'Ecuador continental · Límites: geoBoundaries', 'regular',
              17, 416, '#C2D5E3')

    draw_mountain_icon(draw, 614, 1720)
    draw_line(draw, 708, 1741, 'Henry P. Conteron Moreta', 'bold', 22, 309,
              WHITE)
    draw_line(draw, 709, 1779, 'Ing. Geociencias', 'regular', 20, 186,
              '#EBEEF0')

    draw_tiktok_icon(draw, 711, 1795)
    draw_instagram_icon(draw, 763, 1799)
    draw_line(draw, 812, 1822, SOCIAL_HANDLE, 'bold', 20, 186, '#EAF2F7')

    # ---- capa superior: bordes, ciudades, etiquetas ------------------------
    top = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))

    main_lines = outline_layer(
        (MAIN_W, MAIN_H),
        [
            (geometry['main_provinces'], PROVINCE_BORDER, 1.2),
            (geometry['main_rings'], MAP_BORDER, 2.2),
        ],
    )
    top.alpha_composite(main_lines, (MAIN_X, MAIN_Y))

    gal_lines = outline_layer(
        (GAL_W, GAL_H),
        [(geometry['gal_rings'], MAP_BORDER, 1.4)],
    )
    top.alpha_composite(gal_lines, (GAL_X, GAL_Y))

    top_draw = ImageDraw.Draw(top)

    draw_line(top_draw, 60, 828, 'Galápagos', 'regular', 20, 112, MUTED)

    city_size, city_wd = fit_cap_width(
        'bold', 24, 77,
        lambda s, w: text_width(make_font('bold', s, w), 'Quito'))
    city_font = make_font('bold', city_size, city_wd)
    for name, lon, lat in CITIES:
        cx, cy = geometry['main_xy'](lon, lat)
        cx += MAIN_X
        cy += MAIN_Y
        top_draw.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill='white')
        top_draw.text(
            (cx + 16, cy - 16), name, font=city_font, fill='white',
            anchor='lm', stroke_width=3, stroke_fill='#06131C',
        )

    dynamic = {
        'date_font': make_font('display', date_size, date_wd),
        'counter_fonts': counter_fonts,
        'scale': scale,
    }
    return frame, top, dynamic


def draw_dynamic(frame, dynamic, date, total_days):
    draw = ImageDraw.Draw(frame)

    date_text = f'{date.day:02d} {MONTHS[date.month - 1]} {date.year}'
    font = dynamic['date_font']
    left = text_bbox(font, date_text)[0]
    draw.text((151 - left, 485), date_text, font=font, fill=WHITE,
              anchor='ls')

    day_of_year = date.timetuple().tm_yday
    fonts = dynamic['counter_fonts']
    k = dynamic['scale']
    baseline = 490

    # Se alinea a la derecha del contador y fluye hacia la izquierda.
    right = 1013
    draw.text((right, baseline), str(total_days), font=fonts['tot'],
              fill=WHITE, anchor='rs')
    right -= text_width(fonts['tot'], str(total_days)) + round(15 * k)
    draw.text((right, baseline), '/', font=fonts['tot'], fill=SLASH,
              anchor='rs')
    right -= text_width(fonts['tot'], '/') + round(21 * k)
    number = f'{day_of_year:02d}'
    draw.text((right, baseline), number, font=fonts['num'], fill=AQUA,
              anchor='rs')
    right -= text_width(fonts['num'], number) + round(14 * k)
    draw.text((right, baseline), 'DÍA', font=fonts['dia'], fill=WHITE,
              anchor='rs')


# =============================================================================
# ZONA SEGURA (TikTok / Instagram Reels / Shorts)
# =============================================================================

def build_safe_layout():
    """Calcula cómo entra el diseño en la zona libre de interfaz."""
    left, top, right, bottom = DESIGN_CROP
    crop_w, crop_h = right - left, bottom - top

    box_w = WIDTH - SAFE_LEFT - SAFE_RIGHT
    box_h = HEIGHT - SAFE_TOP - SAFE_BOTTOM

    scale = min(box_w / crop_w, box_h / crop_h, 1.0)
    new_w, new_h = round(crop_w * scale), round(crop_h * scale)

    x = SAFE_LEFT + (box_w - new_w) // 2
    y = SAFE_TOP + (box_h - new_h) // 2

    return {
        'crop': DESIGN_CROP,
        'size': (new_w, new_h),
        'pos': (x, y),
        'scale': scale,
    }


def compose_final(design, layout):
    """Mete el diseño (RGB 1080x1920) dentro de la zona segura."""
    if layout is None:
        return design

    canvas = Image.new('RGB', (WIDTH, HEIGHT), BG)
    piece = design.crop(layout['crop']).resize(
        layout['size'], Image.Resampling.LANCZOS)
    canvas.paste(piece, layout['pos'])
    return canvas


def draw_guides(image):
    """Tiñe de rojo las zonas que tapan las apps (solo para revisar)."""
    overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    red = (255, 60, 60, 80)
    d.rectangle((0, 0, WIDTH, SAFE_TOP), fill=red)
    d.rectangle((0, HEIGHT - SAFE_BOTTOM, WIDTH, HEIGHT), fill=red)
    d.rectangle((0, SAFE_TOP, SAFE_LEFT, HEIGHT - SAFE_BOTTOM), fill=red)
    d.rectangle((WIDTH - SAFE_RIGHT, SAFE_TOP, WIDTH, HEIGHT - SAFE_BOTTOM),
                fill=red)
    return Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', default='2024-01-01')
    parser.add_argument('--days', type=int, default=7)
    parser.add_argument('--no-safe', action='store_true',
                        help='diseño a pantalla completa, sin zona segura')
    parser.add_argument('--guides', action='store_true',
                        help='pinta las zonas que tapan las apps (revisión)')
    args = parser.parse_args()

    if not 1 <= args.days <= 366:
        parser.error('days must be 1..366')

    use_safe = SAFE_ZONE and not args.no_safe
    layout = build_safe_layout() if use_safe else None

    start = dt.date.fromisoformat(args.start)
    year = start.year
    total_days_year = 366 if calendar.isleap(year) else 365

    # ---- carpetas ----------------------------------------------------------
    out = ROOT / '_local' / 'climate-studio' / f'{start}-{args.days}days'
    out.mkdir(parents=True, exist_ok=True)
    cache = ROOT / '_local' / 'climate-studio' / 'cache'
    cache.mkdir(parents=True, exist_ok=True)

    # ---- bordes ------------------------------------------------------------
    base = ('https://github.com/wmgeolab/geoBoundaries/raw/9469f09/'
            'releaseData/gbOpen/ECU/')
    adm0_url = base + 'ADM0/geoBoundaries-ECU-ADM0.geojson'
    adm1_url = base + 'ADM1/geoBoundaries-ECU-ADM1.geojson'

    adm0 = json.loads(fetch(adm0_url, cache / 'ecuador-adm0.geojson'))
    adm1 = json.loads(fetch(adm1_url, cache / 'ecuador-adm1.geojson'))

    # ---- geometría ---------------------------------------------------------
    main_mask, main_rings, main_xy = build_mask_and_rings(
        adm0, MAIN_BOX, MAIN_W, MAIN_H)
    main_provinces = extract_outline_rings(adm1, MAIN_BOX, MAIN_W, MAIN_H)
    gal_mask, gal_rings, _ = build_mask_and_rings(
        adm0, GALAPAGOS_BOX, GAL_W, GAL_H)

    main_mask_array = np.asarray(main_mask)
    gal_mask_array = np.asarray(gal_mask)

    geometry = {
        'main_mask': main_mask,
        'main_rings': main_rings,
        'main_provinces': main_provinces,
        'main_xy': main_xy,
        'gal_mask': gal_mask,
        'gal_rings': gal_rings,
    }

    static_bg, static_top, dynamic = build_static(
        year, total_days_year, geometry)

    # ---- receipt -----------------------------------------------------------
    receipt = {
        'source': 'CHIRPS v2 daily',
        'units': 'mm/day',
        'native_grid_degrees': 0.05,
        'mainland_bbox': MAIN_BOX,
        'galapagos_bbox': GALAPAGOS_BOX,
        'display': (
            'bicubic interpolation of the native grid for visual display '
            'only; land cells without data (coast, islands) are filled with '
            'the mean of valid neighbouring cells, display only'
        ),
        'fill_iterations': FILL_ITERATIONS,
        'temporal_interpolation': False,
        'legend_stops_mm': STOPS.tolist(),
        'adm0_url': adm0_url,
        'adm1_url': adm1_url,
        'video_resolution': [WIDTH, HEIGHT],
        'video_fps': FPS,
        'safe_zone': (
            {
                'enabled': True,
                'margins_px': {
                    'left': SAFE_LEFT,
                    'right': SAFE_RIGHT,
                    'top': SAFE_TOP,
                    'bottom': SAFE_BOTTOM,
                },
                'design_scale': round(layout['scale'], 4),
            }
            if use_safe else {'enabled': False}
        ),
        'frames': [],
    }

    # ---- video -------------------------------------------------------------
    suffix = '-guides' if args.guides else ''
    video = out / f'ecuador-lluvia-diaria-preview{suffix}.mp4'

    writer = imageio_ffmpeg.write_frames(
        str(video),
        (WIDTH, HEIGHT),
        fps=FPS,
        codec='libx264',
        pix_fmt_in='rgb24',
        pix_fmt_out='yuv420p',
        macro_block_size=1,
        output_params=['-crf', '18', '-preset', 'fast',
                       '-movflags', '+faststart'],
    )
    writer.send(None)

    try:
        for i in range(args.days):
            date = start + dt.timedelta(days=i)
            filename = f'chirps-v2.0.{date:%Y.%m.%d}.tif.gz'
            url = ('https://data.chc.ucsb.edu/products/CHIRPS-2.0/'
                   f'global_daily/tifs/p05/{date.year}/{filename}')

            print('Loading', date, flush=True)

            raw = fetch(url, cache / 'chirps' / str(date.year) / filename)

            with MemoryFile(gzip.decompress(raw)) as mem:
                with mem.open() as src:
                    main_overlay, main_valid, main_filled = (
                        render_chirps_region(
                            src, MAIN_BOX, MAIN_W, MAIN_H,
                            main_mask_array))
                    gal_overlay, gal_valid, gal_filled = (
                        render_chirps_region(
                            src, GALAPAGOS_BOX, GAL_W, GAL_H,
                            gal_mask_array))

            # ---- composición del frame ------------------------------------
            frame = static_bg.copy()
            draw_dynamic(frame, dynamic, date, total_days_year)
            frame.paste(main_overlay, (MAIN_X, MAIN_Y), main_mask)
            frame.paste(gal_overlay, (GAL_X, GAL_Y), gal_mask)
            frame.alpha_composite(static_top)

            rgb_frame = compose_final(frame.convert('RGB'), layout)
            if args.guides:
                rgb_frame = draw_guides(rgb_frame)
            pixels = np.asarray(rgb_frame)

            # ---- duración --------------------------------------------------
            if args.days == 1:
                hold_frames = 30
            elif i == 0:
                hold_frames = 21          # 0,7 s de apertura
            elif i == args.days - 1:
                hold_frames = 30          # 1 s al final
            elif date.day == 1:
                hold_frames = 4           # micro-pausa al cambiar de mes
            else:
                hold_frames = 2

            for _ in range(hold_frames):
                writer.send(pixels)

            if i in (0, args.days - 1):
                rgb_frame.save(out / f'frame-{date}{suffix}.png')

            receipt['frames'].append({
                'date': str(date),
                'source_url': url,
                'sha256': hashlib.sha256(raw).hexdigest(),
                'mainland_missing_cells': int((~main_valid).sum()),
                'galapagos_missing_cells': int((~gal_valid).sum()),
                'mainland_land_cells_filled': main_filled,
                'galapagos_land_cells_filled': gal_filled,
            })

    finally:
        writer.close()

    receipt['video_sha256'] = hashlib.sha256(video.read_bytes()).hexdigest()
    (out / 'receipt.json').write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    print(video, flush=True)


if __name__ == '__main__':
    main()