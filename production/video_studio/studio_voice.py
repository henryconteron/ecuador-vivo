"""Local, verified narration assets and an independent 30 fps audio schedule.

Tracks live in studio.audio_tracks. Times are global seconds; duration defaults
to the trimmed source span. Missing mute stays silent for imported projects.
No speech service, network request or persistent decoded PCM is needed.
"""
import hashlib
import math
import re
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

import imageio_ffmpeg

AUDIO_SUFFIXES = {'.mp3', '.wav', '.m4a'}
MAX_AUDIO_BYTES = 100*1024*1024
MAX_AUDIO_SECONDS = 7200
MAX_AUDIO_TRACKS = 16
_ID = re.compile(r'[\w.-]{1,180}')


def audio_media_path(value):
    from storyboard import MEDIA_ROOT
    path = Path(str(value)).resolve()
    if not path.is_relative_to(MEDIA_ROOT.resolve()) or not path.is_file() or path.suffix.lower() not in AUDIO_SUFFIXES:
        raise ValueError('Falta un audio seguro del proyecto. Vuelve a importarlo.')
    return path


def _audio_header(content, suffix):
    signatures = {
        '.wav': len(content)>=12 and content[:4]==b'RIFF' and content[8:12]==b'WAVE',
        '.mp3': content[:3]==b'ID3' or (len(content)>=2 and content[0]==255 and content[1]&224==224),
        '.m4a': len(content)>=12 and content[4:8]==b'ftyp',
    }
    if suffix not in signatures or not signatures[suffix]:
        raise ValueError('El contenido no coincide con un audio MP3, WAV o M4A válido.')


def probe_audio(path, *, content_hash=None):
    """Decode bounded local audio, not merely its extension/container header."""
    path = Path(path).resolve()
    stat = path.stat()
    if not 0<stat.st_size<=MAX_AUDIO_BYTES or path.suffix.lower() not in AUDIO_SUFFIXES:
        raise ValueError('El audio debe ocupar entre 1 byte y 100 MB.')
    with path.open('rb') as stream: _audio_header(stream.read(16),path.suffix.lower())
    return dict(_probe_cached(str(path),stat.st_mtime_ns,stat.st_size,content_hash))


@lru_cache(maxsize=64)
def _probe_cached(path,modified,size,content_hash):
    demuxer = {'.mp3':'mp3','.wav':'wav','.m4a':'mov'}[Path(path).suffix.lower()]
    # Explicit demuxer and local-only protocols exclude playlists/remote fetches.
    # https://ffmpeg.org/ffmpeg.html#Generic-options (progress, xerror)
    with tempfile.TemporaryFile() as progress, tempfile.TemporaryFile() as errors:
        command = [imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-xerror','-nostdin',
            '-protocol_whitelist','file,pipe','-f',demuxer,'-i',path,'-map','0:a:0','-vn',
            '-t',str(MAX_AUDIO_SECONDS+.04),'-ac','2','-ar','48000','-progress','pipe:1',
            '-nostats','-f','null','-']
        try:
            result = subprocess.run(command,stdin=subprocess.DEVNULL,stdout=progress,stderr=errors,
                timeout=60,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        except subprocess.TimeoutExpired as error:
            raise ValueError('No se pudo verificar el audio dentro de 60 segundos.') from error
        if result.returncode or progress.tell()>65536 or errors.tell()>65536:
            raise ValueError('El audio está dañado o no contiene una pista decodificable.')
        progress.seek(0)
        times = re.findall(rb'^out_time_us=(\d+)\r?$',progress.read(65536),re.MULTILINE)
        duration = int(times[-1])/1_000_000 if times else 0
    if not math.isfinite(duration) or not 0<duration<=MAX_AUDIO_SECONDS:
        raise ValueError('La duración del audio debe ser mayor que cero y como máximo dos horas.')
    return {'duration':duration,'audio':True,'sample_rate':48000,'channels':2}


def import_audio(content,name):
    """Store original bytes once, only after full decoding has succeeded."""
    from storyboard import MEDIA_ROOT
    if not isinstance(content,(bytes,bytearray)) or not 0<len(content)<=MAX_AUDIO_BYTES:
        raise ValueError('El audio debe ocupar entre 1 byte y 100 MB.')
    suffix = Path(str(name)).suffix.lower()
    _audio_header(content,suffix)
    MEDIA_ROOT.mkdir(parents=True,exist_ok=True)
    digest = hashlib.sha256(content).hexdigest()
    target = MEDIA_ROOT.resolve()/(digest+suffix)
    if target.exists():
        target = audio_media_path(target)
        if target.stat().st_size!=len(content) or hashlib.sha256(target.read_bytes()).hexdigest()!=digest:
            raise ValueError('El audio guardado cambió. No se sobrescribirá.')
        metadata = probe_audio(target,content_hash=digest)
    else:
        with tempfile.TemporaryDirectory(prefix='.voice-import-',dir=MEDIA_ROOT) as folder:
            candidate = Path(folder)/('source'+suffix)
            candidate.write_bytes(content)
            metadata = probe_audio(candidate,content_hash=digest)
            # Candidate is an owned temporary file, target is content-addressed.
            candidate.replace(target)
    return {'kind':'audio','path':str(target),'sha256':digest,'name':Path(str(name)).name,
            'bytes':len(content),**metadata}


def _number(value,label,low=0,high=MAX_AUDIO_SECONDS):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not low<=value<=high:
        raise ValueError(f'{label} debe ser un número finito entre {low} y {high}.')
    return float(value)


def validate_audio_tracks(studio,total_frames=None):
    """Return normalized copies without mutating any saved project values."""
    from studio_captions import caption_frame
    if not isinstance(studio,dict): raise ValueError('Studio inválido para audio.')
    if total_frames is not None and (type(total_frames) is not int or not 1<=total_frames<=MAX_AUDIO_SECONDS*30):
        raise ValueError('Duración global inválida para audio.')
    tracks = studio.get('audio_tracks',[])
    if not isinstance(tracks,list) or len(tracks)>MAX_AUDIO_TRACKS:
        raise ValueError('Se permiten como máximo 16 pistas de voz/audio.')
    media = studio.get('media',{})
    if not isinstance(media,dict): raise ValueError('Biblioteca multimedia inválida.')
    result = []; seen = set()
    for track in tracks:
        if not isinstance(track,dict): raise ValueError('Pista de audio inválida.')
        identifier = track.get('id'); aid = track.get('asset_id')
        if not isinstance(identifier,str) or not _ID.fullmatch(identifier) or identifier in seen:
            raise ValueError('ID de pista de audio inválido o repetido.')
        seen.add(identifier)
        if not isinstance(aid,str) or not _ID.fullmatch(aid) or aid not in media or not isinstance(media[aid],dict) or media[aid].get('kind')!='audio':
            raise ValueError('La pista necesita un audio importado de la biblioteca.')
        source_duration = _number(media[aid].get('duration'),'Duración de origen',1e-6)
        start = _number(track.get('start',0),'Inicio')
        left = _number(track.get('trim_in',0),'Recorte inicial')
        right = _number(track.get('trim_out',source_duration),'Recorte final')
        if not left<right<=source_duration+.000001:
            raise ValueError('El recorte de audio excede la duración de origen.')
        duration = _number(track.get('duration',right-left),'Duración de pista',1/30)
        start_frame=caption_frame(start); duration_frames=max(1,caption_frame(duration))
        if start_frame+duration_frames>(total_frames if total_frames is not None else MAX_AUDIO_SECONDS*30):
            raise ValueError('La pista de audio excede el final del video.')
        from studio_audio import audio_settings
        mute,volume = audio_settings(track)
        loop = track.get('loop',False)
        if type(loop) is not bool: raise ValueError('Repetir audio debe ser booleano.')
        result.append({'id':identifier,'asset_id':aid,'start':start_frame/30,'trim_in':left,
            'trim_out':right,'duration':duration_frames/30,'volume':volume,'mute':mute,'loop':loop})
    return result


def narration_sources(project,rows,assets):
    """Adapt independent tracks to the same immutable schedule as clip audio."""
    from studio_audio import AudioSource
    from studio_captions import caption_frame
    total = max((row['end_frame'] for row in rows),default=None)
    sources = []
    for track in validate_audio_tracks(project['studio'],total):
        aid = track['asset_id']
        if aid not in assets.audios: raise ValueError('Audio ausente de la biblioteca segura.')
        path,metadata = assets.audios[aid]
        if abs(metadata['duration']-project['studio']['media'][aid]['duration'])>1/30:
            raise ValueError('La duración del audio cambió. Vuelve a importarlo.')
        if track['mute'] or track['volume']==0: continue
        sources.append(AudioSource('narration/'+track['id'],aid,path,assets.records[aid]['sha256'],
            caption_frame(track['start']),max(1,caption_frame(track['duration'])),caption_frame(track['trim_in']),
            max(1,caption_frame(track['trim_out']-track['trim_in'])),track['volume'],track['loop'],'narration'))
    return sources
