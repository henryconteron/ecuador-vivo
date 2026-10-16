"""Copy checkpoint and historical blocks; retain every original."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
archive=ROOT/'documentation/archive/v1-usable-20261009'
archive.mkdir(parents=True,exist_ok=True)
source=ROOT/'tmp/ecuador-vivo-studio-2-checkpoint.md'
destination=archive/source.name
assert not destination.exists()
shutil.copy2(source,destination)
records=[{'source':str(source.relative_to(ROOT)),'copy':str(destination.relative_to(ROOT)),
          'bytes':destination.stat().st_size,'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
          'matches_original':source.read_bytes()==destination.read_bytes()}]
for name in ('plan','todo'):
    source=ROOT/f'tasks/{name}.md';destination=archive/f'{name}-historico.md'
    assert not destination.exists()
    started=False;original_hash=hashlib.sha256()
    with source.open('rb') as incoming,destination.open('xb') as outgoing:
        for line in incoming:
            if line.startswith(b'## HISTOR'):started=True
            if started:outgoing.write(line);original_hash.update(line)
    copied_hash=hashlib.sha256(destination.read_bytes()).hexdigest()
    assert copied_hash==original_hash.hexdigest() and started
    records.append({'source':str(source.relative_to(ROOT)),'copy':str(destination.relative_to(ROOT)),
                    'bytes':destination.stat().st_size,'sha256':copied_hash,'matches_original_suffix':True})
(ROOT/'tmp/v1-definitive-archive.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print(json.dumps(records))
