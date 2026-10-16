"""Validate real Blender → Studio movies, optionally save one owned demo project."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'production/video_studio'))
from studio_blender import verified_product
from studio_blender_scene import create_scene_project
from studio_media import import_asset
from studio_recovery import save_snapshot
from studio_timeline import export_movie,PreparedTimeline
from studio_ffmpeg import read_frames


def inspect_movie(path,expected_size,expected_frames,folder):
    reader=read_frames(str(path),input_params=['-protocol_whitelist','file,pipe'])
    metadata=next(reader);count=0;digests=[]
    try:
        if tuple(metadata['size'])!=tuple(expected_size):raise ValueError('Dimensiones incorrectas.')
        for pixels in reader:
            if count in (0,expected_frames//2,expected_frames-1):
                from PIL import Image
                image=Image.frombytes('RGB',tuple(metadata['size']),pixels)
                image.save(folder/(path.stem+'-'+str(count)+'.png'));image.close()
                digests.append(hashlib.sha256(pixels).hexdigest())
            count+=1
    finally:reader.close()
    if count!=expected_frames:raise ValueError('Conteo de cuadros incorrecto.')
    if len(set(digests))<2:raise ValueError('El recurso no presenta animación visible.')
    with path.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
    return dict(size=list(metadata['size']),frames=count,fps=metadata['fps'],duration=metadata['duration'],
        bytes=path.stat().st_size,sha256=digest,key_frames=digests)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('identifier');parser.add_argument('--save-demo',action='store_true')
    parser.add_argument('--refresh-owned-demo',action='store_true',help='Refresh only the unchanged demonstration created by this verification tool.')
    args=parser.parse_args()
    job,recipe,receipt=verified_product(args.identifier)
    folder=ROOT/'_local/resource-development-20261012'/'blender-proof-final'
    folder.mkdir(parents=True,exist_ok=True)
    report={'recipe':recipe,'blender_receipt':receipt,'outputs':{}}
    report['source']=inspect_movie(job/'video.mp4',receipt['size'],receipt['frames'],folder)
    asset=import_asset((job/'video.mp4').read_bytes(),'orografia-blender.mp4')
    if args.refresh_owned_demo:
        target=ROOT/'_local/video-studio/projects/recurso-3d-orografia-20261012.json'
        original=ROOT/'_local/resource-development-20261012/blender-proof/tiktok-project.json'
        if not original.is_file() or not target.is_file() or target.read_bytes()!=original.read_bytes():
            raise ValueError('La demostración tiene cambios o no coincide con la copia creada por esta herramienta. No se sobrescribirá.')
        updated=create_scene_project(recipe,asset,args.identifier,'La montaña no fabrica agua',{'id':'tiktok'})
        # This is the untouched, owned demonstration, not a pilot or user edit.
        save_snapshot(target,updated)
        print(json.dumps({'refreshed_owned_demo':str(target),'previous_snapshot_preserved':True}))
        return
    for preset in ('tiktok','youtube'):
        project=create_scene_project(recipe,asset,args.identifier,'La montaña no fabrica agua',{'id':preset})
        output=folder/preset;output.mkdir(parents=True,exist_ok=True)
        path=output/'video.mp4'
        started=time.monotonic()
        export_movie(project,path)
        prepared=PreparedTimeline(project)
        record=inspect_movie(path,(prepared.profile.width,prepared.profile.height),prepared.total_frames,output)
        record['compose_seconds']=round(time.monotonic()-started,3)
        report['outputs'][preset]=record
        save_snapshot(output/'editable-project.json',project)
        if preset=='tiktok' and args.save_demo:
            target=ROOT/'_local/video-studio/projects/recurso-3d-orografia-20261012.json'
            if target.exists():report['existing_demo_preserved']=str(target)
            else:save_snapshot(target,project);report['saved_demo']=str(target)
    (folder/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':main()
