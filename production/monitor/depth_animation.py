"""Original perspective depth lesson; geometric diagrams, not ground-motion models."""
import math
from functools import lru_cache

from PIL import Image, ImageDraw, ImageChops

from export_video import font
from reel_design import TEXT, MUTED, TEAL, GOLD, PANEL, LINE

DEEP_EXAMPLE = 500
INTERMEDIATE_EXAMPLE = 150
SHALLOW_EXAMPLE = 10
HORIZONTAL_DISTANCE = 40
DEPTH_SCALE = .95
WAVE_BOX = (210,540,807,1240)


def clamp(value):
    return max(0.0, min(1.0, value))


def ease(value):
    value=clamp(value)
    return value*value*(3-2*value)


def project_block(x, y, depth):
    # Fixed camera and identical scale in all three hypothetical experiments.
    return 510+1.5*(x+.55*y), 610+1.5*(.1*x+.28*y)+DEPTH_SCALE*depth


def path_length(depth):
    return math.hypot(HORIZONTAL_DISTANCE, depth)


def block_geometry():
    surface=[project_block(x,y,0) for x,y in [(-150,-75),(150,-75),(150,75),(-150,75)]]
    bottom=[project_block(x,y,600) for x,y in [(-150,-75),(150,-75),(150,75),(-150,75)]]
    return surface,bottom


@lru_cache(maxsize=1)
def wave_mask():
    top,bottom=block_geometry()
    mask=Image.new('L',(WAVE_BOX[2]-WAVE_BOX[0],WAVE_BOX[3]-WAVE_BOX[1]))
    d=ImageDraw.Draw(mask)
    for face in ([top[0],top[3],bottom[3],bottom[0]],
                 [top[3],top[2],bottom[2],bottom[3]],
                 [top[1],top[2],bottom[2],bottom[1]],top):
        d.polygon([(x-WAVE_BOX[0],y-WAVE_BOX[1]) for x,y in face],fill=255)
    return mask


def render_depth_block(image, depth, elapsed, color=GOLD):
    """Transparent, generic volume exposes focus depth; no local strata or fault."""
    d=ImageDraw.Draw(image)
    top,bottom=block_geometry()
    left=[top[0],top[3],bottom[3],bottom[0]]
    front=[top[3],top[2],bottom[2],bottom[3]]
    right=[top[1],top[2],bottom[2],bottom[1]]
    d.polygon(left,fill='#20343e',outline=LINE,width=2)
    d.polygon(right,fill='#243b46',outline=LINE,width=2)
    d.polygon(front,fill='#2d4650',outline=LINE,width=2)
    # A coordinate grid, NOT layers of geological material.
    for z in (70,150,300,500,600):
        points=[project_block(x,y,z) for x,y in [(-150,75),(150,75),(150,-75)]]
        d.line(points,fill='#405963',width=2)
    for x in (-75,0,75):
        d.line([project_block(x,75,0),project_block(x,75,600)],fill='#405963',width=1)
    d.polygon(top,fill='#41666b',outline=TEAL,width=3)
    # In-volume conceptual rings: do not draw propagating waves on the data plots.
    layer=Image.new('RGBA',wave_mask().size)
    waves=ImageDraw.Draw(layer)
    for delay in (0,1.2,2.4):
        phase=elapsed%9
        if phase<delay:continue
        radius=(phase-delay)*85
        points=[project_block(radius*math.cos(i*math.pi/72),0,depth+radius*math.sin(i*math.pi/72)) for i in range(145)]
        points=[(x-WAVE_BOX[0],y-WAVE_BOX[1]) for x,y in points]
        waves.line(points,fill=(110,223,211,130),width=2)
        transverse=[project_block(0,radius*math.cos(i*math.pi/72),depth+radius*math.sin(i*math.pi/72)) for i in range(145)]
        transverse=[(x-WAVE_BOX[0],y-WAVE_BOX[1]) for x,y in transverse]
        waves.line(transverse,fill=(110,223,211,75),width=2)
    layer.putalpha(ImageChops.multiply(layer.getchannel('A'),wave_mask()))
    image.paste(layer,WAVE_BOX[:2],layer)
    d=ImageDraw.Draw(image)
    epicenter=project_block(0,0,0)
    focus=project_block(0,0,depth)
    city=project_block(HORIZONTAL_DISTANCE,0,0)
    # Keep the city fixed: no unsupported model of house amplitude or collapse.
    cx,cy=city
    d.rounded_rectangle((cx-22,cy-43,cx+22,cy),radius=3,fill=TEXT,outline=PANEL,width=2)
    d.polygon([(cx-30,cy-43),(cx,cy-67),(cx+30,cy-43)],fill=GOLD)
    d.rectangle((cx-5,cy-23,cx+6,cy),fill=PANEL)
    d.text((cx-49,cy-106),'CIUDAD',font=font(23),fill=TEXT)
    d.line((epicenter[0],epicenter[1],city[0],city[1]),fill=TEXT,width=3)
    for yy in range(int(epicenter[1]+7),int(focus[1]),18):
        d.line((focus[0],yy,focus[0],min(yy+8,focus[1])),fill=MUTED,width=2)
    fraction=ease(elapsed/2.1)
    tip=(focus[0]+(city[0]-focus[0])*fraction,focus[1]+(city[1]-focus[1])*fraction)
    d.line((focus,tip),fill=GOLD,width=5)
    # Editorial travelling pointer, not a physical particle or arrival time.
    f=(elapsed*.20)%1
    dot=(focus[0]+(city[0]-focus[0])*f,focus[1]+(city[1]-focus[1])*f)
    d.ellipse((dot[0]-5,dot[1]-5,dot[0]+5,dot[1]+5),fill=TEXT)
    d.ellipse((focus[0]-10,focus[1]-10,focus[0]+10,focus[1]+10),fill=color,outline=TEXT,width=2)
    d.polygon([(epicenter[0],epicenter[1]-8),(epicenter[0]+8,epicenter[1]),(epicenter[0],epicenter[1]+8),(epicenter[0]-8,epicenter[1])],fill=TEAL)
    # Depth-axis label spacing is >=80 km except the separately annotated 10 km.
    for z in (0,150,300,500,600):
        yy=project_block(0,0,z)[1]
        d.line((838,yy,850,yy),fill=MUTED,width=2)
        d.text((858,yy-13),str(z),font=font(23),fill=GOLD if z==depth else MUTED)
    d.line((845,610,845,1180),fill=LINE,width=2)
    d.text((843,559),'km ↓',font=font(22),fill=MUTED)
    # Structured outside-the-volume annotation keeps shallow focus legible.
    ax,ay=135,715 if depth<70 else focus[1]-36
    d.line((ax+235,ay+25,focus[0]-15,focus[1]),fill=color,width=2)
    d.rounded_rectangle((ax,ay,ax+230,ay+75),radius=13,fill=PANEL,outline=color,width=2)
    d.text((ax+16,ay+10),f'FOCO · {depth} km',font=font(26),fill=TEXT)
    return dict(focus=focus,epicenter=epicenter,city=city,depth=depth,path_km=path_length(depth))
