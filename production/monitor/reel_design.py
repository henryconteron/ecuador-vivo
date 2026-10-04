"""Code-native science graphics for the Andes Pulso editorial Reel.

No generated photos, invented geological layers, or inferred fault geometry.
"""
import json
import math
from functools import lru_cache
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw

from export_video import WIDTH, HEIGHT, font, depth_color
from historical import magnitude_size

BG, PANEL, LINE = "#101f29", "#1b303c", "#35515b"
TEXT, MUTED, GOLD, TEAL = "#f6f0df", "#b9cbd0", "#f4c46b", "#65dfcd"
MAP = (90,360,930,1150)
SAFE_RIGHT = 930
CREDIT_NAME = "Henry Conteron"
CREDIT_SPECIALTY = "Ingeniero en geociencias e investigador independiente"
CREDIT = f"{CREDIT_NAME}, {CREDIT_SPECIALTY.lower()}"
DEPTH_BOX = (90,1300,930,1500)
MAG_BOX = (90,1516,930,1608)


def write(draw,xy,text,size=30,fill=TEXT,serif=False,right=SAFE_RIGHT):
    face=font(size,serif)
    if xy[0]+draw.textlength(text,font=face)>right:
        raise ValueError(f"Text exceeds safe content width: {text}")
    if xy[1]+face.getbbox(text)[3]>1705:
        raise ValueError(f"Text exceeds safe content height: {text}")
    draw.text(xy,text,font=face,fill=fill)


def panel(draw,box,accent=None):
    draw.rounded_rectangle(box,radius=22,fill=PANEL,outline=LINE,width=2)
    if accent:
        draw.rounded_rectangle((box[0],box[1]+18,box[0]+5,box[3]-18),radius=2,fill=accent)


def canvas(chapter):
    image=Image.new("RGB",(WIDTH,HEIGHT),BG)
    draw=ImageDraw.Draw(image)
    # Quiet editorial guide lines, not simulated seismic measurements.
    for y in range(120,1730,100):
        draw.line((70,y,955,y),fill="#142630")
    write(draw,(90,145),"ANDES PULSO",26,fill=GOLD)
    write(draw,(90,184),chapter,25,fill=MUTED)
    # Two lines keep the full professional credit legible inside the safe area.
    write(draw,(90,1621),CREDIT_NAME,28,fill=TEXT)
    write(draw,(90,1659),CREDIT_SPECIALTY,23,fill=MUTED)
    return image


def project(lon,lat):
    x0,y0,x1,y1=MAP
    return x0+(lon+83)/8.5*(x1-x0),y0+(2.5-lat)/8*(y1-y0)


@lru_cache(maxsize=1)
def land_map():
    x0,y0,x1,y1=MAP
    image=Image.new("RGB",(x1-x0,y1-y0),"#afc9cc")
    draw=ImageDraw.Draw(image)
    countries=json.loads((Path(__file__).parent/"assets"/"andes_countries.geojson").read_text(encoding="utf-8"))
    for feature in countries["features"]:
        points=[(project(x,y)[0]-x0,project(x,y)[1]-y0) for x,y in feature["geometry"]["coordinates"][0]]
        draw.polygon(points,fill="#d3d9ba" if feature["properties"]["name"]=="Ecuador" else "#e1dfc9",outline="#7b8b7b",width=2)
    return image


def depth_legend(draw,box=DEPTH_BOX):
    x0,y0,x1,y1=box
    panel(draw,box,TEAL)
    write(draw,(x0+24,y0+17),"COLOR → PROFUNDIDAD",27,fill=TEAL)
    write(draw,(x1-94,y0+20),"km",26,fill=MUTED)
    start,end=x0+40,x1-70
    for x in range(start,end+1):
        draw.line((x,y0+67,x,y0+93),fill=depth_color((x-start)/(end-start)*300))
    # Only four ticks: linear positions, legible gaps, no bunched early values.
    for depth,label in [(0,"0"),(70,"70"),(150,"150"),(300,"≥300")]:
        x=start+depth/300*(end-start)
        draw.line((x,y0+94,x,y0+101),fill=MUTED,width=2)
        draw.text((x-draw.textlength(label,font=font(27))/2,y0+108),label,font=font(27),fill=TEXT)
    cy=y0+170
    draw.polygon([(start,cy-7),(start+7,cy),(start,cy+7),(start-7,cy)],fill=depth_color(float("nan")))
    write(draw,(start+20,cy-17),"Gris: profundidad desconocida",25,fill=MUTED)


def magnitude_legend(draw,box=MAG_BOX):
    x0,y0,x1,y1=box
    panel(draw,box,GOLD)
    write(draw,(x0+24,y0+29),"TAMAÑO → MAGNITUD",25,fill=GOLD)
    for mag,x in [(4,520),(6,665),(8,810)]:
        r=magnitude_size(mag)*1.4/2
        draw.ellipse((x-r,y0+48-r,x+r,y0+48+r),fill=depth_color(30),outline=TEXT,width=1)
        write(draw,(x+30,y0+31),f"M{mag}",26)


def base_map(first,last,minimum):
    image=canvas("03 / EL ARCHIVO, AÑO A AÑO")
    draw=ImageDraw.Draw(image)
    write(draw,(90,228),"Ecuador bajo tus pies",56,serif=True)
    write(draw,(90,303),f"{first}–{last} · USGS · M ≥ {minimum:g}",29,fill=MUTED)
    image.paste(land_map(),MAP[:2])
    draw.rectangle(MAP,outline=TEAL,width=2)
    for lon in [-82,-80,-78,-76]:
        x,_=project(lon,0)
        draw.text((x-25,1158),f"{abs(lon)}° O",font=font(23),fill=MUTED)
    for lat in [-4,-2,0,2]:
        _,y=project(-83,lat)
        draw.text((32,y-12),f"{abs(lat)}°"+("S" if lat<0 else "N" if lat>0 else ""),font=font(22),fill=MUTED)
    depth_legend(draw)
    magnitude_legend(draw)
    return image


def lesson(year):
    if year<1950:
        return "Pocos registros ≠ pocos sismos."
    if year<1985:
        return "Círculo grande ≠ área de daños."
    if year<2001:
        return "Oscuro = profundo, no más peligroso."
    return "Más registros ≠ más peligro."


def render_map(base,selected,year):
    image=base.copy()
    layer=Image.new("RGBA",image.size,(0,0,0,0))
    draw=ImageDraw.Draw(layer)
    for row in selected.itertuples():
        x,y=project(row.longitude,row.latitude)
        r=magnitude_size(row.magnitude)*1.4/2
        color=depth_color(row.depth)+(210,)
        if pd.isna(row.depth):
            draw.polygon([(x,y-r),(x+r,y),(x,y+r),(x-r,y)],fill=color,outline="#502b2a")
        else:
            draw.ellipse((x-r,y-r,x+r,y+r),fill=color,outline=(80,43,42,180))
    crop=layer.crop(MAP)
    image.paste(crop,MAP[:2],crop)
    draw=ImageDraw.Draw(image)
    for label,lon,lat in [("ECUADOR",-78.8,-1.4),("COLOMBIA",-76.5,2),("PERÚ",-76.3,-4.8)]:
        x,y=project(lon,lat)
        draw.text((x,y),label,font=font(25),fill="#243a36",stroke_width=2,stroke_fill="#f6f0df")
    write(draw,(860,383),"N ↑",27,fill="#243a36")
    write(draw,(90,1193),str(year),48,fill=GOLD,serif=True)
    write(draw,(278,1198),f"{len(selected)} registros acumulados",29)
    write(draw,(90,1255),lesson(year),29,fill=TEAL)
    return image


def section_diagram(draw,box=(90,485,930,1195),origin_y=990):
    """Illustration only: no inferred strata, fault, or physical wavefront."""
    panel(draw,box,TEAL)
    write(draw,(115,511),"ESQUEMA · SIN ESCALA",24,fill=MUTED)
    draw.rectangle((130,665,890,1120),fill="#263d46")
    draw.line((130,665,890,665),fill=TEAL,width=5)
    write(draw,(160,598),"Epicentro: lo que ubica el mapa",31)
    draw.ellipse((447,652,473,678),fill=TEAL)
    for y in range(690,origin_y-20,26):
        draw.line((460,y,460,y+12),fill=MUTED,width=3)
    draw.line((600,685,600,origin_y-14),fill=GOLD,width=4)
    draw.polygon([(600,origin_y),(590,origin_y-18),(610,origin_y-18)],fill=GOLD)
    write(draw,(635,825),"Profundidad",28,fill=GOLD)
    write(draw,(635,863),"en km",28,fill=GOLD)
    draw.ellipse((434,origin_y-26,486,origin_y+26),fill=GOLD,outline=TEXT,width=2)
    write(draw,(165,1140),"Hipocentro: donde empieza la ruptura",29)


def intro_card(first,last,minimum,second=False):
    if second:
        return guide_card()
    image=canvas("01 / UNA PREGUNTA BAJO LA SUPERFICIE")
    draw=ImageDraw.Draw(image)
    write(draw,(90,250),"¿Dónde empieza",64,serif=True)
    write(draw,(90,333),"un terremoto?",64,fill=GOLD,serif=True)
    section_diagram(draw)
    panel(draw,(90,1230,930,1515),GOLD)
    write(draw,(118,1263),"Un punto no cuenta",45,serif=True)
    write(draw,(118,1323),"toda la historia.",45,serif=True)
    write(draw,(118,1410),f"Ecuador · {first}–{last} · M ≥ {minimum:g}",31,fill=MUTED)
    write(draw,(90,1550),"Entender para prepararnos, no para predecir.",29,fill=TEAL)
    return image


def purpose_card():
    image=canvas("02 / ANTES DE VIAJAR EN EL TIEMPO")
    draw=ImageDraw.Draw(image)
    write(draw,(90,250),"Un mapa. Tres pistas.",55,serif=True)
    items=[("01","POSICIÓN","¿Dónde ocurrió?","Cada punto ubica un epicentro.",450),
           ("02","TAMAÑO","¿Qué magnitud tuvo?","No es el tamaño de los daños.",770),
           ("03","COLOR","¿A qué profundidad?","No es un semáforo de peligro.",1090)]
    for number,label,title,detail,y in items:
        panel(draw,(90,y,930,y+280),TEAL)
        write(draw,(120,y+24),number,45,fill=TEAL,serif=True)
        write(draw,(215,y+34),label,27,fill=MUTED)
        write(draw,(120,y+104),title,39,serif=True)
        write(draw,(120,y+193),detail,30)
    write(draw,(90,1465),"Los puntos se acumulan: no son simultáneos.",30,fill=GOLD)
    write(draw,(90,1520),"Sin registros no significa sin sismos.",30,fill=MUTED)
    return image


def guide_card():
    image=canvas("02 / APRENDE A DESCIFRAR LOS PUNTOS")
    draw=ImageDraw.Draw(image)
    write(draw,(90,250),"Dos claves, sin confusión.",48,serif=True)
    depth_legend(draw,(90,420,930,620))
    panel(draw,(90,650,930,870),TEAL)
    for depth,x,label in [(20,145,"Claro: más superficial"),(200,145,"Oscuro: más profundo")]:
        y=695 if depth==20 else 794
        draw.ellipse((x-17,y-17,x+17,y+17),fill=depth_color(depth),outline=TEXT,width=2)
        write(draw,(190,y-22),label,34)
    panel(draw,(90,910,930,1320),GOLD)
    write(draw,(120,937),"TAMAÑO → MAGNITUD",30,fill=GOLD)
    for mag,x in [(4,250),(6,510),(8,770)]:
        r=magnitude_size(mag)*2.8/2
        draw.ellipse((x-r,1070-r,x+r,1070+r),fill=depth_color(30),outline=TEXT,width=2)
        write(draw,(x-28,1140),f"M{mag}",35)
    write(draw,(120,1210),"Mayor círculo = mayor magnitud",34)
    write(draw,(120,1260),"Ejemplos ampliados para explicar",25,fill=MUTED)
    panel(draw,(90,1360,930,1565),GOLD)
    write(draw,(120,1387),"OJO CON LA TRAMPA",27,fill=GOLD)
    write(draw,(120,1440),"Ni el color ni el tamaño dicen",33)
    write(draw,(120,1490),"cuánto daño hubo en tu ciudad.",33)
    return image


def depth_card():
    image=canvas("02 / LA OTRA DIMENSIÓN")
    draw=ImageDraw.Draw(image)
    write(draw,(90,250),"No todo pasa",60,serif=True)
    write(draw,(90,326),"cerca de la superficie.",54,fill=GOLD,serif=True)
    section_diagram(draw,(90,445,930,1195))
    for title,detail,color,y in [("SUPERFICIAL","0 a menos de 70 km",depth_color(20),1230),
                                 ("INTERMEDIO","70 a menos de 300 km",depth_color(150),1340),
                                 ("PROFUNDO","300 a unos 700 km",depth_color(300),1450)]:
        panel(draw,(90,y,930,y+94))
        draw.ellipse((115,y+32,141,y+58),fill=color,outline=TEXT,width=1)
        write(draw,(160,y+14),title,25,fill=MUTED)
        write(draw,(420,y+28),detail,30)
    write(draw,(90,1580),"Clasificación general · USGS",25,fill=MUTED)
    return image


def depth_counts(df):
    known=df.depth.dropna()
    return dict(shallow=int((known<70).sum()),intermediate=int(((known>=70)&(known<300)).sum()),
                deep=int((known>=300).sum()),unknown=int(df.depth.isna().sum()))


def profile_point(position,depth,limits,box):
    x0,y0,x1,y1=box
    return x0+(position-limits[0])/(limits[1]-limits[0])*(x1-x0),y0+depth/300*(y1-y0)


def profile_card(df):
    known=df[df.depth.notna()]
    if not known.depth.between(0,300).all():
        raise ValueError("Depth profiles need an extended axis for this catalog.")
    image=canvas("04 / CAMBIEMOS EL PUNTO DE VISTA")
    draw=ImageDraw.Draw(image)
    write(draw,(90,245),"Ahora míralos de lado.",53,serif=True)
    write(draw,(90,323),"Mismos registros · profundidad hacia abajo",29,fill=MUTED)
    for field,limits,box,title,ticks in [
        ("longitude",(-83,-74.5),(165,460,900,830),"OESTE → ESTE",[-82,-80,-78,-76]),
        ("latitude",(-5.5,2.5),(165,980,900,1350),"SUR → NORTE",[-4,-2,0,2])]:
        x0,y0,x1,y1=box
        write(draw,(90,y0-68),title,30,fill=TEAL)
        write(draw,(730,y0-65),"km ↓",26,fill=MUTED)
        draw.rectangle(box,fill="#243c46",outline=LINE,width=2)
        for depth in [0,70,150,300]:
            _,y=profile_point(limits[0],depth,limits,box)
            draw.line((x0,y,x1,y),fill=LINE,width=2)
            write(draw,(92,y-17),str(depth),25,fill=MUTED)
        for tick in ticks:
            x,_=profile_point(tick,0,limits,box)
            draw.line((x,y0,x,y1),fill=LINE,width=1)
            label=f"{abs(tick)}°"+(" O" if field=="longitude" else " S" if tick<0 else " N" if tick>0 else "")
            draw.text((x-28,y1+10),label,font=font(25),fill=MUTED)
        layer=Image.new("RGBA",image.size,(0,0,0,0))
        points=ImageDraw.Draw(layer)
        for row in known.itertuples():
            x,y=profile_point(getattr(row,field),row.depth,limits,box)
            r=magnitude_size(row.magnitude)*1.4/2
            points.ellipse((x-r,y-r,x+r,y+r),fill=depth_color(row.depth)+(210,),outline=(220,226,211,90))
        crop=layer.crop(box)
        image.paste(crop,box[:2],crop)
    counts=depth_counts(df)
    panel(draw,(90,1420,930,1595),GOLD)
    write(draw,(115,1438),f"Máximo de esta selección: {known.depth.max():g} km",34,fill=GOLD)
    write(draw,(115,1496),f"{counts['shallow']} superficiales · {counts['intermediate']} intermedios",28)
    write(draw,(115,1544),f"{counts['deep']} ≥300 km · {counts['unknown']} sin profundidad",26,fill=MUTED)
    return image


def action_card():
    image=canvas("05 / DE LA CURIOSIDAD A LA ACCIÓN")
    draw=ImageDraw.Draw(image)
    write(draw,(90,245),"El mapa no te prepara.",53,serif=True)
    write(draw,(90,324),"Tus decisiones, sí.",58,fill=GOLD,serif=True)
    for i,(heading,detail) in enumerate([("CONVERSA","Acuerden qué hacer en familia."),
                                         ("PRACTICA","Participen en simulacros."),
                                         ("PREPARA","Tengan un kit de emergencia.")]):
        y=480+i*315
        panel(draw,(90,y,930,y+275),TEAL)
        cx,cy=170,y+92
        if i==0:
            draw.rounded_rectangle((125,cy-31,205,cy+22),radius=10,outline=TEAL,width=4)
            draw.line((144,cy+22,136,cy+39,161,cy+22),fill=TEAL,width=4)
        elif i==1:
            draw.ellipse((146,cy-40,180,cy-6),outline=TEAL,width=4)
            draw.line((163,cy-6,163,cy+38),fill=TEAL,width=4)
            draw.line((128,cy+10,195,cy+10),fill=TEAL,width=4)
            draw.line((163,cy+38,140,cy+64),fill=TEAL,width=4)
            draw.line((163,cy+38,188,cy+64),fill=TEAL,width=4)
        else:
            draw.rounded_rectangle((130,cy-25,200,cy+46),radius=10,outline=TEAL,width=4)
            draw.arc((147,cy-48,183,cy-13),180,360,fill=TEAL,width=4)
            draw.line((152,cy+10,178,cy+10),fill=TEAL,width=4)
            draw.line((165,cy-3,165,cy+23),fill=TEAL,width=4)
        write(draw,(245,y+65),heading,37,fill=TEAL,serif=True)
        write(draw,(120,y+179),detail,32)
    write(draw,(90,1480),"Conciencia sísmica = información + acción",30,fill=GOLD)
    write(draw,(90,1540),"Guía de preparación: IG-EPN",27,fill=MUTED)
    return image


def closing_card(manifest,tagline=False):
    image=canvas("06 / LO QUE SÍ PODEMOS CONCLUIR")
    draw=ImageDraw.Draw(image)
    if tagline:
        write(draw,(90,240),"La tierra se mueve.",53,serif=True)
        write(draw,(90,310),"Prepararnos importa.",53,fill=GOLD,serif=True)
    else:
        write(draw,(90,250),"Entender, no adivinar.",55,fill=GOLD,serif=True)
    panel(draw,(90,395,930,645),TEAL)
    write(draw,(120,426),str(manifest["exported_count"]),76,serif=True)
    write(draw,(120,535),f"registros USGS · M ≥ {manifest['minimum']:g}",35)
    write(draw,(120,590),"1900–2025 · fechas UTC",28,fill=MUTED)
    for title,lines,y in [("EL ALCANCE",["Continente, océano y zonas vecinas.","Sin Galápagos; no sigue fronteras."],690),
                           ("LOS LÍMITES",["Archivo incompleto. Datos revisables.","Magnitudes originales, no todas Mw."],960),
                           ("LA IDEA QUE TE LLEVAS",["Leer el pasado sirve para aprender.","Este video no predice el próximo sismo."],1230)]:
        panel(draw,(90,y,930,y+230),TEAL)
        write(draw,(120,y+23),title,25,fill=TEAL)
        for j,line in enumerate(lines):
            write(draw,(120,y+81+j*54),line,31)
    write(draw,(90,1510),f"Descarga USGS: {manifest['downloaded_at_utc'][:10]}",26,fill=MUTED)
    write(draw,(90,1560),"Mapa: Natural Earth · fuentes en descripción",26,fill=MUTED)
    return image


def text_card(title,lines,footer=""):
    """Compatibility helper for independent proof cards."""
    image=canvas("ANDES PULSO / EXPLICACIÓN")
    draw=ImageDraw.Draw(image)
    write(draw,(90,250),title,54,serif=True)
    for i,line in enumerate(lines):
        y=440+i*170
        panel(draw,(90,y,930,y+140),TEAL)
        write(draw,(115,y+45),line,32)
    write(draw,(90,1545),footer,27,fill=MUTED)
    return image


def animate_card(image,kind,phase,overall):
    """Editorial motion only: no distortion of catalog coordinates or point sizes."""
    result=image.copy()
    draw=ImageDraw.Draw(result)
    if kind in ["intro","depth"]:
        # A focus highlight, not propagating physical waves.
        r=36+7*math.sin(phase*math.pi*4)
        draw.ellipse((460-r,990-r,460+r,990+r),outline=TEAL,width=3)
    if kind in ["purpose","action"]:
        boxes=[(90,450,930,730),(90,770,930,1050),(90,1090,930,1370)] if kind=="purpose" else [(90,480,930,755),(90,795,930,1070),(90,1110,930,1385)]
        draw.rounded_rectangle(boxes[min(2,int(phase*3))],radius=22,outline=TEAL,width=4)
    draw.line((90,1690,930,1690),fill=LINE,width=4)
    draw.line((90,1690,90+840*overall,1690),fill=GOLD,width=4)
    return result
