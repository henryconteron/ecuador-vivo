"""Reflow for vertical social video. Insets are editorial guides, not platform guarantees."""
import copy
import datetime as dt
import io

import numpy as np
from PIL import Image, ImageDraw, ImageColor

from data import map_dimensions
from render import font, colorize, CITIES

LAYOUTS = {'social': (80, 220, 880, 1480), 'conservative': (80, 280, 880, 1240)}


def lines_for(text, size, width, max_lines, field, bold=False):
    """Never silently truncate or make long copy microscopic."""
    if not text.strip():
        return []
    lines = []
    for word in text.split():
        if font(size, bold).getlength(word) > width:
            raise ValueError(f'{field}: hay una palabra demasiado larga. Acórtala para el formato móvil.')
        if lines and font(size, bold).getlength(lines[-1] + ' ' + word) <= width:
            lines[-1] += ' ' + word
        else:
            lines.append(word)
    if len(lines) > max_lines:
        raise ValueError(f'{field}: acorta el texto a {max_lines} líneas para que sea legible en el teléfono.')
    return lines


def compose_social(p, values, boundary, date, index, count):
    from render import compose
    left, top, right, bottom = LAYOUTS[p['layout']]
    width = right-left
    frame = Image.new('RGB', (1080,1920), p['background'])
    d = ImageDraw.Draw(frame)
    light = sum(ImageColor.getrgb(p['background'])) > 440
    secondary = '#354c58' if light else '#c4d4da'
    boxes = []

    def block(text, y, size, field, bold=False, color=None, max_lines=2):
        for line in lines_for(text, size, width, max_lines, field, bold):
            box = d.textbbox((left,y), line, font=font(size,bold), anchor='lt')
            if box[2] > right or box[3] > bottom:
                raise ValueError(f'{field}: no cabe en el área protegida. Acorta los textos.')
            d.text((left,y),line,font=font(size,bold),fill=color or p['text'],anchor='lt')
            boxes.append(box)
            y += size+7
        return y

    y = block(p['brand'], top, 30, 'Marca', True, p['accent'], 1) + 10
    y = block(p['title'], y, 64, 'Título', True) + 12
    y = block(p['description'], y, 34, 'Descripción', color=secondary) + 12
    day = dt.date.fromisoformat(date)
    fmt = {'DD / MM / AAAA':'%d / %m / %Y', 'AAAA-MM-DD':'%Y-%m-%d','MM / DD / AAAA':'%m / %d / %Y'}[p['date_format']]
    date_label = day.strftime('%m / %Y' if p['cadence']=='Mensual' else '%Y' if p['cadence']=='Anual' else fmt)
    prefix = p['counter_label'] or {'Diaria':'DÍA','Mensual':'MES','Anual':'AÑO','Por observación':'OBS.'}[p['cadence']]
    counter = f'{prefix} {index+1:02} / {count:02}'
    if font(28).getlength(counter) > 360:
        raise ValueError('Acorta la palabra del contador para que no choque con la fecha.')
    d.text((left,y),date_label,font=font(34,True),fill=p['text'],anchor='lt')
    d.text((right,y+3),counter,font=font(28),fill=secondary,anchor='rt')
    map_top = y+50

    # Reserve space for all sources and personal credits BEFORE sizing the map.
    notes = [('Escala',p['scale_note']) ,('Resolución',p['resolution_note']),('Nota',p['note'])] if p['kind']=='continuous' else [('Categorías',p['category_note'])]
    caption = p['boundary_note'] or ('Ecuador continental' if p['clip_ecuador'] else 'Ventana geográfica') + ' · límites: geoBoundaries'
    footers = [('Fuente',p['citation'],False),('Límites',caption,False),('Autoría',p['author'],True),('Créditos',p['credits'],False)]
    footer_height = sum(len(lines_for(text,28,width,2,label,bold))*35 for label,text,bold in footers) + 16
    notes_height = sum(len(lines_for(text,28,width,2,label))*35 for label,text in notes) + 8
    legend = p['legend'] + (f' · {p["units"]}' if p['units'] else '')
    legend_height = len(lines_for(legend,30,width,2,'Leyenda',True))*37
    key_height = 68 if p['kind']=='continuous' else ((len(p['classes'])+1)//2)*38
    legend_top = bottom-footer_height-notes_height-legend_height-key_height-16
    map_bottom = legend_top-16
    available = map_bottom-map_top
    if available < 300:
        raise ValueError('Demasiado texto para el formato móvil: acorta las notas/créditos o usa Redes sociales en vez de Márgenes amplios. No se recortó contenido.')

    # Reuse the exact data/polygon drawing, not a screenshot or a different color scale.
    base = copy.deepcopy(p)
    base.update(layout='original',width=1080,cities=[])
    original = compose(base,values,boundary,date,index,count)
    mw,mh = map_dimensions(p['bbox'])
    mx,my = 60+(960-mw)//2,360+(1034-mh)//2
    factor = min(width/mw,available/mh)
    dw,dh = max(1,int(mw*factor)),max(1,int(mh*factor))
    dx,dy = left+(width-dw)//2,map_top+(available-dh)//2
    resampling = Image.Resampling.NEAREST if p['kind']=='categorical' else Image.Resampling.LANCZOS
    frame.paste(original.crop((mx,my,mx+mw,my+mh)).resize((dw,dh),resampling),(dx,dy))
    box = p['bbox']
    placed = []
    for name,lon,lat,_,_ in CITIES:
        if name not in p['cities'] or not (box[0]<=lon<=box[2] and box[1]<=lat<=box[3]):
            continue
        x,y = dx+(lon-box[0])/(box[2]-box[0])*dw,dy+(box[3]-lat)/(box[3]-box[1])*dh
        d.ellipse((x-4,y-4,x+4,y+4),fill='white')
        label = p['city_labels'].get(name,name)
        if not label:
            continue
        lines_for(label,28,width,1,'Etiqueta de ciudad',True)
        tw = font(28,True).getlength(label)
        tx = min(max(left+3,x+10),right-tw-3)
        ty = min(max(map_top+3,y-32),map_bottom-34)
        rect = (tx-3,ty-3,tx+tw+3,ty+31)
        while any(rect[0]<b[2] and rect[2]>b[0] and rect[1]<b[3] and rect[3]>b[1] for b in placed):
            ty += 35
            if ty+31>map_bottom:
                raise ValueError('Las etiquetas de ciudades se superponen: desactiva alguna o cambia el encuadre.')
            rect=(tx-3,ty-3,tx+tw+3,ty+31)
        placed.append(rect)
        d.text((tx,ty),label,font=font(28,True),fill='white',stroke_width=2,stroke_fill='#10212c',anchor='lt')

    y = block(legend,legend_top,30,'Leyenda',True)
    if p['kind']=='continuous':
        # Inset endpoints so the first/last numerical label never crosses the margin.
        stops=p['stops']; start=left+32; length=width-64
        gradient=np.interp(np.linspace(0,len(stops)-1,length),np.arange(len(stops)),stops)
        frame.paste(Image.fromarray(colorize(gradient[None,:],p)).resize((length,22)),(start,y))
        for j,val in enumerate(stops):
            label=f'{val:g}'+('+' if j==len(stops)-1 else '')
            text_width=font(26).getlength(label)
            if text_width > min(64,length/(len(stops)-1)-8):
                raise ValueError('Los valores de la escala son demasiado largos para el teléfono. Usa menos decimales o menos intervalos.')
            d.text((start+j*length/(len(stops)-1),y+30),label,font=font(26),fill=secondary,anchor='mt')
        y += 68
    else:
        for i,row in enumerate(p['classes']):
            x=left+(i%2)*400; yy=y+(i//2)*38
            lines_for(row['label'],26,350,1,'Nombre de categoría')
            d.rectangle((x,yy,x+22,yy+22),fill=row['color'])
            d.text((x+32,yy),row['label'],font=font(26),fill=p['text'],anchor='lt')
        y += key_height
    for label,text in notes:
        y=block(text,y,28,label,color=secondary)
    y+=8
    d.line((left,y,right,y),fill=secondary,width=1)
    y+=16
    for label,text,bold in footers:
        y=block(text,y,28,label,bold,color=p['text'] if bold else secondary)
    frame.info['safe_text_boxes']=boxes
    if p['width'] != 1080:
        frame=frame.resize((p['width'],p['width']*16//9),Image.Resampling.LANCZOS)
    return frame


def guided_preview(png, layout):
    """Guide is ONLY a preview. Export never calls this function."""
    image=Image.open(io.BytesIO(png)).convert('RGBA')
    scale=image.width/1080
    left,top,right,bottom=LAYOUTS.get(layout,LAYOUTS['social'])
    left,top,right,bottom=[round(n*scale) for n in (left,top,right,bottom)]
    overlay=Image.new('RGBA',image.size)
    d=ImageDraw.Draw(overlay)
    for rect in [(0,0,image.width,top),(0,bottom,image.width,image.height),(0,top,left,bottom),(right,top,image.width,bottom)]:
        d.rectangle(rect,fill=(210,50,65,65))
    d.rectangle((left,top,right,bottom),outline=(100,255,195,255),width=2)
    d.text((left,round(80*scale)),'GUÍA ORIENTATIVA · NO SE EXPORTA',font=font(max(12,round(28*scale)),True),fill='white')
    return Image.alpha_composite(image,overlay).convert('RGB')
