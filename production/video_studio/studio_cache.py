"""Bounded presentation-only caches owned by one editor session.

Never stores FFmpeg readers or scientific computations. AssetFrames verifies
the actual file hashes before these caches can be used on each rerun.
"""
from collections import OrderedDict
import copy
from dataclasses import asdict
import hashlib
import io
import json
from layout_engine import _png


class _MemoryLRU:
    def __init__(self,max_bytes):
        if type(max_bytes) is not int or max_bytes<0: raise ValueError('Presupuesto de cache inválido.')
        self.max_bytes=max_bytes;self.bytes_used=0;self.entries=OrderedDict()

    def get(self,key):
        entry=self.entries.get(key)
        if entry is None: return None
        self.entries.move_to_end(key)
        return entry[0]

    def put(self,key,value,size):
        old=self.entries.pop(key,None)
        if old is not None:
            self.bytes_used-=old[1]
            if old[0] is not value: self._release(old[0])
        if size>self.max_bytes: return
        while self.entries and (self.bytes_used+size>self.max_bytes or len(self.entries)>=512):
            _,(evicted,weight)=self.entries.popitem(last=False);self.bytes_used-=weight
            self._release(evicted)
        self.entries[key]=(value,size);self.bytes_used+=size

    @staticmethod
    def _release(value):
        close=getattr(value,'close',None)
        if close is not None: close()

    def clear(self):
        for value,weight in self.entries.values(): self._release(value)
        self.entries.clear();self.bytes_used=0


class MediaCache:
    """Decoded images and probe metadata; no open files/readers survive a rerun."""
    def __init__(self,max_bytes): self._lru=_MemoryLRU(max_bytes)

    @property
    def bytes_used(self): return self._lru.bytes_used

    def image(self,key):
        value=self._lru.get(('image',key))
        return None if value is None else value.copy()

    def remember_image(self,key,image):
        size=image.width*image.height*4+512
        if size<=self._lru.max_bytes: self._lru.put(('image',key),image.copy(),size)

    def video(self,key):
        value=self._lru.get(('video',key))
        return None if value is None else copy.deepcopy(value)

    def remember_video(self,key,metadata):
        self._lru.put(('video',key),copy.deepcopy(metadata),len(json.dumps(metadata).encode())+512)

    def clear(self): self._lru.clear()


class StudioPreviewCache:
    """Reuse independent scene products after complete document/file validation."""
    def __init__(self, *, max_bytes=32*1024*1024,media_max_bytes=32*1024*1024):
        self.media=MediaCache(media_max_bytes);self._products=_MemoryLRU(max_bytes)

    @property
    def bytes_used(self): return self._products.bytes_used

    def for_timeline(self,prepared,assets): return _PreviewSession(self,prepared,assets)

    def clear(self):
        self._products.clear();self.media.clear()


class _PreviewSession:
    def __init__(self,cache,prepared,assets):
        self.cache=cache;self.prepared=prepared;self.assets=assets
        self.rows=prepared.rows;studio=prepared.project['studio']
        self.scenes={s['id']:s for s in studio['scenes']}
        assets.check_budget([e for row in self.rows for e in self.scenes[row['id']]['elements']])
        self.keys={}
        for row in self.rows:
            scene=self.scenes[row['id']];scene['duration']=row['seconds']
            bindings={e['data_binding']['result_id'] for e in scene['elements'] if e.get('data_binding')}
            media={e.get('style',{}).get('asset_id') for e in scene['elements'] if e['type'] in ('map','image','logo','video')}
            media.update(i['asset_id'] for i in scene.get('map_instances',{}).values())
            signature={'renderer':'studio_preview_v2','scene':scene,'profile':asdict(prepared.profile),
                'calculations':{rid:studio['calculations'][rid] for rid in bindings},
                'media':{aid:assets.records.get(aid) for aid in media if aid is not None}}
            self.keys[row['id']]=hashlib.sha256(json.dumps(signature,sort_keys=True,allow_nan=False).encode()).hexdigest()

    def _row(self,sid):
        return next(row for row in self.rows if row['id']==sid)

    def _verify_maps(self,sid,frame=None):
        scene=self.scenes[sid]
        if scene.get('map_instances'):
            start=self._row(sid)['start_frame']
            self.assets.temporal_at(0 if frame is None else (frame-start)/30,scene['elements'],scene['map_instances'])

    def _thumbnail(self,sid,image=None):
        self._verify_maps(sid)
        key=(self.keys[sid],'thumbnail');value=self.cache._products.get(key)
        if value is None:
            if image is None: image=self.prepared.frame_at(self._row(sid)['start_frame'],assets=self.assets,authoring=True)
            thumbnail=image.copy();thumbnail.thumbnail((160,100));value=_png(thumbnail)
            self.cache._products.put(key,value,len(value.encode())+256)
        return value

    def canvas(self,sid,payload_builder):
        self._verify_maps(sid)
        key=(self.keys[sid],'canvas');value=self.cache._products.get(key)
        if value is None:
            image=self.prepared.frame_at(self._row(sid)['start_frame'],assets=self.assets,authoring=True)
            value=payload_builder(image,self.scenes[sid],self.prepared.profile)
            self._thumbnail(sid,image)
            self.cache._products.put(key,copy.deepcopy(value),len(json.dumps(value).encode())+256)
        return copy.deepcopy(value)

    def thumbnails(self):
        return [{**row,'thumbnail':self._thumbnail(row['id'])} for row in self.rows]

    def preview(self,frame):
        if type(frame) is not int or not 0<=frame<self.prepared.total_frames:
            raise ValueError('Playhead fuera de la timeline.')
        row=next(r for r in self.rows if r['start_frame']<=frame<r['end_frame'])
        self._verify_maps(row['id'],frame)
        key=(self.keys[row['id']],'preview',frame-row['start_frame'])
        value=self.cache._products.get(key)
        if value is None:
            output=io.BytesIO();self.prepared.frame_at(frame,assets=self.assets).save(output,format='PNG')
            value=output.getvalue();self.cache._products.put(key,value,len(value)+256)
        return value
