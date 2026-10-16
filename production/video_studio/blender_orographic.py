"""Trusted Blender script. Inputs are a finite recipe, never executable content.

Stylized explanatory geometry, not a DEM, forecast or cloud microphysics model.
The controller consumes one PNG at a time and acknowledges it before reuse.
"""
import json
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector


def material(name,color,roughness=.7,metallic=0):
    channels=[int(color[i:i+2],16)/255 for i in (1,3,5)]
    channels=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in channels]
    result=bpy.data.materials.new(name);result.diffuse_color=(*channels,1)
    result.use_nodes=True
    shader=result.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(*channels,1)
    shader.inputs['Roughness'].default_value=roughness
    shader.inputs['Metallic'].default_value=metallic
    return result


def mesh(name,vertices,faces,mat):
    geometry=bpy.data.meshes.new(name);geometry.from_pydata(vertices,[],faces);geometry.update()
    obj=bpy.data.objects.new(name,geometry);bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def sphere(name,position,scale,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,location=position)
    obj=bpy.context.object;obj.name=name;obj.scale=scale;obj.data.materials.append(mat)
    for face in obj.data.polygons:face.use_smooth=True
    return obj


def line(name,points,mat,radius=.04):
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.bevel_depth=radius;curve.bevel_resolution=3
    spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
    for target,point in zip(spline.points,points):target.co=(*point,1)
    obj=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat)
    return obj


def build(recipe,mode):
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT'
    scene.render.resolution_x=1080 if mode=='final' else 640
    scene.render.resolution_y=900 if mode=='final' else 534
    scene.render.resolution_percentage=100;scene.render.fps=30
    scene.frame_start=1;scene.frame_end=round(recipe['duration']*30)
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
    scene.render.film_transparent=False;scene.render.use_file_extension=True
    scene.view_settings.view_transform='AgX'
    scene.world.use_nodes=True
    bg=material('Backdrop',recipe['background'])
    scene.world.node_tree.nodes.get('Background').inputs[0].default_value=bg.diffuse_color
    scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.4
    if hasattr(scene.eevee,'taa_render_samples'):scene.eevee.taa_render_samples=64 if mode=='final' else 24
    grass=material('Relieve',recipe['ground']);rock=material('Corte de roca',recipe['rock'])
    water=material('Agua y recorrido',recipe['water'],.25,.15)
    snow=material('Cumbre','#ede5cf');cloud_mat=material('Nube ilustrativa','#edf5fa',.9)
    sand=material('Plataforma','#17313d',.6)
    elevation=lambda x,y:.1+recipe['mountain']*math.exp(-(x-.35)**2/.85)*( .88+.12*math.cos(y*1.6))+.12*math.cos(x*2+y)
    count=65;vertices=[];faces=[]
    for j in range(count):
        y=-1.9+j*3.8/(count-1)
        for i in range(count):
            x=-3.4+i*6.8/(count-1);vertices.append((x,y,elevation(x,y)))
    for j in range(count-1):
        for i in range(count-1):
            a=j*count+i;faces.append((a,a+1,a+1+count,a+count))
    terrain=mesh('Montaña conceptual',vertices,faces,grass);terrain.data.materials.append(snow)
    for face in terrain.data.polygons:
        face.use_smooth=True
        if face.center.z>recipe['mountain']*.85:face.material_index=1
    edge=[]
    for i in range(count):edge.append(vertices[i])
    for j in range(1,count):edge.append(vertices[j*count+count-1])
    for i in range(count-2,-1,-1):edge.append(vertices[(count-1)*count+i])
    for j in range(count-2,0,-1):edge.append(vertices[j*count])
    sides=[];side_faces=[]
    for i,p in enumerate(edge):sides.extend([p,(p[0],p[1],-.8)])
    for i in range(len(edge)):
        a=i*2;b=((i+1)%len(edge))*2;side_faces.append((a,b,b+1,a+1))
    mesh('Estratos en corte',sides,side_faces,rock)
    for z in (-.3,-.65):line('Contacto ilustrativo',[(p[0],p[1],z) for p in edge]+[(edge[0][0],edge[0][1],z)],sand,.018)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,-.9));base=bpy.context.object;base.name='Base del diorama';base.scale=(7.3,4.3,.2);base.data.materials.append(sand)
    bevel=base.modifiers.new('Bordes suaves','BEVEL');bevel.width=.1;bevel.segments=3
    # No river drawn across a ridge: that would confuse the orographic process.
    route=[]
    for i in range(61):
        x=-3.1+i*5.5/60;route.append((x,.25,.8+recipe['mountain']*.8*(math.sin(i/60*math.pi/2))))
    for start in range(0,60,4):line('Trayectoria del aire',route[start:start+3],water,.018)
    parcel=sphere('Parcela de aire',route[0],(.18,.18,.18),water)
    clouds=[]
    for i in range(13):
        position=(.45+(i%5)*.25,.15+math.sin(i*2.3)*.32,recipe['mountain']+.65+math.cos(i*1.7)*.16)
        clouds.append(sphere('Condensación ilustrativa',position,(.34,.26,.25),cloud_mat))
    drops=[]
    for i in range(18):drops.append(sphere('Precipitación ilustrativa',(0,0,0),(.025,.025,.09),water))
    bpy.ops.object.camera_add();camera=bpy.context.object;camera.name='Cámara del recurso';camera.data.type='ORTHO';camera.data.ortho_scale=recipe['distance'];scene.camera=camera
    target=Vector((0,0,.8));pitch=math.radians(recipe['pitch'])
    keys=list(range(1,scene.frame_end+1,max(1,scene.frame_end//24)))+[scene.frame_end]
    for frame in sorted(set(keys)):
        t=(frame-1)/max(1,scene.frame_end-1);yaw=math.radians(recipe['yaw']+recipe['orbit']*(t-.5))
        camera.location=(10*math.sin(yaw),-10*math.cos(yaw),.8+10*math.tan(pitch))
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        camera.keyframe_insert(data_path='location',frame=frame);camera.keyframe_insert(data_path='rotation_euler',frame=frame)
        q=min(1,t*1.4);parcel.location=(-3.1+q*5.5,.25,.8+recipe['mountain']*.8*math.sin(q*math.pi/2));parcel.keyframe_insert(data_path='location',frame=frame)
        growth=max(0,min(1,(t-.3)/.25)) if recipe['moist'] else 0
        for obj in clouds:
            obj.scale=(.34*growth,.26*growth,.25*growth);obj.keyframe_insert(data_path='scale',frame=frame)
        for i,obj in enumerate(drops):
            visible=recipe['rain'] and recipe['moist'] and t>.62
            x=.3+(i%6)*.22;y=-.2+(i//6)*.25
            fall=(t*4+i*.13)%1;top=recipe['mountain']+.6;ground=elevation(x,y)+.04
            obj.location=(x,y,top+(ground-top)*fall)
            obj.scale=(.025,.025,.09) if visible else (0,0,0)
            obj.keyframe_insert(data_path='location',frame=frame);obj.keyframe_insert(data_path='scale',frame=frame)
    bpy.ops.object.light_add(type='AREA',location=(-4,-5,8));light=bpy.context.object;light.name='Luz principal';light.data.energy=recipe['light'];light.data.shape='DISK';light.data.size=5
    light.rotation_euler=(Vector((0,0,0))-light.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.light_add(type='AREA',location=(4,3,6));rim=bpy.context.object;rim.name='Luz de contorno';rim.data.energy=recipe['light']*.8;rim.data.color=(.35,.7,1);rim.data.size=4
    rim.rotation_euler=(Vector((0,0,1))-rim.location).to_track_quat('-Z','Y').to_euler()
    scene['ecuador_vivo_recipe']=json.dumps(recipe,sort_keys=True)
    scene['scientific_status']='Ilustración conceptual: no DEM, pronóstico ni simulación física.'
    return scene


def main():
    job=Path(sys.argv[sys.argv.index('--')+1]).resolve()
    # A trusted script imports the same validator, not code supplied by a recipe.
    sys.path.insert(0,str(Path(__file__).parent))
    from studio_blender import validate_recipe
    request=json.loads((job/'request.json').read_text(encoding='utf-8'))
    recipe=validate_recipe(request['recipe']);mode=request['mode']
    if mode not in ('poster','preview','final'):raise ValueError('Modo inválido.')
    scene=build(recipe,mode)
    scene.frame_set(round(scene.frame_end*.65))
    bpy.ops.wm.save_as_mainfile(filepath=str(job/'scene.blend'),compress=True)
    frames=[round(scene.frame_end*.65)] if mode=='poster' else range(1,scene.frame_end+1)
    for index,frame in enumerate(frames):
        if (job/'cancel.request').exists():raise InterruptedError('Render cancelado.')
        scene.frame_set(frame);scene.render.filepath=str(job/'frame.png')
        bpy.ops.render.render(write_still=True)
        print('EV_FRAME:'+str(index),flush=True)
        if sys.stdin.readline().strip()!='EV_ACK':raise InterruptedError('El controlador del render se cerró.')
    print('EV_DONE',flush=True)


if __name__=='__main__':main()
