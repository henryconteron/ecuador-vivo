"""Private disk jobs for the scientific assistant, using the existing pipeline.

The worker never publishes a project. Its completed, hash-verified review is
input to the existing scene factory only after an explicit user action.
"""
import copy
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
import uuid

from model import STORE, validate
from jobs import write_json, read_json, sha256, process_alive
from studio_project import source_projection
from visualization_ui import capture_snapshot, scientific_identity
from studio_editing import snapshot_revision
from studio_science import generate_scientific_project, restored_snapshot, _hash

ROOT = STORE / 'scientific-preparations'


def job_path(job, root=None):
    root = Path(root or ROOT).resolve()
    job = Path(job).resolve()
    if job.parent != root or not job.is_dir():
        raise ValueError('Preparación científica fuera de su carpeta.')
    return job


def start_preparation(source, *, root=None):
    # Validate the legacy projection; Studio scenes must not reach that validator.
    from studio_project import _metadata
    _metadata(source)
    validate(source_projection(source))
    job = Path(root or ROOT) / uuid.uuid4().hex
    job.mkdir(parents=True)
    write_json(job / 'source.json', copy.deepcopy(source))
    write_json(job / 'status.json', {'state':'queued', 'progress':0,
                                   'message':'Preparación en cola', 'updated':time.time()})
    try:
        with (job / 'worker.log').open('w', encoding='utf-8') as log:
            process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), str(job)],
                stdin=subprocess.DEVNULL, stdout=log, stderr=log, close_fds=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        write_json(job / 'process.json', {'pid':process.pid})
    except Exception as error:
        write_json(job / 'status.json', {'state':'failed', 'progress':0,
                   'message':str(error), 'updated':time.time()})
        raise
    return job


def preparation_status(job, *, root=None):
    job = job_path(job, root)
    status = read_json(job / 'status.json', {})
    if not isinstance(status,dict): raise ValueError('Estado de preparación inválido.')
    amount = status.get('progress',0)
    if isinstance(amount,bool) or not isinstance(amount,(int,float)) or not math.isfinite(amount) or not 0 <= amount <= 1:
        raise ValueError('Progreso de preparación inválido.')
    if status.get('state') in ('queued','running'):
        process = read_json(job / 'process.json', {})
        if not isinstance(process,dict): raise ValueError('Estado del worker inválido.')
        pid = status.get('pid') or process.get('pid')
        if time.time() - status.get('updated', time.time()) > 10 and pid and not process_alive(pid):
            status = {**status, 'state':'failed', 'message':'La preparación se interrumpió; puedes volver a intentarla.'}
    return status


def cancel_preparation(job, *, root=None):
    job_path(job, root).joinpath('cancel.request').touch(exist_ok=True)


def execute(job, *, root=None):
    job = job_path(job, root)
    progress = 0
    def cancelled(): return (job / 'cancel.request').exists()
    def check():
        if cancelled(): raise InterruptedError('Preparación cancelada; el proyecto activo se conserva.')
    def status(state, message):
        write_json(job / 'status.json', {'state':state, 'progress':progress,
                   'message':message, 'updated':time.time(), 'pid':os.getpid()})
    def report(start, extent):
        def update(index, total, date):
            nonlocal progress
            check()
            progress = start + extent * index / total
            status('running', f'{index}/{total} · {date}')
        return update
    try:
        check()
        source = read_json(job / 'source.json')
        projection = source_projection(source)
        status('running', 'Validando y registrando archivos de origen')
        def calculate(settings):
            from data import boundary
            from endcard import summary_for_project
            return summary_for_project(settings, validate(settings), boundary(),
                progress=report(.25, .65), cancelled=cancelled)
        snapshot = restored_snapshot(source)
        if snapshot and snapshot['scientific_identity'] == scientific_identity(projection):
            status('running', 'Verificando revisión calculada y archivos originales')
            verify_sources(source, snapshot, progress=report(0, .9), cancelled=cancelled)
        else:
            snapshot = capture_snapshot(projection, calculate,
                                        progress=report(0, .25), cancelled=cancelled)
        check()
        progress = .95
        status('running', 'Guardando revisión científica verificable')
        review = {'source':source, 'snapshot':snapshot, 'revision':snapshot_revision(snapshot)}
        checksum = _hash(review)
        write_json(job / 'review.json', review)
        check()
        progress = 1
        write_json(job / 'status.json', {'state':'complete', 'progress':1,
                   'message':'Revisión científica lista', 'review_sha256':checksum,
                   'updated':time.time(), 'pid':os.getpid()})
    except InterruptedError as error: status('cancelled', str(error))
    except Exception as error:
        traceback.print_exc()
        status('failed', f'{type(error).__name__}: {error}')


def read_review(job, *, root=None):
    job = job_path(job, root)
    state = preparation_status(job, root=root)
    if state.get('state') != 'complete' or (job / 'cancel.request').exists():
        raise ValueError('La preparación no tiene una revisión completa publicable.')
    path = job / 'review.json'
    if path.stat().st_size > 64 * 1024 * 1024:
        raise ValueError('La revisión supera el límite de 64 MiB.')
    review = read_json(path)
    if not isinstance(review, dict) or _hash(review) != state.get('review_sha256'):
        raise ValueError('La revisión científica cambió; prepara una revisión nueva.')
    if snapshot_revision(review['snapshot']) != review['revision']:
        raise ValueError('Identidad de revisión inválida.')
    return review


def verify_sources(source, snapshot, *, progress=None, cancelled=None):
    if scientific_identity(source_projection(source)) != snapshot['scientific_identity']:
        raise ValueError('La fuente cambió después de la preparación; prepara una revisión nueva.')
    checked = set()
    for index, record in enumerate(snapshot['source_records']):
        if cancelled and cancelled(): raise InterruptedError('Preparación científica cancelada.')
        path = record['file']
        if path not in checked and sha256(path) != record['sha256']:
            raise ValueError('Cambió un archivo de origen; prepara una revisión nueva.')
        checked.add(path)
        if progress: progress(index + 1, len(snapshot['source_records']), record.get('date','archivo'))


def create_from_review(review, profile, *, selected=None, theme='Ecuador Vivo', title=None,
                       duration=6., cover_template='cover'):
    if isinstance(duration, bool) or not math.isfinite(duration) or not .1 <= duration <= 120:
        raise ValueError('Duración por escena: 0.1 a 120 segundos.')
    source, snapshot = review['source'], review['snapshot']
    if snapshot_revision(snapshot) != review['revision']:
        raise ValueError('La revisión científica cambió.')
    verify_sources(source, snapshot)
    selected = list(snapshot['results']) if selected is None else selected
    if not selected or len(set(selected)) != len(selected) or any(k not in snapshot['results'] for k in selected):
        raise ValueError('Selecciona resultados existentes sin duplicados.')
    if not any(snapshot['results'][k].get('value') is not None or
               any(row.get('value') is not None for row in snapshot['results'][k].get('rows',[]))
               for k in selected):
        raise ValueError('Los indicadores seleccionados están sin datos; elige al menos un resultado con valores válidos.')
    # Attach the full immutable revision. Selection affects presentation only.
    candidate = generate_scientific_project(source, snapshot, profile, theme=theme, title=title)
    active = set(candidate['studio']['timeline'])
    prefix = 'calc.' + review['revision'][:16] + '.'
    selected_ids = {prefix + rid for rid in selected}
    scenes = [s for s in candidate['studio']['scenes'] if s['id'] in active]
    visible = [s for s in scenes if all(e['data_binding']['result_id'] in selected_ids
               for e in s['elements'] if e.get('data_binding'))]
    candidate['studio']['timeline'] = [s['id'] for s in visible]
    for scene in visible: scene['duration'] = float(duration)
    if cover_template != 'cover':
        from studio_science import propose_template, apply_proposal
        if cover_template not in ('map_title','quote','methodology'):
            raise ValueError('Plantilla inicial no compatible.')
        cover = visible[0]
        candidate = apply_proposal(candidate, propose_template(candidate, cover['id'], cover_template), 'replace')
        opening = next(s for s in candidate['studio']['scenes'] if s['id'] == cover['id'])
        heading = next((e for e in opening['elements'] if e['id'] == 'title'), None)
        if heading is not None: heading['style']['text'] = title or source.get('title','Resultados científicos')
    from studio_timeline import PreparedTimeline
    for scene in candidate['studio']['scenes']:
        if scene['id'] in candidate['studio']['timeline'] and scene.get('generation'):
            scene['generation']['initial_content_sha256'] = _hash({k:v for k,v in scene.items() if k != 'generation'})
    PreparedTimeline(candidate)
    return candidate


if __name__ == '__main__': execute(sys.argv[1])
