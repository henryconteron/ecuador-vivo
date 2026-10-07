"""Disk-backed render jobs. Browser reruns never restart an export."""
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
import uuid

import imageio_ffmpeg
import numpy as np

from model import STORE, validate, frame_counts
from data import boundary, load_values, sha256
from render import compose
from endcard import SummaryAccumulator, compose_endcard
from variables import endcard_copy


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    # Windows readers may briefly have the destination open during polling.
    for attempt in range(20):
        try:
            temp.replace(path)
            return
        except PermissionError:
            if attempt == 19:
                raise
            time.sleep(.05)


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return default


def process_alive(pid):
    """Query only; never signal/terminate a process (notably on Windows)."""
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        api = ctypes.WinDLL('kernel32', use_last_error=True)
        api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        api.OpenProcess.restype = wintypes.HANDLE
        api.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        api.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = api.OpenProcess(0x1000, False, pid)
        if not handle:
            return ctypes.get_last_error() != 87  # Access denied is not evidence of death.
        try:
            code = wintypes.DWORD()
            return not api.GetExitCodeProcess(handle, ctypes.byref(code)) or code.value == 259
        finally:
            api.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def statuses():
    result = []
    for path in sorted((STORE / 'jobs').glob('*/status.json'), reverse=True):
        state = read_json(path, {})
        age = time.time() - state.get('updated', time.time())
        if state.get('state') in ('queued', 'running') and age > 10:
            dead = not process_alive(state['pid']) if state.get('pid') else age > 120
            if dead:
                # Re-read after the process check in case it just finished writing.
                fresh = read_json(path, {})
                if fresh == state:
                    state.update(state='failed', message='El proceso se interrumpió. Puedes generar otra exportación; se conservan los datos.', updated=time.time())
                    write_json(path, state)
        result.append((path.parent, state))
    return result


def start_job(project):
    from storyboard import base_timing
    project = base_timing(project)
    validate(project)
    job = STORE / 'jobs' / (dt.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8])
    job.mkdir(parents=True)
    write_json(job / 'project.json', project)
    write_json(job / 'status.json', {'state': 'queued', 'progress': 0, 'message': 'Preparando exportación', 'updated': time.time()})
    log = (job / 'worker.log').open('w', encoding='utf-8')
    try:
        subprocess.Popen([sys.executable, str(Path(__file__).resolve()), str(job)],
                         stdin=subprocess.DEVNULL, stdout=log, stderr=log, close_fds=True,
                         creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    except Exception as error:
        write_json(job / 'status.json', {'state': 'failed', 'progress': 0, 'message': str(error), 'updated': time.time()})
        raise
    finally:
        log.close()
    return job


def execute(job):
    job = Path(job).resolve()
    if not job.is_relative_to((STORE / 'jobs').resolve()):
        raise ValueError('Carpeta de trabajo no válida.')
    writer = None
    progress = 0
    def status(state, message):
        write_json(job / 'status.json', {'state': state, 'progress': progress,
                   'message': message, 'updated': time.time(), 'pid': os.getpid()})
    try:
        from storyboard import base_timing, assemble
        p = base_timing(read_json(job / 'project.json'))
        rows = validate(p)
        counts = frame_counts(len(rows), p['duration'])
        status('running', 'Preparando mapa y datos')
        shape = boundary()
        summary = SummaryAccumulator(p, shape)
        receipt = {'project': p, 'temporal_interpolation': False, 'frames_per_date': counts,
                   'boundary_source': 'geoBoundaries · https://www.geoboundaries.org/',
                   'map_duration_seconds': sum(counts)/30,
                   'endcard_duration_seconds': (
                       p['endcard_duration'] if p.get('endcard_enabled', True) else 0
                   ),
                   'duration_seconds': sum(counts)/30 + (
                       p['endcard_duration'] if p.get('endcard_enabled', True) else 0
                   ),
                   'galapagos': {
                       'enabled': bool(p.get('show_galapagos', True)
                                       and p.get('clip_ecuador', False)),
                       'bbox': [-92.2, -1.8, -88.8, 1.9],
                       'source_note': 'Mismos rásteres y misma escala visual que el mapa '
                                      'principal. Para el ranking provincial se usa la media '
                                      'de píxeles fuente válidos; NoData permanece sin dato y '
                                      'el océano no entra en las estadísticas.'
                   },
                   'source_records': [], 'complete': False}
        partial = job / 'video-incompleto.mp4'
        writer = imageio_ffmpeg.write_frames(str(partial), (p['width'], p['width']*16//9),
            fps=30, codec='libx264', pix_fmt_in='rgb24', pix_fmt_out='yuv420p', macro_block_size=1,
            output_params=['-crf', str(p['crf']), '-preset', 'fast', '-movflags', '+faststart'])
        writer.send(None)
        hashes = {}
        for i, row in enumerate(rows):
            if (job / 'cancel.request').exists():
                raise InterruptedError('Exportación cancelada. El archivo parcial no es un video terminado.')
            status('running', f'{i+1}/{len(rows)} · preparando {row["date"]}')
            values, metadata = load_values(
                p, row, province_features=summary.rank_features
            )
            summary.observe(
                row['date'], values,
                metadata.get('point_samples'), metadata.get('province_samples'),
                metadata.get('province_extremes')
            )
            path = metadata['path']
            if path not in hashes:
                hashes[path] = sha256(path)
            frame = compose(p, values, shape, row['date'], i, len(rows))
            pixels = np.asarray(frame)
            for n in range(counts[i]):
                if n % 30 == 0 and (job / 'cancel.request').exists():
                    raise InterruptedError('Exportación cancelada por el usuario.')
                writer.send(pixels)
            if i in (0, len(rows)-1):
                frame.save(job / f'frame-{row["date"]}.png')
            metadata.update(date=row['date'], sha256=hashes[path])
            receipt['source_records'].append(metadata)
            progress = (i+1)/len(rows)
            status('running', f'{i+1}/{len(rows)} · {row["date"]}')

        if p.get('endcard_enabled', True):
            status('running', 'Dibujando cierre con métricas')
            summary_data = summary.to_dict()
            display_copy = endcard_copy(p, summary_data)
            endcard = compose_endcard(p, summary_data)
            endcard.save(job / 'endcard.png')
            endcard_pixels = np.asarray(endcard)
            endcard_frames = max(1, round(p['endcard_duration'] * p['fps']))
            for frame_index in range(endcard_frames):
                if frame_index % 30 == 0 and (job / 'cancel.request').exists():
                    raise InterruptedError('Exportación cancelada durante el cierre.')
                writer.send(endcard_pixels)
            receipt['endcard'] = {
                'enabled': True,
                'duration_seconds': endcard_frames / p['fps'],
                'frames': endcard_frames,
                'summary': summary_data,
                'display_copy': display_copy,
            }
        else:
            receipt['endcard'] = {'enabled': False}
        writer.close()
        writer = None
        if (job / 'cancel.request').exists():
            raise InterruptedError('Exportación cancelada antes de finalizar.')
        final = job / 'ecuador-vivo.mp4'
        status('running', 'Ajustando formato y secuencia')
        assembled, montage = assemble(job, partial, p, map_duration=receipt['map_duration_seconds'],
            endcard_duration=receipt['endcard_duration_seconds'], status=lambda message: status('running', message))
        if (job / 'cancel.request').exists():
            raise InterruptedError('Exportación cancelada antes de finalizar el montaje.')
        assembled.replace(final)
        receipt.update(montage=montage, duration_seconds=montage['duration_seconds'])
        receipt.update(complete=True, video_sha256=sha256(final))
        write_json(job / 'receipt.json', receipt)
        status('complete', 'Video terminado')
    except InterruptedError as error:
        status('cancelled', str(error))
    except Exception as error:
        traceback.print_exc()
        status('failed', f'{type(error).__name__}: {error}')
    finally:
        if writer is not None:
            writer.close()


if __name__ == '__main__':
    execute(sys.argv[1])
