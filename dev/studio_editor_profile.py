"""Short profile of actual eight-scene editor products, without touching originals."""
import copy
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'production/video_studio'))
from studio_workspace import WorkspaceSession
from studio_media import AssetFrames
from studio_timeline import PreparedTimeline,validate_export
from studio_ui import canvas_payload
from studio_recovery import save_snapshot

project=json.loads((ROOT/'_local/video-studio/projects/borrador-studio-demo-fullhd-8escenas.json').read_text(encoding='utf8'))
label=sys.argv[1] if len(sys.argv)>1 else 'before'
records=[]
def measured(name,operation):
    start=time.perf_counter();value=operation();elapsed=(time.perf_counter()-start)*1000
    records.append({'operation':name,'ms':round(elapsed,3)});print(name,round(elapsed,3),flush=True)
    return value
state={}
session=measured('session_open',lambda:WorkspaceSession(state,'profile',project,store=ROOT/'tmp/editor-profile'))
measured('document_validation',lambda:validate_export(project))
def products(document,phase):
    prepared=measured(phase+'.timeline_validation',lambda:PreparedTimeline(document))
    assets=measured(phase+'.resource_verification',lambda:AssetFrames(document['studio']['media'],cache=session.cache.media))
    try:
        view=measured(phase+'.product_keys',lambda:session.cache.for_timeline(prepared,assets))
        measured(phase+'.canvas',lambda:view.canvas(session.selected,canvas_payload))
        measured(phase+'.thumbnails',view.thumbnails)
        measured(phase+'.preview_frame',lambda:view.preview(0))
    finally:assets.close()
products(project,'cold')
candidate=copy.deepcopy(session.project)
candidate['name']='Profile rename — private measurement'
measured('rename.commit',lambda:session.commit(candidate))
products(session.project,'rename')
candidate=copy.deepcopy(session.project)
scene=next(s for s in candidate['studio']['scenes'] if s['id']==session.selected)
element=next(e for e in scene['elements'] if not e.get('locked'))
element['transform']['x']+=4
measured('geometry.commit',lambda:session.commit(candidate))
products(session.project,'geometry')
measured('snapshot_save',lambda:save_snapshot(ROOT/'tmp/editor-profile/measured.json',session.project))
report={'label':label,'fixture':'borrador-studio-demo-fullhd-8escenas','records':records,'draft':state['profile_draft']}
(ROOT/f'tmp/editor-performance-{label}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
