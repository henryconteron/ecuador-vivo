"""Declarative data-bound Pillow visualizations; one geometry for all renders.

No dataset reads, calculations, expression evaluation or mutable scientific
state. Line x is an ordered category index, not an inferred temporal interval.
"""
from dataclasses import dataclass, field, asdict
import json
import hashlib
import math
import re
from PIL import Image, ImageDraw
from calculation_results import CalculationResult, resolve_binding, ordered_rows, _value
from studio_model import validate_binding
from editorial import editorial_font
from studio_typography import studio_font, validate_family
from studio_palettes import validate_color_scale, scale_color, scale_geometry, legend_height, draw_legend

KINDS=frozenset(('kpi','metric','horizontal_bar','vertical_bar','dot','lollipop','line','ranking','comparison'))


def snapshot_checksum(payload):
    # Integrity checksum, not authentication of an external scientific source.
    return hashlib.sha256(json.dumps({key:value for key,value in payload.items()
        if key!='snapshot_sha256'},sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def validate_snapshot(payload):
    """Validate stored scientific metadata without reading its source paths."""
    if not isinstance(payload,dict) or payload.get('mode')!='static_snapshot':
        raise ValueError('Instantánea científica inválida.')
    try:
        if payload.get('snapshot_sha256')!=snapshot_checksum(payload):
            raise ValueError('La procedencia o el diseño de la instantánea cambió después de crear su PNG.')
        spec=VisualizationSpec(**payload['spec'])
        spec.to_dict()
        result=CalculationResult(payload['result']).to_dict()
        resolve_binding({result['id']:result},spec.binding)
        records=payload['source_records']
        if not isinstance(records,list) or len(records)>10000:
            raise ValueError('Procedencia de instantánea demasiado grande.')
        for record in records:
            if not isinstance(record,dict) or not re.fullmatch(r'[a-f0-9]{64}',str(record.get('sha256',''))):
                raise ValueError('Falta el hash original de una fuente de la visualización.')
        dimensions=payload['output_dimensions']
        if not isinstance(dimensions,list) or len(dimensions)!=2 or any(type(n) is not int or not 160<=n<=3840 for n in dimensions):
            raise ValueError('Dimensiones de instantánea inválidas.')
        if not re.fullmatch(r'[a-f0-9]{64}',str(payload.get('scientific_identity',''))):
            raise ValueError('Identidad científica inválida.')
        if not re.fullmatch(r'[a-f0-9]{64}',str(payload.get('image_sha256',''))):
            raise ValueError('Falta el hash del PNG de la instantánea.')
        if len(json.dumps(payload,allow_nan=False))>2_000_000:
            raise ValueError('La procedencia de la instantánea supera 2 MB.')
    except (KeyError,TypeError,RecursionError) as error:
        raise ValueError('Metadatos incompletos de visualización.') from error


def verify_snapshot_image(payload,path):
    """Pixels must represent the stored values/style at the original size."""
    validate_snapshot(payload)
    spec=VisualizationSpec(**payload['spec'])
    result=payload['result']
    expected=render_visualization(spec,{result['id']:result},tuple(payload['output_dimensions']))
    with Image.open(path) as actual:
        if actual.size!=expected.size or actual.convert('RGBA').tobytes()!=expected.tobytes():
            raise ValueError('El PNG no representa el resultado científico y diseño registrados.')


@dataclass(frozen=True)
class VisualizationSpec:
    kind: str
    binding: dict
    style: dict = field(default_factory=dict)
    top_n: int | None = None
    descending: bool = True

    def to_dict(self):
        if not isinstance(self.kind,str) or self.kind not in KINDS:
            raise ValueError('Visualización desconocida.')
        validate_binding(self.binding)
        expected='value' if self.kind in ('kpi','metric') else 'rows'
        if self.binding['field']!=expected:
            raise ValueError(f'{self.kind} requiere el campo {expected}.')
        if type(self.descending) is not bool or (self.top_n is not None and
                (type(self.top_n) is not int or not 1<=self.top_n<=1000)):
            raise ValueError('Sort/Top N inválido.')
        if self.kind in ('line','comparison') and self.top_n is not None:
            raise ValueError('Line/comparison conserva su secuencia completa; filtra los datos explícitamente.')
        if not isinstance(self.style,dict) or set(self.style)-{'color','background','text','title','font_size','decimals','font_family','color_scale'}:
            raise ValueError('Estilo de visualización desconocido.')
        if 'font_family' in self.style: validate_family(self.style['font_family'])
        if 'color_scale' in self.style: validate_color_scale(self.style['color_scale'])
        for name in ('color','background','text'):
            if name in self.style and (not isinstance(self.style[name],str) or
                                      not re.fullmatch(r'#[0-9a-fA-F]{6}',self.style[name])):
                raise ValueError('Color de visualización inválido.')
        title=self.style.get('title','')
        if not isinstance(title,str) or len(title)>200:
            raise ValueError('Título de visualización inválido.')
        for name,low,high in (('font_size',8,200),('decimals',0,8)):
            if name in self.style and (type(self.style[name]) is not int or not low<=self.style[name]<=high):
                raise ValueError(f'{name} fuera de rango.')
        return asdict(self)


def _label(value,units,decimals):
    if value is None: return 'Sin datos'
    number=f'{value:.{decimals}f}'
    if decimals: number=number.rstrip('0').rstrip('.')
    return (number+' '+units).strip()


def visualization_geometry(spec,registry,size):
    options=spec.to_dict()
    if (len(size)!=2 or any(type(n) is not int or n<80 or n>3840 for n in size)
            or size[0]*size[1]>8_294_400):
        raise ValueError('Tamaño de visualización fuera del presupuesto.')
    width,height=size
    result=registry.get(spec.binding['result_id'],{})
    units=result.get('units','')
    if not isinstance(units,str) or len(units)>200:
        raise ValueError('Unidad de visualización inválida.')
    bound=resolve_binding(registry,spec.binding)
    warnings=result.get('provenance',{}).get('warnings',[])
    if not isinstance(warnings,list) or any(not isinstance(w,str) for w in warnings):
        raise ValueError('Advertencias científicas inválidas.')
    geometry=dict(kind=spec.kind,size=size,units=units,style=options['style'],warnings=list(warnings),
                  title=spec.style.get('title',result.get('variable','')))
    decimals=spec.style.get('decimals',2)
    scale=spec.style.get('color_scale')
    reserved=0
    if scale is not None:
        geometry['scale']=scale_geometry(scale,units)
        reserved=legend_height(scale)+(max(24,round(height*.08)) if warnings else 0)
        if width<160 or height-reserved<120:
            raise ValueError('La escala y su leyenda necesitan más espacio: amplía la visualización.')
    if spec.kind in ('kpi','metric'):
        _value(bound)
        geometry.update(value=bound,value_label=_label(bound,units,decimals))
        if scale is not None:
            if geometry['scale']['type']=='categorical': raise ValueError('Una métrica escalar requiere dominio numérico, no categorías inferidas.')
            geometry['value_color']=scale_color(scale,bound)
            geometry['content_height']=height-reserved
        return geometry
    if not isinstance(bound,list) or len(bound)>10000:
        raise ValueError('Una visualización requiere filas con name/value.')
    if spec.kind in ('line','comparison'):
        for row in bound:
            if not isinstance(row,dict) or not isinstance(row.get('name'),str):
                raise ValueError('Cada fila requiere name/value.')
            _value(row.get('value'))
        rows=bound
    else:
        rows=ordered_rows(bound,descending=spec.descending,top_n=spec.top_n)
        if scale is not None and spec.top_n is None:
            # Explicit scales expose missing rows neutrally after the valid
            # ranking. Default/no-scale ordering remains byte-compatible.
            rows=rows+[dict(row) for row in bound if row.get('value') is None]
    if spec.kind=='comparison' and (len(rows)!=2 or any(r.get('value') is None for r in rows)):
        raise ValueError('Comparison requiere exactamente dos observaciones válidas.')
    if spec.kind=='comparison' and rows[0].get('coverage',1)!=rows[1].get('coverage',1):
        raise ValueError('Comparison requiere cobertura comparable, no ocultar diferencias de soporte.')
    values=[r['value'] for r in rows if r.get('value') is not None]
    # Include zero for bar length semantics; label numeric endpoints explicitly.
    amplitude=max((abs(v) for v in values),default=1) or 1
    low=min([0]+[v/amplitude for v in values])
    high=max([0]+[v/amplitude for v in values])
    if low==high: high=low+1
    plot=(width*.30,height*.18,width*.90,height*.84)
    if spec.kind in ('vertical_bar','line','comparison'):
        plot=(width*.12,height*.18,width*.90,height*.78)
    left,top,right,bottom=plot
    if scale is not None:
        bottom=min(bottom,height-reserved-max(24,height*.1))
        if bottom-top<32: raise ValueError('La leyenda no deja espacio para los datos: amplía la visualización.')
        plot=(left,top,right,bottom)
    fraction=lambda value:(value/amplitude-low)/(high-low)
    horizontal=lambda value:left+fraction(value)*(right-left)
    vertical=lambda value:bottom-fraction(value)*(bottom-top)
    zero=vertical(0) if spec.kind in ('vertical_bar','line','comparison') else horizontal(0)
    marks=[]
    step=((right-left) if spec.kind in ('vertical_bar','line','comparison') else (bottom-top))/max(1,len(rows))
    for index,row in enumerate(rows):
        value=row.get('value')
        mark=dict(name=row['name'],value=value,value_label=_label(value,units,decimals),
                  coverage=row.get('coverage'))
        if scale is not None: mark['color']=scale_color(scale,value,row['name'])
        if spec.kind in ('vertical_bar','line','comparison'):
            x=left+(index+.5)*step
            mark.update(point=(x,vertical(value)) if value is not None else None,
                        end=vertical(value) if value is not None else None, thickness=step*.55)
        else:
            y=top+(index+.5)*step
            mark.update(point=(horizontal(value),y) if value is not None else None,
                        end=horizontal(value) if value is not None else None,thickness=step*.55)
        marks.append(mark)
    segments=[]
    if spec.kind=='line':
        segments=[(a['point'],b['point']) for a,b in zip(marks,marks[1:])
                  if a['point'] is not None and b['point'] is not None]
    geometry.update(plot=plot,zero=zero,marks=marks,segments=segments,
                    minimum=low*amplitude,maximum=high*amplitude,
                    partial_coverage=any(r.get('coverage',1)<1 for r in rows))
    return geometry


def render_visualization(spec,registry,size):
    geometry=visualization_geometry(spec,registry,size)
    width,height=size
    style=spec.style
    image=Image.new('RGBA',size,style.get('background','#04151e'))
    draw=ImageDraw.Draw(image)
    color=style.get('color','#13bfd1')
    text=style.get('text','#f0f5f8')
    size_font=style.get('font_size',max(12,round(min(size)*.04)))
    def load_font(pixels,bold=False):
        return (studio_font(pixels,family=style['font_family'],bold=bold) if 'font_family' in style
                else editorial_font(pixels,bold=bold))
    def write(position,content, *, anchor='lt',large=False,max_width=None):
        chosen=load_font(size_font*3 if large else size_font,bold=large)
        if max_width:
            pixels=chosen.size
            while pixels>8 and chosen.getlength(content)>max_width:
                pixels-=1
                chosen=load_font(pixels,bold=large)
        draw.text(position,content,font=chosen,fill=text,anchor=anchor)
    write((width*.05,height*.05),geometry['title'],max_width=width*.9)
    if spec.kind in ('kpi','metric'):
        if 'scale' in geometry: text=geometry['value_color']
        write((width*.5,geometry.get('content_height',height)*.5),geometry['value_label'],anchor='mm',large=True,max_width=width*.9)
        text=style.get('text','#f0f5f8')
    else:
        left,top,right,bottom=geometry['plot']
        zero=geometry['zero']
        vertical=spec.kind in ('vertical_bar','line','comparison')
        if vertical:
            draw.line((left,zero,right,zero),fill=text,width=1)
            write((left,top),_label(geometry['maximum'],'',2),anchor='rt')
            write((left,bottom),_label(geometry['minimum'],'',2),anchor='rt')
        else:
            draw.line((zero,top,zero,bottom),fill=text,width=1)
            write((left,bottom+size_font),_label(geometry['minimum'],'',2))
            write((right,bottom+size_font),_label(geometry['maximum'],'',2),anchor='rt')
        if 'scale' in geometry:
            for start,end in geometry['segments']:
                draw.line((*start,*end),fill=text,width=3)
        for mark in geometry['marks']:
            color=mark.get('color',style.get('color','#13bfd1'))
            point=mark['point']
            if point is None:
                if 'scale' in geometry:
                    index=geometry['marks'].index(mark)
                    if vertical:
                        x=left+(index+.5)*(right-left)/max(1,len(geometry['marks']))
                        write((x,bottom+size_font),mark['name']+' · Sin datos',anchor='mt',max_width=mark['thickness']*1.6)
                    else:
                        y=top+(index+.5)*(bottom-top)/max(1,len(geometry['marks']))
                        write((left-size_font*.5,y),mark['name'],anchor='rm',max_width=width*.26)
                        write((right,y),'Sin datos',anchor='rm',max_width=width*.25)
                continue
            x,y=point
            radius=max(2,min(8,size_font*.15))
            if spec.kind in ('horizontal_bar','ranking'):
                half=mark['thickness']/2
                if x!=zero: draw.rectangle((min(x,zero),y-half,max(x,zero),y+half),fill=color)
            elif spec.kind in ('vertical_bar','comparison'):
                half=mark['thickness']/2
                if y!=zero: draw.rectangle((x-half,min(y,zero),x+half,max(y,zero)),fill=color)
            elif spec.kind=='lollipop':
                draw.line((zero,y,x,y),fill=color,width=2)
            if spec.kind in ('dot','lollipop','line'):
                draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill=color)
            if vertical:
                write((x,bottom+size_font),mark['name'],anchor='mt',max_width=mark['thickness']*1.6)
            else:
                write((left-size_font*.5,y),mark['name'],anchor='rm',max_width=width*.26)
                write((right+size_font*.5,y),_label(mark['value'],'',style.get('decimals',2)),anchor='lm',max_width=width*.08)
        if 'scale' not in geometry:
            for start,end in geometry['segments']:
                draw.line((*start,*end),fill=color,width=3)
        caption=geometry['units']
        if geometry['partial_coverage']: caption+=' · Cobertura parcial: revisa la procedencia'
        if not geometry['marks']: caption='Sin datos · '+caption
        caption_y=height-legend_height(geometry['scale'])-max(24,round(height*.08)) if 'scale' in geometry else height*.95
        write((width*.05,caption_y),caption,anchor='lb',max_width=width*.9)
    if 'scale' in geometry:
        draw_legend(image,{**geometry['scale'],'text_color':text},font_family=style.get('font_family'),
                    warning_height=max(24,round(height*.08)) if geometry['warnings'] else 0)
    image.info['visualization_geometry']=geometry
    if geometry['warnings']:
        # The full warning remains in provenance/UI. A visible flag travels
        # with PNG and MP4, including KPI cards for incomplete periods.
        partial=any(any(word in warning.lower() for word in ('parcial','incomplet','sin dato'))
                    for warning in geometry['warnings'])
        notice=('Periodo/cobertura parcial' if partial else 'Advertencias metodológicas')+' · consultar procedencia'
        if geometry['units']: notice=geometry['units']+' · '+notice
        draw.rectangle((0,height*.92,width,height),fill='#523d18')
        write((width*.05,height*.95),notice,max_width=width*.9)
    return image
