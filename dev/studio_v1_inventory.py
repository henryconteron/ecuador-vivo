"""Inventory changed/new files including ignored evidence and private drafts."""
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'tmp/v1-definitive-inventory-before.json'
RESULT=ROOT/'tmp/v1-definitive-files.json'
def snapshot():
    result={}
    for base,dirs,files in os.walk(ROOT):
        dirs[:]=[d for d in dirs if d not in ('.git','node_modules','.pnpm-store','.venv','__pycache__')]
        for name in files:
            p=Path(base)/name
            try:s=p.stat();result[p.relative_to(ROOT).as_posix()]=[s.st_size,s.st_mtime_ns]
            except OSError:pass
    return result
if sys.argv[1]=='before':
    BASE.write_text(json.dumps(snapshot()),encoding='utf-8')
else:
    before=json.loads(BASE.read_text(encoding='utf-8'));after=snapshot()
    result={'created':sorted(set(after)-set(before)),
            'modified':sorted(p for p in before.keys()&after.keys() if before[p]!=after[p]),
            'missing':sorted(set(before)-set(after)),
            'note':'Includes ignored outputs and retained temporary Chrome profile; excludes .venv, node_modules, .git and Python bytecode.'}
    result['created'].append(RESULT.relative_to(ROOT).as_posix())
    for p in ('documentation/ESTADO.md','dev/studio_v1_inventory.py','dev/studio_v1_opacity.py'):
        if p not in result['created']:result['created'].append(p)
    if 'dev/studio_v1_measure.py' not in result['modified']:result['modified'].append('dev/studio_v1_measure.py')
    RESULT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:len(v) for k,v in result.items() if isinstance(v,list)}))
