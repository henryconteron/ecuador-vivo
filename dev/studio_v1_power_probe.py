"""Preserve actual NASA POWER responses; never infer availability from latency."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
today = dt.date.today()
base = dict(parameters='T2M', community='SB', format='JSON',
            **{'latitude-min': -3, 'latitude-max': -1,
               'longitude-min': -80, 'longitude-max': -78})
queries = [
    ('daily-recent', 'daily/regional', dict(start=(today-dt.timedelta(days=14)).strftime('%Y%m%d'), end=today.strftime('%Y%m%d'), **{'time-standard': 'UTC'})),
    ('climatology-1991-2020', 'climatology/regional', dict(start='1991', end='2020')),
    ('custom-climatology-1991-2020', 'monthly/climatology/regional', dict(start='1991', end='2020', **{'time-standard': 'UTC'})),
]
report = {'observed_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'local_date': str(today), 'requests': []}
for label, endpoint, arguments in queries:
    url = 'https://power.larc.nasa.gov/api/temporal/'+endpoint+'?'+urllib.parse.urlencode(base | arguments)
    entry = {'label': label, 'url': url}
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=55) as response:
            raw = response.read()
            entry.update(status=response.status, response_headers=dict(response.headers))
    except urllib.error.HTTPError as error:
        raw = error.read()
        entry.update(status=error.code, error=repr(error), response_headers=dict(error.headers))
    except Exception as error:
        raw = b''
        entry.update(error=repr(error))
    entry['seconds'] = time.perf_counter()-started
    path = ROOT/'tmp'/('v1-definitive-power-'+label+'.json')
    path.write_bytes(raw)
    entry.update(path=str(path.relative_to(ROOT)), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    try:
        data = json.loads(raw)
        entry['header'] = data.get('header')
        entry['messages'] = data.get('messages')
        features = data.get('features', [])
        entry['feature_count'] = len(features)
        if features:
            entry['first_feature'] = features[0]
            entry['latitudes'] = sorted({f['geometry']['coordinates'][1] for f in features})
            entry['longitudes'] = sorted({f['geometry']['coordinates'][0] for f in features})
        else:
            entry['body'] = data
    except (ValueError, KeyError, TypeError):
        entry['response_excerpt'] = raw[:1000].decode('utf8', errors='replace')
    report['requests'].append(entry)
    (ROOT/'tmp/v1-definitive-power-probe.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf8')
    print(json.dumps(entry, ensure_ascii=False), flush=True)
