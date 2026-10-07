"""Data-first social layouts: measured text, not decorative stock imagery."""
from __future__ import annotations

import itertools
import math
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor

from maqueta import compose_final, fit_text, gradient_text
from render import font
from layout_engine import (begin_layout, finish_layout, scene_for, place_layer, full_layer,
                           draw as layout_draw, editable_text_box)

FONT_ASSETS = Path(__file__).parent/'assets'/'fonts'


@lru_cache(maxsize=180)
def editorial_font(size, bold=False, display=False):
    """Bundled condensed fonts: same shape on Windows and exported previews."""
    filename = 'BarlowCondensed-ExtraBold.ttf' if display else ('BarlowCondensed-SemiBold.ttf' if bold else 'BarlowCondensed-Regular.ttf')
    path = FONT_ASSETS/filename
    if not path.is_file():
        return font(size, bold or display)
    if display:
        # Display sizes specify actual cap height, just like the rain template.
        for pixels in range(size, size*2+1):
            result = ImageFont.truetype(str(path), pixels)
            if result.getbbox('H')[3]-result.getbbox('H')[1] >= size:
                return result
    return ImageFont.truetype(str(path), size)


@lru_cache(maxsize=8)
def _background(color):
    """Subtle editorial light, not fake terrain or decorative stock photos."""
    yy, xx = np.mgrid[0:1920, 0:1080]
    glow = np.exp(-((xx-550)/670)**2-((yy-800)/1150)**2)
    base = np.asarray(ImageColor.getrgb(color), dtype=float)
    rgb = base[None, None, :]+glow[:, :, None]*np.array([0, 11, 18])
    return Image.fromarray(np.clip(rgb, 0, 255).astype('uint8')).convert('RGBA')


def editorial_background(config):
    return _background(config.get('background', '#03141f')).copy()


def compose_editorial(image, config):
    """Do not shrink the entire approved artwork by 27% a second time."""
    image = finish_layout(image)
    custom = config.get('_layout_capture') or config.get('visual_layout', {}).get('full_canvas')
    result = compose_final(image) if config.get('editorial_margins') == 'amplios' and not custom else image.convert('RGB')
    result.info['layout_boxes'] = image.info.get('layout_boxes', [])
    return result


def panel(image, box, *, radius=24):
    if scene_for(image):
        layer = Image.new('RGBA', image.size)
        panel(layer, box, radius=radius)
        full_layer(image, layer, kind='panel', label='Panel / tarjeta')
        return
    glow = Image.new('RGBA', image.size)
    ImageDraw.Draw(glow).rounded_rectangle(box, radius=radius, outline=(39, 205, 244, 42), width=4)
    image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(5)))
    glass = Image.new('RGBA', image.size)
    ImageDraw.Draw(glass).rounded_rectangle(box, radius=radius, fill=(2, 23, 35, 130))
    image.alpha_composite(glass)
    ImageDraw.Draw(image).rounded_rectangle(box, radius=radius, outline='#367a92', width=2)


def vertical_bar(image, box, bottom_color, top_color, *, negative=False):
    x0, y0, x1, y1 = [round(value) for value in box]
    width, height = max(1, x1-x0), max(1, y1-y0)
    a, b = np.asarray(ImageColor.getrgb(top_color)), np.asarray(ImageColor.getrgb(bottom_color))
    t = np.linspace(0, 1, height)[:, None, None]
    rgb = np.repeat(a[None, None, :]*(1-t)+b[None, None, :]*t, width, axis=1).astype('uint8')
    layer = Image.fromarray(rgb).convert('RGBA')
    mask = Image.new('L', (width*3, height*3))
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, width*3-1, height*3-1), radius=28, fill=255)
    flat = (0, 0, width*3, height*3//2) if negative else (0, height*3//2, width*3, height*3)
    d.rectangle(flat, fill=255)
    layer.putalpha(mask.resize((width, height), Image.Resampling.LANCZOS))
    place_layer(image, layer, (x0, y0), kind='data', editable=False, label='Barra calculada')


def stamp_icon(image, cx, cy, kind, *, diameter=88):
    """Reuse the polished, supersampled icon painters of the rain endcard."""
    scene = scene_for(image)
    key = scene.key('icon') if scene else None
    if scene:
        kind = scene.overrides.get(key, {}).get('icon', kind)
    from endcard import (_paint_cloud, _paint_calendar, _paint_bars,
                         _paint_thermometer, _paint_wind, _paint_index, _paint_pin)
    painters = {'rain': _paint_cloud, 'calendar': _paint_calendar, 'bars': _paint_bars,
                'temperature': _paint_thermometer, 'wind': _paint_wind, 'index': _paint_index, 'pin': _paint_pin}
    ss, side = 4, diameter*4
    layer = Image.new('RGBA', (side, side))
    d = ImageDraw.Draw(layer)
    middle, unit = side/2, side/80
    p = lambda x, y: (middle+x*unit, middle+y*unit)
    d.ellipse((2, 2, side-3, side-3), fill='#123747', outline='#23607a', width=3*ss)
    if kind == 'trend':
        d.line([p(-23, 19), p(-6, -1), p(4, 8), p(25, -19)], fill='#ff5569', width=5*ss, joint='curve')
        d.line([p(10, -19), p(25, -19), p(25, -3)], fill='#ff5569', width=5*ss)
    elif kind == 'clock':
        d.ellipse((*p(-24, -24), *p(24, 24)), outline='#42e8da', width=3*ss)
        d.line([p(0, -15), p(0, 0), p(12, 0)], fill='#42e8da', width=3*ss)
    else:
        painters.get(kind, _paint_index)(d, p, unit)
    place_layer(image, layer.resize((diameter, diameter), Image.Resampling.LANCZOS),
                (round(cx-diameter/2), round(cy-diameter/2)), key=key, kind='icon', label='Icono · '+kind, icon=kind)


@editable_text_box
def text_box(image, text, box, *, size=28, color='#d3e5ed', bold=False,
             display=False, lines=2, align='left', min_size=8):
    """Fit ALL words inside a measured box, recording bounds for layout tests."""
    draw = layout_draw(image)
    x0, y0, x1, y1 = box
    words = str(text or '').split()
    for cap in range(size, min_size-1, -1):
        selected = editorial_font(cap, bold, display)
        wrapped, current = [], ''
        for word in words:
            trial = (current + ' ' + word).strip()
            if current and draw.textlength(trial, font=selected) > x1-x0:
                wrapped.append(current)
                current = word
            else:
                current = trial
        if current:
            wrapped.append(current)
        line_h = max((selected.getbbox(line)[3]-selected.getbbox(line)[1] for line in wrapped), default=0)+6
        if (len(wrapped) <= lines and len(wrapped)*line_h <= y1-y0
                and all(draw.textlength(line, font=selected) <= x1-x0 for line in wrapped)):
            break
    else:
        if min_size > 8:
            raise ValueError('El texto no cabe con letra legible. Acórtalo o divídelo en otra tarjeta.')
    bounds = []
    for i, line in enumerate(wrapped):
        width = draw.textlength(line, font=selected)
        x = (x0+x1-width)/2 if align == 'center' else x0
        y = y0+i*line_h
        draw.text((x, y), line, font=selected, fill=color, anchor='lt')
        bounds.append(draw.textbbox((x, y), line, font=selected, anchor='lt'))
    image.info.setdefault('layout_boxes', []).append({'text': str(text), 'box': box, 'bounds': bounds})
    return bounds


def headline_lines(title, width=930, max_lines=3, cap=76):
    """Balanced lines at a large condensed size; no silent truncation."""
    words = str(title).upper().replace(' 2 M', ' 2 m').split()
    selected = editorial_font(cap, display=True)
    for count in range(1, min(max_lines, len(words))+1):
        options = []
        for breaks in itertools.combinations(range(1, len(words)), count-1):
            cuts = (0, *breaks, len(words))
            rows = [' '.join(words[cuts[i]:cuts[i+1]]) for i in range(count)]
            widths = [selected.getlength(row) for row in rows]
            options.append((max(widths), max(widths)-min(widths), rows))
        best = min(options, key=lambda item: (item[0], item[1]))
        if best[0] <= width or count == min(max_lines, len(words)):
            return best[2]
    return ['']


def draw_header(image, config, *, metrics=False, subtitle=''):
    white, accent = config.get('text', '#f4f8fb'), config.get('accent', '#55e2cb')
    x0 = 72 if metrics else 108
    brand_bounds = text_box(image, config.get('brand', 'ECUADOR VIVO / ANDES PULSO'),
             (x0, 54, 700, 95), size=34, color=accent, bold=True, lines=1)
    brand_end = brand_bounds[-1][2] if brand_bounds else x0
    layout_draw(image).line((brand_end+24, 75, brand_end+81, 75), fill='#adbec7', width=2)
    title = str(config.get('endcard_title', 'MÉTRICAS FINALES') if metrics else config.get('title', 'EL TERRITORIO CAMBIA')).upper()
    if metrics and title == 'MÉTRICAS FINALES':
        rows = ['MÉTRICAS', 'FINALES']
    elif title == '¿CÓMO CAMBIÓ LA TEMPERATURA MEDIA DEL AIRE A 2 M?':
        rows = ['¿CÓMO CAMBIÓ LA', 'TEMPERATURA MEDIA', 'DEL AIRE A 2 m?']
    else:
        rows = headline_lines(title, width=950-x0+72, max_lines=2 if metrics else 3, cap=96)
    cap = 104 if metrics else 90
    measuring_font = editorial_font(cap, display=True)
    longest = max(rows, key=measuring_font.getlength)
    # Accented ascenders can exceed the nominal cap height in the display font.
    # Measure actual glyphs, including ¿ and É, rather than guessing from "H".
    for cap in range(cap, 8, -1):
        selected = editorial_font(cap, display=True)
        row_bounds = [selected.getbbox(row, anchor='ls') for row in rows]
        total_height = sum(b[3]-b[1] for b in row_bounds)+10*(len(rows)-1)
        if total_height <= (230 if metrics else 270) and selected.getlength(longest) <= 1008-x0:
            break
    top = 114
    cursor = top
    highlight = {'TEMPERATURA', 'LLUVIA', 'VIENTO', 'HUMEDAD', 'ESPECIES', 'FINALES'}
    draw = layout_draw(image)
    for row, row_bbox in zip(rows, row_bounds):
        x, baseline = x0-row_bbox[0], cursor-row_bbox[1]
        for word in row.split():
            bounds = draw.textbbox((x, baseline), word, font=selected, anchor='ls')
            image.info.setdefault('layout_boxes', []).append({'text': word, 'box': (x0, 104, 1008, 392 if not metrics else 348), 'bounds': [bounds]})
            if word.strip('¿?.,:') in highlight:
                gradient_text(image, x, baseline, word, selected,
                              config.get('title_gradient_1', '#26ede0' if metrics else '#17cfee'),
                              config.get('title_gradient_2', '#229ffa' if metrics else '#33f2d3'))
            else:
                draw.text((x, baseline), word, font=selected, fill=white, anchor='ls')
            x += selected.getlength(word+' ')
        cursor = baseline+row_bbox[3]+10
    bottom = cursor
    # Fixed body starts at 425; short titles retain breathing room without moving the maps.
    y = 356 if metrics else 408
    draw.rounded_rectangle((x0, y, 1008 if metrics else 935, y+52), radius=17, fill='#102d3e')
    text_box(image, subtitle or config.get('subtitle', ''), (x0+18, y+5, 987 if metrics else 919, y+48),
             size=36, lines=1)


def draw_footer(image, config, source, method='', *, y=1715):
    draw = layout_draw(image)
    accent = config.get('accent', '#55e2cb')
    from maqueta import draw_database_icon, draw_instagram_icon, draw_tiktok_icon
    draw.line((62, y, 1018, y), fill='#4dc9db', width=2)
    draw.line((571, y+22, 571, y+168), fill='#466777', width=2)
    draw_database_icon(draw, 67, y+25, '#38d6f4')
    text_box(image, 'FUENTE Y ESCALA', (128, y+17, 552, y+48), size=29, bold=True, color=accent, lines=1)
    parts = str(source).split('·')
    if len(parts) >= 3:
        text_box(image, ' · '.join(parts[:2]), (128, y+51, 552, y+80), size=29, lines=1)
        text_box(image, ' · '.join(parts[2:]), (128, y+84, 552, y+112), size=27, lines=1)
    else:
        text_box(image, source, (128, y+51, 552, y+111), size=29, lines=2)
    if method:
        text_box(image, method, (128, y+113, 552, y+176), size=24, lines=3)
    text_box(image, config.get('author', 'Henry P. Conteron Moreta'),
             (613, y+18, 1008, y+72), size=31, bold=True, color=config.get('text', '#f4f8fb'), lines=2)
    text_box(image, config.get('credits', 'Ing. Geociencias'), (613, y+77, 1008, y+112), size=29, lines=1)
    for i, key in enumerate(('tiktok', 'instagram')):
        painter = draw_tiktok_icon if i == 0 else draw_instagram_icon
        # Native rain icons are cropped and scaled, keeping the export crisp.
        icon_layer = Image.new('RGBA', (300, 300))
        painter(ImageDraw.Draw(icon_layer), 100, 100, '#f0f8fa')
        bbox = icon_layer.getbbox()
        if bbox:
            icon = icon_layer.crop(bbox)
            icon.thumbnail((24, 25), Image.Resampling.LANCZOS)
            place_layer(image, icon, (613, y+116+i*32), kind='icon', label=key)
        text_box(image, config.get(key, ''), (650, y+112+i*32, 1008, y+145+i*32),
                 size=28, color='#d7e9ef', lines=1)


def comparison_findings(summary):
    """Describe only the selected observations; never infer a climatic trend."""
    periods = sorted(summary['period_values'], key=lambda row: row['year'])
    first, last = periods[0], periods[-1]
    delta = last['value']-first['value']
    units = summary['aggregate_units']
    months = summary['months']
    names = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
             'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    label = names[min(months)-1] if len(months) == 1 else names[min(months)-1]+'–'+names[max(months)-1]
    window = label.capitalize()+' de cada año.'
    qualifier = 'acumulado' if summary['aggregation'] == 'sum' else 'promedio'
    display_delta = 0. if abs(delta) < .05 else delta
    if len(periods) < 2:
        change = 'Un solo año seleccionado: no hay diferencia entre años.'
    elif display_delta == 0:
        change = f"La diferencia entre {last['year']} y {first['year']} se redondea a 0.0 {units}."
    else:
        direction = 'menor' if delta < 0 else 'mayor'
        change = f"En {last['year']}, el {qualifier} fue {abs(display_delta):.1f} {units} {direction} que en {first['year']}."
    # Even an exact tie is not evidence of stability across unobserved years.
    return [
        {'title': 'EL CAMBIO OBSERVADO', 'body': change},
        {'title': 'MISMA VENTANA', 'body': window+' Solo meses completos.'},
        {'title': 'NO ES UNA TENDENCIA', 'body': 'Comparamos años seleccionados, no una serie climática continua.'},
    ]


def compose_temporal_closing(config, summary):
    """Reference-inspired closing for 1–3 years, separate from 24-province rankings."""
    image = begin_layout(editorial_background(config), config, 'endcard')
    draw = layout_draw(image)
    white, accent = config.get('text', '#f4f8fb'), config.get('accent', '#55e2cb')
    copy = summary['comparison_copy']
    draw_header(image, config, metrics=True, subtitle=copy['subtitle'])

    def section(number, title, box, note=''):
        x0, y0, x1, y1 = box
        panel(image, box)
        draw.rounded_rectangle((x0+27, y0+23, x0+91, y0+80), radius=10, fill=accent)
        text_box(image, f'{number:02d}', (x0+36, y0+28, x0+85, y0+76), size=31, display=True, color='#04141f', lines=1)
        draw.line((x0+125, y0+25, x0+125, y0+69), fill='#92aeb9', width=2)
        text_box(image, title, (x0+150, y0+27, x1-264, y0+79), size=40, display=True, color=white, lines=1)
        if note:
            text_box(image, note, (x1-245, y0+22, x1-27, y0+85), size=29, lines=2, align='center')

    section(1, copy['section_1'], (30, 425, 1050, 735), copy['section_1_note'])
    variable = str(config.get('parameter', config.get('variable', ''))).lower()
    variable_kind = ('temperature' if 't2m' in variable or 'temperatura' in variable else
                     'wind' if 'ws' in variable or 'viento' in variable else
                     'rain' if 'prec' in variable or 'lluvia' in variable else 'index')
    for i, item in enumerate(summary['comparison_cards']):
        x, cx = 50+i*252, 165+i*252
        if i:
            draw.line((x-11, 525, x-11, 715), fill='#466d81', width=2)
        stamp_icon(image, cx, 548, [variable_kind, 'calendar', 'bars', 'index'][i], diameter=89)
        text_box(image, item['value'], (x, 604, x+230, 667), size=48, display=True, color=white, lines=1, align='center')
        text_box(image, item['label'], (x, 670, x+230, 702), size=30, lines=1, align='center')
        text_box(image, item['sub'], (x, 704, x+230, 730), size=29, bold=True, color=accent, lines=1, align='center')

    section(2, copy['section_2'], (30, 755, 1050, 1296), copy['section_2_note'])
    text_box(image, copy['rank_axis_label'], (62, 849, 992, 887), size=30, lines=1)
    rows = sorted(summary['period_values'], key=lambda row: row['year'])
    values = [row['value'] for row in rows]
    low, high = min(0., min(values)), max(0., max(values))
    span = max(high-low, .1)
    step = 10**math.floor(math.log10(span/5))
    step *= next(candidate for candidate in (1, 2, 5, 10) if candidate*step >= span/5)
    low, high = math.floor(low/step)*step, math.ceil(high/step)*step
    if high <= low:
        high = low+step
    # Reserve headroom for value labels OUTSIDE bars, including negative values.
    x0, x1, y0, y1 = 133, 1016, 947, 1208
    py = lambda value: y1-(value-low)/(high-low)*(y1-y0)
    for value in [low+i*(high-low)/5 for i in range(6)]:
        y = py(value)
        for dx in range(x0, x1, 13):
            draw.line((dx, y, min(dx+4, x1), y), fill='#395263', width=1)
        text_box(image, f'{value:g}', (57, y-18, 117, y+18), size=30, lines=1, align='center')
    draw.line((x0, py(0), x1, py(0)), fill='#b0d0dc', width=2)
    draw.line((x0, y0, x0, y1), fill='#b0d0dc', width=1)
    colors = [('#ff2e67', '#fc577b'), ('#ffb03e', '#ffdc64'), ('#129cf1', '#31e8ef')]
    for i, row in enumerate(rows):
        center = x0+(i+.5)*(x1-x0)/len(rows)
        width = min(178, (x1-x0)/len(rows)*.54)
        top, bottom = sorted((py(0), py(row['value'])))
        if bottom-top > 1:
            vertical_bar(image, (center-width/2, top, center+width/2, bottom), *colors[i%3], negative=row['value'] < 0)
        label_y = top-53 if row['value'] >= 0 else bottom+5
        text_box(image, f"{row['value']:.1f} {summary['aggregate_units']}", (center-135, label_y, center+135, label_y+43), size=37, bold=True, color=white, lines=1, align='center')
        text_box(image, str(row['year']), (center-70, 1260, center+70, 1293), size=32, color=white, lines=1, align='center')

    section(3, copy['section_3'], (30, 1316, 1050, 1690), copy['section_3_note'])
    for i, finding in enumerate(summary['findings']):
        x, cx = 60+i*335, 202+i*335
        if i:
            draw.line((x-13, 1441, x-13, 1668), fill='#456b7d', width=2)
        stamp_icon(image, cx, 1455, ['trend', 'calendar', 'clock'][i], diameter=90)
        text_box(image, finding['title'], (x, 1518, x+286, 1569), size=30, display=True, color=white, lines=2, align='center')
        text_box(image, finding['body'], (x, 1582, x+286, 1675), size=32, lines=4, align='center')
    draw_footer(image, config, copy['footer'], copy['footer_2'], y=1715)
    return compose_editorial(image, config)
