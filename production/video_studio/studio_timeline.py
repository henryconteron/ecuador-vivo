"""Frame-exact free-scene preview/export; no providers or calculation calls."""
import copy
import hashlib
import json
from contextlib import contextmanager
from pathlib import Path
import imageio_ffmpeg
from studio_model import check_schema, validate_studio
from studio_editing import timeline_rows, _timeline_rows_validated
from studio_media import AssetFrames
from studio_render import render_scene, _render_validated_scene
from output_profiles import profile_for
from calculation_results import CalculationResult
from studio_audio import audio_settings, video_sources, mux_audio


def validate_export(project):
    check_schema(project)
    try: json.dumps(project,allow_nan=False)
    except (TypeError,ValueError) as error:
        raise ValueError('El proyecto completo debe ser JSON finito y serializable.') from error
    studio=validate_studio(project['studio'])
    if any(not isinstance(record,dict) for record in studio['media'].values()):
        raise ValueError('Registro multimedia inválido.')
    from studio_temporal import validate_maps
    validate_maps(project)
    if 'geography' in studio:
        from studio_geography import validate_geography
        validate_geography(studio)
    profile=profile_for(studio['output_profile'])
    active=set(studio['timeline'])
    for scene in studio['scenes']:
        if scene['id'] not in active: continue
        if scene.get('renderer','studio')!='studio':
            raise ValueError('Esta timeline contiene una referencia legacy; expórtala desde Montaje o crea una escena libre.')
        for element in scene['elements']:
            if element['type']=='video': audio_settings(element.get('style',{}))
    for rid,value in studio['calculations'].items():
        if value.get('id',rid)!=rid: raise ValueError('El ID de CalculationResult no coincide con su registro.')
        CalculationResult({'id':rid, **value})
    return profile


def _scene_assets(assets,time,scene):
    if scene.get('map_instances'):
        return assets.at(time,copy.deepcopy(scene['elements']),map_instances=copy.deepcopy(scene['map_instances']))
    return assets.at(time,copy.deepcopy(scene['elements']))


def frame_at(project,frame, *, assets=None, authoring=False):
    studio=project['studio']
    rows=timeline_rows(studio)
    if type(frame) is not int or not 0<=frame<rows[-1]['end_frame']:
        raise ValueError('Playhead fuera de la timeline.')
    row=next(r for r in rows if r['start_frame']<=frame<r['end_frame'])
    scene=next(s for s in studio['scenes'] if s['id']==row['id'])
    # Quantized timing is authoritative for both preview and movie.
    scene=copy.deepcopy(scene);scene['duration']=row['seconds']
    time=(frame-row['start_frame'])/30
    profile=profile_for(studio['output_profile'])
    if assets is None:
        with AssetFrames(studio['media']) as source:
            return render_scene(scene,profile,studio['calculations'],assets=_scene_assets(source,time,scene),
                                time=None if authoring else time)
    return render_scene(scene,profile,studio['calculations'],assets=_scene_assets(assets,time,scene),
                        time=None if authoring else time)


class PreparedTimeline:
    """Validate and isolate a document once for a sequence of render calls.

    No cache of external files: AssetFrames still verifies media for each
    preview/export session. Public accessors return copies of the snapshot.
    """
    def __init__(self,project):
        self._project=copy.deepcopy(project)
        self.profile=validate_export(self._project)
        self._rows=_timeline_rows_validated(self._project['studio'])
        self._scenes={s['id']:copy.deepcopy(s) for s in self._project['studio']['scenes']}
        for row in self._rows: self._scenes[row['id']]['duration']=row['seconds']

    @property
    def project(self): return copy.deepcopy(self._project)

    @property
    def rows(self): return copy.deepcopy(self._rows)

    @property
    def total_frames(self): return self._rows[-1]['end_frame']

    def frame_at(self,frame, *, assets=None,authoring=False):
        if type(frame) is not int or not 0<=frame<self.total_frames:
            raise ValueError('Playhead fuera de la timeline.')
        row=next(r for r in self._rows if r['start_frame']<=frame<r['end_frame'])
        scene=self._scenes[row['id']]
        time=(frame-row['start_frame'])/30
        if assets is None:
            with AssetFrames(self._project['studio']['media']) as source:
                return self.frame_at(frame,assets=source,authoring=authoring)
        return _render_validated_scene(scene,self.profile,self._project['studio']['calculations'],
            assets=_scene_assets(assets,time,scene),time=None if authoring else time)


def _write_staged_json(path,value):
    """Create one owned staging file and remove it if writing/closing fails."""
    stream=path.open('x',encoding='utf-8')
    try:
        with stream: json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False)
    except Exception:
        path.unlink(missing_ok=True)
        raise


@contextmanager
def _publication_guard():
    """Roll back owned products even when resource cleanup raises."""
    published=[]
    try: yield published
    except Exception:
        for path in reversed(published): path.unlink(missing_ok=True)
        raise


def export_movie(project,target, *, progress=None, cancelled=None):
    """Preflight every active scene before creating files; receipt only on success."""
    prepared=PreparedTimeline(project)
    project=prepared.project
    profile=prepared.profile
    rows=prepared.rows
    target=Path(target)
    if target.suffix.lower()!='.mp4':
        raise ValueError('El destino de exportación debe ser un archivo .mp4.')
    total=rows[-1]['end_frame']
    partial=target.with_name(target.stem+'.partial.mp4')
    products=(target,target.parent/'project.json',target.parent/'receipt.json')
    if partial.exists() or any(path.exists() for path in products):
        raise ValueError('Exporta en un destino nuevo; no se sobrescribirán productos existentes.')
    project_hash=hashlib.sha256(json.dumps(project,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()
    staged_project=target.parent/'.project.studio-partial.json'
    staged_receipt=target.parent/'.receipt.studio-partial.json'
    staging=(staged_project,staged_receipt,staged_project.with_suffix('.json.tmp'),staged_receipt.with_suffix('.json.tmp'))
    reservation=target.parent/'.studio-export.lock'
    with _publication_guard() as published, AssetFrames(project['studio']['media']) as assets:
        for row in rows: prepared.frame_at(row['start_frame'],assets=assets,authoring=True)
        audio=video_sources(project,rows,assets)
        target.parent.mkdir(parents=True,exist_ok=True)
        owned_staging=[];lock_owned=False
        try:
            try:
                lock=reservation.open('x',encoding='utf-8')
            except FileExistsError as error:
                raise ValueError('Ya hay una exportación reservada en este destino.') from error
            lock_owned=True
            with lock: pass
            if partial.exists() or any(path.exists() for path in (*products,*staging)):
                raise ValueError('Exporta en un destino nuevo; no se sobrescribirán productos existentes.')
            writer=imageio_ffmpeg.write_frames(str(partial),(profile.width,profile.height),fps=30,
                codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',macro_block_size=1,
                output_params=['-crf','18','-preset','fast','-movflags','+faststart'])
            try:
                writer.send(None)
                for frame in range(total):
                    if cancelled and cancelled(): raise InterruptedError('Exportación cancelada; se conserva el borrador.')
                    image=prepared.frame_at(frame,assets=assets).convert('RGB')
                    writer.send(image.tobytes())
                    if progress and (frame%30==0 or frame==total-1): progress((frame+1)/total*(.8 if audio else 1))
            finally: writer.close()
            if not partial.is_file() or partial.stat().st_size==0: raise ValueError('FFmpeg no produjo un video válido.')
            audio_receipt=mux_audio(partial,audio,total,cancelled=cancelled,
                progress=(lambda value:progress(.8+.15*value)) if progress else None)
            receipt={'renderer':'studio_scene_v1','fps':30,'total_frames':total,'duration':total/30,
                'dimensions':[profile.width,profile.height],'timeline':rows,
                'calculations':project['studio']['calculations'],'media':project['studio']['media'],
                'datasets':project['studio']['datasets'],'project_sha256':project_hash,
                'video_sha256':hashlib.sha256(partial.read_bytes()).hexdigest(),
                'audio':audio_receipt,'preview_method':'frame_at / render_scene; audiovisual worker MP4',
                 'scientific_computation':'none; stored CalculationResult registry'}
            from studio_temporal import calendar_receipt
            receipt['scientific_calendar'] = calendar_receipt(project,rows)
            if 'geography' in project['studio']:
                from studio_geography import geographic_receipt
                receipt['geographic_views']=geographic_receipt(project)
            from job_products import video_artifact
            receipt['artifacts']={'video':video_artifact(target.name,receipt['video_sha256'])}
            # Stage both sidecars before exposing a final MP4. The movie is the
            # publication signal; worker status switches to complete afterward.
            _write_staged_json(staged_project,project);owned_staging.append(staged_project)
            _write_staged_json(staged_receipt,receipt);owned_staging.append(staged_receipt)
            for source,destination in ((staged_project,products[1]),(staged_receipt,products[2]),(partial,target)):
                source.replace(destination);published.append(destination)
            if progress: progress(1.)
        finally:
            try:
                for path in owned_staging: path.unlink(missing_ok=True)
            finally:
                if lock_owned: reservation.unlink(missing_ok=True)
    return receipt
