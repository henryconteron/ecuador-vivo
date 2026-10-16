"""Real source, isolated proof export and paired geometry performance check."""
import copy,hashlib,json,statistics,sys,time
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'production/video_studio'))
from studio_sig_raster import _display_geometry,_GEOMETRY
from studio_territory import DEFAULT,boundaries,geometry
from maqueta import paint_map_outline
from studio_sig_timelapse import configure,output_frame
from studio_sig_layers import workspace_for
from studio_sig_transfer import transfer_series
from studio_timeline import PreparedTimeline,export_movie
from studio_recovery import save_snapshot
from studio_home import create_project

tag=datetime.now().strftime('%Y%m%d-%H%M%S')
out=ROOT/'tmp/sig-presentation-review'/('final-'+tag);out.mkdir(parents=True)
p=create_project('free',{'id':'tiktok'},name='Septiembre 2026 · temperatura · diseño corregido')
p['studio']['geography']=json.loads((out.parent/'baseline-project.json').read_text(encoding='utf-8'))['studio']['geography']
ids=workspace_for(p)['raster_time']['layers']
for lid in ids:p['studio']['geography']['map_workspace']['layers'][lid]['style']['opacity']=1.
p=configure(p,ids,duration=6.,cadence='daily',presentation=DEFAULT)
originals={s['path']:hashlib.sha256(Path(s['path']).read_bytes()).hexdigest() for s in p['studio']['geography']['sources'].values() if s['type']=='raster'}
box=output_frame(p)['bbox'];size=(800,900);records=boundaries()[1]
raw=[];cached=[]
for n in range(4):
    start=time.perf_counter();mask,rings,provinces=geometry(box,size,DEFAULT)
    ink=paint_map_outline(size,rings,provinces,province_color=(90,125,142,200))
    raw.append(time.perf_counter()-start);expected=(mask.tobytes(),ink.tobytes());mask.close();ink.close()
    a,b=_display_geometry(box,size,DEFAULT,records);a.close();b.close() # prime, not counted
    start=time.perf_counter();a,b=_display_geometry(box,size,DEFAULT,records);cached.append(time.perf_counter()-start)
    assert (a.tobytes(),b.tobytes())==expected;a.close();b.close()
report={'geometry_uncached_seconds':raw,'geometry_cached_seconds':cached,
    'geometry_speedup_median':statistics.median(raw)/statistics.median(cached)}
start=time.perf_counter();sent=transfer_series(p);report['first_send_seconds']=time.perf_counter()-start
start=time.perf_counter();again=transfer_series(sent);report['repeat_send_seconds']=time.perf_counter()-start
prepared=PreparedTimeline(sent)
for frame,label in [(0,'primero'),(prepared.rows[-1]['end_frame']-1,'ultimo')]:
    with prepared.frame_at(frame) as image:image.save(out/(label+'.png'))
save_snapshot(out/'review-project.json',sent)
project=ROOT/'_local/video-studio/projects'/('andes-pulso-temperatura-septiembre-2026-'+tag+'.json')
save_snapshot(project,sent);report['project']=str(project)
print(json.dumps(report),flush=True)
receipt=export_movie(sent,out/'video.mp4',progress=lambda n:print('Exportación '+str(round(n*100))+'%',flush=True))
import imageio_ffmpeg
reader=imageio_ffmpeg.read_frames(str(out/'video.mp4'));metadata=next(reader);frames=sum(1 for _ in reader)
assert tuple(metadata['size'])==(1080,1920) and frames==180
assert originals=={path:hashlib.sha256(Path(path).read_bytes()).hexdigest() for path in originals}
report.update(video=str(out/'video.mp4'),frames_decoded=frames,fps=metadata['fps'],dimensions=metadata['size'],
    original_hashes_unchanged=True,scientific_calendar=receipt['scientific_calendar'])
(out/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(out.parent/'latest-final.json').write_text(json.dumps({'folder':str(out),'project':str(project)}),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='scientific_calendar'},ensure_ascii=False),flush=True)
