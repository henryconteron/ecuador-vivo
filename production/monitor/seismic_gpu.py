"""GPU-lit, depth-tested 3D teaching models; not measured waveforms or damage."""
import math
import numpy as np
import moderngl
from PIL import Image

BG=(16/255,31/255,41/255)
COLORS={'p':(.40,.88,.80),'s':(1,.57,.37),'love':(.72,.51,.95),'rayleigh':(.95,.77,.42)}


def front_radius(seconds,speed):
    # Editorial loop long enough to reach the surface from every cited depth.
    # No physical seconds, travel-time solution, velocity or amplitude implied.
    return .15+((seconds*speed)%8)


def displacement(kind, rest, seconds):
    """Idealized polarization in dimensionless units, +x propagation.

    Surface-mode exponential envelope is illustrative, not an elastic solution.
    Rayleigh surface ellipse is retrograde. Love presumes a guiding layered medium.
    """
    rest=np.asarray(rest,dtype=float)
    phase=2.1*rest[...,0]-seconds*2.1
    result=np.zeros_like(rest)
    if kind=='p': result[...,0]=.20*np.cos(phase)
    elif kind=='s': result[...,1]=.34*np.sin(phase)
    elif kind=='love': result[...,2]=.42*np.sin(phase)*np.exp(rest[...,1]*1.6)
    elif kind=='rayleigh':
        envelope=np.exp(rest[...,1]*1.6)
        result[...,0]=-.28*np.cos(phase)*envelope
        result[...,1]=.40*np.sin(phase)*envelope
    else: raise ValueError(kind)
    return result


def look_at(eye,target):
    eye=np.array(eye,float); target=np.array(target,float)
    f=target-eye; f/=np.linalg.norm(f); s=np.cross(f,[0,1,0]); s/=np.linalg.norm(s); u=np.cross(s,f)
    m=np.eye(4); m[0,:3]=s; m[1,:3]=u; m[2,:3]=-f
    m[:3,3]=-m[:3,:3]@eye
    return m


def perspective(aspect):
    f=1/math.tan(math.radians(38)/2); near=.1; far=80
    return np.array([[f/aspect,0,0,0],[0,f,0,0],[0,0,(far+near)/(near-far),2*far*near/(near-far)],[0,0,-1,0]],float)


def triangles(grid,color):
    a=grid[:-1,:-1].reshape(-1,3);b=grid[1:,:-1].reshape(-1,3)
    c=grid[1:,1:].reshape(-1,3);d=grid[:-1,1:].reshape(-1,3)
    pts=np.stack((a,b,c,a,c,d),axis=1).reshape(-1,3,3)
    normals=np.cross(pts[:,1]-pts[:,0],pts[:,2]-pts[:,0])
    normals/=np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-8)
    normals[normals[:,1]<0]*=-1
    points=pts.reshape(-1,3); normals=np.repeat(normals,3,axis=0)
    return np.column_stack((points,normals,np.tile(color,(len(points),1)))).astype('f4')


def flat_mesh(faces,colors):
    """Flat-shaded triangular solids; retain wall normals rather than forcing up."""
    pts=np.asarray(faces,float).reshape(-1,3,3)
    normals=np.cross(pts[:,1]-pts[:,0],pts[:,2]-pts[:,0])
    normals/=np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-8)
    return np.column_stack((pts.reshape(-1,3),np.repeat(normals,3,axis=0),
        np.repeat(np.asarray(colors,float).reshape(-1,3),3,axis=0))).astype('f4')


def sphere_mesh():
    rows=[]
    for j in range(8):
        for i in range(12):
            def v(a,b):
                lat=math.pi*a/8; lon=2*math.pi*b/12
                return (math.sin(lat)*math.cos(lon),math.cos(lat),math.sin(lat)*math.sin(lon))
            a,b,c,d=v(j,i),v(j+1,i),v(j+1,i+1),v(j,i+1)
            for point in (a,b,c,a,c,d): rows.append((*point,*point))
    return np.array(rows,'f4')


class SeismicGPU:
    def __init__(self,size=(940,850)):
        self.size=size; self.ctx=moderngl.create_context(standalone=True,require=330)
        self.renderer=self.ctx.info['GL_RENDERER']
        self.fbo=self.ctx.simple_framebuffer(size,components=3,samples=4)
        self.resolve=self.ctx.simple_framebuffer(size,components=3)
        vertex='''#version 330
        in vec3 in_pos; in vec3 in_normal; in vec3 in_color;
        uniform mat4 mvp; out vec3 normal; out vec3 world; out vec3 color;
        void main(){world=in_pos;normal=in_normal;color=in_color;gl_Position=mvp*vec4(in_pos,1.0);}'''
        fragment='''#version 330
        in vec3 normal; in vec3 world; in vec3 color; uniform vec3 eye; uniform float opacity;
        out vec4 frag;
        void main(){vec3 n=normalize(normal);
          vec3 l=normalize(vec3(-.4,1.0,.7));vec3 v=normalize(eye-world);
          float diffuse=max(dot(n,l),0.0);float spec=pow(max(dot(n,normalize(l+v)),0.0),48.0);
          float rim=pow(1.0-max(dot(n,v),0.0),3.0);
          vec3 c=color*(.32+.68*diffuse)+vec3(.7,.9,1.0)*spec*.28+color*rim*.20;
          frag=vec4(pow(c,vec3(.80)),opacity);}'''
        self.solid=self.ctx.program(vertex_shader=vertex,fragment_shader=fragment)
        self.particles=self.ctx.program(vertex_shader='''#version 330
          in vec3 in_pos;in vec3 in_normal;in vec3 offset;in vec3 tint;in float radius;
          uniform mat4 mvp;out vec3 normal;out vec3 world;out vec3 color;
          void main(){world=offset+in_pos*radius;normal=in_normal;color=tint;gl_Position=mvp*vec4(world,1.0);}''',fragment_shader=fragment)
        self.lines=self.ctx.program(vertex_shader='''#version 330
          in vec3 position; in vec3 tint; uniform mat4 mvp;out vec3 color;
          void main(){gl_Position=mvp*vec4(position,1.0);color=tint;}''',fragment_shader='''#version 330
          in vec3 color;out vec4 frag;void main(){frag=vec4(color,1.0);}''')
        self.sphere=self.ctx.buffer(sphere_mesh().tobytes())
        self.instances=self.ctx.buffer(reserve=8192*7*4)
        self.sphere_vao=self.ctx.vertex_array(self.particles,[(self.sphere,'3f 3f','in_pos','in_normal'),(self.instances,'3f 3f 1f /i','offset','tint','radius')])
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.matrix=None

    def begin(self,seconds,target=(0,-.5,0),distance=1):
        angle=.94+.06*math.sin(seconds*.22)
        eye=np.array([math.sin(angle)*11,6.0,math.cos(angle)*11])*distance
        self.matrix=perspective(self.size[0]/self.size[1])@look_at(eye,target)
        for program in (self.solid,self.particles,self.lines): program['mvp'].write(self.matrix.astype('f4').T.tobytes())
        for program in (self.solid,self.particles):
            program['eye'].value=tuple(eye);program['opacity'].value=1.0
        self.fbo.use(); self.fbo.clear(*BG,1,depth=1)

    def mesh(self,vertices):
        if len(vertices)==0:return
        buffer=self.ctx.buffer(np.asarray(vertices,'f4').tobytes()); vao=self.ctx.vertex_array(self.solid,[(buffer,'3f 3f 3f','in_pos','in_normal','in_color')])
        vao.render(); vao.release();buffer.release()

    def balls(self,positions,colors,radii):
        data=np.column_stack((positions,colors,radii)).astype('f4')
        self.instances.write(data.tobytes()); self.sphere_vao.render(instances=len(data))

    def segments(self,points,color=(.25,.44,.49)):
        points=np.array(points,'f4').reshape(-1,3)
        if not len(points):return
        data=np.column_stack((points,np.tile(color,(len(points),1)))).astype('f4')
        buf=self.ctx.buffer(data.tobytes());vao=self.ctx.vertex_array(self.lines,[(buf,'3f 3f','position','tint')])
        vao.render(mode=moderngl.LINES);vao.release();buf.release()

    def screen(self,point):
        q=self.matrix@np.array([*point,1]); q=q[:3]/q[3]
        return (q[0]+1)*self.size[0]/2,(1-q[1])*self.size[1]/2

    def finish(self):
        self.ctx.copy_framebuffer(self.resolve,self.fbo)
        return Image.frombytes('RGB',self.size,self.resolve.read(components=3,alignment=1)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)

    def wave(self,kind,seconds,camera_seconds=None):
        # Fixed-camera option lets QA distinguish material motion from orbit.
        self.begin(seconds if camera_seconds is None else camera_seconds)
        color=COLORS[kind]
        # Smooth continuous front/top meshes, coupled to the same motion law.
        for surface in ('top','front'):
            grid=np.zeros((11,55,3),float)
            for j in range(11):
                for i in range(55): grid[j,i]=(-4+i*8/54,0 if surface=='top' else -j*1.5/10,-1.35+j*2.7/10 if surface=='top' else 1.35)
            grid+=displacement(kind,grid,seconds)
            if kind!='p': self.mesh(triangles(grid,tuple(c*.42 for c in color)))
        rest=np.array([(x,y,z) for x in np.linspace(-4,4,25) for y in (0,-.5,-1,-1.5) for z in (-1.35,0,1.35)])
        moved=rest+displacement(kind,rest,seconds)
        colors=np.tile(color,(len(rest),1));radii=np.full(len(rest),.048)
        # Yellow tracer: same material particle, not a parcel travelling with the wave.
        trace_rest=np.array([[0,0,1.35]]); tracer=(trace_rest+displacement(kind,trace_rest,seconds))[0]
        self.balls(moved,colors,radii);self.balls([tracer],[(1,.87,.46)],[.11])
        if kind=='p':
            for y in (0,-.5,-1,-1.5):
                for z in (-1.35,0,1.35):
                    pts=np.array([(x,y,z) for x in np.linspace(-4,4,25)])
                    pts+=displacement(kind,pts,seconds)
                    self.segments([p for a,b in zip(pts,pts[1:]) for p in (a,b)],(.28,.57,.54))
            for x in np.linspace(-4,4,25):
                pts=np.array([(x,y,1.35) for y in (0,-.5,-1,-1.5)])
                pts+=displacement(kind,pts,seconds)
                self.segments([p for a,b in zip(pts,pts[1:]) for p in (a,b)],(.34,.68,.62))
        trail=[]
        for t in np.linspace(seconds-3,seconds,80):trail.append((trace_rest+displacement(kind,trace_rest,t))[0])
        self.segments([p for a,b in zip(trail,trail[1:]) for p in (a,b)],(1,.8,.32))
        for z in (-1.35,0,1.35):
            pts=np.array([(x,0,z) for x in np.linspace(-4,4,80)])
            pts+=displacement(kind,pts,seconds)
            self.segments([p for a,b in zip(pts,pts[1:]) for p in (a,b)],tuple(c*.6 for c in color))
        # Persistent +x arrow, far enough away from deformed material.
        self.segments([(-3,.9,-1.4),(3,.9,-1.4),(3,.9,-1.4),(2.65,1.04,-1.4),(3,.9,-1.4),(2.65,.76,-1.4)],(.95,.96,.91))
        tracer_screen=self.screen(tracer)
        return self.finish(),tracer_screen

    def depth(self,depth_km,seconds):
        self.begin(seconds,target=(0,-2.2,0),distance=1.30)
        # Same 0–700 km reference for all three cases; no invented rock layers.
        zmax=5.6; focus_y=-depth_km/700*zmax
        lines=[]
        for d in (0,70,300,700):
            y=-d/700*zmax
            lines.extend([(-3,y,-1.8),(3,y,-1.8),(3,y,-1.8),(3,y,1.8)])
        for x in (-3,0,3):lines.extend([(x,0,-1.8),(x,-zmax,-1.8)])
        # Foreground reference edge: the opaque surface must not hide the scale.
        # Tick heights are projected from the same geometry as the focal depth.
        lines.extend([(-3,0,1.8),(-3,-zmax,1.8)])
        for d in (0,70,300,700):
            y=-d/700*zmax
            lines.extend([(-3,y,1.8),(-2.8,y,1.8)])
        self.segments(lines)
        grid=np.array([[(-3,0,-1.8),(3,0,-1.8)],[(-3,0,1.8),(3,0,1.8)]],float)
        self.segments([(0,0,0),(0,focus_y,0)],(.96,.77,.42))
        self.balls([(0,focus_y,0),(0,0,0)],[(1,.72,.34),(.36,.88,.81)],[.13,.08])
        # 3D P/S schematic wavefronts expanding at different editorial rates.
        for speed,color in ((1.1,COLORS['p']),(.65,COLORS['s'])):
            r=front_radius(seconds,speed)
            for plane in range(3):
                ring=[]
                for a in np.linspace(0,2*math.pi,100):
                    u,v=r*math.cos(a),r*math.sin(a)
                    p=(u,focus_y+v,0) if plane==0 else (0,focus_y+u,v) if plane==1 else (u,focus_y,v)
                    ring.append(p if -zmax<=p[1]<=0 and abs(p[0])<=3 and abs(p[2])<=1.8 else None)
                self.segments([p for a,b in zip(ring,ring[1:]) if a is not None and b is not None for p in (a,b)],color)
            if r>abs(focus_y):
                # Intersection with surface, lifted slightly to avoid z-fighting.
                rr=math.sqrt(r*r-focus_y*focus_y);ring=[]
                for a in np.linspace(0,2*math.pi,100):
                    x,z=rr*math.cos(a),rr*math.sin(a)
                    ring.append((x,.025,z) if abs(x)<=3 and abs(z)<=1.8 else None)
                self.segments([p for a,b in zip(ring,ring[1:]) if a is not None and b is not None for p in (a,b)],color)
        # Render the reference surface last with transparency, so even a shallow
        # focus remains visible. This is an x-ray teaching view, not real rock.
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func=moderngl.SRC_ALPHA,moderngl.ONE_MINUS_SRC_ALPHA
        self.solid['opacity'].value=.28
        self.mesh(triangles(grid,(.24,.40,.35)))
        self.solid['opacity'].value=1.0
        self.ctx.disable(moderngl.BLEND)
        self.segments([(-3,0,-1.8),(3,0,-1.8),(3,0,-1.8),(3,0,1.8),
            (3,0,1.8),(-3,0,1.8),(-3,0,1.8),(-3,0,-1.8)],(.31,.59,.51))
        anchors={d:self.screen((-3,-d/700*zmax,1.8)) for d in (0,70,300,700)}
        anchors['focus']=self.screen((0,focus_y,0));anchors['epicenter']=self.screen((0,0,0))
        return self.finish(),anchors

    def piedmont(self,progress,seconds):
        from piedmont_animation import state,terrain_height
        info=state(progress)
        self.begin(seconds,target=(0,.25,0),distance=.97)
        def position(x,y): return np.array([(x-.5)*7,terrain_height(x,y)*2.2-.5,y*4])
        grid=np.array([[position(x,y) for x in np.linspace(0,1,55)] for y in np.linspace(-.63,.63,35)])
        self.mesh(triangles(grid,(.27,.48,.33)))
        if not hasattr(self,'_piedmont_solids'):
            faces=[];colors=[]
            def face(a,b,c,color):faces.append((a,b,c));colors.append(color)
            # Solid cutaway walls, not geological strata or real terrain data.
            edges=[[(x,-.63) for x in np.linspace(0,1,55)],[(1,y) for y in np.linspace(-.63,.63,35)],
                [(x,.63) for x in np.linspace(1,0,55)],[(0,y) for y in np.linspace(.63,-.63,35)]]
            for edge in edges:
                for a,b in zip(edge,edge[1:]):
                    p,q=position(*a),position(*b);u=p.copy();v=q.copy();u[1]=v[1]=-.9
                    face(p,q,v,(.21,.30,.27));face(p,v,u,(.21,.30,.27))
            # Original low-poly vegetation gives a visible scale and stable terrain cues.
            for i in range(55):
                x=.035+((i*37)%94)/100;y=-.57+((i*47)%114)/100
                if (.21<x<.46 and -.15<y<.27) or .72<x<.86:continue
                base=position(x,y);h=.25+(i%5)*.035
                for offset,radius,height,color in [(0,.024,h*.65,(.39,.28,.16)),(h*.25,.12,h*.85,(.20,.40,.28)),(h*.55,.09,h*.65,(.32,.52,.33))]:
                    origin=base+[0,offset,0];peak=origin+[0,height,0]
                    ring=[origin+[radius*math.cos(a),0,radius*math.sin(a)] for a in np.linspace(0,2*math.pi,7)]
                    for p,q in zip(ring,ring[1:]):face(p,peak,q,color)
            self._piedmont_solids=flat_mesh(faces,colors)
        self.mesh(self._piedmont_solids)
        river=np.array([[position(.79+.014*math.sin(y*8)+dx,y)+[0,.025,0]
            for dx in (-.015,.015)] for y in np.linspace(-.63,.63,90)])
        self.mesh(triangles(river,(.25,.74,.75)))
        # An irregular persistent scar, not a rectangular cutout or a DEM claim.
        if info['scar']:
            center=position(.33,.065)+[0,.028,0];ring=[]
            for a in np.linspace(0,2*math.pi,38):
                jagged=1+.10*math.sin(a*7)+.06*math.cos(a*11)
                ring.append(position(.33+.105*math.cos(a)*jagged,.065+.15*math.sin(a)*jagged)+[0,.028,0])
            faces=[(center,p,q) for p,q in zip(ring,ring[1:])]
            self.mesh(flat_mesh(faces,[(.63,.43,.24)]*len(faces)))
        cx,cy=info['center'];rest=[]
        for i in range(75):
            x=cx+(((i*37)%101)/100-.5)*(.14+.07*info['slide'])*(1-.65*info['flow'])
            y=cy+(((i*53)%103)/102-.5)*(.20+.18*info['flow'])
            rest.append(position(x,y)+[0,.065,0])
        # Angular soil/rock parcels, moving down slope then into the channel.
        template=np.array([[[0,1,0],[1,0,0],[0,0,1]],[[0,1,0],[0,0,1],[-1,0,0]],
            [[0,1,0],[-1,0,0],[0,0,-1]],[[0,1,0],[0,0,-1],[1,0,0]],
            [[0,-1,0],[0,0,1],[1,0,0]],[[0,-1,0],[-1,0,0],[0,0,1]],
            [[0,-1,0],[0,0,-1],[-1,0,0]],[[0,-1,0],[1,0,0],[0,0,-1]]],float)
        sizes=np.array([.055+(i%4)*.014 for i in range(len(rest))])
        faces=(template[None,:,:,:]*sizes[:,None,None,None]+np.array(rest)[:,None,None,:]).reshape(-1,3,3)
        colors=[(.65+.04*(i%4),.46+.03*(i%4),.25+.02*(i%4)) for i in range(len(rest)) for _ in range(8)]
        self.mesh(flat_mesh(faces,colors))
        if info['phase']==0:
            drops=[]
            for i in range(55):
                x=.04+(i*37%90)/100;y=-.60+(i*53%120)/100;base=position(x,y)
                height=.25+((i/55-progress*9)%1)*1.3
                drops.extend([base+[0,height,0],base+[-.025,height-.15,0]])
            self.segments(drops,(.42,.71,.86))
        elif info['phase']==1:
            for offset in (0,.4):
                r=.15+((progress*5+offset)%1)*2
                ring=[position(.45+math.cos(a)*r/7,.15+math.sin(a)*r/4)+[0,.05,0] for a in np.linspace(0,2*math.pi,90)]
                self.segments([p for a,b in zip(ring,ring[1:]) for p in (a,b)],(.95,.75,.4))
        return self.finish(),info['phase']


if __name__=='__main__':
    from pathlib import Path
    folder=Path('artifacts/serie_memoria_sismica/00_profundidad_danos/v5');folder.mkdir(parents=True,exist_ok=True)
    renderer=SeismicGPU()
    for kind in COLORS:renderer.wave(kind,2)[0].save(folder/f'gpu_{kind}.png')
    renderer.piedmont(.58,5)[0].save(folder/'gpu_piedmont.png')
    renderer.depth(631.3,2)[0].save(folder/'gpu_depth.png')
    print(renderer.renderer)
