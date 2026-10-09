"""Local, deterministic scene graph shared by the visual editor and MP4 renderer.

No global monkeypatches: each Pillow image owns its scene. Data/maps are unchanged;
only drawing geometry is editable. Coordinates are native authoring pixels;
legacy artwork uses 1080×1920, Studio scenes use their OutputProfile dimensions.
"""
from __future__ import annotations

import base64
import functools
import inspect
import io
import math
import re
from collections import defaultdict

from PIL import Image, ImageDraw, ImageColor

ICONS = ('rain', 'temperature', 'wind', 'calendar', 'bars', 'index', 'pin', 'trend', 'clock')


def clean_layout(value):
    """Validate JSON from the browser/imports; never accept arbitrary file/code paths."""
    if not isinstance(value, dict):
        return {}
    result = {'version': 1, 'full_canvas': bool(value.get('full_canvas', False))}
    for name in ('map', 'endcard'):
        entries = value.get(name, {})
        if not isinstance(entries, dict) or len(entries) > 600:
            raise ValueError('La maqueta debe contener como máximo 600 elementos por tarjeta.')
        result[name] = {}
        custom_pixels = 0
        for key, item in entries.items():
            if not isinstance(key, str) or len(key) > 180 or not isinstance(item, dict):
                raise ValueError('Elemento de maqueta inválido.')
            row = {}
            for field in ('x', 'y', 'w', 'h', 'font_size', 'z'):
                if field in item:
                    number = float(item[field])
                    if not math.isfinite(number):
                        raise ValueError('Las medidas de la maqueta deben ser finitas.')
                    lower, upper = ((4, 400) if field == 'font_size' else
                                    (1, 3840) if field in ('w', 'h') else (-3840, 3840))
                    if not lower <= number <= upper:
                        raise ValueError(f'Medida fuera de rango: {field}.')
                    row[field] = number
            if 'text' in item:
                row['text'] = str(item['text'])[:500]
            if 'color' in item:
                color = str(item['color'])
                if not re.fullmatch(r'#[0-9a-fA-F]{6}', color):
                    raise ValueError('Usa un color hexadecimal #RRGGBB.')
                row['color'] = color
            if 'icon' in item:
                if item['icon'] not in ICONS:
                    raise ValueError('Icono no admitido.')
                row['icon'] = item['icon']
            if 'hidden' in item:
                row['hidden'] = bool(item['hidden'])
            if 'deleted' in item:
                row['deleted'] = bool(item['deleted'])
            if 'locked' in item:
                if type(item['locked']) is not bool:
                    raise ValueError('locked debe ser booleano.')
                row['locked'] = item['locked']
            if 'name' in item:
                if not isinstance(item['name'], str) or len(item['name']) > 180:
                    raise ValueError('Nombre de capa inválido (máximo 180 caracteres).')
                row['name'] = item['name']
            if key.startswith('custom.'):
                custom_pixels += row.get('w', 500) * row.get('h', 120)
                if custom_pixels > 20_000_000:
                    raise ValueError('Los elementos añadidos ocupan demasiado espacio. Reduce su tamaño o cantidad.')
            result[name][key] = row
    return result


def _png(image):
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return 'data:image/png;base64,'+base64.b64encode(buffer.getvalue()).decode('ascii')


class Scene:
    def __init__(self, image, config, name):
        self.base = image.copy().convert('RGBA')
        self.name = name
        self.capture = bool(config.get('_layout_capture'))
        self.overrides = clean_layout(config.get('visual_layout', {})).get(name, {})
        self.items = []
        self.counters = defaultdict(int)

    def key(self, tag):
        frame = inspect.currentframe().f_back
        skip = {'text_box', '_ink', '_center', '_parts', 'draw_line', 'draw_tracked'}
        while frame and (frame.f_code.co_filename == __file__ or frame.f_code.co_name in skip):
            frame = frame.f_back
        function = frame.f_code.co_name if frame else 'scene'
        base = function+'.'+tag
        self.counters[base] += 1
        return f'{base}.{self.counters[base]}'

    def put(self, image, pos, *, key=None, label='', kind='graphic', editable=True,
            text='', font_size=None, color=None, content_editable=False, offset=(0, 0),
            transformed=False, icon=None):
        key = key or self.key(kind)
        image = image.convert('RGBA')
        x, y = pos[0]+offset[0], pos[1]+offset[1]
        w, h = image.size
        original = {'x': x, 'y': y, 'w': w, 'h': h}
        override = self.overrides.get(key, {})
        if not transformed:
            x, y = override.get('x', x), override.get('y', y)
            new_w, new_h = override.get('w', w), override.get('h', h)
            # Geographic shapes and icons MUST keep their aspect ratio. Their
            # distance bars, if present, travel and scale with the same group.
            if kind in ('map', 'icon'):
                factor = new_w/max(1, w)
                new_h = h*factor
            size = (max(1, round(new_w)), max(1, round(new_h)))
            if size != image.size:
                image = image.resize(size, Image.Resampling.LANCZOS)
            w, h = image.size
        item = dict(id=key, label=override.get('name', label or text[:60] or kind), kind=kind, editable=editable,
                    x=round(x), y=round(y), w=round(w), h=round(h), original=original,
                    z=override.get('z', len(self.items)), hidden=override.get('hidden', False),
                    deleted=override.get('deleted', False),
                    locked=override.get('locked', False),
                    text=text, content_editable=content_editable, font_size=font_size,
                    color=color, icon=icon, image=image)
        self.items.append(item)

    def finish(self):
        if not any(row['id'].startswith('custom.') for row in self.items):
            self.add_custom()
        canvas = self.base.copy()
        for row in sorted(self.items, key=lambda row: row['z']):
            if not row['hidden'] and not row['deleted']:
                canvas.alpha_composite(row['image'], (row['x'], row['y']))
        canvas.info['visual_scene'] = self
        return canvas

    def add_custom(self):
        from editorial import editorial_font, stamp_icon
        for key, item in self.overrides.items():
            if not key.startswith('custom.'):
                continue
            x, y = item.get('x', 100), item.get('y', 100)
            if 'icon' in item:
                side = round(item.get('w', 88))
                tile = Image.new('RGBA', (side, side))
                stamp_icon(tile, side/2, side/2, item['icon'], diameter=side)
                self.put(tile, (x, y), key=key, kind='icon', label='Icono añadido', icon=item['icon'], transformed=True)
            else:
                size, text, color = round(item.get('font_size', 40)), item.get('text', 'Tu texto'), item.get('color', '#ffffff')
                tile = Image.new('RGBA', (round(item.get('w', 500)), round(item.get('h', 120))))
                d = ImageDraw.Draw(tile)
                selected = editorial_font(size, bold=True)
                lines, current = [], ''
                for word in text.split():
                    trial = (current+' '+word).strip()
                    if current and selected.getlength(trial) > tile.width:
                        lines.append(current)
                        current = word
                    else:
                        current = trial
                if current:
                    lines.append(current)
                for i, line in enumerate(lines):
                    d.text((0, i*(size+8)), line, font=selected, fill=color, anchor='lt')
                self.put(tile, (x, y), key=key, kind='text', label=text[:60], text=text, font_size=size,
                         color=color, content_editable=True, transformed=True)

    def payload(self):
        return {'width': self.base.width, 'height': self.base.height, 'background': _png(self.base), 'scene': self.name,
                'layers': [{**{k: v for k, v in row.items() if k != 'image'},
                            'src': _png(row['image'])} for row in self.items]}


def begin_layout(image, config, name='map'):
    if config.get('_layout_capture') or config.get('visual_layout'):
        image.info['_visual_scene'] = Scene(image, config, name)
    return image


def scene_for(image):
    return image.info.get('_visual_scene')


def attach_layout(image, parent, offset=(0, 0)):
    if scene_for(parent):
        image.info['_visual_scene'] = scene_for(parent)
        image.info['_visual_offset'] = offset
    return image


def finish_layout(image):
    scene = scene_for(image)
    if not scene:
        return image
    result = scene.finish()
    result.info['layout_boxes'] = image.info.get('layout_boxes', [])
    return result


def place_layer(image, layer, pos, *, key=None, label='', kind='graphic', editable=True,
                text='', font_size=None, color=None, content_editable=False, icon=None):
    scene = scene_for(image)
    if scene:
        scene.put(layer, pos, key=key, label=label, kind=kind, editable=editable,
                  text=text, font_size=font_size, color=color, content_editable=content_editable,
                  icon=icon, offset=image.info.get('_visual_offset', (0, 0)))
    else:
        layer = layer.convert('RGBA')
        position = tuple(round(v) for v in pos)
        if image.mode == 'RGBA':
            image.alpha_composite(layer, position)
        else:
            image.paste(layer, position, layer.getchannel('A'))


def full_layer(image, layer, **kwargs):
    box = layer.getbbox()
    if box:
        place_layer(image, layer.crop(box), box[:2], **kwargs)


class SceneDraw:
    """Capture Pillow primitives, without changing helpers on unrelated images."""
    def __init__(self, image):
        self.image, self.scene = image, scene_for(image)
        self.real = ImageDraw.Draw(image)

    def __getattr__(self, name):
        if name not in ('text', 'line', 'rectangle', 'rounded_rectangle', 'ellipse', 'arc', 'polygon'):
            return getattr(self.real, name)
        def paint(*args, **kwargs):
            key = self.scene.key(name)
            override = self.scene.overrides.get(key, {})
            layer = Image.new('RGBA', self.image.size)
            d = ImageDraw.Draw(layer)
            params = dict(kwargs)
            kind, label, meta = 'graphic', 'Detalle', {}
            if name == 'text':
                original_text = str(args[1] if len(args) > 1 else params.get('text', ''))
                content_editable = not bool(re.search(r'\d', original_text))
                text = override.get('text', original_text) if content_editable else original_text
                arguments = (args[0], text, *args[2:])
                selected = params.get('font')
                if selected and override.get('font_size'):
                    selected = selected.font_variant(size=round(override['font_size']))
                    params['font'] = selected
                if override.get('color'):
                    params['fill'] = override['color']
                kind, label = 'text', original_text[:60]
                meta = dict(text=original_text, content_editable=content_editable,
                            font_size=getattr(selected, 'size', None), color=params.get('fill'))
                getattr(d, name)(*arguments, **params)
            else:
                getattr(d, name)(*args, **params)
                if name in ('rectangle', 'rounded_rectangle'):
                    kind, label = 'panel', 'Panel / tarjeta'
            box = layer.getbbox()
            if box:
                self.scene.put(layer.crop(box), box[:2], key=key, label=label, kind=kind,
                               editable=kind in ('text', 'panel'),
                               offset=self.image.info.get('_visual_offset', (0, 0)), **meta)
            elif name == 'text':
                # An intentionally emptied text must stay selectable. Losing its
                # layer would make the next save reject the otherwise valid ID.
                # This transparent tile changes no exported pixels.
                anchor = args[0] if args else params.get('xy', (0, 0))
                self.scene.put(Image.new('RGBA', (1, 1)), anchor, key=key,
                               label=label, kind='text', editable=True,
                               offset=self.image.info.get('_visual_offset', (0, 0)), **meta)
        return paint


def draw(image):
    return SceneDraw(image) if scene_for(image) else ImageDraw.Draw(image)


def editable_text_box(function):
    @functools.wraps(function)
    def wrapped(image, text, box, **kwargs):
        scene = scene_for(image)
        if not scene:
            return function(image, text, box, **kwargs)
        key = scene.key('textbox')
        override = scene.overrides.get(key, {})
        ox, oy = image.info.get('_visual_offset', (0, 0))
        x, y = override.get('x', box[0]+ox), override.get('y', box[1]+oy)
        w, h = override.get('w', box[2]-box[0]), override.get('h', box[3]-box[1])
        params = dict(kwargs)
        if 'font_size' in override:
            params['size'] = round(override['font_size'])
        if 'color' in override:
            params['color'] = override['color']
        editable = not bool(re.search(r'\d', str(text)))
        new_text = override.get('text', text) if editable else text
        tile = Image.new('RGBA', (max(1, round(w)), max(1, round(h))))
        bounds = function(tile, new_text, (0, 0, w, h), **params)
        scene.put(tile, (x, y), key=key, kind='text', label=str(text)[:60],
                  text=str(text), content_editable=editable, font_size=params.get('size', 28),
                  color=params.get('color', '#d3e5ed'), transformed=True)
        translated = [(a+x, b+y, c+x, d+y) for a, b, c, d in bounds]
        image.info.setdefault('layout_boxes', []).append(dict(text=str(new_text), box=(x,y,x+w,y+h), bounds=translated))
        return translated
    return wrapped


def editable_icon(function):
    """Rain-template draw_* helpers become one selectable icon, not 20 shapes."""
    @functools.wraps(function)
    def wrapped(d, *args, **kwargs):
        if not isinstance(d, SceneDraw):
            return function(d, *args, **kwargs)
        tile = Image.new('RGBA', d.image.size)
        function(ImageDraw.Draw(tile), *args, **kwargs)
        key = d.scene.key(function.__name__)
        replace = d.scene.overrides.get(key, {}).get('icon')
        if replace:
            box = tile.getbbox()
            if box:
                from editorial import stamp_icon
                tile = Image.new('RGBA', d.image.size)
                stamp_icon(tile, (box[0]+box[2])/2, (box[1]+box[3])/2, replace,
                           diameter=round(min(box[2]-box[0],box[3]-box[1])))
        full_layer(d.image, tile, key=key, kind='icon', label=function.__name__.replace('draw_', '').replace('_', ' '))
    return wrapped
