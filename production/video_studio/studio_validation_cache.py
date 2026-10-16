"""Session-owned proofs for unchanged scientific registries and external files.

Document/scene schema validation always runs. Export uses no proof cache.
Proofs expire on a registry change or any change of file identity/stat metadata.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
from collections import OrderedDict


def file_revision(path):
    """NTFS ChangeTime is a revision; Python's Windows ctime is creation time."""
    if os.name!='nt':return path.stat().st_ctime_ns
    import ctypes
    from ctypes import wintypes
    class BasicInfo(ctypes.Structure):
        _fields_=[('creation',ctypes.c_longlong),('access',ctypes.c_longlong),
                  ('write',ctypes.c_longlong),('change',ctypes.c_longlong),('attributes',wintypes.DWORD)]
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.CreateFileW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
    kernel.CreateFileW.restype=wintypes.HANDLE
    kernel.GetFileInformationByHandleEx.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD]
    kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    handle=kernel.CreateFileW(str(path),0x80,7,None,3,0,None)
    if handle==ctypes.c_void_p(-1).value:raise ctypes.WinError(ctypes.get_last_error())
    try:
        info=BasicInfo()
        if not kernel.GetFileInformationByHandleEx(handle,0,ctypes.byref(info),ctypes.sizeof(info)):
            raise ctypes.WinError(ctypes.get_last_error())
        return info.change
    finally:kernel.CloseHandle(handle)


class ResourceProofs:
    def __init__(self): self.entries=OrderedDict()

    def _key(self,project):
        value=copy.deepcopy(project)
        value.pop('name',None)
        value.get('project_meta',{}).pop('revision',None)
        for scene in value['studio']['scenes']:
            scene.pop('name',None);scene.pop('modified',None)
            for element in scene['elements']:
                element.pop('transform',None);element.pop('name',None)
        return hashlib.sha256(json.dumps(value,sort_keys=True,allow_nan=False).encode()).hexdigest()

    @staticmethod
    def files(project):
        from storyboard import media_path
        paths=set()
        for record in project['studio']['media'].values():
            if record.get('kind')=='temporal_map':
                manifest=Path(record['manifest_path']).resolve();paths.add(manifest)
                from studio_map_bundles import _root,MANIFEST_LIMIT
                if not manifest.is_relative_to(_root()) or manifest.stat().st_size>MANIFEST_LIMIT:
                    raise ValueError('Manifiesto fuera del almacenamiento permitido.')
                data=json.loads(manifest.read_text(encoding='utf8'))
                items=[data['thumbnail'],*data.get('auxiliaries',{}).values()]
                items.extend(item for observation in data['observations'] for item in observation['layers'].values())
                for item in items:
                    path=(manifest.parent/item['path']).resolve()
                    if not path.is_relative_to(manifest.parent):raise ValueError('Tile fuera del bundle verificado.')
                    paths.add(path)
            elif record.get('kind')=='audio':
                from studio_voice import audio_media_path
                paths.add(audio_media_path(record.get('path')))
            elif record.get('path'):paths.add(media_path(record['path']).resolve())
        for source in project['studio'].get('geography',{}).get('sources',{}).values():
            if source.get('path'):paths.add(Path(source['path']).resolve())
        return paths

    @staticmethod
    def tokens(paths):
        result=[]
        for path in sorted(paths):
            stat=path.stat()
            result.append((str(path),stat.st_dev,stat.st_ino,stat.st_size,stat.st_mtime_ns,file_revision(path)))
        return tuple(result)

    def verify(self,project,operation):
        key=self._key(project);entry=self.entries.get(key)
        if entry and self.tokens(entry[0])==entry[1]:
            self.entries.move_to_end(key);return
        paths=self.files(project);before=self.tokens(paths)
        operation()
        if self.tokens(paths)!=before:raise ValueError('Los recursos cambiaron durante la validación.')
        self.entries[key]=(paths,before)
        while len(self.entries)>16:self.entries.popitem(last=False)
