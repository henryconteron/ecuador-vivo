"""Admission of dated provider rasters into the ONE canonical SIG workspace.

No temporal aggregation or interpolation occurs here. One native band per date;
provider originals/manifests remain untouched and their hashes travel as tags.
"""
import hashlib,json,re
from pathlib import Path
from datetime import date
from urllib.parse import urlsplit,urlunsplit
from studio_sig_layers import workspace_for
from studio_sig_raster import add_raster


def series_groups(project):
    state=workspace_for(project);sources=project['studio'].get('geography',{}).get('sources',{})
    groups={}
    for lid in state['order']:
        layer=state['layers'][lid];source=sources.get(layer['source_id'],{})
        if layer['type']!='raster' or not source.get('date'):continue
        provenance=source['provenance']
        citation=provenance['citation'].split(' · original gzip SHA256 ')[0]
        # Dates and per-file hashes identify observations, not different products.
        citation=re.sub(r'\b[0-9a-f]{64}\b','<hash>',citation)
        url=re.sub(r'\d{4}[-.]\d{2}[-.]\d{2}','<date>',provenance.get('url',''))
        url=re.sub(r'/\d{4}/','/<year>/',url)
        key=(citation,url,source['variable'],source['units'],source['semantics'])
        if key not in groups:
            groups[key]={'id':hashlib.sha256(json.dumps(key).encode()).hexdigest()[:16],
                'source':citation,'variable':source['variable'],'units':source['units'],
                'semantics':source['semantics'],'layers':[],'dates':[]}
        groups[key]['layers'].append(lid);groups[key]['dates'].append(source['date'])
    for group in groups.values():
        paired=sorted(zip(group['dates'],group['layers']));group['dates'],group['layers']=map(list,zip(*paired))
    return list(groups.values())


def admit_download(project,download):
    """All-or-nothing document admission; split multiband without resampling."""
    import rasterio
    from rasterio.io import MemoryFile
    entries=download.get('entries',[])
    if len(entries)<2:raise ValueError('La fuente debe devolver al menos dos fechas con datos para un timelapse.')
    days=[date.fromisoformat(e['date']).isoformat() for e in entries]
    if len(set(days))!=len(days):raise ValueError('La descarga contiene fechas duplicadas; revisa el producto.')
    manifest=download.get('manifest',{})
    public_url=manifest.get('source_url') or download.get('source_url','')
    if isinstance(public_url,list):public_url=public_url[0]
    parsed=urlsplit(public_url);public_url=urlunsplit((parsed.scheme,parsed.netloc,parsed.path,'',''))
    provenance={'citation':download['citation'],
        'license':manifest.get('license_note','NASA POWER: datos de acceso público; conservar atribución y condiciones del proveedor.'),
        'url':public_url}
    kind=download.get('profile_kind','precipitation' if download.get('provider')=='CHIRPS v3' else 'scalar')
    semantics=kind if kind in ('precipitation','temperature') else 'scalar'
    candidate=project;ids=[];digests={}
    for entry in entries:
        path=Path(entry['path']);raw_hash=digests.setdefault(str(path),None)
        if raw_hash is None:
            raw_hash=hashlib.sha256(path.read_bytes()).hexdigest();digests[str(path)]=raw_hash
        if entry.get('artifact_sha256')!=raw_hash:raise ValueError('El archivo descargado cambió respecto de su manifiesto.')
        band=entry.get('band',1)
        with rasterio.open(path) as ds:
            if type(band) is not int or not 1<=band<=ds.count:raise ValueError('Banda de la observación inválida.')
            values=ds.read(band);mask=ds.read_masks(band);profile=ds.profile.copy()
            profile.update(count=1,compress='deflate')
            profile.pop('photometric',None)
            with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=True),MemoryFile() as memory:
                with memory.open(**profile) as out:
                    out.write(values,1);out.write_mask(mask)
                    out.scales=(ds.scales[band-1],);out.offsets=(ds.offsets[band-1],)
                    out.update_tags(**ds.tags())
                    out.update_tags(original_sha256=raw_hash,original_band=str(band),observed_date=entry['date'],
                        original_request_urls=json.dumps(entry.get('source_url',[])),
                        time_standard=manifest.get('time_standard','provider-defined'))
                content=memory.read()
        candidate,lid=add_raster(candidate,content,download['provider']+' · '+entry['date']+'.tif',provenance,
            observed_date=entry['date'],variable=download['variable'],units=download['units'],semantics=semantics)
        ids.append(lid)
    return candidate,ids


def activate_series(project,ids,*,cadence='irregular',index=0,presentation=None):
    """Activate the existing canonical clock; no frames/calculations/export yet."""
    from studio_sig_timelapse import configure
    from studio_sig_layers import layer_command
    previous=workspace_for(project).get('raster_time',{})
    duration=max(len(ids)/30,max(3.,len(ids)/10))
    if len(ids)>3600:raise ValueError('Reduce la serie a 3600 observaciones para este video.')
    candidate=configure(project,ids,duration=min(120.,duration),cadence=cadence,
        presentation=presentation,safe_guides=previous.get('safe_guides',True))
    return layer_command(candidate,{'action':'raster_date','index':index})


def select_observation(project,lid):
    """A dated layer click selects its observation, not just an inspector row."""
    from studio_sig_layers import layer_command
    time=workspace_for(project).get('raster_time',{})
    if lid in time.get('layers',[]):
        return layer_command(project,{'action':'raster_date','index':time['layers'].index(lid)})
    group=next((g for g in series_groups(project) if lid in g['layers'] and len(g['layers'])>=2),None)
    if group:
        return activate_series(project,group['layers'],index=group['layers'].index(lid))
    return layer_command(project,{'action':'active','layer_id':lid})


def restore_downloaded_series(session):
    """One-time repair of the old download-only state, not a render-time guess.

    Only one unambiguous dated product and verified provider-admission tags.
    Imported static maps and ambiguous products are never automatically animated.
    A successful transaction marks the attempt, so undo is respected this session.
    """
    state=workspace_for(session.project)
    if state.get('raster_time'):return False
    groups=series_groups(session.project)
    if len(groups)!=1 or not 2<=len(groups[0]['layers'])<=3600:return False
    group=groups[0];ids=group['layers']
    marker=session.key+'_restored_series_'+hashlib.sha256('|'.join(ids).encode()).hexdigest()
    if session.state.get(marker) or any(not state['layers'][lid]['visible'] for lid in ids):return False
    sources=session.project['studio']['geography']['sources']
    from studio_sig_raster import compatible,verify_source
    records=[sources[state['layers'][lid]['source_id']] for lid in ids]
    if len(set(group['dates']))!=len(ids):return False
    try:compatible(records)
    except ValueError:return False
    import rasterio
    for source in records:
        with rasterio.open(verify_source(source)) as dataset:
            tags=dataset.tags()
            if 'original_request_urls' not in tags or tags.get('observed_date')!=source['date']:return False
    from studio_territory import DEFAULT
    candidate=activate_series(session.project,ids,presentation=DEFAULT)
    session.commit(candidate);session.state[marker]=True
    return True
