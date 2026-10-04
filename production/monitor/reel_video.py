"""Publication-ready educational Reel from an audited, reproducible snapshot."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw

from export_video import font, depth_color, WIDTH, HEIGHT
from historical import magnitude_size

PAPER, INK, OCEAN = "#eee9d9", "#314238", "#d6e3e1"
MAP = (90,430,930,1220)
FPS = 30
YEAR_FRAMES = 9
SAFE_RIGHT = 930


def project(lon,lat):
    x0,y0,x1,y1=MAP
    return x0+(lon+83)/8.5*(x1-x0),y0+(2.5-lat)/8*(y1-y0)


def write(draw,xy,text,size=30,fill=INK,serif=False):
    """Do not shrink important copy silently to fit a social-video canvas."""
    face=font(size,serif)
    if xy[0]+draw.textlength(text,font=face)>SAFE_RIGHT:
        raise ValueError(f"Text exceeds safe content width: {text}")
    draw.text(xy,text,font=face,fill=fill)


def base_map(first,last,minimum):
    image=Image.new("RGB",(WIDTH,HEIGHT),PAPER)
    draw=ImageDraw.Draw(image)
    write(draw,(90,156),"ANDES PULSO",26,fill="#9b643f")
    write(draw,(90,206),"Memoria sísmica",65,serif=True)
    write(draw,(90,284),"del Ecuador",65,serif=True)
    write(draw,(90,368),f"{first}–{last} · USGS · M ≥ {minimum:g}",30)
    x0,y0,x1,y1=MAP
    land=Image.new("RGB",(x1-x0,y1-y0),OCEAN)
    painter=ImageDraw.Draw(land)
    countries=json.loads((Path(__file__).parent/"assets"/"andes_countries.geojson").read_text(encoding="utf-8"))
    for feature in countries["features"]:
        points=[(project(x,y)[0]-x0,project(x,y)[1]-y0) for x,y in feature["geometry"]["coordinates"][0]]
        painter.polygon(points,fill="#ccd4b5" if feature["properties"]["name"]=="Ecuador" else "#e0e3ce",outline="#7f8c6d",width=2)
    image.paste(land,(x0,y0))
    for lon in [-82,-80,-78,-76]:
        x,_=project(lon,0)
        draw.text((x-24,y1+9),f"{abs(lon)}° O",font=font(23),fill=INK)
    for lat in [-4,-2,0,2]:
        _,y=project(-83,lat)
        draw.text((36,y-10),f"{abs(lat)}°"+("S" if lat<0 else "N" if lat>0 else ""),font=font(22),fill=INK)
    write(draw,(870,451),"N",30)
    draw.line((881,532,881,495),fill=INK,width=4)
    draw.polygon([(881,487),(872,505),(890,505)],fill=INK)
    write(draw,(90,1350),"COLOR = PROFUNDIDAD (km)",26)
    for x in range(450):
        draw.line((90+x,1390,90+x,1415),fill=depth_color(x/449*300))
    for depth,label in [(0,"0"),(30,"30"),(70,"70"),(120,"120"),(200,"200"),(300,"≥300")]:
        draw.text((90+depth/300*450-5,1425),label,font=font(24),fill=INK)
    write(draw,(620,1350),"TAMAÑO = MAGNITUD",24)
    for mag,x in [(4,657),(6,757),(8,857)]:
        radius=magnitude_size(mag)*1.4/2
        draw.ellipse((x-radius,1403-radius,x+radius,1403+radius),fill="#e9ba7c",outline="#502b2a",width=2)
        draw.text((x-19,1425),f"M{mag}",font=font(24),fill=INK)
    draw.polygon([(95,1475),(102,1482),(95,1489),(88,1482)],fill=depth_color(float("nan")))
    write(draw,(116,1465),"Diamante gris: profundidad desconocida",26)
    write(draw,(90,1592),"Datos: USGS · Mapa: Natural Earth",25)
    write(draw,(90,1630),"Henry · Geociencias, Universidad Ikiam",24)
    return image


def lesson(year):
    if year<1950:
        return "Archivo incompleto: pocos puntos ≠ pocos sismos."
    if year<1985:
        return "El tamaño indica magnitud, no un área de daños."
    if year<2001:
        return "El color indica profundidad, no nivel de peligro."
    return "Más registros no demuestra más peligro."


def render_map(base,selected,year):
    image=base.copy()
    layer=Image.new("RGBA",image.size,(0,0,0,0))
    draw=ImageDraw.Draw(layer)
    for row in selected.itertuples():
        x,y=project(row.longitude,row.latitude)
        radius=magnitude_size(row.magnitude)*1.4/2
        color=depth_color(row.depth)+(210,)
        if pd.isna(row.depth):
            draw.polygon([(x,y-radius),(x+radius,y),(x,y+radius),(x-radius,y)],fill=color,outline="#502b2a")
        else:
            draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill=color,outline=(80,43,42,190),width=1)
    cropped=layer.crop(MAP)
    image.paste(cropped,MAP[:2],cropped)
    draw=ImageDraw.Draw(image)
    for label,lon,lat in [("ECUADOR",-78.8,-1.4),("COLOMBIA",-76.5,2),("PERÚ",-76.3,-4.8)]:
        x,y=project(lon,lat)
        draw.text((x,y),label,font=font(25),fill=INK,stroke_width=2,stroke_fill=PAPER)
    write(draw,(90,1254),str(year),58,serif=True)
    write(draw,(298,1262),f"{len(selected)} registros acumulados",29)
    write(draw,(298,1300),"Puntos del pasado, no sismos en curso",26)
    write(draw,(90,1520),lesson(year),29)
    return image


def intro_card(first,last,minimum,second=False):
    image=Image.new("RGB",(WIDTH,HEIGHT),PAPER)
    draw=ImageDraw.Draw(image)
    write(draw,(90,170),"ANDES PULSO",28,fill="#9b643f")
    write(draw,(90,320),"La tierra se mueve.",62,serif=True)
    write(draw,(90,407),"Prepararnos importa.",56,serif=True)
    write(draw,(90,555),f"Ecuador · {first}–{last} · USGS · M ≥ {minimum:g}",31)
    if second:
        write(draw,(90,760),"Así se lee el mapa",48,serif=True)
        for mag,x in [(4,170),(6,290),(8,440)]:
            r=magnitude_size(mag)*2.8/2
            draw.ellipse((x-r,900-r,x+r,900+r),fill="#e9ba7c",outline=INK,width=2)
            draw.text((x-25,950),f"M{mag}",font=font(28),fill=INK)
        write(draw,(90,1030),"Círculo mayor = mayor magnitud",35)
        for x in range(700):
            draw.line((90+x,1150,90+x,1185),fill=depth_color(x/699*300))
        for depth,label in [(0,"0"),(30,"30"),(70,"70"),(120,"120"),(200,"200"),(300,"≥300 km")]:
            write(draw,(90+depth/300*700-5,1202),label,26)
        write(draw,(90,1300),"El color no indica peligro.",35)
    else:
        write(draw,(90,795),"La conciencia sísmica comienza",36)
        write(draw,(90,855),"con información, no con miedo.",36)
        write(draw,(90,1045),"Conocer el pasado nos recuerda",34)
        write(draw,(90,1105),"por qué debemos prepararnos.",34)
    write(draw,(90,1480),"Continente, océano y zonas vecinas.",31)
    write(draw,(90,1533),"No incluye Galápagos.",31)
    return image


def text_card(title,lines,footer=""):
    image=Image.new("RGB",(WIDTH,HEIGHT),PAPER)
    draw=ImageDraw.Draw(image)
    write(draw,(90,170),"ANDES PULSO",28,fill="#9b643f")
    write(draw,(90,350),title,54,serif=True)
    for i,line in enumerate(lines):
        write(draw,(90,690+i*85),line,35)
    write(draw,(90,1510),footer,28)
    return image


def depth_card():
    image=text_card("¿A qué profundidad?",[],"Esquema conceptual · no está a escala")
    draw=ImageDraw.Draw(image)
    write(draw,(90,495),"Es la distancia bajo la superficie",35)
    write(draw,(90,555),"hasta donde comienza la ruptura.",35)
    draw.rectangle((140,760,900,1110),fill="#e0d4bf")
    draw.line((140,760,900,760),fill=INK,width=5)
    draw.line((365,770,365,1000),fill="#9b643f",width=4)
    draw.ellipse((353,748,377,772),fill=INK)
    draw.ellipse((349,991,381,1023),fill=depth_color(70),outline=INK,width=3)
    draw.polygon([(365,993),(353,975),(377,975)],fill="#9b643f")
    write(draw,(410,722),"Epicentro: en superficie",28)
    write(draw,(410,870),"Profundidad (km)",30)
    write(draw,(410,985),"Hipocentro: origen",30)
    write(draw,(90,1190),"Superficial: 0 a menos de 70 km",32)
    write(draw,(90,1250),"Intermedio: 70 a menos de 300 km",32)
    write(draw,(90,1310),"Profundo: 300 a unos 700 km",32)
    write(draw,(90,1410),"Más profundo no significa más peligro.",32)
    return image


def depth_counts(df):
    known=df.depth.dropna()
    return dict(shallow=int((known<70).sum()),intermediate=int(((known>=70)&(known<300)).sum()),
                deep=int((known>=300).sum()),unknown=int(df.depth.isna().sum()))


def profile_point(position,depth,limits,box):
    x0,y0,x1,y1=box
    return x0+(position-limits[0])/(limits[1]-limits[0])*(x1-x0),y0+depth/300*(y1-y0)


def profile_card(df):
    """Whole-window orthographic projections, NOT a fault/plate cross-section."""
    known=df[df.depth.notna()]
    if not known.depth.between(0,300).all():
        raise ValueError("Depth profiles use a fixed 0–300 km axis; extend it before exporting this catalog.")
    image=text_card("También bajo tus pies",[],"Vista regional · no es una sección de falla")
    draw=ImageDraw.Draw(image)
    write(draw,(90,440),"Los mismos registros, vistos de lado.",34)
    for field,limits,box,title,ticks in [
        ("longitude",(-83,-74.5),(150,575,900,860),"OESTE → ESTE · longitud",[-82,-80,-78,-76]),
        ("latitude",(-5.5,2.5),(150,1060,900,1345),"SUR → NORTE · latitud",[-4,-2,0,2])]:
        x0,y0,x1,y1=box
        write(draw,(90,y0-86),title,30)
        write(draw,(90,y0-42),"Profundidad (km) ↓",26)
        draw.rectangle(box,fill="#e2e1d3",outline="#8e9b8e",width=2)
        for depth in [0,70,150,300]:
            _,y=profile_point(limits[0],depth,limits,box)
            draw.line((x0,y,x1,y),fill="#a5ada0",width=2)
            draw.text((92,y-15),str(depth),font=font(25),fill=INK)
        for tick in ticks:
            x,_=profile_point(tick,0,limits,box)
            draw.line((x,y0,x,y1),fill="#c4c9bb",width=1)
            label=f"{abs(tick)}°"+(" O" if field=="longitude" else " S" if tick<0 else " N" if tick>0 else "")
            draw.text((x-25,y1+10),label,font=font(25),fill=INK)
        layer=Image.new("RGBA",image.size,(0,0,0,0))
        points=ImageDraw.Draw(layer)
        for row in known.itertuples():
            x,y=profile_point(getattr(row,field),row.depth,limits,box)
            r=magnitude_size(row.magnitude)*1.4/2
            points.ellipse((x-r,y-r,x+r,y+r),fill=depth_color(row.depth)+(190,),outline=(80,43,42,150))
        cropped=layer.crop(box)
        image.paste(cropped,box[:2],cropped)
    counts=depth_counts(df)
    write(draw,(90,1430),f"{counts['shallow']} superficiales · {counts['intermediate']} intermedios",30)
    write(draw,(90,1475),f"{counts['deep']} ≥300 km · {counts['unknown']} sin profundidad (no graficado)",27)
    write(draw,(90,1580),f"Máximo registrado: {known.depth.max():g} km · USGS",28)
    return image


def closing_card(manifest):
    image=Image.new("RGB",(WIDTH,HEIGHT),INK)
    draw=ImageDraw.Draw(image)
    write(draw,(90,175),"ANDES PULSO",28,fill="#f0c262")
    write(draw,(90,340),"Leer el pasado.",68,fill=PAPER,serif=True)
    write(draw,(90,425),"No predecir el futuro.",56,fill=PAPER,serif=True)
    write(draw,(90,635),f"{manifest['exported_count']} registros · M ≥ {manifest['minimum']:g}",40,fill=PAPER)
    lines=["Ecuador continental, océano y zonas vecinas.","La selección no sigue fronteras políticas.",
           "El archivo histórico es incompleto.","Las redes de observación cambian.",
           "Los datos son estimaciones revisables.","Tipos de magnitud sin homogeneizar a Mw."]
    for i,line in enumerate(lines):
        write(draw,(90,770+i*76),line,32,fill=PAPER)
    write(draw,(90,1290),"Tamaño y color no describen daño local.",34,fill="#f0c262")
    write(draw,(90,1430),"Fuente de los puntos: USGS FDSN",28,fill=PAPER)
    write(draw,(90,1477),f"Descarga: {manifest['downloaded_at_utc'][:10]} · años UTC",28,fill=PAPER)
    write(draw,(90,1550),"Henry · Geociencias, Universidad Ikiam",27,fill=PAPER)
    write(draw,(90,1600),"Made with Natural Earth · fuentes en descripción",25,fill=PAPER)
    return image


def timeline(first,last):
    """Durations are exact frame counts, keeping titles readable at 30 FPS."""
    return [("intro",None,7*FPS),("purpose",None,7*FPS),("guide",None,6*FPS),("depth",None,10*FPS)]+[("year",year,YEAR_FRAMES) for year in range(first,last+1)]+[("hold",last,3*FPS),("profile",None,10*FPS),("action",None,6*FPS),("end",None,12*FPS)]


def export_reel(folder):
    import imageio_ffmpeg
    folder=Path(folder)
    manifest=json.loads((folder/"manifest.json").read_text(encoding="utf-8"))
    csv=(folder/"catalog.csv").read_bytes()
    if sha256(csv).hexdigest()!=manifest["csv_sha256"] or not all(manifest["checks"].values()):
        raise ValueError("Catalog does not match the audited snapshot.")
    df=pd.read_csv(folder/"catalog.csv")
    df.time=pd.to_datetime(df.time,utc=True,format="ISO8601")
    if len(df)!=manifest["exported_count"]:
        raise ValueError("Record count mismatch.")
    first,last,minimum=(manifest[k] for k in ["first","last","minimum"])
    base=base_map(first,last,minimum)
    output=folder/"andes_pulso_reel_1900_2025.mp4"
    writer=imageio_ffmpeg.write_frames(str(output),(WIDTH,HEIGHT),fps=FPS,codec="libx264",pix_fmt_in="rgb24",pix_fmt_out="yuv420p",
              quality=8,macro_block_size=2,output_params=["-movflags","+faststart","-profile:v","high","-level","4.1"],ffmpeg_log_level="error")
    writer.send(None)
    frames=0
    scenes=[]
    try:
        for kind,year,repeat in timeline(first,last):
            if kind in ["intro","guide"]:
                image=intro_card(first,last,minimum,second=kind=="guide")
            elif kind=="purpose":
                image=text_card("Mirar para comprender",["Cada punto es un sismo registrado.","Viajaremos por el archivo, año a año.","Los puntos anteriores permanecen:","no están ocurriendo a la vez.","Esto no predice el próximo sismo."],"Memoria sísmica ≠ pronóstico")
            elif kind=="depth":
                image=depth_card()
            elif kind=="profile":
                image=profile_card(df)
            elif kind=="action":
                image=text_card("Conocer. Prepararse.",["Habla con tu familia.","Practiquen simulacros.","Preparen su kit de emergencia.","Consulten información del IG-EPN."],"Conciencia sísmica: llevar lo aprendido a la acción")
            elif kind=="end":
                image=closing_card(manifest)
            else:
                image=render_map(base,df[df.time.dt.year<=year],year)
            if kind=="intro":
                image.save(folder/"portada.jpg",quality=95)
            if kind!="year" or year in [1900,1906,1960,2016,2025]:
                image.save(folder/f"qa_{kind}_{year or 0}.jpg",quality=92)
            scenes.append(dict(kind=kind,year=year,start_frame=frames,frames=repeat))
            raw=image.tobytes()
            for _ in range(repeat):
                writer.send(raw)
            frames+=repeat
            if year and year%25==0:
                print(f"Rendered through {year}",flush=True)
    finally:
        writer.close()
    metadata=dict(width=WIDTH,height=HEIGHT,fps=FPS,frames=frames,duration_seconds=frames/FPS,codec="H.264",pixel_format="yuv420p",audio="none",
                  video_sha256=sha256(output.read_bytes()).hexdigest(),csv_sha256=manifest["csv_sha256"],scenes=scenes,
                  depth_counts=depth_counts(df),depth_max_km=float(df.depth.max()))
    (folder/"video_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in metadata.items() if k!="scenes"},indent=2),flush=True)
    return output


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder",type=Path)
    print(export_reel(parser.parse_args().folder))
