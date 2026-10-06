"""Download/cache CHIRPS v2 daily inputs without rendering a video.

Uses the same period folders as render_daily_rain.py. Standard library only.
Writes a separate download receipt; never replaces the video receipt.
"""
import argparse
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]


def validate(payload):
    data = gzip.decompress(payload)  # Includes gzip integrity check.
    if data[:4] not in (b'II\x2a\x00', b'MM\x00\x2a', b'II\x2b\x00', b'MM\x00\x2b'):
        raise ValueError('El archivo no contiene una cabecera TIFF reconocida.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start', required=True, help='Primera fecha, AAAA-MM-DD')
    parser.add_argument('--days', type=int, required=True, help='1 a 366 dias')
    args = parser.parse_args()
    try:
        start = dt.date.fromisoformat(args.start)
    except ValueError:
        parser.error('Fecha invalida: usa AAAA-MM-DD.')
    if not 1 <= args.days <= 366:
        parser.error('--days debe estar entre 1 y 366.')
    if start < dt.date(1981, 1, 1):
        parser.error('CHIRPS comienza en 1981.')
    out = ROOT / '_local' / 'climate-studio' / f'{start}-{args.days}days'
    out.mkdir(parents=True, exist_ok=True)
    receipt = {'source': 'CHIRPS v2 daily', 'start': str(start),
               'requested_days': args.days, 'complete': False, 'files': []}
    receipt_path = out / 'download-receipt.json'
    try:
        for offset in range(args.days):
            date = start + dt.timedelta(days=offset)
            name = f'chirps-v2.0.{date:%Y.%m.%d}.tif.gz'
            url = f'https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/{date.year}/{name}'
            target = out / name
            if target.exists():
                raw = target.read_bytes()
                validate(raw)
                state = 'cache verificada'
            else:
                for attempt in range(3):
                    try:
                        with urllib.request.urlopen(url, timeout=120) as response:
                            raw = response.read()
                        validate(raw)
                        break
                    except urllib.error.HTTPError as error:
                        if error.code == 404 or attempt == 2:
                            raise
                        time.sleep(2 * (attempt + 1))
                    except (urllib.error.URLError, TimeoutError):
                        if attempt == 2:
                            raise
                        time.sleep(2 * (attempt + 1))
                partial = target.with_suffix(target.suffix + '.part')
                partial.write_bytes(raw)
                partial.replace(target)
                state = 'descargado'
            receipt['files'].append({'date': str(date), 'source_url': url,
                                     'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
            print(f'{offset + 1}/{args.days} {date}: {state}', flush=True)
        receipt['complete'] = True
    finally:
        receipt['checked_at_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Datos listos: {out}')


if __name__ == '__main__':
    main()
