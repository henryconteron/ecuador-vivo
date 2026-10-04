"""Create/verify a bounded, portable backup of the PUBLIC geology pilot only."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
FILES = ('data/geology/manifest.json', 'data/geology/tena-units.geojson',
         'data/geology/tena-sheets.geojson', 'documentation/geologia-y-aportes.md',
         'documentation/laboratorio-y-almacenamiento.md', 'LICENSE-DATA.md')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify(path):
    with ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or len(names) > 30:
            raise ValueError('Duplicate or excessive entries')
        if any(info.file_size > 20_000_000 for info in archive.infolist()) or sum(i.file_size for i in archive.infolist()) > 50_000_000:
            raise ValueError('Oversized archive')
        if 'backup-manifest.json' not in names:
            raise ValueError('Missing manifest')
        manifest = json.loads(archive.read('backup-manifest.json'))
        if manifest.get('schema_version') != 1 or manifest.get('scope') != 'public-geology-pilot':
            raise ValueError('Unknown backup schema/scope')
        rows = manifest['files']
        if {row['path'] for row in rows} != set(FILES) or len(rows) != len(FILES):
            raise ValueError('Unexpected file inventory')
        if set(names) != {'backup-manifest.json', *FILES}:
            raise ValueError('Unlisted archive entries')
        for row in rows:
            name = row['path']
            if PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts or '\\' in name:
                raise ValueError('Unsafe path')
            data = archive.read(name)
            if len(data) != row['bytes'] or digest(data) != row['sha256']:
                raise ValueError('Checksum mismatch: ' + name)
        return manifest


def build(root=ROOT, output=None):
    root = Path(root).resolve()
    content = {}
    for name in FILES:
        source = (root / name).resolve()
        if not source.is_relative_to(root) or not source.is_file():
            raise ValueError('Missing or external input: ' + name)
        content[name] = source.read_bytes()
    manifest = {'schema_version': 1, 'scope': 'public-geology-pilot',
                'created': datetime.now(timezone.utc).isoformat(),
                'files': [{'path': name, 'bytes': len(data), 'sha256': digest(data)} for name, data in content.items()]}
    if output is None:
        directory = root / '_local/backups'
        directory.mkdir(parents=True, exist_ok=True)
        output = directory / ('ecuador-vivo-geology-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.zip')
    output = Path(output)
    with ZipFile(output, 'x', compression=ZIP_DEFLATED) as archive:
        for name, data in content.items():
            archive.writestr(name, data)
        archive.writestr('backup-manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2).encode())
    verify(output)
    return {'path': str(output.resolve()), 'bytes': output.stat().st_size, 'sha256': digest(output.read_bytes())}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', type=Path, help='Verify an archive without extracting it')
    args = parser.parse_args()
    print(json.dumps({'verified': verify(args.verify)} if args.verify else build(), ensure_ascii=False, indent=2))
