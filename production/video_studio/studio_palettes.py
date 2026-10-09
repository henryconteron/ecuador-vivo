"""Explicit presentation-only color scales. No domain/category inference."""
import copy
import math
import re
from studio_templates import PALETTES

MISSING_COLOR = '#89949c'


def _finite(value):
    try: return type(value) in (int,float) and math.isfinite(value)
    except OverflowError: return False


def validate_color_scale(scale):
    if not isinstance(scale,dict) or not isinstance(scale.get('palette'),str) or scale['palette'] not in PALETTES:
        raise ValueError('Paleta de escala desconocida.')
    kind=PALETTES[scale['palette']]['type']
    fields={'palette','colors'} | ({'categories'} if kind=='categorical' else {'domain','center'} if kind=='diverging' else {'domain'})
    if set(scale)-fields: raise ValueError('Propiedad de escala desconocida.')
    colors=scale.get('colors',PALETTES[scale['palette']]['colors'])
    if not isinstance(colors,(list,tuple)) or not 2<=len(colors)<=12 or any(
            not isinstance(c,str) or not re.fullmatch(r'#[0-9a-fA-F]{6}',c) for c in colors):
        raise ValueError('Declara entre dos y doce colores #RRGGBB.')
    if kind=='diverging' and len(colors)!=3: raise ValueError('La escala divergente requiere tres colores y un centro explícito.')
    if kind=='categorical':
        categories=scale.get('categories')
        if (not isinstance(categories,list) or not 1<=len(categories)<=len(colors) or
                any(not isinstance(c,str) or not c or len(c)>200 or any(char in c for char in '\n\r\t') for c in categories) or
                len(set(categories))!=len(categories)):
            raise ValueError('Categorías únicas y explícitas: un color distinto por categoría, máximo doce.')
        if len(set(c.lower() for c in colors[:len(categories)]))!=len(categories):
            raise ValueError('Cada categoría requiere un color distinto.')
    else:
        domain=scale.get('domain')
        if not isinstance(domain,list) or len(domain)!=2 or not all(_finite(v) for v in domain) or domain[0]>=domain[1]:
            raise ValueError('Declara mínimo y máximo finitos del dominio de color.')
        if kind=='diverging' and (not _finite(scale.get('center')) or not domain[0]<scale['center']<domain[1]):
            raise ValueError('Declara un centro interior al dominio; no se infiere un cero físico.')
    return copy.deepcopy(scale)


def _fraction(value,low,high):
    # Avoid overflow for opposite finite endpoints such as ±1e308.
    if value==low: return 0.
    if value==high: return 1.
    span=high-low
    if _finite(span): return (value-low)/span
    amplitude=max(abs(low),abs(high))
    return (value/amplitude-low/amplitude)/(high/amplitude-low/amplitude)


def _mix(a,b,fraction):
    rgb=lambda c:tuple(int(c[i:i+2],16) for i in (1,3,5))
    return '#'+''.join(f'{round(x+(y-x)*fraction):02x}' for x,y in zip(rgb(a),rgb(b)))


def scale_color(scale,value,category=None):
    validate_color_scale(scale)
    if value is None: return MISSING_COLOR
    if not _finite(value): raise ValueError('Valor de escala inválido.')
    definition=PALETTES[scale['palette']];kind=definition['type']
    colors=scale.get('colors',definition['colors'])
    if kind=='categorical':
        if category not in scale['categories']: raise ValueError('Falta una categoría representada en la escala declarada.')
        return colors[scale['categories'].index(category)]
    low,high=scale['domain']
    if not low<=value<=high: raise ValueError('Hay valores fuera del dominio de color: amplía la escala explícitamente.')
    if kind=='diverging':
        center=scale['center']
        return (_mix(colors[0],colors[1],_fraction(value,low,center)) if value<=center else
                _mix(colors[1],colors[2],_fraction(value,center,high)))
    fraction=_fraction(value,low,high)*(len(colors)-1)
    index=min(len(colors)-2,int(fraction))
    return _mix(colors[index],colors[index+1],fraction-index)


def scale_geometry(scale,units):
    validate_color_scale(scale)
    if any(char in units for char in '\n\r\t'): raise ValueError('La unidad no cabe en una línea de leyenda; conserva su registro y revisa la presentación.')
    definition=PALETTES[scale['palette']];kind=definition['type']
    colors=scale.get('colors',definition['colors'])
    if kind=='categorical':
        legend=[{'label':name,'color':colors[i]} for i,name in enumerate(scale['categories'])]
    else:
        low,high=scale['domain'];values=[low,scale['center'],high] if kind=='diverging' else [low,high]
        legend=[{'label':(str(v)+' '+units).strip(),'color':scale_color(scale,v)} for v in values]
    legend.append({'label':'Sin datos','color':MISSING_COLOR})
    return {**copy.deepcopy(scale),'type':kind,'colors':list(colors),'legend':legend,'missing_color':MISSING_COLOR}


def legend_height(scale):
    kind=PALETTES[scale['palette']]['type']
    return 12+16*(len(scale['categories'])+1 if kind=='categorical' else 4 if kind=='diverging' else 3)


def draw_legend(image,geometry, *, font_family=None, warning_height=0):
    from PIL import ImageDraw
    from studio_typography import studio_font
    draw=ImageDraw.Draw(image);width,height=image.size
    rows=geometry['legend'];top=height-warning_height-legend_height(geometry)
    for index,row in enumerate(rows):
        font=studio_font(12,family=font_family or 'Barlow Condensed')
        while font.size>8 and font.getlength(row['label'])>width-48:
            font=studio_font(font.size-1,family=font_family or 'Barlow Condensed')
        if font.getlength(row['label'])>width-48: raise ValueError('La leyenda no cabe a 8 px: amplía la visualización.')
        y=top+6+index*16
        draw.rectangle((12,y,24,y+10),fill=row['color'])
        draw.text((32,y),row['label'],font=font,fill=geometry.get('text_color','#f0f5f8'),anchor='lt')
