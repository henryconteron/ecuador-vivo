"""One frame composer shared by preview and final video export."""
from functools import lru_cache
import datetime as dt

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageColor

from data import map_dimensions
from model import upgrade_project

CITIES = [
    ('Quito', -78.4678, -.1807, -92, -30), ('Guayaquil', -79.889, -2.17, -155, 7),
    ('Cuenca', -79.005, -2.9, -110, 4), ('Tena', -77.813, -.994, 15, 8),
    ('Archidona', -77.808, -.909, 15, -30),
]


@lru_cache(maxsize=120)
def font(size, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/' + ('segoeuib.ttf' if bold else 'segoeui.ttf'), size)


def fitted(text, size, width, bold=False):
    for value in range(size, 11, -1):
        f = font(value, bold)
        if f.getlength(text) <= width:
            return f
    return font(12, bold)


def colorize(values, p):
    if p['kind'] == 'categorical':
        rgb = np.zeros((*values.shape, 3), dtype='uint8')
        for row in p['classes']:
            rgb[values == row['value']] = ImageColor.getrgb(row['color'])
        return rgb
    colors = np.array([ImageColor.getrgb(c) for c in p['palette']])
    safe = np.nan_to_num(values, nan=p['stops'][0])
    return np.stack([np.interp(safe, p['stops'], colors[:, i]) for i in range(3)], axis=-1).astype('uint8')


def compose(p, values, boundary, date, index, count):
    upgrade_project(p)
    if p['layout'] != 'original':
        from social import compose_social
        return compose_social(p, values, boundary, date, index, count)
    box = p['bbox']
    w, h = map_dimensions(box)
    map_x, map_y = 60 + (960 - w) // 2, 360 + (1034 - h) // 2
    def xy(lon, lat):
        return ((lon - box[0]) / (box[2] - box[0]) * w, (box[3] - lat) / (box[3] - box[1]) * h)

    mask = Image.new('L', (w, h), 0 if p['clip_ecuador'] else 255)
    md = ImageDraw.Draw(mask)
    rings = []
    for feature in boundary['features']:
        g = feature['geometry']
        for polygon in g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]:
            for i, ring in enumerate(polygon):
                points = [xy(*point[:2]) for point in ring]
                if p['clip_ecuador']:
                    md.polygon(points, fill=255 if i == 0 else 0)
                rings.append(points)
    valid = np.isfinite(values)
    resampling = Image.Resampling.NEAREST if p['kind'] == 'categorical' else Image.Resampling.BILINEAR
    weights = np.asarray(Image.fromarray(valid.astype('float32')).resize((w, h), resampling))
    smooth = np.asarray(Image.fromarray(np.where(valid, values, 0).astype('float32')).resize((w, h), resampling))
    smooth = np.divide(smooth, weights, out=np.zeros_like(smooth), where=weights > 0)
    combined = np.minimum(np.asarray(mask), (weights > .99).astype('uint8') * 255)
    if not combined.any():
        raise ValueError('El encuadre y la máscara no contienen datos visibles. Revisa la región.')
    frame = Image.new('RGB', (1080, 1920), p['background'])
    d = ImageDraw.Draw(frame)
    rgb = ImageColor.getrgb(p['background'])
    light = sum(rgb) > 440
    muted = '#475e68' if light else '#b0c5cc'
    foot = '#526b76' if light else '#89a5ae'
    note_color = '#475e68' if light else '#a5bec6'
    card = '#dde5e8' if light else '#19333e'
    date_color = '#152c37' if light else '#ffffff'
    d.text((64, 58), p['brand'], font=fitted(p['brand'], 27, 940, True), fill=p['accent'])
    d.text((60, 117), p['title'], font=fitted(p['title'], 76, 960, True), fill=p['text'])
    d.text((64, 218), p['description'], font=fitted(p['description'], 35, 940), fill=muted)
    d.rounded_rectangle((64, 290, 440, 350), radius=16, fill=card)
    day = dt.date.fromisoformat(date)
    date_label = day.strftime({'DD / MM / AAAA': '%d / %m / %Y', 'AAAA-MM-DD': '%Y-%m-%d',
                              'MM / DD / AAAA': '%m / %d / %Y'}[p['date_format']])
    if p['cadence'] == 'Mensual':
        date_label = day.strftime('%m / %Y')
    elif p['cadence'] == 'Anual':
        date_label = str(day.year)
    d.text((84, 298), date_label, font=font(34, True), fill=date_color)
    prefix = p['counter_label'] or {'Diaria': 'DÍA', 'Mensual': 'MES', 'Anual': 'AÑO', 'Por observación': 'OBS.'}[p['cadence']]
    counter = f'{prefix} {index + 1:02} / {count:02}'
    d.text((730, 310), counter, font=fitted(counter, 25, 290), fill=muted)
    frame.paste(Image.fromarray(colorize(smooth, p)), (map_x, map_y), Image.fromarray(combined))
    # Draw outlines on a clipped map canvas so an out-of-window polygon cannot cross the titles.
    outlines = Image.new('RGBA', (w, h))
    od = ImageDraw.Draw(outlines)
    for ring in rings:
        od.line(ring, fill='#667e83' if light else '#d1e1d8', width=2)
    frame.paste(outlines, (map_x, map_y), outlines)
    d = ImageDraw.Draw(frame)
    for name, lon, lat, dx, dy in CITIES:
        if name not in p['cities'] or not (box[0] <= lon <= box[2] and box[1] <= lat <= box[3]):
            continue
        x, y = xy(lon, lat)
        x += map_x
        y += map_y
        d.ellipse((x-5, y-5, x+5, y+5), fill='white')
        label = p['city_labels'].get(name, name)
        label_font = fitted(label, 26, min(300, w), True)
        tx = min(max(map_x, x + dx), map_x + w - label_font.getlength(label))
        d.text((tx, y + dy), label, font=label_font, fill='white', stroke_width=2, stroke_fill='#10212c')
    legend = p['legend'] + (f' · {p["units"]}' if p['units'] else '')
    d.text((65, 1430), legend, font=fitted(legend, 29, 940, True), fill=p['text'])
    if p['kind'] == 'continuous':
        stops = p['stops']
        gradient = np.interp(np.linspace(0, len(stops)-1, 940), np.arange(len(stops)), stops)
        frame.paste(Image.fromarray(colorize(gradient[None, :], p)).resize((940, 30)), (65, 1490))
        d = ImageDraw.Draw(frame)
        for j, val in enumerate(stops):
            label = f'{val:g}' + ('+' if j == len(stops)-1 else '')
            d.text((65+j*940/(len(stops)-1), 1533), label, font=font(24), fill=muted if light else '#cbdadd', anchor='mt')
        d.text((65, 1590), p['scale_note'], font=fitted(p['scale_note'], 24, 940), fill=note_color)
        d.text((65, 1640), p['resolution_note'], font=fitted(p['resolution_note'], 26, 940), fill=note_color)
        d.text((65, 1685), p['note'], font=fitted(p['note'], 26, 940), fill=note_color)
    else:
        for i, row in enumerate(p['classes']):
            x, y = 65 + (i % 3) * 320, 1490 + (i // 3) * 46
            d.rounded_rectangle((x, y, x+23, y+23), radius=4, fill=row['color'])
            d.text((x+34, y-2), row['label'], font=fitted(row['label'], 23, 274), fill=p['text'])
        d.text((65, 1685), p['category_note'], font=fitted(p['category_note'], 24, 940), fill=note_color)
    d.line((65, 1750, 1005, 1750), fill='#32505b', width=2)
    has_credits = bool(p['author'] or p['credits'])
    d.text((65, 1766 if has_credits else 1780), p['citation'], font=fitted(p['citation'], 24, 940), fill=foot)
    caption = 'Ecuador continental · límites: geoBoundaries' if p['clip_ecuador'] else 'Ventana geográfica · límites: geoBoundaries'
    caption = p['boundary_note'] or caption
    d.text((65, 1800 if has_credits else 1820), caption, font=fitted(caption, 24, 940), fill=foot)
    d.text((65, 1834), p['author'], font=fitted(p['author'], 25, 940, True), fill=p['text'])
    d.text((65, 1868), p['credits'], font=fitted(p['credits'], 22, 940), fill=foot)
    if p['width'] != 1080:
        frame = frame.resize((p['width'], p['width'] * 16 // 9), Image.Resampling.LANCZOS)
    return frame
