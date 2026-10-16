"""Repeatable, isolated real September data benchmark and visual evidence."""
import cProfile,json,pstats,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'production/video_studio'))
from studio_home import create_project
from studio_sig_series import admit_download
from studio_sig_timelapse import configure
from studio_sig_transfer import transfer_series
from studio_territory import DEFAULT
from studio_timeline import PreparedTimeline
from studio_recovery import save_snapshot

folder=ROOT/'_local/video-studio/downloads/nasa-power-20261011-191938-4671f5a6'
metadata=json.loads((folder/'metadata.json').read_text(encoding='utf-8'))
tiff=next(folder.glob('nasa-power-T2M-*.tif'))
download={'provider':'NASA POWER','variable':metadata['parameter_name'],'units':metadata['units'],
    'profile_kind':'temperature','citation':metadata['citation'],'manifest':metadata,
    'entries':[{'date':day,'path':str(tiff),'band':i,'artifact_sha256':metadata['derived_geotiff_sha256'],
        'source_url':metadata['request_urls']} for i,day in enumerate(metadata['returned_dates'],1)]}
project=create_project('free',{'id':'tiktok'},name='Septiembre 2026 · temperatura · revisión visual')
baseline=ROOT/'tmp/sig-presentation-review/baseline-project.json'
if baseline.is_file():
    project['studio']['geography']=json.loads(baseline.read_text(encoding='utf-8'))['studio']['geography']
    ids=project['studio']['geography']['map_workspace']['raster_time']['layers']
else:project,ids=admit_download(project,download)
project=configure(project,ids,duration=6.,cadence='daily',presentation=DEFAULT)
out=ROOT/'tmp/sig-presentation-review';out.mkdir(parents=True,exist_ok=True)
tag=sys.argv[1] if len(sys.argv)>1 else 'baseline'
profile=cProfile.Profile();start=time.perf_counter();profile.enable()
sent=transfer_series(project)
profile.disable();elapsed=time.perf_counter()-start
with (out/(tag+'-profile.txt')).open('w',encoding='utf-8') as stream:
    pstats.Stats(profile,stream=stream).sort_stats('cumulative').print_stats(35)
prepared=PreparedTimeline(sent)
with prepared.frame_at(0) as image:image.save(out/(tag+'.png'))
save_snapshot(out/(tag+'-project.json'),sent)
start=time.perf_counter();again=transfer_series(sent);repeated=time.perf_counter()-start
report={'tag':tag,'observations':len(ids),'first_send_seconds':elapsed,'repeat_send_seconds':repeated}
(out/(tag+'-timing.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
