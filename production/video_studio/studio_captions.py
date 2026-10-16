"""Plain-text subtitles on a global 30-fps timeline, shared by preview and MP4.

The optional ``studio['captions']`` object contains ``enabled``, ``cues`` and
``style``. Cue intervals are half-open [start, end), in global video seconds.
Times are rounded half up to video frames without mutating the saved document.
All dimensions below (including font size, padding and stroke) are fractions
of the output canvas; x/width use its width, the others its height. No HTML is
rendered. Imported formatting is removed and unsupported tags are rejected.

SRT/VTT imports accept UTF-8, including a BOM. VTT header metadata and NOTE,
STYLE and REGION blocks are ignored; cue settings never override editor style.
No speech, cloud, filesystem or subprocess access is performed by this module.
"""
from bisect import bisect_right
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from functools import lru_cache
from html import escape
from html.parser import HTMLParser
import json
import math
import re

from PIL import Image, ImageDraw

from studio_typography import studio_font, validate_family


FPS = 30
MAX_CAPTION_BYTES = 2 * 1024 * 1024
MAX_CAPTION_CUES = 5000
MAX_CAPTION_TEXT = 800
DEFAULT_CAPTION_STYLE = {
    'x': .08, 'y': .72, 'width': .84, 'height': .12,
    'font_size': .028, 'min_font_size': .018,
    'font_family': 'Barlow Condensed', 'bold': True,
    'color': '#ffffff', 'background': '#04151e', 'background_opacity': .88,
    'stroke_color': '#04151e', 'stroke_width': .0015,
    'padding': .012, 'alignment': 'center',
}
_TIMESTAMP = re.compile(r'(?:(\d{2,6}):)?(\d{2}):(\d{2})[.,](\d{3})\Z')
_COLOR = re.compile(r'#[0-9a-fA-F]{6}\Z')
_CONTROL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')


def _number(value, name, lower=0, upper=None):
    if type(value) not in (int, float):
        raise ValueError(f'{name}: introduce un número finito, no un booleano.')
    if value < lower or (upper is not None and value > upper):
        raise ValueError(f'{name}: valor fuera de rango.')
    try:
        if not math.isfinite(value):
            raise ValueError(f'{name}: introduce un número finito.')
    except OverflowError as error:
        raise ValueError(f'{name}: valor fuera de rango.') from error
    return float(value)


def caption_frame(seconds):
    """Quantize non-negative global seconds, including decimal half frames."""
    _number(seconds, 'Tiempo del subtítulo', upper=3_600_000_000)
    try:
        frame = int((Decimal(str(seconds)) * FPS).to_integral_value(rounding=ROUND_HALF_UP))
        if frame >= 108_000_000_000:
            raise ValueError('La marca temporal supera las seis cifras de horas admitidas.')
        return frame
    except (InvalidOperation, OverflowError, ValueError) as error:
        raise ValueError('Tiempo del subtítulo inválido.') from error


def _style(value):
    if not isinstance(value, dict):
        raise ValueError('El estilo de subtítulos debe ser un objeto.')
    if any(key not in DEFAULT_CAPTION_STYLE for key in value):
        raise ValueError('El estilo de subtítulos contiene propiedades desconocidas.')
    style = {**DEFAULT_CAPTION_STYLE, **value}
    for field in ('x', 'y', 'width', 'height', 'background_opacity'):
        _number(style[field], field, 0, 1)
    if style['width'] <= 0 or style['height'] <= 0:
        raise ValueError('La caja de subtítulos debe tener ancho y alto positivos.')
    if style['x'] + style['width'] > 1 + 1e-9 or style['y'] + style['height'] > 1 + 1e-9:
        raise ValueError('La caja de subtítulos debe quedar dentro del lienzo.')
    for field in ('font_size', 'min_font_size'):
        _number(style[field], field, .005, .15)
    if style['min_font_size'] > style['font_size']:
        raise ValueError('El tamaño mínimo no puede superar al tamaño solicitado.')
    _number(style['stroke_width'], 'Borde del texto', 0, .01)
    _number(style['padding'], 'Margen interior', 0, .1)
    if style['padding'] * 2 >= style['height']:
        raise ValueError('El margen interior debe dejar espacio para el texto.')
    validate_family(style['font_family'])
    if type(style['bold']) is not bool:
        raise ValueError('El peso de subtítulos debe ser booleano.')
    if style['alignment'] not in ('left', 'center', 'right'):
        raise ValueError('La alineación debe ser left, center o right.')
    for key in ('color', 'background', 'stroke_color'):
        if not isinstance(style[key], str) or not _COLOR.fullmatch(style[key]):
            raise ValueError('Los colores de subtítulos deben ser #RRGGBB.')
    return style


def _plain_text(text):
    if not isinstance(text, str) or not text.strip() or len(text) > MAX_CAPTION_TEXT:
        raise ValueError('Cada subtítulo necesita texto de 1 a 800 caracteres.')
    if _CONTROL.search(text):
        raise ValueError('El texto del subtítulo contiene caracteres de control.')
    return text.strip().replace('\r\n', '\n').replace('\r', '\n')


def _cues(value, total_frames=None):
    if not isinstance(value, list) or len(value) > MAX_CAPTION_CUES:
        raise ValueError('Se admiten como máximo 5000 subtítulos.')
    if total_frames is not None and (type(total_frames) is not int or total_frames < 0):
        raise ValueError('La duración del video debe expresarse en fotogramas enteros.')
    rows = []
    identifiers = set()
    previous_end = -1
    for index, cue in enumerate(value):
        if not isinstance(cue, dict):
            raise ValueError('Cada subtítulo debe ser un objeto.')
        identifier = cue.get('id')
        if not isinstance(identifier, str) or not 1 <= len(identifier) <= 128 or _CONTROL.search(identifier):
            raise ValueError('Cada subtítulo necesita un identificador de 1 a 128 caracteres.')
        if identifier in identifiers:
            raise ValueError('Los identificadores de subtítulos no se pueden repetir.')
        identifiers.add(identifier)
        start, end = caption_frame(cue.get('start')), caption_frame(cue.get('end'))
        if end <= start:
            raise ValueError(f'Subtítulo {index + 1}: el final debe ir después del inicio a 30 fps.')
        if start < previous_end:
            raise ValueError('Los subtítulos deben estar ordenados y no pueden solaparse.')
        if total_frames is not None and end > total_frames:
            raise ValueError(f'Subtítulo {index + 1}: termina fuera de la duración del video.')
        previous_end = end
        rows.append((identifier, start, end, _plain_text(cue.get('text'))))
    # Bound encoded JSON, not merely source-file length or Python characters.
    try:
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False).encode('utf-8')
    except (TypeError, ValueError, UnicodeEncodeError, RecursionError) as error:
        raise ValueError('Los subtítulos deben contener datos JSON válidos.') from error
    if len(encoded) > MAX_CAPTION_BYTES:
        raise ValueError('El conjunto de subtítulos supera el límite de 2 MB.')
    return tuple(rows)


@dataclass(frozen=True)
class PreparedCaptions:
    """Validated private track; prepare once, locate each cue in O(log n)."""
    enabled: bool
    cues: tuple
    starts: tuple
    style: tuple


def prepare_captions(captions, total_frames=None):
    """Validate/compile a captions object without mutating the user's project."""
    if not isinstance(captions, dict):
        raise ValueError('Los subtítulos deben ser un objeto.')
    enabled = captions.get('enabled', False)
    if type(enabled) is not bool:
        raise ValueError('La activación de subtítulos debe ser booleana.')
    rows = _cues(captions.get('cues', []), total_frames)
    style = _style(captions.get('style', {}))
    return PreparedCaptions(enabled, rows, tuple(row[1] for row in rows), tuple(style.items()))


def validate_captions(studio, total_frames=None):
    """Optional studio track. Validate even disabled cues, preserving all input."""
    if not isinstance(studio, dict):
        raise ValueError('El proyecto Studio debe ser un objeto.')
    if 'captions' in studio:
        prepare_captions(studio['captions'], total_frames)


class _FormattingToText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == 'br':
            self.parts.append('\n')
            return
        if tag.split('.')[0] not in ('b', 'i', 'u', 's', 'font', 'c', 'v', 'lang'):
            raise ValueError('El archivo contiene HTML no admitido; importa subtítulos de texto.')

    def handle_endtag(self, tag):
        self.handle_starttag(tag, [])

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self.parts.append('\n')
        else:
            self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        self.parts.append(data)

    def handle_comment(self, data):
        raise ValueError('No se admiten comentarios HTML en los subtítulos.')

    def handle_decl(self, decl):
        raise ValueError('No se admiten declaraciones HTML en los subtítulos.')


def _import_text(text):
    # WebVTT karaoke timestamps are presentation markup, not additional cues.
    text = re.sub(r'<(?:\d{2,6}:)?\d{2}:\d{2}[.]\d{3}>', '', text)
    parser = _FormattingToText()
    try:
        parser.feed(text)
        parser.close()
    except (ValueError, AssertionError) as error:
        raise ValueError('Formato HTML del subtítulo no admitido.') from error
    return _plain_text(''.join(parser.parts))


def _seconds(timestamp):
    match = _TIMESTAMP.fullmatch(timestamp)
    if not match:
        raise ValueError('Marca temporal inválida: usa HH:MM:SS,mmm o MM:SS.mmm.')
    hours, minutes, seconds, milliseconds = match.groups()
    if int(minutes) >= 60 or int(seconds) >= 60:
        raise ValueError('Los minutos y segundos deben estar entre 00 y 59.')
    return (int(hours or 0) * 3600000 + int(minutes) * 60000 + int(seconds) * 1000 + int(milliseconds)) / 1000


def parse_captions(content, name):
    """Return canonical cues from bounded UTF-8 SRT or WebVTT content."""
    if not isinstance(name, str) or not name.lower().endswith(('.srt', '.vtt')):
        raise ValueError('Importa un archivo .srt o .vtt.')
    if isinstance(content, bytes):
        if len(content) > MAX_CAPTION_BYTES:
            raise ValueError('El archivo de subtítulos supera 2 MB.')
        try:
            content = content.decode('utf-8-sig')
        except UnicodeDecodeError as error:
            raise ValueError('Guarda los subtítulos con codificación UTF-8.') from error
    elif not isinstance(content, str):
        raise ValueError('El archivo de subtítulos debe ser texto UTF-8.')
    try:
        if len(content.encode('utf-8')) > MAX_CAPTION_BYTES:
            raise ValueError('El archivo de subtítulos supera 2 MB.')
    except UnicodeEncodeError as error:
        raise ValueError('El archivo de subtítulos no contiene Unicode válido.') from error
    content = content.lstrip('\ufeff').replace('\r\n', '\n').replace('\r', '\n').strip()
    is_vtt = name.lower().endswith('.vtt')
    blocks = re.split(r'\n[ \t]*\n', content)
    if is_vtt:
        if not blocks or not re.match(r'^WEBVTT(?:[ \t]|\n|$)', blocks[0]):
            raise ValueError('El archivo VTT debe empezar por WEBVTT.')
        blocks = blocks[1:]
    cues = []
    for block in blocks:
        lines = block.split('\n')
        first = lines[0].strip()
        if is_vtt and re.match(r'^(?:NOTE(?:[ \t]|$)|STYLE$|REGION$)', first):
            continue
        time_index = 0 if '-->' in lines[0] else 1
        if len(lines) <= time_index + 1 or '-->' not in lines[time_index]:
            raise ValueError('Bloque de subtítulo inválido: faltan tiempo o texto.')
        match = re.fullmatch(r'\s*(\S+)\s+-->\s+(\S+)(?:[ \t]+.*)?', lines[time_index])
        if not match:
            raise ValueError('Intervalo de subtítulo inválido.')
        start = caption_frame(_seconds(match[1]))
        end = caption_frame(_seconds(match[2]))
        cues.append({'id': f'caption-{len(cues) + 1:04d}', 'start': start / FPS,
                     'end': end / FPS, 'text': _import_text('\n'.join(lines[time_index + 1:]))})
        if len(cues) > MAX_CAPTION_CUES:
            raise ValueError('Se admiten como máximo 5000 subtítulos.')
    _cues(cues)
    return cues


def _timestamp(frame, separator):
    milliseconds = int((Decimal(frame) * 1000 / FPS).to_integral_value(rounding=ROUND_HALF_UP))
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f'{hours:02d}:{minutes:02d}:{seconds:02d}{separator}{milliseconds:03d}'


def export_captions(cues, format):
    """Export text with escaped markup; frame identity survives round trips."""
    if format not in ('srt', 'vtt'):
        raise ValueError('Elige formato srt o vtt para exportar subtítulos.')
    rows = _cues(cues)
    separator = ',' if format == 'srt' else '.'
    blocks = []
    for index, (_, start, end, text) in enumerate(rows, 1):
        blocks.append(f'{index}\n{_timestamp(start, separator)} --> {_timestamp(end, separator)}\n{escape(text, quote=False)}')
    return ('WEBVTT\n\n' if format == 'vtt' else '') + '\n\n'.join(blocks) + ('\n' if blocks else '')


def _load_font(size, style):
    font = studio_font(max(8, min(600, size)), family=style['font_family'], bold=style['bold'])
    if size < 8:
        font = font.font_variant(size=max(1, size))
        if style['font_family'] == 'Lora':
            font.set_variation_by_axes([600 if style['bold'] else 400])
    return font


def _lines(text, font, width, stroke):
    lines = []
    for paragraph in text.split('\n'):
        words = paragraph.split()
        current = ''
        for word in words:
            trial = f'{current} {word}' if current else word
            bounds = font.getbbox(trial, anchor='lt', stroke_width=stroke)
            if current and bounds[2] - bounds[0] > width:
                lines.append(current)
                current = word
            else:
                current = trial
        lines.append(current)
    return lines


def render_captions(image, captions, frame, authoring=False):
    """Composite one cue on a new RGBA image; authoring uses identical pixels.

    Pass ``prepare_captions(...)`` from a prepared timeline to avoid repeating
    validation at every frame. No captions are ever added to the scene graph.
    An overfull box raises a user-facing error instead of hiding any words.
    """
    if type(frame) is not int or frame < 0 or type(authoring) is not bool:
        raise ValueError('Selecciona un fotograma entero no negativo.')
    if not isinstance(image, Image.Image):
        raise ValueError('El lienzo debe ser una imagen.')
    track = captions if isinstance(captions, PreparedCaptions) else prepare_captions(captions)
    output = image.convert('RGBA').copy()
    output.info.update(image.info)
    output.info.pop('caption_overlay', None)
    if not track.enabled or not track.cues:
        return output
    index = bisect_right(track.starts, frame) - 1
    if index < 0 or frame >= track.cues[index][2]:
        return output
    width, height = image.size
    style = dict(track.style)
    x, y = round(style['x'] * width), round(style['y'] * height)
    # Cache text-sized tiles only, bounded to eight RGBA megapixels in total.
    # Full-screen subtitle backgrounds remain supported but are never cached.
    tile_pixels = math.ceil(style['width'] * width) * math.ceil(style['height'] * height)
    tile_builder = _cached_caption_tile if tile_pixels <= 1_000_000 else _caption_tile
    tile = tile_builder(track.cues[index][3], track.style, width, height)
    output.alpha_composite(tile, (x, y))
    if authoring:
        # Canvas reconstruction uses a non-interactive presentation overlay,
        # not an editable scene element. Never expose the private cached tile.
        output.info['caption_overlay'] = {'image': tile.copy(), 'x': x, 'y': y}
    return output


@lru_cache(maxsize=8)
def _cached_caption_tile(text, style_tuple, width, height):
    return _caption_tile(text, style_tuple, width, height)


@lru_cache(maxsize=64)
def _caption_layout(text, style_tuple, width, height):
    """Bounded text-only geometry cache; no video images or media handles."""
    style = dict(style_tuple)
    x, y = round(style['x'] * width), round(style['y'] * height)
    right = round((style['x'] + style['width']) * width)
    bottom = round((style['y'] + style['height']) * height)
    box_width, box_height = right - x, bottom - y
    padding = round(style['padding'] * height)
    available_width, available_height = box_width - 2 * padding, box_height - 2 * padding
    if available_width < 1 or available_height < 1:
        raise ValueError('La caja de subtítulos es demasiado pequeña; amplíala.')
    stroke = round(style['stroke_width'] * height)
    maximum = max(1, min(600, round(style['font_size'] * height)))
    minimum = max(1, round(style['min_font_size'] * height))
    for pixels in range(maximum, minimum - 1, -1):
        font = _load_font(pixels, style)
        lines = _lines(text, font, available_width, stroke)
        boxes = [font.getbbox(line or ' ', anchor='lt', stroke_width=stroke) for line in lines]
        leading = max(1, round(pixels * .18))
        text_height = sum(bounds[3] - bounds[1] for bounds in boxes) + leading * (len(lines) - 1)
        if (len(lines) <= 2 and text_height <= available_height
                and all(bounds[2] - bounds[0] <= available_width for bounds in boxes)):
            break
    else:
        raise ValueError('El subtítulo no cabe en dos líneas: divide el texto, amplía la caja o ajusta su tamaño mínimo.')
    return box_width, box_height, padding, font, tuple(lines), tuple(boxes), text_height, leading, stroke


def validate_caption_layout(captions, width, height):
    """Preflight every enabled cue, including captions starting mid-scene.

    This performs text layout only, before movie/sidecar files are created.
    Normalized placement/font sizes remain valid for every output profile.
    """
    if any(type(value) is not int or value < 1 for value in (width, height)):
        raise ValueError('El lienzo requiere dimensiones enteras positivas.')
    track = captions if isinstance(captions, PreparedCaptions) else prepare_captions(captions)
    if track.enabled:
        for text in dict.fromkeys(row[3] for row in track.cues):
            _caption_layout(text, track.style, width, height)


def _caption_tile(text, style_tuple, width, height):
    """Lay out all text before painting: never clip or silently drop a line."""
    style = dict(style_tuple)
    (box_width, box_height, padding, font, lines, boxes,
     text_height, leading, stroke) = _caption_layout(text, style_tuple, width, height)
    tile = Image.new('RGBA', (box_width, box_height))
    draw = ImageDraw.Draw(tile)
    rgb = tuple(int(style['background'][offset:offset + 2], 16) for offset in (1, 3, 5))
    draw.rounded_rectangle((0, 0, box_width - 1, box_height - 1),
                           radius=max(1, round(height * .009)),
                           fill=rgb + (round(style['background_opacity'] * 255),))
    line_y = (box_height - text_height) / 2
    for line, bounds in zip(lines, boxes):
        ink_width = bounds[2] - bounds[0]
        line_x = (padding if style['alignment'] == 'left' else
                  box_width - padding - ink_width if style['alignment'] == 'right' else
                  (box_width - ink_width) / 2)
        draw.text((line_x - bounds[0], line_y - bounds[1]), line, font=font,
                  anchor='lt', fill=style['color'], stroke_width=stroke,
                  stroke_fill=style['stroke_color'])
        line_y += bounds[3] - bounds[1] + leading
    return tile
