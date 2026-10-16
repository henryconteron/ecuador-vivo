"""Real already-downloaded two-day NASA evidence; never edits a personal project."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'production/video_studio'))
from studio_home import create_project
from studio_sig_series import admit_download
from studio_sig_timelapse import configure
from studio_sig_transfer import transfer_series
from studio_territory import DEFAULT
from studio_timeline import PreparedTimeline,export_movie
from studio_recovery import save_snapshot


def main():
    manifest_path=Path(sys.argv[1]);metadata=json.loads(manifest_path.read_text(encoding='utf-8'))
    folder=manifest_path.parent;tiff=next(folder.glob('nasa-power-T2M-*.tif'))
    download={'provider':'NASA POWER','variable':metadata['parameter_name'],'units':metadata['units'],
        'profile_kind':'temperature','citation':metadata['citation'],'manifest':metadata,
        'entries':[{'date':day,'path':str(tiff),'band':i,'artifact_sha256':metadata['derived_geotiff_sha256'],
                    'source_url':metadata['request_urls']} for i,day in enumerate(metadata['returned_dates'],1)]}
    project=create_project('free',{'id':'tiktok'},name='Comprobación NASA · septiembre 2026')
    project,ids=admit_download(project,download)
    out=ROOT/'tmp/sig-series-20261011';out.mkdir(parents=True,exist_ok=True)
    report={'source_manifest':str(manifest_path),'dates':metadata['returned_dates'],'checks':[]}
    for scope in ('ecuador','galapagos','province'):
        presentation={**DEFAULT,'territory':scope,**({'province':'Napo'} if scope=='province' else {})}
        configured=configure(project,ids,duration=1.,cadence='daily',presentation=presentation)
        result=transfer_series(configured);timeline=PreparedTimeline(result)
        with timeline.frame_at(0) as frame:frame.save(out/(scope+'.png'))
        record=result['studio']['media'][result['studio']['sig_map_transfer']['asset_id']]
        manifest=json.loads(Path(record['manifest_path']).read_text(encoding='utf-8'))
        report['checks'].append({'scope':scope,'presentation':presentation,'size':[timeline.profile.width,timeline.profile.height],
            'coverage':[o['layers']['continent']['data_pixels'] for o in manifest['observations']],
            'no_basemap':not manifest['geographic_binding']['basemap_included'],'warnings':manifest['warnings']})
        if scope=='province':
            movie=out/'napo-temperatura-septiembre-prueba.mp4'
            if not movie.exists():export_movie(result,movie)
            save_snapshot(out/'napo-temperatura-prueba.json',result)
            report['movie']=str(movie)
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':main()
