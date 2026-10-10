"""Presentation plan in the existing canonical raster_time, not a second clock."""
import copy
import math
from datetime import date,timedelta
from output_profiles import profile_for,adaptive_regions
from studio_sig_layers import workspace_for,layer_command


def configure(project,lids,*,duration=3.,cadence='irregular',profile=None,safe_guides=True):
    state=workspace_for(project);registry=project['studio']['geography']
    ids=sorted(lids,key=lambda lid:registry['sources'][state['layers'][lid]['source_id']].get('date') or '')
    candidate=layer_command(project,{'action':'raster_time','value':{'layers':ids,'index':0,'compare':False,
        'duration':duration,'cadence':cadence,'safe_guides':safe_guides}})
    if profile is not None:
        from studio_workspace_commands import workspace_command
        candidate=workspace_command(candidate,candidate['studio']['timeline'][0],{'action':'profile','profile':profile})
    return layer_command(candidate,{'action':'raster_date','index':0})


def output_frame(project):
    """Fit a geographic window to the *actual* adaptive Studio map slot.

    A contained window (never outside the current view) has the slot's aspect;
    the exported raster uses that same bbox. Angular display is not an area/scale
    measurement. Existing old comparison resources keep their full view bbox.
    """
    state=workspace_for(project);time=state.get('raster_time',{})
    profile=profile_for(project['studio']['output_profile']);slot=adaptive_regions(profile)['map']
    box=state['view']['bbox'].copy()
    if 'duration' in time:
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
