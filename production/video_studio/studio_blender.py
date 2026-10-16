"""Local Blender integration: finite recipes, explicit jobs, no engine at startup."""
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys

VERSION='orographic-blender-v2'
BLENDER_VERSION='4.5.4'
MODES=('poster','preview','final')


def default_recipe():
    return dict(version=VERSION,model='orographic',fps=30,duration=10.,
        yaw=25.,pitch=28.,distance=12.,orbit=12.,mountain=2.4,
        moist=True,rain=True,light=1000.,background='#04151e',
        ground='#418776',rock='#bf986b',water='#57ccec')


def validate_recipe(value):
    defaults=default_recipe()
    if not isinstance(value,dict) or set(value)!=set(defaults):
        raise ValueError('Receta 3D incompleta o con campos no permitidos; no admite código ni rutas.')
    if value['version']!=VERSION or value['model']!='orographic' or type(value['fps']) is not int or value['fps']!=30:
        raise ValueError('Versión, modelo o reloj 3D no compatibles.')
    for field,low,high in [('duration',1,30),('yaw',-80,80),('pitch',10,70),('distance',8,20),('orbit',0,45),('mountain',1,3.5),('light',100,3000)]:
        number=value[field]
        if type(number) not in (int,float) or not math.isfinite(number) or not low<=number<=high:
            raise ValueError(field+': número finito fuera de rango.')
    for field in ('moist','rain'):
        if type(value[field]) is not bool:raise ValueError(field+': opción inválida.')
    for field in ('background','ground','rock','water'):
        if not isinstance(value[field],str) or not re.fullmatch(r'#[a-fA-F0-9]{6}',value[field]):
            raise ValueError(field+': usa un color #RRGGBB.')
    return copy.deepcopy(value)


def recipe_identity(recipe):
    return hashlib.sha256(json.dumps(validate_recipe(recipe),sort_keys=True,allow_nan=False).encode()).hexdigest()


def tools_root():
    from model import STORE
    return Path(STORE)/'tools'


def blender_executable():
    path=tools_root()/('blender-'+BLENDER_VERSION+'-windows-x64')/'blender.exe'
    if not path.is_file():
        raise ValueError('Blender no está instalado. Ejecuta install_blender.ps1 una vez; no se descarga al abrir Inicio.')
    manifest=path.with_name('ecuador-vivo-install.json')
    try:
        record=json.loads(manifest.read_text(encoding='utf-8-sig'))
        with path.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
        if record['version']!=BLENDER_VERSION or record['executable_sha256']!=digest:raise ValueError('Huella distinta.')
    except (OSError,ValueError,KeyError,TypeError) as error:
        raise ValueError('La instalación Blender no coincide con la instalación verificada.') from error
    return path


def job_root(identifier,store=None):
    if not isinstance(identifier,str) or not re.fullmatch(r'[a-f0-9]{64}-(poster|preview|final)',identifier):
        raise ValueError('Identificador de recurso 3D inválido.')
    if store is None:
        from model import STORE
        store=STORE
    root=(Path(store)/'resource-3d').resolve()
    job=(root/identifier).resolve()
    if not job.is_relative_to(root):raise ValueError('El recurso está fuera de la biblioteca 3D.')
    return job


def _write(path,value):
    # Only owned control/receipt files, atomically replaced in one job directory.
    temporary=path.with_suffix('.pending.json')
    temporary.write_text(json.dumps(value,ensure_ascii=False,allow_nan=False,indent=2),encoding='utf-8')
    os.replace(temporary,path)


def start_job(recipe,*,mode='poster',store=None,executable=None):
    recipe=validate_recipe(recipe)
    if mode not in MODES:raise ValueError('Tipo de render 3D desconocido.')
    engine=Path(executable) if executable is not None else blender_executable()
    if not engine.is_file():raise ValueError('Blender no está disponible.')
    identifier=recipe_identity(recipe)+'-'+mode
    job=job_root(identifier,store)
    if job.exists():
        state=job_status(identifier,store)
        if state['state'] in ('queued','running','complete'):return identifier
        raise ValueError('El render anterior falló o se canceló. Cambia un ajuste para crear una nueva receta; los archivos anteriores se conservan.')
    job.mkdir(parents=True)
    _write(job/'request.json',dict(recipe=recipe,mode=mode))
    _write(job/'status.json',dict(state='queued',progress=0,message='Preparando Blender'))
    with (job/'worker.log').open('w',encoding='utf-8') as log:
        try:
            process=subprocess.Popen([sys.executable,str(Path(__file__).with_name('studio_blender_worker.py')),str(job),str(engine)],
                stdin=subprocess.DEVNULL,stdout=log,stderr=log,close_fds=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            _write(job/'launch.json',dict(pid=process.pid))
        except OSError:
            _write(job/'status.json',dict(state='failed',progress=0,message='No se pudo iniciar Blender.'))
            raise
    return identifier


def job_status(identifier,store=None):
    job=job_root(identifier,store)
    try:
        state=json.loads((job/'status.json').read_text(encoding='utf-8'))
        if not isinstance(state,dict) or state.get('state') not in ('queued','running','complete','failed','cancelled'):
            raise ValueError('Estado inválido.')
        progress=state.get('progress',0)
        if type(progress) not in (int,float) or not math.isfinite(progress):raise ValueError('Progreso inválido.')
        message=state.get('message','Render Blender')
        if not isinstance(message,str):raise ValueError('Mensaje inválido.')
        return dict(state=state['state'],progress=max(0.,min(1.,progress)),message=message[:600])
    except (OSError,ValueError):return dict(state='missing',progress=0,message='No se pudo leer el estado del render; revisa su registro antes de reiniciarlo.')


def cancel_job(identifier,store=None):
    job=job_root(identifier,store)
    state=job_status(identifier,store)
    if state['state'] in ('queued','running'):
        (job/'cancel.request').touch(exist_ok=True)


def verified_product(identifier,store=None):
    job=job_root(identifier,store)
    if job_status(identifier,store)['state']!='complete':raise ValueError('El render 3D todavía no ha terminado.')
    request=json.loads((job/'request.json').read_text(encoding='utf-8'))
    recipe=validate_recipe(request['recipe'])
    if identifier!=recipe_identity(recipe)+'-'+request['mode']:raise ValueError('La receta 3D cambió.')
    receipt=json.loads((job/'receipt.json').read_text(encoding='utf-8'))
    expected_frames=1 if request['mode']=='poster' else round(recipe['duration']*30)
    expected_size=[1080,900] if request['mode']=='final' else [640,534]
    if (receipt.get('frames')!=expected_frames or receipt.get('fps')!=30 or receipt.get('size')!=expected_size
            or receipt.get('version')!='4.5.4 LTS' or receipt.get('engine')!='Blender'):
        raise ValueError('El calendario, motor o resolución del recibo 3D no coincide con la receta.')
    for name in ('poster.png','scene.blend')+(() if request['mode']=='poster' else ('video.mp4',)):
        path=job/name
        if not path.resolve().is_relative_to(job) or not path.is_file():raise ValueError('Falta un producto 3D.')
        with path.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
        if receipt.get('files',{}).get(name)!=digest:raise ValueError('El producto 3D cambió; no se incorporará.')
    if receipt.get('recipe_sha256')!=recipe_identity(recipe):raise ValueError('Recibo 3D incompatible.')
    return job,recipe,receipt
