"""Load one existing local CHIRPS day once through the existing science engine."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path('production/video_studio').resolve()))
from model import default_project,validate
from data import rain_path
from endcard import summary_for_project
from visualization_ui import capture_snapshot
from studio_editing import new_workspace,attach_snapshot
from studio_templates import template_scene
from output_profiles import profile_for
p=default_project();p['start']=p['end']='2025-01-01';p['name']='CHIRPS Ecuador · revisión científica real'
rain_path(p['start'],allow_download=False)
snapshot=capture_snapshot(p,lambda settings:summary_for_project(settings,validate(settings)))
p=attach_snapshot(new_workspace(p),snapshot);p['studio']['output_profile']={'id':'custom','width':640,'height':360}
rid=next(rid for rid,r in p['studio']['calculations'].items() if 'rows' not in r and r.get('value') is not None)
scene=template_scene('metric_focus',profile_for(p['studio']['output_profile']),bindings={'metric':{'result_id':rid,'field':'value'}})
scene['duration']=.5;p['studio']['scenes'].append(scene);p['studio']['timeline']=[scene['id']]
Path('tmp/ux-redesign/scientific-project.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'source':'existing cached CHIRPS 2025-01-01','results':len(p['studio']['calculations']),'datasets':len(p['studio']['datasets']),'id':rid,'value':p['studio']['calculations'][rid]['value']}))
