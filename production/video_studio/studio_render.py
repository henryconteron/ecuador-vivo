"""Deterministic free-scene Pillow renderer using the existing scene graph.

Assets are resolved images supplied by the secure media/map layer, never file
paths. Unsupported features raise instead of silently disappearing in export.
"""
import re
import unicodedata
from PIL import Image, ImageDraw, ImageOps
from studio_model import validate_scene
from layout_engine import begin_layout, place_layer, finish_layout
from studio_typography import studio_font
from calculation_results import resolve_binding
from visualizations import VisualizationSpec, render_visualization

SUPPORTED=frozenset(('text','source','metric','ranking','chart','shape','background','map','image','logo','video','legend'))


def _color(value):
    if not isinstance(value,str) or not re.fullmatch(r'#[0-9a-fA-F]{6}',value):
        raise ValueError('El color de escena debe ser #RRGGBB.')
    return value


def _text_layer(style,size,content, *, preview_scale=1,check_only=False):
    if not isinstance(content,str) or len(content)>2000:
        raise ValueError('Texto de escena inválido.')
    color=_color(style.get('color','#f0f5f8'))
    pixels=style.get('font_size',max(10,round(min(size)*.16)))
    if type(pixels) is not int or not 8<=pixels<=400:
        raise ValueError('Tamaño de fuente fuera de rango.')
    # Validate authored typography before scaling presentation pixels. Scientific
    # bindings and the final scene keep their original styles and dimensions.
    if preview_scale!=1 and 'font_size' in style:pixels=max(1,round(pixels*preview_scale))
    minimum=max(1,round(8*preview_scale));leading=max(1,round(4*preview_scale))
    alignment=style.get('alignment','left')
    if alignment not in ('left','center','right'): raise ValueError('Alineación de texto desconocida.')
    family=style.get('font_family','Barlow Condensed')
    def load_font(size):
        font=studio_font(max(8,size),family=family,bold=style.get('bold',False))
        if size<8:
            font=font.font_variant(size=size)
            if family=='Lora':font.set_variation_by_axes([600 if style.get('bold',False) else 400])
        return font
    font=load_font(pixels)
    if not content: return (None if check_only else Image.new('RGBA',size)),pixels,color
    paragraphs=[]
    for paragraph in content.split('\n'):
        clusters=[]
        for character in paragraph:
            if clusters and (unicodedata.category(character).startswith('M') or
                    0x1f3fb<=ord(character)<=0x1f3ff or character=='\u200d' or clusters[-1].endswith('\u200d')):
                clusters[-1]+=character
            else: clusters.append(character)
        # Soft breakpoints follow complete clusters, including a space + mark.
        # NBSP remains inside a token and every literal separator is retained.
        tokens=[];token=[]
        for cluster in clusters:
            if token and token[-1][0] in ' \t' and cluster[0] not in ' \t':
                tokens.append(token);token=[]
            token.append(cluster)
        if token: tokens.append(token)
        paragraphs.append(tokens)
    def lines_for(font):
        def split_word(clusters):
            parts=[];current=''
            for cluster in clusters:
                if current and font.getlength(current+cluster)>size[0]: parts.append(current);current=cluster
                else: current+=cluster
            return parts+[current]
        lines=[]
        for tokens in paragraphs:
            current=''
            for clusters in tokens:
                word=''.join(clusters)
                if font.getlength(word)>size[0]:
                    if current: lines.append(current)
                    parts=split_word(clusters);lines.extend(parts[:-1]);current=parts[-1]
                    continue
                trial=current+word
                if current and font.getlength(trial)>size[0]:
                    lines.append(current);current=word
                else: current=trial
            lines.append(current)
        return lines
    lines=lines_for(font)
    while pixels>minimum and (len(lines)*(pixels+leading)>size[1] or
                       any(font.getlength(line)>size[0] for line in lines)):
        pixels-=1; font=load_font(pixels);lines=lines_for(font)
    if len(lines)*(pixels+leading)>size[1] or any(font.getlength(line)>size[0] for line in lines):
        raise ValueError('El texto no cabe: amplía el elemento antes de exportar.')
    if check_only:return None,pixels,color
    image=Image.new('RGBA',size)
    draw=ImageDraw.Draw(image)
    for index,line in enumerate(lines):
        remaining=size[0]-font.getlength(line)
        x=0 if alignment=='left' else remaining/2 if alignment=='center' else remaining
        draw.text((x,index*(pixels+leading)),line,font=font,fill=color,anchor='lt',
                  stroke_width=max(1,round(2*preview_scale)) if style.get('_cartographic_halo') else 0,
                  stroke_fill='#04151e')
    if 'gradient' in style:
        colors=style['gradient']
        if not isinstance(colors,list) or len(colors)!=2:raise ValueError('El degradado requiere dos colores.')
        colors=[_color(color) for color in colors]
        ramp=Image.linear_gradient('L').rotate(-90).resize((size[0],1)).resize(size)
        tinted=ImageOps.colorize(ramp,*colors).convert('RGBA')
        tinted.putalpha(image.getchannel('A'));image.close();ramp.close();image=tinted
    return image,pixels,color


def render_scene(scene,profile,registry, *, assets=None, time=None):
    validate_scene(scene)
    return _render_validated_scene(scene,profile,registry,assets=assets,time=time)


def _render_validated_scene(scene,profile,registry, *, assets=None, time=None,preview_scale=1,check_only=False):
    """Internal renderer for a private, already validated timeline snapshot."""
    if scene.get('renderer','studio')!='studio':
        raise ValueError('Las escenas legacy conservan su render original.')
    assets=assets or {}
    width,height=profile.width,profile.height
    background=_color(scene.get('background','#04151e'))
    config={'_layout_capture':True}
    image=None if check_only else begin_layout(Image.new('RGBA',(width,height),background),config)
    pixel_budget=0
    for element in scene['elements']:
        kind=element['type']
        transform=element.get('transform',{})
        if kind not in SUPPORTED:
            raise ValueError(f'Elemento {kind} aún no soportado por el render Studio.')
        animation=element.get('animation',{})
        rotation=transform.get('rotation',0)
        if not -360<=rotation<=360 or (rotation!=0 and kind not in ('image','video','logo','map','shape','background')):
            raise ValueError('Rotación requiere multimedia/forma y un ángulo entre -360 y 360.')
        animated=any(animation.get(name,'none')!='none' for name in ('in','out'))
        if animated:
            duration,delay=animation.get('duration',0),animation.get('delay',0)
            spans=duration*sum(animation.get(name,'none')!='none' for name in ('in','out'))+delay
            if duration<=0 or spans>scene['duration']:
                raise ValueError('Animación requiere duración positiva y debe caber en la escena sin solaparse.')
        if time is not None and (isinstance(time,bool) or not isinstance(time,(int,float)) or not 0<=time<scene['duration']):
            raise ValueError('Tiempo de cuadro fuera de la escena.')
        x,y,w,h=(round(transform.get(key,default)) for key,default in
                 (('x',0),('y',0),('width',100),('height',100)))
        if preview_scale!=1 and kind=='shape':
            # A one-pixel authored rule must survive a downscaled editor preview.
            w,h=max(1,w),max(1,h)
        if x<0 or y<0 or w<1 or h<1 or x+w>width or y+h>height:
            raise ValueError('Elemento fuera del canvas; corrige sus límites antes de exportar.')
        native_x,native_y=x,y
        pixel_budget+=w*h
        if pixel_budget>40_000_000:
            raise ValueError('Las capas superan el presupuesto de 40 MP por escena.')
        style=element.get('style',{})
        temporal=element.get('temporal_binding')
        context=assets.get('temporal.'+element['id']) if temporal else None
        if temporal and not isinstance(context,dict):raise ValueError('Falta la observación científica del binding temporal.')
        if kind=='legend' and not temporal:raise ValueError('Leyenda semántica pendiente; utiliza el auxiliar verificado del bundle.')
        fields={'opacity'}|({'text','color','font_size','bold','alignment','font_family','date_format','gradient'} if kind in ('text','source') else
            {'visualization'} if kind in ('metric','chart','ranking') else
            {'asset_id','fit','trim_in','trim_out','loop','mute','volume'} if kind=='video' else
            {'asset_id','fit'} if kind in ('map','image','logo','legend') else {'fill','shape','outline','radius'})
        if set(style)-fields or set(animation)-{'in','out','duration','delay'}:
            raise ValueError('Propiedad de estilo/animación desconocida; no se ignorará.')
        if 'bold' in style and type(style['bold']) is not bool: raise ValueError('Bold debe ser booleano.')
        binding=element.get('data_binding')
        font_size=None;color=None;content=''
        if kind in ('metric','chart','ranking'):
            if binding is None: raise ValueError('La visualización requiere DataBinding explícito.')
            settings=style.get('visualization',{})
            if not isinstance(settings,dict): raise ValueError('VisualizationSpec inválido.')
            if preview_scale!=1 and settings.get('style',{}).get('presentation'):
                settings={**settings,'style':{**settings['style'],'font_size':max(8,round(settings['style'].get('font_size',28)*preview_scale))}}
            try:
                spec=VisualizationSpec(**{'kind':'metric' if kind=='metric' else 'ranking' if kind=='ranking' else 'horizontal_bar',
                                          **settings,'binding':binding})
            except TypeError as error:
                raise ValueError('VisualizationSpec desconocido.') from error
            tile=render_visualization(spec,registry,(w,h))
        elif kind in ('map','image','logo','video','legend'):
            if kind=='video':
                from studio_audio import audio_settings
                audio_settings(style)
            asset_id='map.'+element['id'] if temporal else 'video.'+element['id'] if kind=='video' else style.get('asset_id')
            if not isinstance(asset_id,str) or not re.fullmatch(r'[\w.-]{1,180}',asset_id):
                raise ValueError('Solo se admiten IDs internos de assets, no rutas.')
            asset=assets.get(asset_id)
            if not isinstance(asset,Image.Image) or asset.width*asset.height>40_000_000:
                raise ValueError('Asset ausente o demasiado grande; impórtalo por la biblioteca segura.')
            fit=style.get('fit','contain')
            if fit not in ('contain','cover') or (kind in ('map','legend') and fit!='contain'):
                raise ValueError('Un mapa siempre conserva proporción y límites con contain.')
            tile=None if check_only else (ImageOps.contain(asset.convert('RGBA'),(w,h),Image.Resampling.LANCZOS) if fit=='contain'
                  else ImageOps.fit(asset.convert('RGBA'),(w,h),method=Image.Resampling.LANCZOS))
            if tile is not None:x+=(w-tile.width)//2;y+=(h-tile.height)//2
        elif kind in ('shape','background'):
            tile=Image.new('RGBA',(w,h));draw=ImageDraw.Draw(tile)
            fill=_color(style.get('fill','#13bfd1'))
            shape=style.get('shape','rectangle')
            box=(0,0,w-1,h-1)
            if shape=='rectangle': draw.rectangle(box,fill=fill)
            elif shape=='rounded_rectangle': draw.rounded_rectangle(box,radius=min(w,h)*.08,fill=fill)
            elif shape=='circle': draw.ellipse(box,fill=fill)
            elif shape=='calendar':
                from maqueta import draw_calendar_icon
                large=Image.new('RGBA',(w*3,h*3));pen=ImageDraw.Draw(large)
                scale=min((w*3-3)/44,(h*3-3)/49)
                draw_calendar_icon(pen,1,5*scale+1,fill,s=scale)
                tile=large.resize((w,h),Image.Resampling.LANCZOS);large.close()
            elif shape in ('panel','pill_outline','play','marker') or shape.startswith('icon.'):
                from studio_editorial import graphic
                outline=_color(style['outline']) if 'outline' in style else None
                radius=style.get('radius')
                if radius is not None and (type(radius) not in (int,float) or not 0<=radius<=3840):
                    raise ValueError('Radio de forma fuera de rango.')
                tile.close()
                tile=graphic(shape,(w,h),fill,outline=outline,radius=radius)
            elif shape in ('line','divider'):
                points=(w/2,0,w/2,h) if h>w else (0,h/2,w,h/2)
                draw.line(points,fill=fill,width=max(1,min(4,w,h)))
            else: raise ValueError('Forma no soportada.')
        else:
            content=context['date'] if temporal else style.get('text','')
            if temporal and temporal['channel']=='counter':
                content=f"OBS. {context['source_index']+1:02d} / {context['observation_count']}"
            elif temporal and style.get('date_format')=='long_es':
                import datetime as dt
                day=dt.date.fromisoformat(context['date'])
                month=('ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEP','OCT','NOV','DIC')[day.month-1]
                content=f'{day.day:02d} {month} {day.year}'
            if style.get('date_format') not in (None,'long_es'):raise ValueError('Formato de fecha desconocido.')
            if binding:
                value=resolve_binding(registry,binding)
                if not isinstance(value,(str,int,float)) and value is not None:
                    raise ValueError('El texto requiere un binding escalar.')
                content=content.replace('{{value}}','Sin datos' if value is None else str(value))
            text_style={**style,'_cartographic_halo':True} if element.get('cartographic_point') else style
            tile,font_size,color=_text_layer(text_style,(w,h),content,preview_scale=preview_scale,check_only=check_only)
        opacity=style.get('opacity',1)
        if isinstance(opacity,bool) or not isinstance(opacity,(int,float)) or not 0<=opacity<=1:
            raise ValueError('Opacity debe estar entre 0 y 1.')
        if check_only:
            if tile is not None:tile.close()
            continue
        if opacity!=1:
            tile.putalpha(tile.getchannel('A').point(lambda alpha:round(alpha*opacity)))
        if rotation!=0:
            native=Image.new('RGBA',(w,h));native.alpha_composite(tile,(x-native_x,y-native_y))
            rotated=native.rotate(-rotation,expand=True,resample=Image.Resampling.BICUBIC)
            fitted=ImageOps.contain(rotated,(w,h),Image.Resampling.LANCZOS)
            tile=Image.new('RGBA',(w,h));tile.alpha_composite(fitted,((w-fitted.width)//2,(h-fitted.height)//2))
            x,y=native_x,native_y
        if animated and time is not None:
            tile,x,y=_animate(tile,x,y,animation,time,scene['duration'])
        place_layer(image,tile,(x,y),key=element['id'],label=element.get('name') or kind,
                    kind='map' if kind=='map' else 'text' if kind in ('text','source') else 'graphic',
                    text=content,font_size=font_size,color=color,
                    content_editable=kind in ('text','source') and binding is None and temporal is None)
        row=image.info['_visual_scene'].items[-1]
        row.update(locked=element.get('locked',False),hidden=not element.get('visible',True),
                   z=element.get('z_index',0))
    if check_only:return None
    result=finish_layout(image)
    result.info['studio_scene_id']=scene['id']
    return result


def _animate(tile,x,y,animation,time,scene_duration):
    duration,delay=animation['duration'],animation.get('delay',0)
    for phase in ('in','out'):
        mode=animation.get(phase,'none')
        if mode=='none': continue
        progress=(max(0,min(1,(time-delay)/duration)) if phase=='in'
                  else max(0,min(1,(scene_duration-time)/duration)))
        if mode=='fade':
            tile=tile.copy();tile.putalpha(tile.getchannel('A').point(lambda alpha:round(alpha*progress)))
        elif mode=='slide':
            x-=round(tile.width*(1-progress))
            if progress==0: tile=tile.copy();tile.putalpha(0)
        elif mode=='scale':
            w,h=tile.size
            size=(max(1,round(w*progress)),max(1,round(h*progress)))
            tile=tile.resize(size,Image.Resampling.LANCZOS)
            x+=(w-size[0])//2;y+=(h-size[1])//2
            if progress==0: tile.putalpha(0)
        elif mode=='wipe':
            tile=tile.copy();alpha=tile.getchannel('A')
            alpha.paste(0,(round(tile.width*progress),0,tile.width,tile.height));tile.putalpha(alpha)
    return tile,x,y
