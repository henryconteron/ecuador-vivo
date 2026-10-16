"""Measure native POWER availability and existing provincial pixel selection."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys
import urllib.parse
import urllib.request
import numpy as np
from rasterio.io import MemoryFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'production/video_studio'))
from providers import power_daily_regions, _power_geotiff_bytes
from data import province_boundaries, _polygon_stats

today = dt.date.today()
first = today-dt.timedelta(days=14)
report = {'date': str(today), 'requests': [], 'method': 'existing data._polygon_stats: native centres; cosine latitude area approximation; no interpolation'}
cells = {}
for index, (west, south, east, north) in enumerate(power_daily_regions()):
    args = {'parameters': 'T2M', 'community': 'SB', 'format': 'JSON', 'time-standard': 'UTC',
            'start': first.strftime('%Y%m%d'), 'end': today.strftime('%Y%m%d'),
            'latitude-min': south, 'latitude-max': north, 'longitude-min': west, 'longitude-max': east}
    url = 'https://power.larc.nasa.gov/api/temporal/daily/regional?'+urllib.parse.urlencode(args)
    with urllib.request.urlopen(url, timeout=55) as response: raw=response.read()
    path = ROOT/f'tmp/v1-definitive-power-national-region-{index+1}.json'
    path.write_bytes(raw)
    data = json.loads(raw)
    report['requests'].append({'url': url, 'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest(), 'header': data['header'], 'parameters': data['parameters']})
    fill = data['header']['fill_value']
    for feature in data['features']:
        lon, lat = feature['geometry']['coordinates'][:2]
        values = feature['properties']['parameter']['T2M']
        key = (lat, lon)
        if key in cells: assert cells[key] == values, 'Overlapping cells disagree'
        cells[key] = values
complete = [day for day in sorted(next(iter(cells.values()))) if all(day in values and np.isfinite(values[day]) and values[day] != fill for values in cells.values())]
assert complete, 'No complete recent date across the regional grid'
last = complete[-1]
report.update(native_cells=len(cells), complete_recent_dates=complete, last_complete_date=str(dt.datetime.strptime(last,'%Y%m%d').date()),
              requested_61_day_start=str(dt.datetime.strptime(last,'%Y%m%d').date()-dt.timedelta(days=60)))
rows = [{'date': report['last_complete_date'], 'lat':lat, 'lon':lon, 'value':values[last]} for (lat,lon),values in cells.items()]
raw, dates, dx, dy = _power_geotiff_bytes(rows, 'T2M')
path = ROOT/'tmp/v1-definitive-power-last-complete.tif'
path.write_bytes(raw)
with MemoryFile(raw) as memory, memory.open() as source:
    report['provinces'] = _polygon_stats(source,1,province_boundaries(),include_empty=True)
report.update(native_resolution={'latitude':dy, 'longitude':dx},
              provinces_with_valid_pixels=sum(row['valid_pixels']>0 for row in report['provinces'].values()),
              provinces_without_pixels=[name for name,row in report['provinces'].items() if row['valid_pixels']==0])
(ROOT/'tmp/v1-definitive-power-coverage.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps(report,ensure_ascii=False),flush=True)
