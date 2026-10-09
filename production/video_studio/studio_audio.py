"""Bounded audio scheduling/mixing; providers never perform scientific work.

AudioSource is the extension boundary for later narration/music/SFX providers.
Only the video provider is exposed today. No project version change is needed.
"""
from contextlib import ExitStack
from dataclasses import asdict, dataclass
import hashlib
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import numpy as np
import imageio_ffmpeg

SAMPLE_RATE=48000
SAMPLES_PER_FRAME=SAMPLE_RATE//30
CHANNELS=2
SAMPLE_BYTES=CHANNELS*4
PCM_BUDGET=8*1024**3


def audio_settings(style):
    mute=style.get('mute',True);volume=style.get('volume',1.)
    if type(mute) is not bool: raise ValueError('Mute debe ser booleano.')
    if isinstance(volume,bool) or not isinstance(volume,(int,float)) or not 0<=volume<=2 or not math.isfinite(volume):
        raise ValueError('Volumen debe ser una ganancia finita entre 0 y 2.')
    return mute,float(volume)


@dataclass(frozen=True)
class AudioSource:
    id: str
    asset_id: str
    path: Path
    sha256: str
    start_frame: int
    duration_frames: int
    trim_frame: int
    clip_frames: int
    gain: float
    loop: bool
    kind: str='video'

    def receipt(self):
        value=asdict(self);value.pop('path');return value


def video_sources(project,rows,assets):
    """Adapt visible clips to an immutable, global frame schedule."""
    scenes={scene['id']:scene for scene in project['studio']['scenes']};sources=[]
    for row in rows:
        for element in scenes[row['id']]['elements']:
            if element['type']!='video': continue
            style=element.get('style',{});mute,gain=audio_settings(style)
            aid=style.get('asset_id')
            if aid not in assets.videos: raise ValueError('Video ausente de la biblioteca segura.')
            path,metadata=assets.videos[aid]
            start,end=style.get('trim_in',0),style.get('trim_out',metadata['duration'])
            if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in (start,end)) or not 0<=start<end<=metadata['duration']+.001:
                raise ValueError('Trim del audio fuera de la duración del video.')
            loop=style.get('loop',False)
            if type(loop) is not bool: raise ValueError('Loop debe ser booleano.')
            if mute or gain==0 or not element.get('visible',True) or element.get('editor_deleted',False) or not metadata.get('audio',False): continue
            sources.append(AudioSource(row['id']+'/'+element['id'],aid,path,assets.records[aid]['sha256'],
                row['start_frame'],row['end_frame']-row['start_frame'],round(start*30),
                max(1,round((end-start)*30)),gain,loop))
    return sources


def _check_cancel(cancelled):
    if cancelled and cancelled(): raise InterruptedError('Mezcla cancelada; se conserva el borrador.')


def _run(args,folder,*,cancelled=None,stdout=None):
    """Poll a local FFmpeg process; always reap it and close owned handles."""
    _check_cancel(cancelled)
    with tempfile.TemporaryFile(dir=folder) as errors:
        process=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-nostdin',*args],
            stdin=subprocess.DEVNULL,stdout=stdout if stdout is not None else subprocess.DEVNULL,
            stderr=errors,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        started=time.monotonic()
        try:
            while process.poll() is None:
                _check_cancel(cancelled)
                if time.monotonic()-started>7200: raise ValueError('FFmpeg excedió el tiempo de procesamiento de audio.')
                time.sleep(.05)
            if process.returncode:
                errors.seek(0);detail=errors.read(8192).decode(errors='replace')
                raise ValueError('FFmpeg no pudo procesar audio: '+detail)
        finally:
            if process.poll() is None: process.terminate()
            try: process.wait(timeout=5)
            except subprocess.TimeoutExpired: process.kill();process.wait()


def _verify(sources):
    for path,digest in {(source.path,source.sha256) for source in sources}:
        if path.stat().st_size>100*1024**2 or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError('El recurso de audio cambió; vuelve a importarlo.')


def _decode_key(source):
    frames=source.clip_frames if source.loop else min(source.clip_frames,source.duration_frames)
    return source.path,source.sha256,source.trim_frame,frames


def mix_pcm(sources,total_frames,folder,*,cancelled=None,progress=None,extra_bytes=0):
    """Sum gains without normalization; disk loops keep working memory bounded.

    Source PTS gaps are filled before trim, aligning audio to the global CFR
    grid used by AssetFrames. EOF is padded with silence, never held sound.
    """
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=False)
    total_samples=total_frames*SAMPLES_PER_FRAME
    keys=list(dict.fromkeys(_decode_key(source) for source in sources))
    budget=(2*total_samples+sum(key[3]*SAMPLES_PER_FRAME for key in keys))*SAMPLE_BYTES
    if budget>PCM_BUDGET or shutil.disk_usage(folder).free<budget+extra_bytes+32*1024**2:
        raise ValueError('Audio excede el presupuesto PCM de 8 GiB o el espacio libre; reduce duración/recursos.')
    _verify(sources)
    decoded={}
    for index,key in enumerate(keys):
        path,digest,start,frames=key;count=frames*SAMPLES_PER_FRAME
        output=folder/f'source-{index}.f32'
        # https://ffmpeg.org/ffmpeg-filters.html#aresample-1 and #atrim
        filters=f'aresample=48000:async=1:first_pts=0:min_hard_comp=0,atrim=start_sample={start*SAMPLES_PER_FRAME}:end_sample={(start+frames)*SAMPLES_PER_FRAME},asetpts=PTS-STARTPTS,apad=whole_len={count},atrim=end_sample={count}'
        with output.open('xb') as stream:
            _run(['-protocol_whitelist','file,pipe','-copyts','-start_at_zero','-i',str(path),
                '-map','0:a:0','-vn','-af',filters,'-ac','2','-ar','48000','-f','f32le','pipe:1'],
                folder,cancelled=cancelled,stdout=stream)
        if output.stat().st_size!=count*SAMPLE_BYTES: raise ValueError('Decodificación de audio incompleta.')
        decoded[key]=output
    mixed_path=folder/'mix.f32'
    with ExitStack() as stack:
        streams={key:stack.enter_context(path.open('rb')) for key,path in decoded.items()}
        output=stack.enter_context(mixed_path.open('xb'))
        for start in range(0,total_samples,SAMPLE_RATE):
            _check_cancel(cancelled);count=min(SAMPLE_RATE,total_samples-start)
            mixed=np.zeros((count,CHANNELS),dtype=np.float64)
            for source in sources:
                left=max(start,source.start_frame*SAMPLES_PER_FRAME)
                right=min(start+count,(source.start_frame+source.duration_frames)*SAMPLES_PER_FRAME)
                if left>=right: continue
                key=_decode_key(source);length=key[3]*SAMPLES_PER_FRAME;cursor=left-source.start_frame*SAMPLES_PER_FRAME
                if not source.loop: right=min(right,left+length-cursor)
                while left<right:
                    position=cursor%length if source.loop else cursor
                    take=min(right-left,length-position);stream=streams[key]
                    stream.seek(position*SAMPLE_BYTES);raw=stream.read(take*SAMPLE_BYTES)
                    if len(raw)!=take*SAMPLE_BYTES: raise ValueError('PCM de origen incompleto.')
                    samples=np.frombuffer(raw,dtype='<f4').reshape(-1,CHANNELS)
                    mixed[left-start:left-start+take]+=samples*source.gain
                    left+=take;cursor+=take
            if not np.isfinite(mixed).all(): raise ValueError('Audio no finito; no se publicará.')
            output.write(mixed.astype('<f4').tobytes())
            if progress: progress((start+count)/total_samples)
    _verify(sources)
    return mixed_path


def _decoded_peak(path,folder,cancelled):
    pcm=folder/'peak.f32'
    with pcm.open('wb') as output:
        _run(['-i',str(path),'-map','0:a:0','-ac','2','-ar','48000','-f','f32le','pipe:1'],
            folder,cancelled=cancelled,stdout=output)
    peak=0.
    with pcm.open('rb') as stream:
        while raw:=stream.read(SAMPLE_RATE*SAMPLE_BYTES):
            _check_cancel(cancelled)
            samples=np.frombuffer(raw,dtype='<f4')
            if not np.isfinite(samples).all(): raise ValueError('AAC decodificado no finito.')
            peak=max(peak,float(np.max(np.abs(samples))))
    return peak


def mux_audio(video,sources,total_frames,*,cancelled=None,progress=None):
    """Reuse encoded video; verify final AAC peak before replacing staging MP4."""
    if not sources: return 'silent'
    video=Path(video)
    with tempfile.TemporaryDirectory(prefix='.studio-audio-',dir=video.parent) as directory:
        folder=Path(directory)
        candidate_budget=video.stat().st_size+math.ceil(total_frames/30*40000)+1024**2
        pcm=mix_pcm(sources,total_frames,folder/'pcm',cancelled=cancelled,progress=progress,extra_bytes=candidate_budget)
        candidate=folder/'mixed.mp4';gain=1.;peak=None
        for attempt in range(3):
            # Disable default auto-level and compensate lookahead delay.
            # https://ffmpeg.org/ffmpeg-filters.html#alimiter
            filters=f'alimiter=limit=0.90:attack=5:release=50:level=0:latency=1,volume={gain}'
            _run(['-y','-i',str(video),'-f','f32le','-ar','48000','-ac','2','-i',str(pcm),
                '-map','0:v:0','-map','1:a:0','-c:v','copy','-af',filters,'-c:a','aac','-b:a','320k',
                '-ar','48000','-ac','2','-t',str(total_frames/30),'-movflags','+faststart',str(candidate)],
                folder,cancelled=cancelled)
            peak=_decoded_peak(candidate,folder,cancelled)
            if peak<=.98: break
            gain*=.95/peak
        else: raise ValueError('El AAC excede el techo de picos; no se publicará.')
        _check_cancel(cancelled);_verify(sources)
        candidate.replace(video)
        return {'mode':'original_clip_mix','sample_rate':SAMPLE_RATE,'channels':CHANNELS,
            'samples_per_frame':SAMPLES_PER_FRAME,'total_samples':total_frames*SAMPLES_PER_FRAME,
            'limiter_ceiling':.90,'lookahead_compensated':True,'decoded_peak':peak,'post_limiter_gain':gain,
            'sources':[source.receipt() for source in sources]}
