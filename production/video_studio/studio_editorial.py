"""Ecuador Vivo presentation primitives. No source reads or scientific calculations.

The same local fonts and vector artwork serve the editable canvas and MP4.
All coordinates below describe graphics, never the geographic data support.
"""
import math
from PIL import Image, ImageDraw
from studio_typography import studio_font

INK = '#04151e'
WHITE = '#f3f7f9'
MINT = '#58e4ce'
BLUE = '#65bde9'
MUTED = '#b5cbd5'
LINE = '#285466'
DISPLAY = 'Barlow Condensed Display'
BODY = 'Barlow Condensed'
ICON_NAMES = ('cloud', 'calendar', 'bars', 'peak', 'thermometer', 'wind',
              'index', 'pin', 'database', 'tiktok', 'instagram', 'mountain')
RANK_COLORS = ('#f52d68', '#ff6658', '#ff9f5c', '#ffd572', '#cfec8c',
               '#a0e5aa', '#59d7bd', '#32c9cf', '#29badd', '#25a9e9', '#2797ed', '#327cd9')


def fitted_font(text, pixels, width, *, family=BODY, bold=False, minimum=8):
    font = studio_font(max(8, round(pixels)), family=family, bold=bold)
    while font.size > minimum and font.getlength(text) > width:
        font = studio_font(font.size - 1, family=family, bold=bold)
    return font


def graphic(shape, size, color=WHITE, *, outline=None, fill=None, radius=None):
    """Antialiased vector icons and frames, independently editable as shapes."""
    w, h = size
    factor = 3
    image = Image.new('RGBA', (w * factor, h * factor))
    d = ImageDraw.Draw(image)
    W, H = image.size
    if shape in ('panel', 'pill_outline'):
        r = min(W, H) * (.48 if shape == 'pill_outline' else .065) if radius is None else radius * factor
        d.rounded_rectangle((2, 2, W-3, H-3), radius=r,
                            fill=fill or (INK if shape == 'pill_outline' else '#071b27'),
                            outline=outline or color, width=max(2, round(min(W,H)*.006)))
    elif shape == 'play':
        side = min(W, H); x = (W-side)/2; y = (H-side)/2
        d.ellipse((x, y, x+side-1, y+side-1), fill='#1a303c')
        d.polygon(((x+side*.39,y+side*.28),(x+side*.39,y+side*.72),(x+side*.73,y+side*.5)),fill=color)
    elif shape == 'marker':
        s = min(W,H); x=(W-s)/2; y=(H-s)/2
        d.ellipse((x+2,y+2,x+s-3,y+s-3), fill=color, outline=INK, width=max(2,round(s*.16)))
    elif shape.startswith('icon.'):
        name = shape[5:]
        if name not in ICON_NAMES: raise ValueError('Icono editorial desconocido.')
        from endcard import (_paint_cloud, _paint_calendar, _paint_bars,
                             _paint_thermometer, _paint_wind, _paint_index, _paint_pin)
        from maqueta import (draw_database_icon, draw_tiktok_icon,
                             draw_instagram_icon, draw_mountain_icon)
        diameter = min(W,H); cx=W/2; cy=H/2
        painters = dict(cloud=_paint_cloud, calendar=_paint_calendar, bars=_paint_bars,
                        thermometer=_paint_thermometer,wind=_paint_wind,index=_paint_index,pin=_paint_pin)
        if name in painters or name == 'peak':
            d.ellipse((cx-diameter*.49,cy-diameter*.49,cx+diameter*.49,cy+diameter*.49),fill='#173441')
            u=diameter/84
            p=lambda x,y:(cx+x*u,cy+y*u)
            if name == 'peak':
                d.line([p(-23,20),p(-23,-22)],fill=color,width=max(2,round(2*u)))
                d.line([p(-23,20),p(25,20)],fill=color,width=max(2,round(2*u)))
                d.line([p(-19,12),p(-6,-3),p(3,6),p(20,-22)],fill=BLUE,width=max(3,round(4*u)),joint='curve')
                d.polygon([p(10,-22),p(21,-23),p(22,-11)],fill=BLUE)
            else: painters[name](d,p,u)
        else:
            painters=dict(database=draw_database_icon,tiktok=draw_tiktok_icon,
                          instagram=draw_instagram_icon,mountain=draw_mountain_icon)
            # Legacy painters use their own reference sizes; trim ink and fit it.
            stamp=Image.new('RGBA',(300,300));painters[name](ImageDraw.Draw(stamp),50,50,color)
            bounds=stamp.getbbox()
            if bounds:
                ink=stamp.crop(bounds)
                ratio=min(W*.9/ink.width,H*.9/ink.height)
                ink=ink.resize((max(1,round(ink.width*ratio)),max(1,round(ink.height*ratio))),Image.Resampling.LANCZOS)
                image.alpha_composite(ink,((W-ink.width)//2,(H-ink.height)//2))
            stamp.close()
    else:
        raise ValueError('Gráfico editorial desconocido.')
    out=image.resize(size,Image.Resampling.LANCZOS);image.close()
    return out


def render_data(geometry, spec, size):
    """Style already-resolved values/rows, preserving order, units and absence."""
    w,h=size; style=spec.style
    image=Image.new('RGBA',size,(0,0,0,0));d=ImageDraw.Draw(image)
    white=style.get('text',WHITE); accent=style.get('color',MINT)
    presentation=style['presentation']
    if presentation == 'editorial_value':
        label=geometry['value_label']
        pixels=style.get('font_size',round(h*.65))
        font=fitted_font(label,pixels,w*.98,family=style.get('font_family',DISPLAY),bold=True)
        d.text((w/2,h/2),label,font=font,fill=accent,anchor='mm')
    elif presentation == 'editorial_metric':
        title=geometry['title']; value=geometry['value_label']
        titlefont=fitted_font(title,style.get('font_size',28),w*.90)
        d.text((w*.05,h*.10),title,font=titlefont,fill=MUTED,anchor='lt')
        font=fitted_font(value,round(h*.43),w*.90,family=DISPLAY,bold=True)
        d.text((w*.5,h*.56),value,font=font,fill=white,anchor='mm')
    else:
        marks=geometry['marks']; low=geometry['minimum']; high=geometry['maximum']
        left=w*.33; right=w*.84; top=h*.015; bottom=h*.84
        # Tick spacing is presentation-only. The common authored domain remains intact.
        span=high-low; magnitude=10**math.floor(math.log10(span/5)) if span else 1
        step=next((n*magnitude for n in (1,2,2.5,5,10) if n*magnitude >= span/5),magnitude*10)
        tick=math.ceil(low/step)*step; ticks=[]
        while tick<=high+step*1e-8 and len(ticks)<12:
            ticks.append(tick);tick+=step
        axis=lambda v:left+(v-low)/span*(right-left)
        zero=axis(0)
        for tick in ticks:
            x=axis(tick)
            for y in range(round(top),round(bottom),9):d.line((x,y,x,min(y+3,bottom)),fill='#163b4b',width=1)
        row_h=(bottom-top)/max(1,len(marks)); font_size=style.get('font_size',30)
        for index,mark in enumerate(marks):
            y=top+(index+.5)*row_h; badge_w=w*.042; badge_h=min(row_h*.87,36)
            d.rounded_rectangle((0,y-badge_h/2,badge_w,y+badge_h/2),radius=4,fill='#183342')
            number=str(spec.offset+index+1)
            font=fitted_font(number,min(font_size,row_h*.9),badge_w*.84,family=BODY,bold=True)
            d.text((badge_w/2,y),number,font=font,fill=white,anchor='mm')
            name=mark['name']
            display_name={'Santo Domingo de los Tsáchilas':'Santo Domingo','Zamora Chinchipe':'Zamora Chinchipe'}.get(name,name)
            font=fitted_font(display_name,min(font_size,row_h*1.06),left-w*.065,family=BODY,bold=True)
            d.text((w*.055,y),display_name,font=font,fill=white,anchor='lm')
            value=mark['value']; end=axis(value) if value is not None else zero
            if value is not None and value != 0:
                a,b=sorted((zero,end)); half=row_h*.34
                color=RANK_COLORS[min(index,11)] if spec.offset==0 else RANK_COLORS[min(index+5,11)]
                d.rounded_rectangle((a,y-half,b,y+half),radius=min(3,(b-a)/2),fill=color)
            label=mark['value_label']
            x=min(max(left,end)+w*.012,w*.96)
            font=fitted_font(label,min(font_size,row_h*1.06),w-x-2,family=BODY,bold=True)
            d.text((x,y),label,font=font,fill=white,anchor='lm')
        d.line((left,bottom,right,bottom),fill='#5d7a86',width=1)
        for tick in ticks:
            x=axis(tick); d.line((x,bottom,x,bottom+5),fill=MUTED,width=1)
            font=fitted_font(f'{tick:g}',min(font_size*.8,24),w*.10)
            d.text((x,bottom+9),f'{tick:g}',font=font,fill=MUTED,anchor='mt')
        title=geometry['title']
        font=fitted_font(title,min(font_size*.87,27),w*.88)
        d.text(((left+right)/2,h*.985),title,font=font,fill=MUTED,anchor='mb')
    image.info['visualization_geometry']=geometry
    return image
