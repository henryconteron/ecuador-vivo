"""Secure, content-addressed media with one CFR decoder for preview and export."""
import hashlib
import copy
import io
import math
import re
from PIL import Image, ImageOps
import imageio_ffmpeg
from studio_ffmpeg import read_frames
from storyboard import store_media, media_path, probe_video, IMAGE_SUFFIXES, VIDEO_SUFFIXES

TOTAL_PIXEL_BUDGET=80_000_000


def import_asset(content, name):
    record = store_media(content, name)
    path = media_path(record['path'])
    if record['kind'] == 'image':
        with Image.open(path) as image:
            record['size'] = list(ImageOps.exif_transpose(image).size)
    elif math.prod(record['size']) > 40_000_000:
        raise ValueError('El video supera el presupuesto de 40 MP.')
    record['bytes'] = len(content)
    return record


class AssetFrames:
    """Decode lazily and sequentially; drag operations never touch source rasters.

    Audio is scheduled separately on the same CFR grid. Each element gets its own cursor for
    independent trim/loop. EOF holds the last valid frame rather than zero.
    """
    def __init__(self, records, *, cache=None, tile_cache_bytes=32*1024*1024):
        if not isinstance(records, dict) or len(records) > 600:
            raise ValueError('Biblioteca multimedia inválida.')
        self.records, self.images, self.videos, self.cursors = {}, {}, {}, {}
        from studio_cache import MediaCache
        if type(tile_cache_bytes) is not int or not 0<=tile_cache_bytes<=320_000_000:
            raise ValueError('Presupuesto de tiles fuera de 0–320 MB.')
        self.bundles,self.map_products={},{}
        self.map_cache=MediaCache(tile_cache_bytes)
        image_pixels=0
        bundle_metadata_bytes=0
        try:
            for aid, record in records.items():
                if not isinstance(aid,str) or not re.fullmatch(r'[\w.-]{1,180}',aid) or not isinstance(record,dict):
                    raise ValueError('ID multimedia inválido.')
                if record.get('kind')=='temporal_map':
                    from studio_map_bundles import BundleFrames,MANIFEST_LIMIT
                    bundle=BundleFrames(record,cache=self.map_cache)
                    self.bundles[aid]=bundle
                    bundle_metadata_bytes+=(bundle.root/'manifest.json').stat().st_size
                    if bundle_metadata_bytes>MANIFEST_LIMIT:raise ValueError('Metadata de bundles superior a 8 MiB por sesión.')
                    self.records[aid]=copy.deepcopy(record)
                    continue
                path = media_path(record.get('path'))
                if path.stat().st_size > 100*1024*1024:
                    raise ValueError('Recurso superior a 100 MB.')
                content=path.read_bytes()
                if len(content)>100*1024*1024: raise ValueError('Recurso superior a 100 MB.')
                digest = hashlib.sha256(content).hexdigest()
                if digest != record.get('sha256'):
                    raise ValueError('El recurso multimedia cambió; vuelve a importarlo.')
                kind = record.get('kind')
                cache_key=(str(path.resolve()),digest)
                if kind == 'image' and path.suffix.lower() in IMAGE_SUFFIXES:
                    cached=cache.image(cache_key) if cache is not None else None
                    if cached is not None:
                        self.images[aid]=cached
                        image_pixels+=cached.width*cached.height
                        if image_pixels>TOTAL_PIXEL_BUDGET: raise ValueError('Biblioteca de imágenes superior a 80 MP.')
                    else:
                        # Decode the bytes actually hashed, not a second path read.
                        with Image.open(io.BytesIO(content)) as image:
                            if image.width*image.height > 40_000_000: raise ValueError('Imagen superior a 40 MP.')
                            image_pixels+=image.width*image.height
                            if image_pixels>TOTAL_PIXEL_BUDGET: raise ValueError('Biblioteca de imágenes superior a 80 MP.')
                            self.images[aid] = ImageOps.exif_transpose(image).convert('RGBA')
                        if cache is not None: cache.remember_image(cache_key,self.images[aid])
                elif kind == 'video' and path.suffix.lower() in VIDEO_SUFFIXES:
                    metadata=cache.video(cache_key) if cache is not None else None
                    if metadata is None:
                        metadata=probe_video(path,content_hash=digest)
                        if cache is not None: cache.remember_video(cache_key,metadata)
                    if math.prod(metadata['size']) > 40_000_000: raise ValueError('Video superior a 40 MP.')
                    if 'temporal_map' in record:
                        from studio_temporal import validate_resource
                        validate_resource(record)
                        if metadata['size'] != record['size'] or abs(metadata['duration']-record['duration']) > 1/30:
                            raise ValueError('El video no coincide con su calendario científico.')
                        metadata['duration'] = record['duration']
                    self.videos[aid] = (path, metadata)
                else: raise ValueError('Tipo multimedia incompatible con su archivo.')
                self.records[aid] = copy.deepcopy(record)
                del content
        except Exception:
            self.close()
            raise

    def check_budget(self,elements):
        """Keep the combined cursor budget effective even for warm UI products."""
        sizes={key:math.prod(cursor['size']) for key,cursor in self.cursors.items()}
        for element in elements:
            if element['type']!='video': continue
            aid=element.get('style',{}).get('asset_id')
            if aid not in self.videos: raise ValueError('Video ausente de la biblioteca segura.')
            sizes[(element['id'],aid)]=math.prod(self.videos[aid][1]['size'])
        if sum(i.width*i.height for i in self.images.values())+sum(sizes.values())+self._map_pixels()>TOTAL_PIXEL_BUDGET:
            raise ValueError('Cuadros multimedia superiores al presupuesto de 80 MP.')

    def _map_pixels(self,exclude=None):
        return sum(image.width*image.height for key,product in self.map_products.items() if key!=exclude
            for image in product['images'].values())

    def map_at(self,aid,source_frame,layer_ids=('continent','galapagos'),*,cursor_id=None):
        """Private adapter; source frame is resolved by the shared instance clock."""
        if aid not in self.bundles:raise ValueError('Bundle ausente de la biblioteca segura.')
        cursor_id=aid if cursor_id is None else cursor_id
        if not isinstance(cursor_id,str) or not re.fullmatch(r'[\w.-]{1,180}',cursor_id):raise ValueError('Cursor cartográfico inválido.')
        key=(aid,cursor_id);product=self.bundles[aid].at(source_frame,layer_ids)
        pixels=sum(i.width*i.height for i in self.images.values())+sum(math.prod(c['size']) for c in self.cursors.values())
        pixels+=self._map_pixels(exclude=key)+sum(i.width*i.height for i in product['images'].values())
        if pixels>TOTAL_PIXEL_BUDGET:
            for image in product['images'].values():image.close()
            raise ValueError('Cuadros multimedia superiores al presupuesto de 80 MP.')
        old=self.map_products.get(key)
        if old is not None:
            for image in old['images'].values():image.close()
        self.map_products[key]=product
        return product

    def at(self, time, elements=(), *, map_instances=None):
        self.check_budget(elements)
        result = dict(self.images)
        if map_instances:
            result.update(self.temporal_at(time,elements,map_instances))
        for element in elements:
            if element['type'] != 'video': continue
            style = element.get('style',{})
            aid = style.get('asset_id')
            if aid not in self.videos: raise ValueError('Video ausente de la biblioteca segura.')
            from studio_audio import audio_settings
            audio_settings(style)
            path, metadata = self.videos[aid]
            from studio_temporal import video_frame_index
            index = video_frame_index(time,style,metadata)
            key = (element['id'], aid)
            cursor = self.cursors.get(key)
            if cursor is None or index < cursor['index'] or index-cursor['index']>60:
                if cursor: cursor['reader'].close()
                # Preserve source PTS across seek, then sample the same global
                # CFR grid as sequential decoding. noaccurate_seek preserves
                # the keyframe predecessor even for sparse VFR. Actual decode
                # preroll depends on the source GOP, not only the seek offset.
                # https://ffmpeg.org/ffmpeg.html (copyts/start_at_zero/ss)
                # https://ffmpeg.org/ffmpeg-filters.html#fps-1
                seek=max(0,math.floor(index/30)-1)
                reader = read_frames(str(path), pix_fmt='rgb24',
                    input_params=['-protocol_whitelist','file,pipe','-copyts','-start_at_zero','-noaccurate_seek','-ss',str(float(seek))],
                    output_params=['-vf',f'fps=30:start_time={seek},setpts=PTS-STARTPTS',
                                   '-fps_mode','passthrough'])
                decoded = next(reader)
                pixels=sum(i.width*i.height for i in self.images.values())+sum(
                    math.prod(c['size']) for k,c in self.cursors.items() if k!=key)+math.prod(decoded['size'])+self._map_pixels()
                if math.prod(decoded['size'])>40_000_000 or pixels>TOTAL_PIXEL_BUDGET:
                    reader.close();raise ValueError('Cuadros multimedia superiores al presupuesto de 80 MP.')
                cursor = {'reader':reader,'index':seek*30-1,'frame':None,'size':decoded['size'],'eof':False}
                self.cursors[key] = cursor
            while cursor['index'] < index and not cursor['eof']:
                try:
                    frame = next(cursor['reader'])
                    cursor['frame'] = Image.frombytes('RGB',cursor['size'],frame).convert('RGBA')
                    cursor['index'] += 1
                except StopIteration: cursor['eof'] = True
            if cursor['frame'] is None: raise ValueError('El video no contiene cuadros decodificables.')
            result['video.'+element['id']] = cursor['frame']
        return result

    def temporal_at(self,time,elements,map_instances):
        """Resolve each instance once; every bound element shares its context."""
        from studio_temporal import instance_frame
        result={};frame=max(0,math.floor(time*30+1e-7))
        active={(i['asset_id'],iid) for iid,i in map_instances.items()}
        for key in list(self.map_products):
            if key not in active:
                for image in self.map_products.pop(key)['images'].values():image.close()
        for iid,instance in map_instances.items():
            bound=[e for e in elements if e.get('temporal_binding',{}).get('instance_id')==iid]
            channels=tuple(sorted({e['temporal_binding']['channel'] for e in bound}-{'date'}))
            if not channels:raise ValueError('Instancia sin consumidores cartográficos.')
            aid=instance['asset_id'];product=self.map_at(aid,instance_frame(self.records[aid],instance,frame),channels,cursor_id=iid)
            for e in bound:
                channel=e['temporal_binding']['channel']
                result['temporal.'+e['id']]=dict(product['observation'])
                if channel!='date':result['map.'+e['id']]=product['images'][channel]
        return result

    def close(self):
        error=None
        for cursor in self.cursors.values():
            try: cursor['reader'].close()
            except Exception as failure:
                if error is None: error=failure
            finally:
                if cursor.get('frame') is not None: cursor['frame'].close()
        self.cursors.clear()
        for image in self.images.values(): image.close()
        self.images.clear()
        for product in self.map_products.values():
            for image in product['images'].values():image.close()
        self.map_products.clear()
        for bundle in self.bundles.values():bundle.close()
        self.bundles.clear();self.map_cache.clear()
        if error is not None: raise error

    def __enter__(self): return self
    def __exit__(self,*args): self.close()
