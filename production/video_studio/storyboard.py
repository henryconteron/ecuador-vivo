"""Local media, aspect-ratio previews and an auditable, frame-exact storyboard.

Maps stay intact: output formatting never crops scientific legends or metrics.
Only user-uploaded example images/clips may explicitly opt into cropping.
"""
from __future__ import annotations

import hashlib
import copy
import math
import re
import subprocess
import time
from functools import lru_cache
from pathlib import Path

import imageio_ffmpeg
from studio_ffmpeg import read_frames
from PIL import Image, ImageDraw, ImageOps, ImageColor

from model import STORE

FORMATS = {
    'Vertical · Reels / TikTok / Shorts · 9:16': (1080, 1920),
    'Horizontal · YouTube / presentación · 16:9': (1920, 1080),
    'Cuadrado · publicaciones · 1:1': (1080, 1080),
    'Retrato · publicaciones · 4:5': (1080, 1350),
    'Horizontal clásico · 4:3': (1440, 1080),
}
DEFAULT_FORMAT = next(iter(FORMATS))
MEDIA_ROOT = STORE / 'media'
IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.webp'}
VIDEO_SUFFIXES = {'.mp4', '.mov', '.webm', '.mkv'}
KINDS = {'map', 'endcard', 'snapshot', 'image', 'video', 'text'}


def digest(path):
    path = Path(path)
    info = path.stat()
    return _digest_cached(str(path.resolve()), info.st_mtime_ns, info.st_size)


@lru_cache(maxsize=64)
def _digest_cached(path, modified, size):
    value = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def dimensions(config):
    delivery = config.get('delivery', {})
    if 'output_profile' in delivery:
        from output_profiles import profile_for
        profile = profile_for(delivery['output_profile'])
        return profile.width, profile.height
    name = delivery.get('format', DEFAULT_FORMAT)
    if name not in FORMATS:
        raise ValueError('Formato de video no admitido.')
    quality = delivery.get('quality', '720p' if config.get('width') == 720 else '1080p')
    if quality not in ('1080p', '720p'):
        raise ValueError('Elige calidad 1080p o 720p.')
    width, height = FORMATS[name]
    factor = 2 / 3 if quality == '720p' else 1
    # yuv420p requires even dimensions, including 4:5 at 720p.
    return tuple(round(value * factor / 2) * 2 for value in (width, height))


def delivery_background(config):
    color = config.get('delivery', {}).get('background', config.get('background', '#04151e'))
    if not isinstance(color, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', color):
        raise ValueError('Fondo del formato inválido.')
    return color


def fit_image(image, size, *, background='#04151e', fit='contain'):
    if fit not in ('contain', 'cover'):
        raise ValueError('Encuadre inválido.')
    image = ImageOps.exif_transpose(image).convert('RGBA')
    if fit == 'cover':
        return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS).convert('RGB')
    piece = ImageOps.contain(image, size, method=Image.Resampling.LANCZOS)
    canvas = Image.new('RGB', size, background)
    canvas.paste(piece, ((size[0]-piece.width)//2, (size[1]-piece.height)//2), piece)
    return canvas


def format_preview(image, config):
    return fit_image(image, dimensions(config), background=delivery_background(config))


def media_path(value):
    path = Path(str(value)).resolve()
    if not path.is_relative_to(MEDIA_ROOT.resolve()) or not path.is_file():
        raise ValueError('Falta un recurso del montaje. Vuelve a importarlo en Formato y secuencia.')
    if path.suffix.lower() not in IMAGE_SUFFIXES | VIDEO_SUFFIXES:
        raise ValueError('Tipo de recurso no admitido.')
    return path


def probe_video(path, *, content_hash=None):
    """Read local decoder metadata; never shell out with a string or network URL."""
    path = Path(path)
    info = path.stat()
    return copy.deepcopy(_probe_cached(str(path.resolve()), info.st_mtime_ns, info.st_size, content_hash))


@lru_cache(maxsize=64)
def _probe_cached(path, modified, size, content_hash=None):
    reader = read_frames(str(path), input_params=['-protocol_whitelist', 'file,pipe'])
    try:
        metadata = next(reader)
    finally:
        reader.close()
    duration = float(metadata.get('duration', 0))
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError('No se pudo determinar la duración de este clip.')
    return {'duration': duration, 'size': list(metadata['size']),
            'audio': metadata.get('audio_codec') not in (None, '', 'none')}


def store_media(content, name):
    """Content-addressed copies: repeated imports never duplicate the same file."""
    suffix = Path(name).suffix.lower()
    if suffix not in IMAGE_SUFFIXES | VIDEO_SUFFIXES:
        raise ValueError('Importa PNG, JPG, WebP, MP4, MOV, WebM o MKV.')
    if not content or len(content) > 100 * 1024 * 1024:
        raise ValueError('El recurso debe ocupar entre 1 byte y 100 MB. Recorta/comprime el clip primero.')
    if suffix in IMAGE_SUFFIXES:
        import io
        with Image.open(io.BytesIO(content)) as image:
            if image.width * image.height > 40_000_000:
                raise ValueError('La imagen excede 40 megapíxeles. Reduce su tamaño antes de importar.')
            image.verify()
    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    sha = hashlib.sha256(content).hexdigest()
    target = MEDIA_ROOT / (sha + suffix)
    if not target.exists():
        target.write_bytes(content)
    metadata = probe_video(target) if suffix in VIDEO_SUFFIXES else {}
    return {'path': str(target), 'sha256': sha, 'name': Path(name).name,
            'kind': 'video' if suffix in VIDEO_SUFFIXES else 'image', **metadata}


def cards_for(config):
    storyboard = config.get('storyboard', {})
    if storyboard.get('enabled'):
        cards = storyboard.get('cards', [])
    else:
        cards = [{'id': 'map', 'kind': 'map', 'label': 'Mapa', 'duration': None}]
        if config.get('endcard_enabled', True):
            cards.append({'id': 'endcard', 'kind': 'endcard', 'label': 'Métricas', 'duration': None})
    if not isinstance(cards, list) or not 1 <= len(cards) <= 30:
        raise ValueError('La secuencia debe contener entre 1 y 30 tarjetas.')
    if any(not isinstance(row, dict) for row in cards):
        raise ValueError('Tarjeta inválida.')
    if sum(row.get('kind') == 'map' for row in cards) != 1:
        raise ValueError('La secuencia necesita exactamente una tarjeta del mapa animado.')
    ids = [row.get('id') for row in cards]
    if any(not isinstance(value, str) or not value or len(value) > 100 for value in ids) or len(set(ids)) != len(ids):
        raise ValueError('Identificadores de tarjetas inválidos o repetidos.')
    result = []
    for row in cards:
        if not isinstance(row, dict) or row.get('kind') not in KINDS:
            raise ValueError('Tarjeta desconocida.')
        row = dict(row)
        default = config.get('duration', 20) if row['kind'] == 'map' else config.get('endcard_duration', 6) if row['kind'] == 'endcard' else 6
        seconds = float(row.get('duration') if row.get('duration') is not None else default)
        if not math.isfinite(seconds) or not 1/30 <= seconds <= (3600 if row['kind'] == 'map' else 300):
            raise ValueError('Duración de tarjeta fuera de rango.')
        row['frames'] = max(1, round(seconds * 30))
        row['seconds'] = row['frames'] / 30
        row['fit'] = row.get('fit', 'contain')
        if row['fit'] not in ('contain', 'cover'):
            raise ValueError('Encuadre inválido.')
        if 'data_visualization' in row:
            from visualizations import validate_snapshot
            if row['kind'] != 'image' or row['fit'] != 'contain':
                raise ValueError('Una visualización científica se encaja completa, sin recorte.')
            validate_snapshot(row['data_visualization'])
        if row['kind'] in ('image', 'video'):
            path = media_path(row.get('path'))
            if row['kind'] == 'image' and path.suffix.lower() not in IMAGE_SUFFIXES:
                raise ValueError('Esta tarjeta necesita una imagen.')
            if row['kind'] == 'video':
                if path.suffix.lower() not in VIDEO_SUFFIXES:
                    raise ValueError('Esta tarjeta necesita un clip.')
                metadata = probe_video(path)
                start = float(row.get('start', 0))
                if not math.isfinite(start) or start < 0 or start + row['seconds'] > metadata['duration'] + .04:
                    raise ValueError(f'El fragmento de «{row.get("label", "clip") }» excede la duración del video original.')
                row.update(start=start, has_audio=metadata['audio'])
            if row.get('sha256') and digest(path) != row['sha256']:
                raise ValueError('Un recurso del montaje cambió después de importarse. Vuelve a importarlo.')
            if 'data_visualization' in row:
                from visualizations import verify_snapshot_image
                if row.get('sha256')!=row['data_visualization']['image_sha256']:
                    raise ValueError('El PNG cambió respecto a la instantánea científica.')
                verify_snapshot_image(row['data_visualization'],path)
            row['path'] = str(path)
        for field in ('title', 'body', 'citation', 'label'):
            if len(str(row.get(field, ''))) > (600 if field == 'body' else 300):
                raise ValueError(f'Texto de tarjeta demasiado largo: {field}.')
        result.append(row)
    if sum(row['seconds'] for row in result) > 7200:
        raise ValueError('La secuencia excede dos horas.')
    return result


def base_timing(config):
    """Resolve timeline durations BEFORE generating maps/metrics, not by speed-up."""
    config = dict(config)
    cards = cards_for(config)
    config['duration'] = next(row['seconds'] for row in cards if row['kind'] == 'map')
    closing = next((row for row in cards if row['kind'] == 'endcard'), None)
    config['endcard_enabled'] = closing is not None
    if closing:
        config['endcard_duration'] = closing['seconds']
    dimensions(config)
    delivery_background(config)
    return config


def overlay_card(row, config, *, text_only=False):
    """Readable captions/credits, rendered at the actual output size."""
    from editorial import text_box
    size = dimensions(config)
    width, height = size
    factor = min(width / 1080, height / 1350)
    margin, band = round(60 * factor), round(170 * factor)
    image = Image.new('RGBA', size, delivery_background(config) if text_only else (0, 0, 0, 0))
    d = ImageDraw.Draw(image)
    title, credit = str(row.get('title', '')), str(row.get('citation', ''))
    if text_only:
        # Text scenes use the whole selected format, with larger type and a
        # readable column rather than one extremely long horizontal line.
        type_factor = min(width/1080, height/1080)
        left, right = round(width*.1), round(width*.9)
        d.line((left, round(height*.11), right, round(height*.11)), fill='#367a92', width=2)
        if title:
            text_box(image, title, (left, round(height*.15), right, round(height*.32)),
                size=max(32,round(74*type_factor)), min_size=max(20,round(34*type_factor)),
                bold=True, display=True, lines=2, color='#59eddf', align='center')
        text_box(image, str(row.get('body', '')), (left, round(height*.38), right, round(height*.78)),
            size=max(30,round(60*type_factor)), min_size=max(20,round(32*type_factor)),
            lines=9, color='#ffffff', align='center')
        if credit:
            d.line((left, round(height*.85), right, round(height*.85)), fill='#367a92', width=2)
            text_box(image, credit, (left, round(height*.88), right, round(height*.96)),
                size=max(20,round(30*type_factor)), min_size=max(14,round(20*type_factor)),
                lines=3, color='#d3e5ed', align='center')
        return image
    if title:
        d.rectangle((0, 0, width, band), fill=delivery_background(config))
        text_box(image, title, (margin, margin//2, width-margin, band-margin//3),
                 size=round(52*factor), min_size=max(15, round(28*factor)), bold=True, lines=2, color='#59eddf')
    if credit:
        d.rectangle((0, height-band, width, height), fill=delivery_background(config))
        text_box(image, credit, (margin, height-band+margin//3, width-margin, height-margin//2),
                 size=round(30*factor), min_size=max(12, round(20*factor)), lines=3, color='#d3e5ed')
    return image


def card_preview(row, config):
    if row['kind'] == 'text':
        return overlay_card(row, config, text_only=True).convert('RGB')
    if row['kind'] not in ('image', 'video'):
        return None
    path = media_path(row.get('path'))
    if row['kind'] == 'image':
        with Image.open(path) as source:
            image = ImageOps.exif_transpose(source).copy()
    else:
        reader = read_frames(str(path), pix_fmt='rgb24',
            input_params=['-protocol_whitelist', 'file,pipe', '-ss', str(row.get('start', 0))])
        try:
            metadata = next(reader)
            image = Image.frombytes('RGB', tuple(metadata['size']), next(reader))
        finally:
            reader.close()
    size = dimensions(config)
    width, height = size
    band = round(170 * min(width / 1080, height / 1350))
    top, bottom = band if row.get('title') else 0, band if row.get('citation') else 0
    piece = fit_image(image, (width, height-top-bottom), background=delivery_background(config), fit=row.get('fit', 'contain'))
    canvas = Image.new('RGBA', size, delivery_background(config))
    canvas.paste(piece, (0, top))
    canvas.alpha_composite(overlay_card(row, config))
    return canvas.convert('RGB')


def _run(args, job):
    """Poll cancellation while encoding, without blocking the UI process."""
    with (job / 'montage.log').open('a', encoding='utf-8') as log:
        proc = subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error',
            '-nostdin', '-y', *args], stdin=subprocess.DEVNULL, stdout=log, stderr=log,
            creationflags=subprocess.CREATE_NO_WINDOW if __import__('os').name == 'nt' else 0)
        while proc.poll() is None:
            if (job / 'cancel.request').exists():
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                raise InterruptedError('Montaje cancelado; se conservan los archivos fuente.')
            time.sleep(.1)
        if proc.returncode:
            tail = (job / 'montage.log').read_text(encoding='utf-8', errors='replace')[-1800:]
            raise ValueError('No se pudo ensamblar una tarjeta. ' + tail)


def assemble(job, source, config, *, map_duration, endcard_duration, status=None):
    """Produce final MP4; atomic completion occurs only in the caller afterwards."""
    job, source = Path(job), Path(source)
    cards = cards_for(config)
    width, height = dimensions(config)
    background = delivery_background(config)
    requires = config.get('storyboard', {}).get('enabled') or (width, height) != (1080, 1920)
    if not requires:
        return source, {'width': width, 'height': height, 'fps': 30,
                        'duration_seconds': map_duration + endcard_duration,
                        'cards': [{'kind': row['kind'], 'duration_seconds': row['seconds']} for row in cards]}
    stages = job / 'montage'
    stages.mkdir(exist_ok=True)
    clips, receipts = [], []
    common = ['-r', '30', '-c:v', 'libx264', '-crf', str(config.get('crf', 18)), '-preset', 'fast',
              '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-ar', '48000', '-ac', '2',
              '-video_track_timescale', '15360', '-movflags', '+faststart']
    for index, row in enumerate(cards):
        if (job / 'cancel.request').exists():
            raise InterruptedError('Montaje cancelado.')
        if status:
            status(f'Montando tarjeta {index+1}/{len(cards)} · {row.get("label", row["kind"])}')
        target = stages / f'{index:02d}.mp4'
        inputs, media, static = [], None, False
        if row['kind'] == 'map':
            inputs = ['-i', str(source)]
            # The base renderer generated EXACTLY this duration already.
            frames = round(map_duration * 30)
        elif row['kind'] == 'endcard':
            media, static, frames = job / 'endcard.png', True, row['frames']
        elif row['kind'] == 'snapshot':
            media, static, frames = stages / f'{index:02d}-snapshot.png', True, row['frames']
            _run(['-ss', str(max(0, map_duration - 1/30)), '-i', str(source), '-frames:v', '1', str(media)], job)
        elif row['kind'] in ('image', 'text'):
            media, static, frames = stages / f'{index:02d}-card.png', True, row['frames']
            card_preview(row, config).save(media)
        else:
            inputs = ['-protocol_whitelist', 'file,pipe', '-ss', str(row['start']), '-i', row['path']]
            frames = row['frames']
        if static:
            inputs = ['-loop', '1', '-framerate', '30', '-i', str(media)]
        # Cropping is confined to explicitly chosen example clips. Maps and
        # calculated cards always use uniform scaling + padding.
        cover = row['kind'] == 'video' and row['fit'] == 'cover'
        band = round(170 * min(width / 1080, height / 1350))
        # Even rectangles for yuv420p; caption strips do not cover the clip.
        top = (band // 2 * 2) if row['kind'] == 'video' and row.get('title') else 0
        bottom = (band // 2 * 2) if row['kind'] == 'video' and row.get('citation') else 0
        slot_height = height-top-bottom
        vf = (f'scale={width}:{slot_height}:force_original_aspect_ratio=increase,crop={width}:{slot_height}' if cover else
              f'scale={width}:{slot_height}:force_original_aspect_ratio=decrease,pad={width}:{slot_height}:(ow-iw)/2:(oh-ih)/2:color=0x{background[1:]}')
        if top or bottom:
            vf += f',pad={width}:{height}:0:{top}:color=0x{background[1:]}'
        # The scientific base is already an exact 30 fps frame sequence.
        # Resampling it again can discard its last frame at a short EOF.
        vf += (',setsar=1,setpts=N/(30*TB)' if row['kind'] == 'map'
               else ',setsar=1,fps=30,setpts=PTS-STARTPTS')
        sound = row['kind'] == 'video' and row.get('audio', False) and row.get('has_audio')
        overlay = row['kind'] == 'video' and bool(row.get('title') or row.get('citation'))
        args = list(inputs)
        if overlay:
            plate = stages / f'{index:02d}-overlay.png'
            overlay_card(row, config).save(plate)
            args += ['-loop', '1', '-framerate', '30', '-i', str(plate)]
        silence_index = 2 if overlay else 1
        if not sound:
            args += ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo']
        if overlay:
            args += ['-filter_complex', f'[0:v]{vf}[base];[base][1:v]overlay=0:0:shortest=1[v]', '-map', '[v]']
        else:
            args += ['-vf', vf, '-map', '0:v:0']
        args += ['-map', '0:a:0' if sound else f'{silence_index}:a:0', '-af', 'apad,asetpts=PTS-STARTPTS',
                 '-frames:v', str(frames), '-t', str(frames / 30), *common, str(target)]
        _run(args, job)
        clips.append(target)
        receipts.append({key: row[key] for key in ('id', 'kind', 'label', 'title', 'citation', 'sha256', 'start', 'fit', 'audio', 'data_visualization') if key in row})
        receipts[-1].update(duration_seconds=frames/30, frames=frames)
        if row['kind'] in ('image', 'video'):
            receipts[-1]['sha256'] = digest(row['path'])
    listing = stages / 'clips.txt'
    # Only internally-generated relative filenames reach the concat demuxer.
    listing.write_text(''.join(f"file '{clip.name}'\n" for clip in clips), encoding='utf-8')
    result = job / 'montaje-incompleto.mp4'
    # AAC packet boundaries can introduce gaps between segments. Normalize the
    # final timeline to an exact number of CFR frames rather than copying those
    # timestamps (which can create duplicate frames and longer videos).
    total_frames = sum(row['frames'] for row in receipts)
    _run(['-f', 'concat', '-safe', '1', '-i', str(listing),
          '-vf', 'fps=30,setpts=N/(30*TB)', '-af', 'aresample=async=1:first_pts=0,apad',
          '-frames:v', str(total_frames), '-t', str(total_frames/30), *common, str(result)], job)
    return result, {'width': width, 'height': height, 'fps': 30, 'fit_scientific_cards': 'contain; never crop',
                    'duration_seconds': sum(row['duration_seconds'] for row in receipts), 'cards': receipts,
                    'original_map_seconds': map_duration, 'original_endcard_seconds': endcard_duration}
