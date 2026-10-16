"""Bounded, non-executable ZIP admission. Import is private; staging is explicit.

ZIP hashes establish internal consistency, NOT authorship or scientific truth.
No extractall, subprocess, URLs fetched, code accepted, or Git action here.
"""
import datetime as dt
import hashlib
import io
import json
import re
import stat
import uuid
import zipfile
from urllib.parse import urlsplit
from pathlib import Path
from PIL import Image

PACKAGE_LIMIT=160*1024*1024
JSON_LIMIT=2*1024*1024
ID=re.compile(r'studio-[a-f0-9]{24}\Z')
MAP=re.compile(r'maps/\d{4}-[a-zA-Z0-9_-]{1,32}\.png\Z')
SHA=re.compile(r'[a-f0-9]{64}\Z')

def encoded(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False).encode('utf-8')

def parse(content):
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise ValueError('Claves JSON duplicadas.')
            result[key]=value
        return result
    def invalid(_):raise ValueError('Número no finito.')
    try:return json.loads(content,object_pairs_hook=pairs,parse_constant=invalid)
    except (UnicodeError,json.JSONDecodeError,RecursionError) as error:raise ValueError('JSON inválido.') from error

def validate_case(case):
    if not isinstance(case,dict) or case.get('schema')!='ecuador-vivo-evidence-v1' or case.get('status') not in ('draft','reviewed'):
        raise ValueError('Esquema de evidencia no admitido.')
    if not ID.fullmatch(case.get('id','')) or case.get('video')!='video.mp4':raise ValueError('Identificador o video inválido.')
    for key in ('title','variable','units'):
        if not isinstance(case.get(key),str) or not 0<len(case[key])<=300:raise ValueError('Etiqueta inválida.')
    dates=case.get('observation_dates')
    if not isinstance(dates,list) or not 1<=len(dates)<=1000 or dates!=sorted(set(dates)):raise ValueError('Calendario inválido.')
    for date in dates:
        try:
            if dt.date.fromisoformat(date).isoformat()!=date:raise ValueError()
        except (TypeError,ValueError):raise ValueError('Fecha inválida.') from None
    if case.get('period')!={'start':dates[0],'end':dates[-1]}:raise ValueError('Periodo y calendario diferentes.')
    maps=case.get('maps')
    if not isinstance(maps,list) or [m.get('date') for m in maps]!=dates:raise ValueError('Faltan mapas del calendario.')
    names=[]
    for m in maps:
        channels=m.get('channels')
        if not isinstance(channels,dict) or not 1<=len(channels)<=3:raise ValueError('Canales cartográficos inválidos.')
        for key,name in channels.items():
            if not re.fullmatch(r'[a-zA-Z0-9_-]{1,32}',key) or not isinstance(name,str) or not MAP.fullmatch(name):raise ValueError('Ruta de mapa inválida.')
            names.append(name)
    files=case.get('files')
    if not isinstance(files,dict) or set(files)!={*names,'video.mp4'} or len(names)!=len(set(names)):raise ValueError('Inventario de mapas inconsistente.')
    for name,record in files.items():
        if not isinstance(record,dict) or not SHA.fullmatch(record.get('sha256','')) or type(record.get('bytes')) is not int or record['bytes']<=0:
            raise ValueError('Inventario sin tamaño o huella válida.')
        if record['bytes']>(96*1024*1024 if name=='video.mp4' else 8*1024*1024):raise ValueError('Un archivo supera el tamaño admitido.')
    if sum(record['bytes'] for record in files.values())>PACKAGE_LIMIT-JSON_LIMIT:raise ValueError('Contenido demasiado grande.')
    if case.get('video_sha256')!=files['video.mp4']['sha256']:raise ValueError('La huella de video es inconsistente.')
    if case.get('metrics_status') not in ('linked_results','not_calculated') or not isinstance(case.get('results'),list):raise ValueError('Estado de métricas inválido.')
    if bool(case['results'])!=(case['metrics_status']=='linked_results'):raise ValueError('No asignes métricas inexistentes.')
    if not isinstance(case.get('sources'),list) or not case['sources']:raise ValueError('Falta la procedencia.')
    for source in case['sources']:
        if not isinstance(source,dict) or not SHA.fullmatch(source.get('sha256','')) or source.get('date') not in dates:raise ValueError('Procedencia sin fecha o huella válida.')
        for key in ('citation','license'):
            if not isinstance(source.get(key),str) or not 0<len(source[key])<=1000:raise ValueError('Falta citación o condición de uso.')
        if source.get('url'):
            url=urlsplit(source['url'])
            if url.scheme!='https' or not url.hostname or url.username or url.password or url.query or url.fragment:raise ValueError('La fuente debe tener una URL pública sin credenciales.')
    if not isinstance(case.get('limitations'),list):raise ValueError('Faltan límites de interpretación.')
    # Defense in depth: imported metadata must not leak paths or credentials.
    text=encoded(case).decode()
    if re.search(r'(?i)(?:(?<![a-z])[a-z]:[\\/]|file://|\\\\|(?:token|api_key|password|secret)\s*[=:])',text):
        raise ValueError('El paquete contiene información privada.')
    return case

def validate_contents(case,files):
    validate_case(case)
    if set(files)!=set(case['files']):raise ValueError('Archivos no declarados o ausentes.')
    for name,content in files.items():
        record=case['files'][name]
        if len(content)!=record['bytes'] or hashlib.sha256(content).hexdigest()!=record['sha256']:raise ValueError('El archivo no corresponde a su huella y tamaño.')
        if name.endswith('.png'):
            try:
                with Image.open(io.BytesIO(content)) as image:
                    if image.format!='PNG' or max(image.size)>4096 or image.width*image.height>16_777_216:raise ValueError('Mapa demasiado grande.')
                    image.verify()
            except (OSError,Image.DecompressionBombError) as error:raise ValueError('PNG inválido.') from error
        elif len(content)<12 or content[4:8]!=b'ftyp':raise ValueError('Contenedor MP4 inválido.')

def inspect_package(content):
    if not isinstance(content,bytes) or not 0<len(content)<=PACKAGE_LIMIT:raise ValueError('ZIP vacío o tamaño superior a 160 MiB.')
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            infos=archive.infolist();names=[i.filename for i in infos]
            if len(names)>3002 or len(names)!=len(set(names)) or 'case.json' not in names:raise ValueError('Entradas duplicadas o demasiadas.')
            if sum(i.file_size for i in infos)>PACKAGE_LIMIT:raise ValueError('Contenido descomprimido demasiado grande.')
            for item in infos:
                limit=JSON_LIMIT if item.filename=='case.json' else (16*1024 if item.filename=='LEEME.txt' else (96*1024*1024 if item.filename=='video.mp4' else 8*1024*1024))
                if item.flag_bits&1 or stat.S_ISLNK(item.external_attr>>16) or item.is_dir() or item.file_size>limit:
                    raise ValueError('Entrada cifrada, enlace o tamaño no permitido.')
                if item.filename not in ('case.json','video.mp4','LEEME.txt') and not MAP.fullmatch(item.filename):raise ValueError('Ruta o tipo de archivo no permitido.')
            case=validate_case(parse(archive.read('case.json')))
            if case['status']!='draft':raise ValueError('Solo se importan borradores.')
            if set(names)-{'case.json','LEEME.txt'}!=set(case['files']):raise ValueError('Contenido no declarado.')
            files={name:archive.read(name) for name in case['files']}
            validate_contents(case,files)
            return case,files
    except (zipfile.BadZipFile,RuntimeError,TypeError,KeyError,AttributeError) as error:raise ValueError('Paquete de Studio inválido.') from error

def private_base(root):
    root=Path(root).resolve();base=root/'_local/site-admin/studio-drafts'
    if not base.resolve().is_relative_to(root):raise ValueError('La carpeta privada apunta fuera del proyecto.')
    return base

def import_draft(root,content):
    case,files=inspect_package(content);base=private_base(root);target=base/case['id']
    if target.exists():
        old,old_files=read_draft(root,case['id'])
        if old!=case or old_files!=files:raise ValueError('Ya existe otro contenido con ese identificador; no se sobrescribió.')
        return target
    base.mkdir(parents=True,exist_ok=True);temporary=base/('.import-'+uuid.uuid4().hex)
    temporary.mkdir()
    # No extraction: write only validated relative paths into our new directory.
    for name,data in {**files,'case.json':encoded(case)}.items():
        path=temporary/name;path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as output:output.write(data)
    temporary.rename(target)
    return target

def read_draft(root,identifier):
    if not ID.fullmatch(identifier):raise ValueError('Identificador inválido.')
    base=private_base(root).resolve();target=(base/identifier).resolve()
    if target.parent!=base:raise ValueError('Borrador fuera de la carpeta privada.')
    case_path=(target/'case.json').resolve()
    if not case_path.is_relative_to(target):raise ValueError('Metadata fuera del borrador.')
    if case_path.stat().st_size>JSON_LIMIT:raise ValueError('Metadata demasiado grande.')
    case=validate_case(parse(case_path.read_bytes()));files={}
    if case['id']!=identifier:raise ValueError('Identidad del borrador diferente.')
    for name,record in case['files'].items():
        path=(target/name).resolve()
        if not path.is_relative_to(target) or path.stat().st_size!=record['bytes']:raise ValueError('El archivo no corresponde a su huella y tamaño.')
        files[name]=path.read_bytes()
    validate_contents(case,files)
    return case,files

def draft_metadata(root,identifier):
    """Small reads on panel reruns; full byte validation stays action-driven."""
    if not ID.fullmatch(identifier):raise ValueError('Identificador inválido.')
    base=private_base(root).resolve();target=(base/identifier).resolve()
    if target.parent!=base:raise ValueError('Borrador fuera de la carpeta privada.')
    path=(target/'case.json').resolve()
    if not path.is_relative_to(target) or path.stat().st_size>JSON_LIMIT:raise ValueError('Metadata fuera del borrador o demasiado grande.')
    case=validate_case(parse(path.read_bytes()))
    if case['id']!=identifier:raise ValueError('Identidad distinta del borrador.')
    return case,target

def stage_draft(root,identifier,save,*,reviewed=False):
    if reviewed is not True:raise ValueError('Confirma la revisión científica y los derechos antes de incorporar a la web.')
    root=Path(root).resolve();case,files=read_draft(root,identifier)
    if any(source[key].startswith('No declarada:') for source in case['sources'] for key in ('citation','license')):
        raise ValueError('Falta declarar citación o derechos de una fuente; corrígelo en Studio y vuelve a exportar.')
    case={**case,'status':'reviewed'};folder=f'data/cases/studio/{identifier}'
    index_path=root/'data/cases/studio-index.json'
    baseline=index_path.read_text(encoding='utf-8') if index_path.exists() else None
    index=parse(baseline) if baseline is not None else {'schema_version':1,'cases':[]}
    if index.get('schema_version')!=1 or not isinstance(index.get('cases'),list) or len(index['cases'])>1000:raise ValueError('Índice de Studio inválido.')
    entry={'id':identifier,'title':case['title'],'variable':case['variable'],'units':case['units'],'period':case['period'],'status':'reviewed'}
    existing=next((e for e in index['cases'] if e.get('id')==identifier),None)
    if existing is not None and existing!=entry:raise ValueError('El índice ya contiene otra versión del caso.')
    # Preflight ALL paths before writing; immutable cases are never overwritten.
    payloads={f'{folder}/{n}':b for n,b in {**files,'case.json':encoded(case)}.items()}
    for relative,content in payloads.items():
        path=(root/relative).resolve()
        if not path.is_relative_to(root) or (path.exists() and path.read_bytes()!=content):raise ValueError('Un archivo del caso cambió; no se sobrescribió.')
    for relative,content in payloads.items():
        if not (root/relative).exists():save(relative,content)
    if existing is None:
        index['cases'].append(entry);save('data/cases/studio-index.json',encoded(index),expected=baseline)
    return folder
