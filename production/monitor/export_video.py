"""Render the downloaded historical CSV to a vertical, silent MP4.

Optional dependency: pip install -r requirements-video.txt
Example: python export_video.py artifacts/catalog.csv --output artifacts/ecuador.mp4
"""
import argparse
from datetime import datetime, timezone
import json
from functools import lru_cache
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from historical import DEPTH_SCALE, magnitude_size

WIDTH, HEIGHT = 1080, 1920
PAPER, INK, OCEAN = "#eee9d9", "#314238", "#d6e3e1"
MAP = (60, 340, 1020, 1244)


@lru_cache(maxsize=32)
def font(size, serif=False):
    windows = Path("C:/Windows/Fonts")
    candidates = [windows / ("georgiab.ttf" if serif else "arial.ttf"),
                  Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path),size)
    return ImageFont.load_default(size=size)


def project(lon, lat):
    x0,y0,x1,y1 = MAP
    return x0+(lon+83)/8.5*(x1-x0), y0+(2.5-lat)/8*(y1-y0)


def depth_color(depth):
    if pd.isna(depth):
        return (136,147,146)
    value = min(1,max(0,float(depth)/300))
    for (lo,a),(hi,b) in zip(DEPTH_SCALE,DEPTH_SCALE[1:]):
        if lo <= value <= hi:
            fraction = (value-lo)/(hi-lo)
            rgb_a = tuple(int(a[i:i+2],16) for i in (1,3,5))
            rgb_b = tuple(int(b[i:i+2],16) for i in (1,3,5))
            return tuple(round(x+(y-x)*fraction) for x,y in zip(rgb_a,rgb_b))
    return (32,27,42)


def basemap():
    image=Image.new("RGB",(WIDTH,HEIGHT),PAPER)
    draw=ImageDraw.Draw(image)
    draw.text((60,55),"ANDES PULSO / ATLAS 01",font=font(25),fill="#9b643f")
    draw.text((60,105),"Memoria sísmica",font=font(74,True),fill=INK)
    draw.text((60,194),"del Ecuador.",font=font(74,True),fill=INK)
    draw.text((60,288),"CONTINENTE · MARGEN OCEÁNICO · ANDES",font=font(25),fill=INK)
    # Paint countries on a separate map surface; mask naturally clips surrounding polygons.
    x0,y0,x1,y1=MAP
    land=Image.new("RGB",(x1-x0,y1-y0),OCEAN)
    land_draw=ImageDraw.Draw(land)
    countries=json.loads((Path(__file__).parent/"assets"/"andes_countries.geojson").read_text(encoding="utf-8"))
    for feature in countries["features"]:
        points=[(project(x,y)[0]-x0,project(x,y)[1]-y0) for x,y in feature["geometry"]["coordinates"][0]]
        land_draw.polygon(points,fill="#ccd4b5" if feature["properties"]["name"]=="Ecuador" else "#e0e3ce",
                          outline="#7f8c6d",width=2)
    image.paste(land,(x0,y0))
    draw=ImageDraw.Draw(image)
    for lon in [-82,-80,-78,-76]:
        x,_=project(lon,0)
        draw.text((x-25,y1+12),f"{abs(lon)}° O",font=font(20),fill=INK)
    for lat in [-4,-2,0,2]:
        _,y=project(-83,lat)
        draw.text((5,y),f"{abs(lat)}°"+("S" if lat<0 else "N" if lat>0 else ""),font=font(17),fill=INK)
    draw.text((MAP[2]-50,MAP[1]+28),"N",font=font(30),fill=INK)
    draw.line((MAP[2]-40,MAP[1]+100,MAP[2]-40,MAP[1]+70),fill=INK,width=4)
    draw.polygon([(MAP[2]-40,MAP[1]+62),(MAP[2]-48,MAP[1]+77),(MAP[2]-32,MAP[1]+77)],fill=INK)
    draw.text((70,1350),"PROFUNDIDAD / km",font=font(24),fill=INK)
    for x in range(600):
        draw.line((70+x,1396,70+x,1418),fill=depth_color(x/599*300))
    for depth in [0,20,70,120,200,300]:
        x=70+depth/300*600
        draw.text((x-8,1430),"≥300" if depth==300 else str(depth),font=font(19),fill=INK)
    draw.text((735,1350),"MAGNITUD",font=font(24),fill=INK)
    for mag,x in [(4,766),(6,855),(8,947)]:
        radius=magnitude_size(mag)*1.4/2
        draw.ellipse((x-radius,1407-radius,x+radius,1407+radius),fill="#e9ba7c",outline="#502b2a",width=2)
        draw.text((x-20,1430),f"M{mag}",font=font(22),fill=INK)
    return image


def render_frame(base, selected, year, first, last, minimum, cutoff):
    image=base.copy()
    layer=Image.new("RGBA",image.size,(0,0,0,0))
    draw=ImageDraw.Draw(layer)
    x0,y0,x1,y1=MAP
    for row in selected.itertuples():
        x,y=project(row.longitude,row.latitude)
        if not x0 <= x <= x1 or not y0 <= y <= y1:
            continue
        radius=magnitude_size(row.magnitude)*1.4/2
        color=depth_color(row.depth)+(205,)
        if pd.isna(row.depth):
            draw.polygon([(x,y-radius),(x+radius,y),(x,y+radius),(x-radius,y)],fill=color,outline="#502b2a")
        else:
            draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill=color,outline=(80,43,42,190),width=1)
    # Mask symbol edges to the exact map rectangle as well.
    image.paste(layer.crop(MAP),MAP[:2],layer.crop(MAP))
    draw=ImageDraw.Draw(image)
    for label,lon,lat in [("ECUADOR",-78.8,-1.4),("COLOMBIA",-76.5,2),("PERÚ",-76.3,-4.8)]:
        x,y=project(lon,lat)
        draw.text((x,y),label,font=font(24),fill=INK,stroke_width=2,stroke_fill=PAPER)
    for label,lon,lat in [("Quito",-78.4678,-.1807),("Guayaquil",-79.8891,-2.1709),("Cuenca",-79.0045,-2.9001)]:
        x,y=project(lon,lat)
        draw.ellipse((x-3,y-3,x+3,y+3),fill=INK)
        draw.text((x+7,y+2),label,font=font(18),fill=INK,stroke_width=1,stroke_fill=PAPER)
    draw.text((70,1280),f"{year}",font=font(54,True),fill=INK)
    draw.text((270,1302),f"{len(selected):,} sismos catalogados · acumulado",font=font(30),fill=INK)
    draw.text((70,1502),f"Consulta {first}–{last} · M ≥ {minimum:g} · Fuente: USGS",font=font(27),fill=INK)
    draw.text((70,1545),f"Corte UTC: {cutoff}",font=font(23),fill=INK)
    progress=(year-first)/(last-first) if last>first else 1
    draw.rectangle((70,1612,1010,1620),fill="#ced1b9")
    draw.rectangle((70,1612,70+940*progress,1620),fill="#c95434")
    notes=["Archivo histórico incompleto. Años vacíos ≠ ausencia de sismos.",
           "Incluye países vecinos y océano; no incluye Galápagos.",
           "Magnitudes no homogeneizadas a Mw. Último año parcial.",
           "Los conteos no prueban tendencias físicas. No predice sismos.",
           "Profundidad ≥300 km: color final. Diamantes grises: N/D."]
    for i,line in enumerate(notes):
        draw.text((70,1655+i*32),line,font=font(22),fill="#53634f")
    draw.text((70,1835),"Henry · Geociencias, Ikiam / Made with Natural Earth",font=font(23),fill=INK)
    return image


def load_catalog(csv, first, last, minimum):
    df=pd.read_csv(csv)
    # USGS timestamps mix whole seconds and fractional seconds in the same export.
    df["time"]=pd.to_datetime(df["time"],utc=True,format="ISO8601")
    return df[(df.time.dt.year>=first)&(df.time.dt.year<=last)&(df.magnitude>=minimum)]


def export_video(csv, output, first=1900, last=None, minimum=4, cutoff=None):
    import imageio_ffmpeg
    last=last or datetime.now(timezone.utc).year
    cutoff=cutoff or "no informado / not supplied"
    if not 1900 <= first <= last <= datetime.now(timezone.utc).year:
        raise ValueError("El período debe estar entre 1900 y el año actual.")
    df=load_catalog(csv,first,last,minimum)
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    fps=10
    writer=imageio_ffmpeg.write_frames(str(output),(WIDTH,HEIGHT),fps=fps,codec="libx264",
                                      pix_fmt_in="rgb24",pix_fmt_out="yuv420p",quality=8,macro_block_size=2,
                                      output_params=["-movflags","+faststart"],ffmpeg_log_level="error")
    writer.send(None)
    base=basemap()
    try:
        for year in range(first,last+1):
            selected=df[df.time.dt.year<=year]
            raw=render_frame(base,selected,year,first,last,minimum,cutoff).tobytes()
            # Each year is 0.4s; hold the opening and closing states longer.
            for _ in range(20 if year==first else 30 if year==last else 4):
                writer.send(raw)
    finally:
        writer.close()
    return output


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv",type=Path)
    parser.add_argument("--output",type=Path,default=Path("artifacts/andes_pulso_ecuador.mp4"))
    parser.add_argument("--first",type=int,default=1900)
    parser.add_argument("--last",type=int,default=datetime.now(timezone.utc).year)
    parser.add_argument("--minimum",type=float,default=4)
    parser.add_argument("--cutoff",help="Original catalog UTC cutoff, printed in the video")
    args=parser.parse_args()
    print(export_video(args.csv,args.output,args.first,args.last,args.minimum,args.cutoff))
