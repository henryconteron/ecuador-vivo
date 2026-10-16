"""Independent native-centre coverage check, without rasterio polygon masking."""
import json
from pathlib import Path
import sys
from shapely.geometry import Point, shape

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'production/video_studio'))
from data import province_boundaries
measured=json.loads((ROOT/'tmp/v1-definitive-power-coverage.json').read_text(encoding='utf8'))
centres=set()
for index in (1,2):
    data=json.loads((ROOT/f'tmp/v1-definitive-power-national-region-{index}.json').read_text(encoding='utf8'))
    centres.update(tuple(f['geometry']['coordinates'][:2]) for f in data['features'])
rows=[]
for feature in province_boundaries():
    name=feature['properties']['shapeName']
    polygon=shape(feature['geometry'])
    selected=[list(point) for point in sorted(centres) if polygon.covers(Point(*point))]
    expected=measured['provinces'][name]['total_pixels']
    rows.append({'province':name,'centres':selected,'count':len(selected),'existing_method_count':expected,'same':len(selected)==expected})
report={'method':'Shapely polygon.covers(Point(lon,lat)) over deduplicated POWER response coordinates; no rasterio mask',
        'native_centres':len(centres),'rows':rows,'all_counts_match':all(row['same'] for row in rows),
        'zero_pixel_provinces':[row['province'] for row in rows if row['count']==0],
        'limitation':'Geometric coverage check, not an independent anomaly ranking: real 1991–2020 baseline has not been built.'}
(ROOT/'tmp/v1-definitive-power-coverage-independent.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({key:value for key,value in report.items() if key!='rows'},ensure_ascii=False))
