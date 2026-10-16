"""Private SIG workers: derived results require explicit, verified acceptance."""
import copy,hashlib,json,os,subprocess,sys,time,traceback,uuid
from pathlib import Path
from model import STORE
from jobs import write_json,read_json,process_alive

ROOT=STORE/'sig-analysis'
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def confined(job):
    path=Path(job).resolve()
    if path.parent!=ROOT.resolve() or not path.is_dir():raise ValueError('Trabajo SIG fuera de su carpeta.')
    return path
def validate_request(project,request):
    from studio_sig_tool_catalog import VECTOR_TOOLS
    from studio_sig_layers import workspace_for
    if not isinstance(request,dict):raise ValueError('Solicitud SIG inválida.')
    kind=request.get('kind');keys=set(request)
    if kind=='vector':
        if keys!={'kind','layer','tool','parameters','name','other'} and keys!={'kind','layer','tool','parameters','name'}:raise ValueError('Solicitud vectorial inválida.')
        if request['tool'] not in {t['id'] for t in VECTOR_TOOLS} or not isinstance(request['parameters'],dict):raise ValueError('Operación vectorial desconocida.')
        ids=[request['layer']]+([request['other']] if request.get('other') else [])
    elif kind=='raster':
        if keys!={'kind','layers','tool','name'} or request['tool'] not in ('difference','mean','zonal'):raise ValueError('Solicitud ráster inválida.')
        ids=request['layers']
        if not isinstance(ids,list) or len(ids)!=2:raise ValueError('Se requieren dos entradas.')
    else:raise ValueError('Tipo de análisis desconocido.')
    if not isinstance(request['name'],str) or not request['name'].strip() or len(request['name'])>172:raise ValueError('Nombre de resultado inválido.')
    layers=workspace_for(project)['layers']
    if any(not isinstance(lid,str) or lid not in layers for lid in ids):raise ValueError('Entrada de análisis inexistente.')
    return ids

def start(project,request):
    validate_request(project,request)
    job=ROOT/uuid.uuid4().hex;job.mkdir(parents=True)
    write_json(job/'request.json',{'project':project,'operation':request})
    write_json(job/'status.json',{'state':'queued','message':'Análisis en cola','updated':time.time()})
    try:
        with (job/'worker.log').open('w',encoding='utf-8') as log:
            process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),str(job)],stdin=subprocess.DEVNULL,
                stdout=log,stderr=log,close_fds=True,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        write_json(job/'process.json',{'pid':process.pid})
    except Exception as error:
        write_json(job/'status.json',{'state':'failed','message':str(error),'updated':time.time()});raise
    return job

def status(job):
    job=confined(job);value=read_json(job/'status.json',{})
    if not isinstance(value,dict) or value.get('state') not in ('queued','running','complete','failed','cancelled'):raise ValueError('Estado de análisis inválido.')
    if (job/'cancel.request').exists() and value['state'] not in ('queued','running'):
        return {**value,'state':'cancelled','message':'Análisis cancelado; no se incorporará el resultado.'}
    pid=read_json(job/'process.json',{}).get('pid')
    if value['state'] in ('queued','running') and time.time()-value.get('updated',time.time())>15 and type(pid) is int and pid>0 and not process_alive(pid):
        return {**value,'state':'failed','message':'El proceso se interrumpió. El proyecto se conserva.'}
    if (job/'cancel.request').exists():return {**value,'state':'cancelling','message':'Cancelación solicitada; esperando el cierre del cálculo.'}
    return value

def cancel(job):confined(job).joinpath('cancel.request').touch(exist_ok=True)

def find_pending(project):
    """Bounded recovery on opening Processes, never on zoom or each map frame."""
    project_id=project.get('project_meta',{}).get('id')
    if not project_id or not ROOT.exists():return None
    for job in sorted((p for p in ROOT.iterdir() if p.is_dir()),key=lambda p:p.stat().st_mtime,reverse=True)[:50]:
        if (job/'handled.json').exists():continue
        source=read_json(job/'request.json',{}).get('project',{})
        if source.get('project_meta',{}).get('id')==project_id:return job
    return None

def handled(job,action):
    if action not in ('applied','dismissed'):raise ValueError('Acción de resultado inválida.')
    write_json(confined(job)/'handled.json',{'action':action,'updated':time.time()})

def execute(job):
    job=confined(job)
    last_report=0
    def check():
        if (job/'cancel.request').exists():raise InterruptedError('Análisis cancelado; proyecto conservado.')
    def report(done,total):
        nonlocal last_report
        check();now=time.monotonic()
        if done!=total and now-last_report<.2:return
        last_report=now
        write_json(job/'status.json',{'state':'running','message':f'Procesando {done} de {total}',
            'completed':done,'total':total,'updated':time.time(),'pid':os.getpid()})
    def terminal(state,message):write_json(job/'status.json',{'state':state,'message':message,'updated':time.time(),'pid':os.getpid()})
    try:
        check();request=read_json(job/'request.json');project=request['project'];op=request['operation'];validate_request(project,op)
        terminal('running','Verificando entradas y calculando')
        if op['kind']=='vector':
            from studio_sig_vector import run_operation
            result,lid=run_operation(project,op['layer'],op['tool'],op['parameters'],other=op.get('other'),name=op['name'],progress=report)
        elif op['tool']=='zonal':
            from studio_sig_raster import zonal_layer
            result,lid=zonal_layer(project,*op['layers'],progress=report)
        else:
            from studio_sig_raster import calculate
            result,lid=calculate(project,op['layers'],op['tool'],op['name'],progress=report)
        check();output={'project':result,'layer':lid};write_json(job/'result.json',output)
        write_json(job/'receipt.json',{'request_sha256':digest(request),'result_sha256':digest(output)})
        check();terminal('complete','Resultado listo para incorporar')
    except InterruptedError as error:terminal('cancelled',str(error))
    except Exception as error:traceback.print_exc();terminal('failed',f'{type(error).__name__}: {error}')

def accept(job,current):
    job=confined(job)
    if status(job)['state']!='complete':raise ValueError('El análisis no está listo o fue cancelado.')
    request=read_json(job/'request.json');output=read_json(job/'result.json');receipt=read_json(job/'receipt.json',{})
    if receipt!={'request_sha256':digest(request),'result_sha256':digest(output)}:raise ValueError('La huella del resultado o de la solicitud cambió.')
    base=request['project'];ids=validate_request(base,request['operation'])
    from studio_sig_layers import workspace_for
    from studio_geography import validate_geography
    if current.get('project_meta',{}).get('id')!=base.get('project_meta',{}).get('id'):raise ValueError('El proyecto cambió; vuelve al proyecto de origen.')
    old=base['studio']['geography'];present=current['studio']['geography'];old_layers=workspace_for(base)['layers'];now_layers=workspace_for(current)['layers']
    for lid in ids:
        sid=old_layers[lid]['source_id']
        if now_layers.get(lid,{}).get('source_id')!=sid or present['sources'].get(sid)!=old['sources'][sid]:raise ValueError('Una entrada cambió; ejecuta de nuevo el análisis.')
    derived=output['project']['studio']['geography'];lid=output['layer'];layer=derived['map_workspace']['layers'][lid];sid=layer['source_id']
    if sid in old['sources'] or set(derived['sources'])-set(old['sources'])!={sid}:raise ValueError('Resultado derivado incoherente.')
    validate_geography(output['project']['studio'])
    result=copy.deepcopy(current);registry=result['studio']['geography'];state=registry['map_workspace']
    if sid in registry['sources'] and registry['sources'][sid]!=derived['sources'][sid]:raise ValueError('Colisión de fuente derivada.')
    registry['sources'][sid]=copy.deepcopy(derived['sources'][sid])
    registry['regions'].update({rid:copy.deepcopy(r) for rid,r in derived['regions'].items() if r['source_id']==sid})
    if lid not in state['layers']:state['order'].append(lid)
    state['layers'][lid]=copy.deepcopy(layer);state['active_layer']=lid;state['selection']=[]
    validate_geography(result['studio']);return result,lid

if __name__=='__main__':execute(sys.argv[1])
