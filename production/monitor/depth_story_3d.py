"""Original rotating 3D explanatory geometry; not measured shaking or rupture."""
import math
from PIL import Image, ImageDraw
from export_video import font
from reel_design import PANEL, TEAL, GOLD, MUTED, TEXT

SIZE = (840, 690)
MAX_DEPTH = 700


def camera_point(x, y, depth, seconds):
    yaw = .40 + .16 * math.sin(seconds / 8)
    u = x * math.cos(yaw) - y * math.sin(yaw)
    v = x * math.sin(yaw) + y * math.cos(yaw)
    perspective = 1800 / (1800 + .4*v + .20*depth)
    return 420 + .98*u*perspective, 150 + (.34*v + .64*depth)*perspective


def inside(x, y, z):
    return -300 <= x <= 300 and -180 <= y <= 180 and 0 <= z <= MAX_DEPTH


def render_source(depth, seconds, color=GOLD, mechanism=False):
    """Depth is factual; width, camera and waves are illustrative, not terrain."""
    ss = 1.5
    image = Image.new('RGB', (int(SIZE[0]*ss), int(SIZE[1]*ss)), PANEL)
    d = ImageDraw.Draw(image)
    def project(x,y,z): return tuple(v*ss for v in camera_point(x,y,z,seconds))
    def line(points, fill, width=2): d.line([project(*p) for p in points], fill=fill, width=round(width*ss))
    def poly(points, fill): d.polygon([project(*p) for p in points], fill=fill)
    # Two cutaway walls and a surface: independent actual 3D vertices.
    poly([(-300,180,0),(300,180,0),(300,180,700),(-300,180,700)], '#213d49')
    poly([(300,-180,0),(300,180,0),(300,180,700),(300,-180,700)], '#294853')
    for z in (0,70,150,300,500,700):
        line([(-300,180,z),(300,180,z),(300,-180,z)], '#44616c',1)
    for x in (-300,-150,0,150,300): line([(x,180,0),(x,180,700)], '#36545e',1)
    for y in (-180,0,180): line([(300,y,0),(300,y,700)], '#36545e',1)
    poly([(-300,-180,0),(300,-180,0),(300,180,0),(-300,180,0)], '#45645f')
    for x in (-300,-150,0,150,300): line([(x,-180,0),(x,180,0)], '#61887b',1)
    for y in (-180,-90,0,90,180): line([(-300,y,0),(300,y,0)], '#61887b',1)
    # A small surface settlement provides context, NOT a named city's geometry.
    for x,y,h in ((140,-80,24),(185,-75,37),(160,-120,18)):
        poly([(x-10,y-10,0),(x+10,y-10,0),(x+10,y-10,-h),(x-10,y-10,-h)], '#c8d5cc')
        poly([(x+10,y-10,0),(x+10,y+10,0),(x+10,y+10,-h),(x+10,y-10,-h)], '#93a9a3')
        poly([(x-10,y-10,-h),(x+10,y-10,-h),(x+10,y+10,-h),(x-10,y+10,-h)], TEXT)
    # Spherical wavefront wire-arcs in three orthogonal planes, clipped in 3D.
    # Cycles are editorial repetition, not travel-time or amplitude prediction.
    for offset in (0,1/3,2/3):
        radius = 20 + 410*((seconds/7+offset)%1)
        for plane in range(3):
            points=[]
            for i in range(121):
                angle=i*2*math.pi/120; a=radius*math.cos(angle); b=radius*math.sin(angle)
                p=(a,b,depth) if plane==0 else (a,0,depth+b) if plane==1 else (0,a,depth+b)
                if inside(*p): points.append(p)
                elif points:
                    if len(points)>1: line(points,'#739b9f',1.5)
                    points=[]
            if len(points)>1: line(points,'#739b9f',1.5)
    for z in range(0,math.ceil(depth),16): line([(0,0,z),(0,0,min(z+7,depth))],color,2)
    # Focus is fixed at the cited depth, never moved to match the voice.
    fx,fy=project(0,0,depth); ex,ey=project(0,0,0)
    r=(8+2*math.sin(seconds*2))*ss
    d.ellipse((fx-r,fy-r,fx+r,fy+r),fill=color,outline=TEXT,width=2)
    d.ellipse((ex-5*ss,ey-5*ss,ex+5*ss,ey+5*ss),fill=TEAL)
    image=image.resize(SIZE,Image.Resampling.LANCZOS); d=ImageDraw.Draw(image)
    ex,ey=camera_point(0,0,0,seconds); fx,fy=camera_point(0,0,depth,seconds)
    d.text((ex-135,ey-49),'Epicentro',font=font(25),fill=TEAL)
    d.text((min(625,fx+28),fy-15),'Foco',font=font(27),fill=color)
    for z in (0,70,300,700):
        x,y=camera_point(-300,180,z,seconds)
        d.text((max(12,x-55),y-13),str(z),font=font(22),fill=MUTED)
    d.text((28,22),'ESQUEMA 3D · NO ES UN REGISTRO DEL SISMO',font=font(22),fill=TEAL)
    d.text((28,606),'Eje vertical: km · ancho esquemático',font=font(24),fill=TEXT)
    d.text((28,647),'Ondas ilustrativas: sin escala de tiempo o amplitud',font=font(22),fill=MUTED)
    return image


def render_relocation(seconds):
    """Conceptual settlement relocation; no historical town/ruins reconstruction."""
    image=Image.new('RGB',SIZE,PANEL); d=ImageDraw.Draw(image)
    # Camera rotation, solid extruded foundations and homes, not flat icons.
    def p(x,y,z):
        angle=.28+.10*math.sin(seconds/7)
        u=x*math.cos(angle)-y*math.sin(angle); v=x*math.sin(angle)+y*math.cos(angle)
        return (420+u,350+.38*v-z)
    def settlement(cx, intact):
        corners=[p(cx-140,-110,0),p(cx+140,-110,0),p(cx+140,110,0),p(cx-140,110,0)]
        d.polygon([corners[2],corners[3],p(cx-140,110,-35),p(cx+140,110,-35)],fill='#36565c')
        d.polygon(corners,fill='#59786d')
        for i in range(6):
            x=cx-95+(i%3)*83; y=-55+(i//3)*98; h=35 if intact else 8+(i%3)*6
            d.polygon([p(x-20,y-17,0),p(x+20,y-17,0),p(x+20,y-17,h),p(x-20,y-17,h)],fill='#c4b090' if intact else '#8f806b')
            d.polygon([p(x+20,y-17,0),p(x+20,y+17,0),p(x+20,y+17,h),p(x+20,y-17,h)],fill='#9c896e')
            d.polygon([p(x-24,y-20,h),p(x+24,y-20,h),p(x,y,h+22 if intact else h+4),p(x+24,y+20,h),p(x-24,y+20,h)],fill=GOLD if intact else '#b69c7c')
    settlement(-210,False); settlement(210,True)
    d.text((30,26),'DIAGRAMA CONCEPTUAL · NO RECONSTRUCCIÓN',font=font(22),fill=TEAL)
    d.text((67,460),'Pelileo Viejo',font=font(31),fill=MUTED)
    d.text((478,460),'Reconstrucción',font=font(31),fill=GOLD)
    length=105+35*math.sin(seconds*.6)
    d.line((355,515,355+length,515),fill=TEAL,width=4)
    x=355+length; d.polygon([(x,515),(x-16,506),(x-16,524)],fill=TEAL)
    d.text((30,601),'IG-EPN documenta el cambio de ubicación.',font=font(28),fill=TEXT)
    d.text((30,647),'No representa el trazado ni los edificios de 1949.',font=font(22),fill=MUTED)
    return image


def render_piedmont_orbit(progress):
    """A rotating terrain mesh with a persistent scar and one-way debris path."""
    from piedmont_animation import state, terrain_height, smooth
    q=max(0,min(1,progress)); info=state(q)
    image=Image.new('RGB',SIZE,PANEL); d=ImageDraw.Draw(image)
    angle=.12+.48*smooth(q)
    def p(x,y,z):
        a=(x-.5)*620; b=y*390
        u=a*math.cos(angle)-b*math.sin(angle); v=a*math.sin(angle)+b*math.cos(angle)
        return 425+u,450+.28*v-175*z
    def surface(points): return [p(x,y,terrain_height(x,y)) for x,y in points]
    for edge,color in [([(0,.63),(1,.63)],'#36504b'), ([(1,-.63),(1,.63)],'#293e3e')]:
        a,b=edge
        d.polygon([p(*a,terrain_height(*a)),p(*b,terrain_height(*b)),p(*b,-.18),p(*a,-.18)],fill=color)
    cells=[]
    for ix in range(26):
        for iy in range(20):
            x0,x1=ix/26,(ix+1)/26; y0,y1=-.63+iy*1.26/20,-.63+(iy+1)*1.26/20
            v=(x0-.5)*620*math.sin(angle)+y0*390*math.cos(angle)
            cells.append((v,ix,iy,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]))
    for _,ix,iy,pts in sorted(cells):
        variation=((ix*17+iy*23)%13-6)*2
        d.polygon(surface(pts),fill=tuple(max(0,min(255,c+variation)) for c in (58+ix//2,100+ix//3,78)))
    river=[p(.79+.014*math.sin(y*8),y,terrain_height(.79+.014*math.sin(y*8),y)+.008) for y in [-.63+i*1.26/50 for i in range(51)]]
    d.line(river,fill='#376269',width=23); d.line(river,fill=TEAL,width=9)
    if info['scar']:
        d.polygon(surface([(.23,-.07),(.31,-.105),(.40,-.055),(.433,.093),(.39,.205),(.29,.22),(.245,.137)]),fill='#c1a17a')
    # Trees are outside the parcel: detached soil does not retain fixed trees.
    for i in range(38):
        x=.04+((i*37)%68)/100; y=-.57+((i*47)%110)/100
        if .21<x<.45 and -.13<y<.25: continue
        a,b=p(x,y,terrain_height(x,y)); h=12+i%8
        d.line((a,b,a,b-h),fill='#b5a17a',width=2)
        d.polygon([(a-7,b-h+4),(a,b-h-15),(a+7,b-h+4)],fill='#83aa79')
    cx,cy=info['center']; rocks=[]
    for i in range(52):
        dx=(((i*37)%101)/100-.5)*(.135+.065*info['slide'])
        dy=(((i*53)%103)/102-.5)*(.21+.18*info['flow'])
        x=cx+dx*(1-.65*info['flow']); y=cy+dy; z=terrain_height(x,y)+.015
        rocks.append((p(x,y,z)[1],x,y,z,.011+(i%4)*.003))
    for _,x,y,z,r in sorted(rocks):
        ring=[p(x+r*a,y+r*b,z) for a,b in [(-1,-.4),(-.3,-1),(.8,-.6),(1,.3),(.1,1),(-.8,.7)]]
        peak=p(x,y,z+r*1.8)
        for j in range(6): d.polygon([ring[j],ring[(j+1)%6],peak],fill=('#b49b76','#d6bc92','#9d8462')[j%3])
    if info['phase']==0:
        for i in range(16):
            x=175+i*29; y=110+(i*19+q*550)%120
            d.line((x,y,x-6,y+17),fill='#83c4c4',width=2)
    elif info['phase']==1:
        x,y=p(.45,.3,terrain_height(.45,.3))
        for k in range(3):
            r=14+60*((q*6+k/3)%1); d.ellipse((x-r,y-r*.35,x+r,y+r*.35),outline=GOLD,width=2)
    labels=['1 · LLUVIAS PREVIAS','2 · SACUDIDA','3 · DESLIZAMIENTO','4 · MATERIAL EN EL CAUCE']
    d.text((28,22),'RELIEVE 3D CONCEPTUAL · CÁMARA MÓVIL',font=font(23),fill=TEAL)
    d.text((28,70),labels[info['phase']],font=font(30),fill=GOLD)
    d.text((28,603),'Pendiente + saturación + sacudida',font=font(29),fill=TEXT)
    d.text((28,650),'No reconstruye 1987 ni calcula velocidades.',font=font(23),fill=MUTED)
    return image
