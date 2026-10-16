"""Illustrated, editable scenes; never a scientific map or a calculation."""
import base64
import io
from functools import lru_cache

ENTRY = {
    'id': 'expedition.water_cycle', 'name': 'Expedición · Ciclo del agua',
    'category': 'Agua',
    'summary': 'Paisaje andino ilustrado con cinco procesos y etiquetas independientes.',
    'note': 'Ilustración conceptual con IA, sin escala física ni mediciones. Esquema parcial: no representa todos los flujos y depósitos del ciclo del agua.',
    'sources': [{'title': 'USGS · Water Science School: ciclo del agua',
                 'url': 'https://www.usgs.gov/special-topics/water-science-school/water-cycle'}],
}


def create_scientific_template(identifier, definition, *, duration=8):
    if identifier != ENTRY['id']:
        raise ValueError('Plantilla ilustrada desconocida.')
    from studio_resource_projects import create_resource_project
    from studio_scientific_library import insert_bioicon
    from studio_model import Element, validate_studio
    from output_profiles import profile_for
    project = create_resource_project(ENTRY['name'], definition, duration=duration)
    sid = project['studio']['timeline'][0]
    project = insert_bioicon(project, sid, 'expedicion.agua')
    scene = next(s for s in project['studio']['scenes'] if s['id'] == sid)
    scene['background'] = '#FFF5DF'
    profile = profile_for(definition)
    w, h = profile.width, profile.height
    unit = min(w, h)
    portrait = h / w >= 1.4
    left = max(profile.margin, w * .08)
    right = max(profile.margin, w * (.15 if portrait else .08))
    bw = w - left - right
    top = max(profile.margin, h * (.105 if portrait else .07))
    # This explanatory template needs a readable drawing area, not clipped text.
    if bw < 240 or h - top - profile.margin < 300:
        raise ValueError('La plantilla ilustrada necesita un área útil de al menos 240 × 300 px.')
    image_h = min(bw / 1.5, h * (.28 if portrait else .40))
    image_w = image_h * 1.5
    ix = left + (bw - image_w) / 2
    iy = top + unit * (.34 if portrait else .20)
    image = scene['elements'][0]
    image['transform'] = {'x': round(ix), 'y': round(iy), 'width': round(image_w), 'height': round(image_h)}
    image['style']['fit'] = 'contain'
    image['resource_role'] = 'conceptual_landscape'
    scene['resource'] = {**ENTRY, 'illustrative': True, 'generated_art': True}
    counter = 0

    def add(role, kind, box, style, rotation=0):
        nonlocal counter
        counter += 1
        x, y, width, height = box
        element = Element(id=sid + '.' + role, type=kind, name=role.replace('_', ' '),
            transform={'x': round(x), 'y': round(y), 'width': max(1, round(width)),
                       'height': max(1, round(height)), 'rotation': rotation},
            style=style, z_index=counter).to_dict()
        element['resource_role'] = role
        scene['elements'].append(element)

    def text(role, box, value, size, *, color='#132B46', heading=False):
        add(role, 'text', box, {'text': value, 'font_size': max(8, round(size)),
            'font_family': 'Lora' if heading else 'Atkinson Hyperlegible',
            'bold': heading, 'color': color})

    text('brand', (left, top, bw, unit * .045), 'ECUADOR VIVO / RECURSOS', unit * .022, color='#176F5C')
    text('title', (left, top + unit * .065, bw, unit * .15),
         'El agua conecta el territorio', unit * .055, heading=True)
    text('subtitle', (left, top + unit * .22, bw, unit * .065),
         'De las nubes al suelo, los bosques y los ríos.', unit * .024)
    # Arrows are conceptual flow cues: five separate shafts and arrowheads.
    processes = [
        ('condensation', 'Condensación', .20, .02, 0),
        ('precipitation', 'Precipitación', .76, .18, 90),
        ('evapotranspiration', 'Evapotranspiración', .50, .48, -90),
        ('runoff', 'Escorrentía', .64, .68, 25),
        ('infiltration', 'Infiltración', .24, .57, 90),
    ]
    for index, (role, label, fx, fy, angle) in enumerate(processes):
        cx, cy = ix + image_w * fx, iy + image_h * fy
        length = unit * .055
        add(role + '_arrow_shaft', 'shape', (cx - length/2, cy-length/2, length, length),
            {'shape': 'line', 'fill': '#3976B8', 'outline': '#3976B8', 'opacity': 1}, angle)
        # Two native line segments form a clear arrowhead without an icon asset.
        import math
        ex = cx + math.cos(math.radians(angle)) * length/2
        ey = cy + math.sin(math.radians(angle)) * length/2
        head = unit*.014
        for side in (-1,1):
            direction=(angle+side*135+180)%360-180
            hx=ex+math.cos(math.radians(direction))*head/2
            hy=ey+math.sin(math.radians(direction))*head/2
            add(role + '_arrow_head_' + str(side).replace('-','left'),
                'shape', (hx-head/2,hy-head/2,head,head),
                {'shape':'line','fill':'#3976B8','opacity':1},direction)
        # A readable key avoids obscuring the painting with long, baked-in words.
        ky = iy + image_h + unit*.035 + (index if portrait else index//3)*unit*(.045 if portrait else .058)
        kx = left if portrait else left + (index%3)*bw/3
        kw = bw if portrait else bw/3-unit*.02
        text(role + '_label', (kx, ky, kw, unit*.05), str(index+1) + '  ' + label,
             unit*.027, color='#176F5C')
        add(role + '_badge', 'shape', (cx + unit*.009, cy-unit*.023, unit*.043, unit*.043),
            {'shape': 'circle', 'fill': '#FFF5DF', 'outline': '#3976B8', 'opacity': 1})
        text(role + '_number', (cx + unit*.017, cy-unit*.022, unit*.032, unit*.043),
             str(index+1), unit*.026, heading=True)
    footer = h - max(profile.margin, h*(.20 if portrait else .08)) - unit*(.15 if portrait else .105)
    text('source', (left, footer, bw, unit*.04), 'Base conceptual: USGS · Water Science School', unit*.020)
    text('disclaimer', (left, footer + unit*.042, bw, unit*.055),
         'Ilustración conceptual con IA · esquema parcial · sin escala ni mediciones.', unit*.018)
    text('credits', (left, footer + unit*.102, bw, unit*.045),
         'Henry P. Conteron Moreta · Ing. Geociencias', unit*.021)
    validate_studio(project['studio'])
    return project


@lru_cache(maxsize=12)
def _preview(identifier, definition_json):
    import json
    from studio_media import AssetFrames
    from studio_timeline import PreparedTimeline
    project = create_scientific_template(identifier, json.loads(definition_json))
    timeline = PreparedTimeline(project, preview_max_side=280)
    with AssetFrames(project['studio']['media']) as assets:
        image = timeline.frame_at(0, assets=assets)
        buffer = io.BytesIO()
        try:
            image.convert('RGB').save(buffer, format='PNG')
            return 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode()
        finally:
            image.close()


def illustrated_templates(definition):
    import json
    from output_profiles import profile_for
    profile=profile_for(definition)
    w,h=profile.width,profile.height
    left=max(profile.margin,w*.08)
    right=max(profile.margin,w*(.15 if h/w>=1.4 else .08))
    top=max(profile.margin,h*(.105 if h/w>=1.4 else .07))
    if w-left-right<240 or h-top-profile.margin<300:
        return []
    return [{**ENTRY, 'preview': _preview(ENTRY['id'], json.dumps(definition, sort_keys=True))}]
