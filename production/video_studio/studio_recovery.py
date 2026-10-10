"""Durable plain-JSON snapshots and an explicit previous-version fallback."""
import json
import os
from pathlib import Path
import time
import uuid
from studio_model import migrate_project

MAX_BYTES=64*1024**2


def _document(value):
    try: result=migrate_project(value)
    except AttributeError as error:
        raise ValueError('Estructura de proyecto inválida para recuperar.') from error
    encoded=json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False).encode('utf-8')
    if len(encoded)>MAX_BYTES: raise ValueError('El borrador supera el presupuesto de 64 MiB.')
    return result,encoded


def _atomic(path,content):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp');owned=False
    try:
        with temp.open('xb') as stream:
            owned=True;stream.write(content);stream.flush();os.fsync(stream.fileno())
        for attempt in range(20):
            try: temp.replace(path);break
            except PermissionError:
                if attempt==19: raise
                time.sleep(.05)
    finally:
        if owned: temp.unlink(missing_ok=True)


def _read_document(path):
    path=Path(path)
    if path.stat().st_size>MAX_BYTES: raise ValueError('El borrador supera el presupuesto de 64 MiB.')
    with path.open('rb') as stream: content=stream.read(MAX_BYTES+1)
    if len(content)>MAX_BYTES: raise ValueError('El borrador supera el presupuesto de 64 MiB.')
    return _document(json.loads(content))


def _read(path):return _read_document(path)[0]


def _previous(path):
    path=Path(path);return path.with_name(path.stem+'.previous.json')


def save_snapshot(path,project):
    """Preserve the last valid version before atomically publishing the next."""
    path=Path(path);document,content=_document(project)
    if path.exists():
        # Do not replace a malformed primary or consume the only good backup.
        previous,previous_content=_read_document(path)
        _atomic(_previous(path),previous_content)
    _atomic(path,content)


def recover_snapshot(path):
    """Return (document, used_previous); never rewrite the selected snapshot."""
    try: return _read(path),False
    except (OSError,ValueError,TypeError,KeyError) as original:
        try: return _read(_previous(path)),True
        except (OSError,ValueError,TypeError,KeyError):
            raise ValueError('No hay una versión recuperable de este borrador: '+str(original)) from original


def list_snapshots(folder):
    root=Path(folder).resolve()
    if not root.is_dir(): return []
    paths=[path for path in root.glob('borrador-studio-*.json')
        if not path.name.endswith('.previous.json') and path.is_file() and path.resolve().is_relative_to(root)]
    return sorted(paths,key=lambda path:path.stat().st_mtime_ns,reverse=True)[:100]
