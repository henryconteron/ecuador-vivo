"""Metadata-only presentation of native support and matched result provenance."""
import math
from pyproj import CRS

def grid_info(source):
    if source.get('type')!='raster' or not source.get('native_crs'):return None
    crs=CRS.from_user_input(source['native_crs']);raster=source['raster'];transform=raster['transform']
    units=[axis.unit_name for axis in crs.axis_info[:2]]
    # Column and row vectors, not degrees guessed as kilometres. An affine
    # rotation does not justify discarding its off-diagonal coefficients.
    step=[math.hypot(transform[0],transform[3]),math.hypot(transform[1],transform[4])]
    if len(units)!=2 or units[0]!=units[1]:step=None
    return {'crs':crs.to_string(),'shape':raster['shape'],'step':step,
        'unit':units[0] if step else 'unidades de ejes diferentes',
        **{key:raster[key] for key in ('band','scale','offset','nodata') if key in raster}}

def matching_results(project):
    """Never relabel a stored Studio result as belonging to a new SIG selection."""
    studio=project['studio'];transfer=studio.get('sig_transfer',{})
    if not set(transfer.get('scene_ids',[])).intersection(studio.get('timeline',[])):return []
    geography=studio.get('geography',{});state=geography.get('map_workspace',{});time=state.get('raster_time')
    if time:
        if time.get('presentation',{}).get('territory','ecuador')!='ecuador':return []
        registry=geography.get('sources',{})
        try:sources=[registry[state['layers'][lid]['source_id']] for lid in time['layers']]
        except KeyError:return []
        record=studio.get('media',{}).get(transfer.get('asset_id'),{})
        declared=studio.get('datasets',{}).get(record.get('source_dataset'),[])
        if [(s['sha256'],s['date']) for s in sources]!=[(r['sha256'],r['date']) for r in declared]:return []
        ledger=studio.get('datasets',{}).get(transfer.get('science_dataset'),{}).get('source_records',[])
        for source in sources:
            original=next((r for r in ledger if (r['sha256'],r['date'])==(source['sha256'],source['date'])),None)
            if original is not None and original['units']!=source.get('units'):return []
    return transfer.get('results',[])
