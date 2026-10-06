"""Render real daily CHIRPS data as a vertical, dated video. No temporal morphing.

Usage: python production/monitor/render_daily_rain.py --days 7
Outputs and cached public inputs stay in _local/climate-studio, outside Git.
"""
import argparse
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import urllib.request

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from rasterio.io import MemoryFile
from rasterio.windows import from_bounds

ROOT = Path(__file__).resolve().parents[2]
BOX = (-81.5, -5.2, -75.0, 1.8)
COLORS = ['102b36', '185069', '207ea1', '38b9bc', '8adab0', 'f5df80', 'f39a55', 'b74362']
STOPS = np.array([0, 1, 5, 10, 20, 40, 70, 120], dtype=float)

def fetch(url, target):
    if not target.exists():
        with urllib.request.urlopen(url, timeout=120) as response:
            payload = response.read()
        target.write_bytes(payload)
    return target.read_bytes()

def font(size, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/' + ('segoeuib.ttf' if bold else 'segoeui.ttf'), size)

def colorize(values):
    rgb = np.array([tuple(bytes.fromhex(c)) for c in COLORS])
    return np.stack([np.interp(values, STOPS, rgb[:, i]) for i in range(3)], axis=-1).astype('uint8')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', default='2024-01-01')
    parser.add_argument('--days', type=int, default=7)
    args = parser.parse_args()
    if not 1 <= args.days <= 366:
        parser.error('days must be 1..366')
    start = dt.date.fromisoformat(args.start)
    out = ROOT / '_local' / 'climate-studio' / f'{start}-{args.days}days'
    out.mkdir(parents=True, exist_ok=True)
    boundary_url = 'https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/ECU/ADM0/geoBoundaries-ECU-ADM0.geojson'
    boundary = json.loads(fetch(boundary_url, out / 'ecuador.geojson'))
    map_x, map_y, map_w, map_h = 60, 360, 960, 1034
    def xy(lon, lat):
        return ((lon-BOX[0])/(BOX[2]-BOX[0])*map_w, (BOX[3]-lat)/(BOX[3]-BOX[1])*map_h)
    mask = Image.new('L', (map_w, map_h))
    md = ImageDraw.Draw(mask)
    rings = []
    for feature in boundary['features']:
        g = feature['geometry']
        polygons = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        for polygon in polygons:
            for i, ring in enumerate(polygon):
                points = [xy(*p[:2]) for p in ring]
                md.polygon(points, fill=255 if i == 0 else 0)
                rings.append(points)
    receipt = {'source': 'CHIRPS v2 daily', 'units': 'mm/day', 'native_grid_degrees': .05,
               'bbox': BOX, 'display': 'bilinear interpolation of values with normalized valid-data weights',
               'temporal_interpolation': False, 'legend_stops_mm': STOPS.tolist(),
               'boundary_url': boundary_url, 'frames': []}
    video = out / 'ecuador-lluvia-diaria-preview.mp4'
    writer = imageio_ffmpeg.write_frames(str(video), (1080, 1920), fps=30, codec='libx264',
        pix_fmt_in='rgb24', pix_fmt_out='yuv420p', macro_block_size=1,
        output_params=['-crf', '18', '-preset', 'fast', '-movflags', '+faststart'])
    writer.send(None)
    try:
        for i in range(args.days):
            date = start + dt.timedelta(days=i)
            filename = f'chirps-v2.0.{date:%Y.%m.%d}.tif.gz'
            url = f'https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/{date.year}/{filename}'
            print('Loading', date, flush=True)
            raw = fetch(url, out / filename)
            with MemoryFile(gzip.decompress(raw)) as mem:
                with mem.open() as src:
                    window = from_bounds(*BOX, transform=src.transform).round_offsets().round_lengths()
                    values = src.read(1, window=window, masked=True)
            valid = (~np.ma.getmaskarray(values)) & np.isfinite(values.filled(np.nan)) & (values.filled(-1) >= 0)
            weights = np.asarray(Image.fromarray(valid.astype('float32')).resize((map_w, map_h), Image.Resampling.BILINEAR))
            smooth = np.asarray(Image.fromarray(np.where(valid, values.filled(0), 0).astype('float32')).resize((map_w, map_h), Image.Resampling.BILINEAR))
            smooth = np.divide(smooth, weights, out=np.zeros_like(smooth), where=weights > 0)
            overlay = Image.fromarray(colorize(smooth))
            combined = Image.fromarray(np.minimum(np.asarray(mask), (weights > .99).astype('uint8')*255))
            frame = Image.new('RGB', (1080, 1920), '#0b1922')
            d = ImageDraw.Draw(frame)
            d.text((64, 58), 'ECUADOR VIVO  /  ANDES PULSO', font=font(27, True), fill='#77d8bc')
            d.text((60, 117), 'La lluvia cambia.', font=font(76, True), fill='#f3f1e9')
            d.text((64, 218), 'Mira dónde cae cada día.', font=font(35), fill='#b0c5cc')
            d.rounded_rectangle((64, 290, 440, 350), radius=16, fill='#19333e')
            d.text((84, 298), f'{date:%d / %m / %Y}', font=font(34, True), fill='#ffffff')
            d.text((730, 310), f'DÍA {i+1:02} / {args.days:02}', font=font(25), fill='#b0c5cc')
            frame.paste(overlay, (map_x, map_y), combined)
            d = ImageDraw.Draw(frame)
            for ring in rings:
                d.line([(x+map_x, y+map_y) for x, y in ring], fill='#d1e1d8', width=2)
            for name, lon, lat, dx, dy in [('Quito',-78.4678,-.1807,-92,-30),('Guayaquil',-79.889,-2.17,-155,7),('Cuenca',-79.005,-2.9,-110,4),('Tena',-77.813,-.994,15,8)]:
                x,y=xy(lon,lat); x+=map_x; y+=map_y
                d.ellipse((x-5,y-5,x+5,y+5),fill='white')
                d.text((x+dx,y+dy),name,font=font(26,True),fill='white',stroke_width=2,stroke_fill='#10212c')
            d.text((65, 1430),'LLUVIA ACUMULADA · mm/día',font=font(29,True),fill='#f3f1e9')
            gradient = np.interp(np.linspace(0,7,940), np.arange(8), STOPS)
            bar = Image.fromarray(colorize(gradient[None,:])).resize((940,30))
            frame.paste(bar,(65,1490))
            d = ImageDraw.Draw(frame)
            for j,v in enumerate(STOPS):
                d.text((65+j*940/7,1533), str(int(v)) + ('+' if j==7 else ''), font=font(24),fill='#cbdadd',anchor='mt')
            d.text((65,1590),'Escala fija · intervalos de color no uniformes',font=font(24),fill='#a5bec6')
            d.text((65,1640),'Interpolación visual · dato nativo ≈ 5,6 km',font=font(26),fill='#a5bec6')
            d.text((65,1685),'Cada fecha conserva su acumulado diario.',font=font(26),fill='#a5bec6')
            d.line((65,1750,1005,1750),fill='#32505b',width=2)
            d.text((65,1780),'CHIRPS v2 · UCSB / Climate Hazards Center',font=font(24),fill='#89a5ae')
            d.text((65,1820),'Ecuador continental · límites: geoBoundaries',font=font(24),fill='#89a5ae')
            pixels = np.asarray(frame)
            for _ in range(45):
                writer.send(pixels)
            if i in (0,args.days-1):
                frame.save(out / f'frame-{date}.png')
            receipt['frames'].append({'date':str(date),'source_url':url,'sha256':hashlib.sha256(raw).hexdigest(), 'missing_cells':int((~valid).sum())})
    finally:
        writer.close()
    receipt['video_sha256'] = hashlib.sha256(video.read_bytes()).hexdigest()
    (out/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(video, flush=True)

if __name__ == '__main__':
    main()
