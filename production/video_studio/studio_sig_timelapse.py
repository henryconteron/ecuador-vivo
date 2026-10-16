"""Presentation plan in the existing canonical raster_time, not a second clock."""
import copy
import math
from datetime import date,timedelta
from output_profiles import profile_for,adaptive_regions
from studio_sig_layers import workspace_for,layer_command


def configure(project,lids,*,duration=3.,cadence='irregular',profile=None,safe_guides=True,presentation=None):
    state=workspace_for(project);registry=project['studio'].get('geography',{'sources':{}})
    if not isinstance(lids,list) or len(lids)<2:
        raise ValueError('Selecciona al menos dos observaciones con fechas distintas.')
    for lid in lids:
        layer=state['layers'].get(lid)
        source=registry['sources'].get(layer['source_id']) if layer else None
        if not source or layer['type']!='raster' or not source.get('date'):
            raise ValueError('Cada observación debe ser un ráster del proyecto con fecha declarada.')
    ids=sorted(lids,key=lambda lid:registry['sources'][state['layers'][lid]['source_id']].get('date') or '')
    from studio_territory import options_for,validate
    presentation=validate(presentation or options_for(project))
    candidate=layer_command(project,{'action':'raster_time','value':{'layers':ids,'index':0,'compare':False,
        'duration':duration,'cadence':cadence,'safe_guides':safe_guides,'presentation':presentation,
        **({'palette':state['raster_time']['palette']} if state.get('raster_time',{}).get('palette') else {})}})
    if profile is not None:
        from studio_workspace_commands import workspace_command
        candidate=workspace_command(candidate,candidate['studio']['timeline'][0],{'action':'profile','profile':profile})
    candidate=layer_command(candidate,{'action':'raster_date','index':0})
    if presentation['territory']!='view':
        candidate=layer_command(candidate,{'action':'view','bbox':output_frame(candidate)['bbox']})
    return candidate


def output_frame(project):
    """Fit a geographic window to the *actual* adaptive Studio map slot.

    A contained window (never outside the current view) has the slot's aspect;
    the exported raster uses that same bbox. Angular display is not an area/scale
    measurement. Existing old comparison resources keep their full view bbox.
    """
    state=workspace_for(project);time=state.get('raster_time',{})
    profile=profile_for(project['studio']['output_profile']);slot=adaptive_regions(profile)['map']
    box=state['view']['bbox'].copy()
    from studio_territory import options_for
    presentation=options_for(project)
    if presentation['territory']!='view':
        from studio_social_template import regions
        slot=regions(profile)['continent']
        from studio_territory import territory_bbox
        box=territory_bbox(presentation)
        ratio=slot['width']/slot['height'];cx=(box[0]+box[2])/2;cy=(box[1]+box[3])/2
        # Expand for the full country, never crop it to the social format.
        width=max(box[2]-box[0],(box[3]-box[1])*ratio);height=width/ratio
        box=[cx-width/2,cy-height/2,cx+width/2,cy+height/2]
    elif 'duration' in time:
        ratio=slot['width']/slot['height'];cx=(box[0]+box[2])/2;cy=(box[1]+box[3])/2
        width=min(box[2]-box[0],(box[3]-box[1])*ratio);height=width/ratio
        box=[cx-width/2,cy-height/2,cx+width/2,cy+height/2]
    return {'bbox':box,'width':profile.width,'height':profile.height,'map_width':math.ceil(slot['width']),
        'map_height':math.ceil(slot['height']),'safe_guides':time.get('safe_guides',True),
        'margin_fraction':profile.margin/min(profile.width,profile.height)}


def gaps(dates,cadence):
    """Report holes, never fabricate observations or allocate synthetic frames."""
    if cadence=='irregular':return []
    missing=[]
    for left,right in zip(dates,dates[1:]):
        a=date.fromisoformat(left);b=date.fromisoformat(right)
        if cadence=='daily':
            count=(b-a).days-1
        else:
            count=(b.year-a.year)*12+b.month-a.month-1
        if count>0:missing.append({'after':left,'before':right,'missing_intervals':count})
    return missing
