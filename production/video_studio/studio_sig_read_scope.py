"""Request-local verified reads, never a persistent scientific-result cache.

Each outer operation hashes each original once. Repeated declarations can reuse
that proof only while file identity, size, mtime and NTFS ChangeTime agree.
Proofs are also checked on successful scope exit and discarded on every exit.
"""
import json
from contextlib import contextmanager
from contextvars import ContextVar
from studio_validation_cache import ResourceProofs

_proofs=ContextVar('sig_native_read_proofs',default=None)

def revision(path):return ResourceProofs.tokens([path])

def known(source):
    entries=_proofs.get()
    if entries is None:return None
    entry=entries.get(json.dumps(source,sort_keys=True,allow_nan=False))
    if entry:
        path,token=entry
        if revision(path)!=token:raise ValueError('El original cambió durante la operación SIG.')
        return path
    return None

def begin(path):return revision(path) if _proofs.get() is not None else None

def remember(source,path,token):
    entries=_proofs.get()
    if entries is None:return
    if revision(path)!=token:raise ValueError('El original cambió durante la verificación SIG.')
    entries[json.dumps(source,sort_keys=True,allow_nan=False)]=(path,token)

@contextmanager
def native_read_scope():
    if _proofs.get() is not None:
        yield
        return
    entries={};context=_proofs.set(entries)
    try:
        yield
        for path,token in entries.values():
            if revision(path)!=token:raise ValueError('El original cambió antes de terminar la operación SIG.')
    finally:_proofs.reset(context)
