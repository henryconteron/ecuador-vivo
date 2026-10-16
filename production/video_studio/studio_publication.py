"""Public evidence from one sealed, active SIG transfer; never the private project."""
import hashlib, json, re, zipfile
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from studio_map_bundles import read_bundle, _path, _read, PNG_LIMIT

def encoded(value):
 return json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False).encode('utf-8')

def active_transfer(project):
 studio=project['studio'];active=set(studio['timeline'])
 transfers=[studio[key] for key in ('sig_transfer','sig_map_transfer') if key in studio
  and active.intersection(studio[key].get('scene_ids',[]))]
 if len(transfers)!=1:raise ValueError('La evidencia requiere una sola serie SIG activa; separa las historias antes de publicar.')
 return transfers[0]

def public_url(value):
 try:
  url=urlsplit(value or '')
  if url.scheme!='https' or not url.hostname or url.username or url.password:return None
  return urlunsplit((url.scheme,url.netloc,url.path,'',''))
 except ValueError:return None

def public_case(project,manifest):
 transfer=active_transfer(project);studio=project['studio']
 sources=[{k:r[k] for k in ('date','sha256','band') if k in r}|{'url':public_url(r.get('source_url'))} for r in manifest['source_records']]
 registry=studio.get('geography',{}).get('sources',{})
 for source in sources:
  original=next((s for s in registry.values() if s.get('sha256')==source['sha256'] and s.get('date')==source['date']),{})
  provenance=original.get('provenance',{})
  source.update({k:provenance.get(k,'No declarada: revisar antes de publicar') for k in ('citation','license')})
  raster=original.get('raster',{})
  source['native_grid']={k:raster[k] for k in ('native_crs','shape','transform','nodata','scale','offset','dtype') if k in raster}
 dates=[s['date'] for s in sources]
 results=[]
 for rid in transfer.get('results',[]):
  result=studio.get('calculations',{}).get(rid)
  if not result:raise ValueError('Falta un resultado enlazado de la serie activa.')
  # A public result exposes numbers and the method, not file/credential bindings.
  row={k:result[k] for k in ('id','variable','units','value','rows') if k in result}
  provenance=result.get('provenance',{})
  row['method']={k:provenance[k] for k in ('method','period','warnings') if k in provenance}
  results.append(row)
 binding=manifest.get('geographic_binding',{})
 case={'schema':'ecuador-vivo-evidence-v1','status':'draft','title':project['name'],
  'variable':manifest['variable'],'units':manifest['units'],'period':{'start':min(dates),'end':max(dates)},
  'author':project.get('author_name') or project.get('author'),
  'observation_dates':dates,'sources':sources,'results':results,
  'metrics_status':'linked_results' if results else 'not_calculated',
  'scientific_revision':manifest['scientific_revision'],'presentation':binding.get('presentation',{}),
  'scale':binding.get('scale',{}),'temporal_interpolation':False,
  'limitations':['Representación derivada: no sustituye los rásteres originales.',
   'Suavizado solo visual; consultas y cálculos usan las fuentes nativas.',
   'Revisar derechos de datos, video y audio antes de publicar.'],
  'maps':[]}
 if not results:case['limitations'].append('Esta serie no incluye métricas agregadas verificadas; no se asignan cifras de otra variable.')
 assert_public(case)
 return case

def assert_public(value):
 """Fail closed for private paths/credential text, including nested result rows."""
 if isinstance(value,str) and re.search(r'(?i)(?:(?<![a-z])[a-z]:[\\/]|file://|\\\\|(?:token|api_key|password|secret)\s*[=:])',value):
  raise ValueError('La evidencia contiene información privada; corrige su procedencia antes de prepararla.')
 if isinstance(value,dict):
  for child in value.values():assert_public(child)
 elif isinstance(value,list):
  for child in value:assert_public(child)

def verify_originals(project,manifest):
 from studio_sig_raster import verify_series_binding
 from studio_sig_transfer import validate_transfer
 sources=verify_series_binding(project,manifest)
 validate_transfer(project)
 transfer=active_transfer(project)
 if transfer.get('results'):
  # Publication is an explicit, less frequent operation: recheck numbers from
  # native sources, not just agreement between two mutable copies of a result.
  from studio_sig_summary import summarize_series
  binding=manifest['geographic_binding']
  expected=summarize_series(sources,binding['inset_sources'],cadence=binding['cadence'])
  by_id={r['id']:r for r in expected['results'].values()}
  for rid in transfer['results']:
   if rid not in by_id or project['studio'].get('calculations',{}).get(rid)!=by_id[rid]:
    raise ValueError('Las métricas difieren de los cálculos nativos. Reenvía la serie desde SIG antes de preparar evidencia.')

def map_files(record,manifest,case):
 root=Path(record['manifest_path']).resolve().parent;files={};total=0
 for index,observation in enumerate(manifest['observations']):
  channels={}
  for channel,item in observation['layers'].items():
   content=_read(_path(root,item['path']),PNG_LIMIT)
   if hashlib.sha256(content).hexdigest()!=item['sha256']:raise ValueError('El mapa derivado cambió.')
   total+=len(content)
   if total>64*1024*1024:raise ValueError('Los mapas públicos superan 64 MiB; prepara un periodo menor, sin truncar fechas.')
   name=f'maps/{index:04d}-{channel}.png';files[name]=content;channels[channel]=name
  case['maps'].append({'date':observation['date'],'channels':channels,
   'coverage':{channel:{k:item[k] for k in ('state','data_pixels') if k in item} for channel,item in observation['layers'].items()}})
 return files

def prepare_publication(job,project):
 job=Path(job);receipt=json.loads((job/'receipt.json').read_text(encoding='utf-8'))
 if receipt.get('delivery_kind','final')!='final':raise ValueError('Exporta primero el video final; no se publica el preview reducido.')
 digest=hashlib.sha256(json.dumps(project,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()
 if receipt.get('project_sha256')!=digest or json.loads((job/'project.json').read_text(encoding='utf-8'))!=project:
  raise ValueError('El documento no corresponde al video terminado.')
 with (job/'video.mp4').open('rb') as stream:
  if hashlib.file_digest(stream,'sha256').hexdigest()!=receipt['video_sha256']:raise ValueError('El video cambió después de exportarse.')
 transfer=active_transfer(project);record=project['studio']['media'][transfer['asset_id']]
 manifest=read_bundle(record);verify_originals(project,manifest);case=public_case(project,manifest)
 if (job/'video.mp4').stat().st_size>96*1024*1024:
  raise ValueError('El video público supera 96 MiB: reduce bitrate o usa alojamiento de medios antes de publicar en GitHub.')
 files=map_files(record,manifest,case);files['video.mp4']=(job/'video.mp4').read_bytes()
 if sum(len(data) for data in files.values())>158*1024*1024:
  raise ValueError('El paquete supera el presupuesto local de importación; usa alojamiento de medios para esta historia extensa.')
 case['id']='studio-'+digest[:24];case['video']='video.mp4';case['video_sha256']=receipt['video_sha256']
 case['files']={name:{'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()} for name,data in files.items()}
 files['case.json']=encoded(case)
 if len(files['case.json'])>2*1024*1024:raise ValueError('La metadata pública supera 2 MiB; prepara un caso más acotado.')
 files['LEEME.txt']=('Borrador público de Andes Pulso. No se publicó ni se subió a GitHub.\n'
  'El proyecto privado y sus rutas locales NO forman parte del paquete.\n'
  'Las imágenes mantienen el calendario y la escala de la serie sellada.\n'
  'Los resultados, cuando existen, son los enlazados a la serie activa.\n'
  'Revisar narrativa, licencias y atribución antes de importar en el panel web.\n').encode()
 target=job/f'andes-pulso-publico-{digest[:24]}.zip'
 # Verify a reusable package rather than trusting the presence of a ZIP.
 if target.exists():
  with zipfile.ZipFile(target) as archive:
   if set(archive.namelist())!=set(files) or any(archive.read(n)!=data for n,data in files.items()):
    raise ValueError('El paquete existente cambió; no se sobrescribió.')
  return target
 # An interrupted write never becomes a reusable, apparently complete ZIP.
 import uuid
 partial=job/f'.publication-{uuid.uuid4().hex}.partial'
 try:
  with zipfile.ZipFile(partial,'x',zipfile.ZIP_DEFLATED) as archive:
   for name,data in files.items():archive.writestr(name,data)
  if partial.stat().st_size>160*1024*1024:raise ValueError('El ZIP supera 160 MiB; no se generó un paquete imposible de importar.')
  partial.rename(target) # Windows rename refuses overwriting an existing target.
 finally:partial.unlink(missing_ok=True)
 return target
