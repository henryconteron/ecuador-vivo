"""Profiles-first scientific reel: deep -> intermediate -> shallow -> actual cases."""
from functools import lru_cache
from hashlib import sha256
import json
import math
import subprocess

from PIL import Image, ImageDraw

from prepare_depth_episode import FOLDER, HASH
from reel_depth_damage import DepthDesign, shell, paragraph
from depth_animation import (render_depth_block, DEEP_EXAMPLE, INTERMEDIATE_EXAMPLE,
                             SHALLOW_EXAMPLE, HORIZONTAL_DISTANCE, path_length)
from reel_design import write, panel, BG, TEXT, MUTED, GOLD, TEAL, LINE
from export_video import font, depth_color
from historical import magnitude_size

SCENES=[(0,14,'pregunta_cortes'),(14,30,'leer_cortes'),(30,50,'profundo'),
        (50,65,'intermedio'),(65,77,'superficial'),(77,85,'comparacion'),
        (85,101,'pedernales'),(101,114,'quito'),(114,130,'reventador'),
        (130,143,'factores'),(143,155,'cierre')]
DURATION=155
PROFILE_BOXES=((165,470,900,830),(165,1010,900,1370))
PROFILE_FIELDS=('longitude','latitude')
PROFILE_LIMITS=((-83,-74.5),(-5.5,2.5))


def profile_position(position,depth,index):
    x0,y0,x1,y1=PROFILE_BOXES[index]
    lower,upper=PROFILE_LIMITS[index]
    return x0+(position-lower)/(upper-lower)*(x1-x0), y0+depth/300*(y1-y0)


def reading_depth(elapsed):
    # Smooth downward guide: editorial axis reading only, not an observed wave.
    return 254*min(1,max(0,elapsed/7))


class DepthDesignV2(DepthDesign):
    def __init__(self,folder=FOLDER):
        super().__init__(folder)
        self.known=[r for r in self.rows if r['depth_km'] is not None]
        self.maximum=max(r['depth_km'] for r in self.known)
        if self.maximum>=300: raise ValueError('Review the no-deep-events claim if the selection changes')
        source_audit=json.loads((self.folder/'source_audit_v2.json').read_text(encoding='utf-8'))
        if source_audit['catalog_sha256']!=HASH or source_audit['maximum_selected_depth_km']!=self.maximum:
            raise ValueError('V2 source audit differs from the plotted data')
        for record in list(source_audit['sources'].values())+source_audit['cases']:
            if sha256((self.folder/record['file']).read_bytes()).hexdigest()!=record['sha256']:
                raise ValueError('Verified primary source was modified')

    @lru_cache(maxsize=2)
    def profiles_base(self,lesson=False):
        im=shell('¿Qué significan estos cortes?' if not lesson else 'El mapa, visto de lado.',
                 'En el video anterior: Oeste–Este y Sur–Norte' if not lesson else 'Mismos eventos con profundidad · dos proyecciones, no dos catálogos')
        d=ImageDraw.Draw(im)
        for index,(field,box,limits,label,ticks) in enumerate(zip(PROFILE_FIELDS,PROFILE_BOXES,PROFILE_LIMITS,
                ('OESTE → ESTE','SUR → NORTE'),((-82,-80,-78,-76),(-4,-2,0,2)))):
            x0,y0,x1,y1=box
            write(d,(90,y0-72),label,31,TEAL)
            write(d,(730,y0-67),'km ↓',26,MUTED)
            d.rectangle(box,fill='#233d48',outline=LINE,width=2)
            for depth in (0,70,150,300):
                _,y=profile_position(limits[0],depth,index)
                d.line((x0,y,x1,y),fill=LINE,width=2)
                write(d,(92,y-15),str(depth),24,MUTED)
            for tick in ticks:
                x,_=profile_position(tick,0,index)
                d.line((x,y0,x,y1),fill=LINE,width=1)
                label=f'{abs(tick)}°'+(' O' if index==0 else ' S' if tick<0 else ' N' if tick>0 else '')
                d.text((x-27,y1+14),label,font=font(24),fill=MUTED)
            layer=Image.new('RGBA',(x1-x0,y1-y0))
            points=ImageDraw.Draw(layer)
            for row in self.known:
                x,y=profile_position(row[field],row['depth_km'],index); x-=x0; y-=y0
                r=magnitude_size(row['magnitude'])*1.4/2
                points.ellipse((x-r,y-r,x+r,y+r),fill=depth_color(row['depth_km'])+(210,),outline=(220,226,211,90))
            im.paste(layer,box[:2],layer)
        panel(d,(90,1430,930,1580),GOLD)
        write(d,(120,1446),'USGS · 1900–2025 · selección regional',29,GOLD)
        write(d,(120,1491),f'Máximo: {self.maximum:g} km · 1 dato sin profundidad',27)
        write(d,(120,1533),'No son cortes de capas ni una falla medida.',26,MUTED)
        return im

    def profiles(self,elapsed,lesson=False):
        im=self.profiles_base(lesson).copy()
        d=ImageDraw.Draw(im)
        if not lesson:
            index=min(1,int(elapsed/6))
            box=PROFILE_BOXES[index]
            d.rectangle(box,outline=GOLD,width=3)
        else:
            depth=reading_depth(elapsed)
            for i,box in enumerate(PROFILE_BOXES):
                _,y=profile_position(PROFILE_LIMITS[i][0],depth,i)
                d.line((box[0],y,box[2],y),fill=TEAL,width=3)
                d.rounded_rectangle((690,y+5,879,y+42),radius=7,fill=BG)
                d.text((702,y+7),f'Lectura: {depth:.0f} km',font=font(22),fill=TEAL)
        return im

    def depth_scene(self,name,elapsed):
        depth,title,kind,color,lesson={
            'profundo':(DEEP_EXAMPLE,'Empecemos abajo.','PROFUNDO · 300–700 km','#ce95c9',
                        'A igual magnitud, un trayecto mayor suele reducir la sacudida cercana. No significa que sea inofensivo.'),
            'intermedio':(INTERMEDIATE_EXAMPLE,'Subamos a 150 km.','INTERMEDIO · 70–300 km','#e89772',
                          'La misma ciudad queda más cerca de la fuente. El epicentro no cuenta toda esa distancia.'),
            'superficial':(SHALLOW_EXAMPLE,'Ahora, cerca de la superficie.','SUPERFICIAL · 0–70 km',GOLD,
                           'Menor distancia: suele haber mayor sacudida cerca de la fuente, si lo demás es comparable.')
        }[name]
        im=shell(title,'Tres fuentes hipotéticas · misma magnitud, ciudad y terreno')
        d=ImageDraw.Draw(im)
        panel(d,(90,405,930,496),color)
        write(d,(120,433),kind,30,color)
        write(d,(740,435),f'{depth} km',27)
        render_depth_block(im,depth,elapsed,color)
        d=ImageDraw.Draw(im)
        write(d,(120,522),'Retícula de referencia, no capas.',21,MUTED)
        write(d,(120,1280),f'Distancia al foco ≈ {path_length(depth):.0f} km',31,GOLD)
        write(d,(120,1325),'La ciudad sigue a 40 km del epicentro.',27,MUTED)
        panel(d,(90,1380,930,1575),color)
        paragraph(d,(120,1401),lesson,30,width=772,spacing=40)
        write(d,(120,1530),'Esquema 3D · ondas sin escala temporal',24,MUTED)
        return im

    def comparison_v2(self,elapsed):
        im=shell('Tres profundidades. Una ciudad.','Comparamos escenarios hipotéticos, no terremotos históricos')
        d=ImageDraw.Draw(im)
        for index,(depth,kind,color) in enumerate([(500,'PROFUNDO','#ce95c9'),(150,'INTERMEDIO','#e89772'),(10,'SUPERFICIAL',GOLD)]):
            y=432+index*264
            panel(d,(90,y,930,y+235),color)
            write(d,(122,y+24),kind,27,color)
            write(d,(122,y+84),f'{depth} km',47,serif=True)
            write(d,(445,y+34),'Distancia al foco',27,MUTED)
            write(d,(445,y+85),f'≈ {path_length(depth):.0f} km',44,GOLD,True)
            # Relative GEOMETRIC path-length bars, not amplitude or damage bars.
            d.line((445,y+183,880,y+183),fill=LINE,width=10)
            length=435*path_length(depth)/path_length(500)*min(1,elapsed/1.2)
            d.line((445,y+183,445+length,y+183),fill=color,width=10)
        panel(d,(90,1270,930,1560),TEAL)
        paragraph(d,(125,1300),'Lo que cambia es el trayecto. No calculamos cuánto se mueve un edificio.',37,width=755,spacing=50)
        write(d,(125,1455),'Misma magnitud, ciudad, suelo y estructura.',27,TEAL)
        write(d,(125,1500),'Barras = distancia. No intensidad ni daño.',26,MUTED)
        return im

    def render(self,second):
        a,b,name=next(s for s in SCENES if s[0]<=second<s[1]); elapsed=second-a
        if name in ('pregunta_cortes','leer_cortes'): im=self.profiles(elapsed,name=='leer_cortes')
        elif name in ('profundo','intermedio','superficial'): im=self.depth_scene(name,elapsed)
        elif name=='comparacion': im=self.comparison_v2(elapsed)
        elif name in ('pedernales','quito'): im=self.archive(name,elapsed)
        else: im=getattr(self,{'reventador':'amazon','factores':'factors','cierre':'closing'}[name])(elapsed)
        d=ImageDraw.Draw(im)
        d.line((90,1690,930,1690),fill=LINE,width=4)
        d.line((90,1690,90+840*second/DURATION,1690),fill=GOLD,width=4)
        return im


def export(storyboard_only=False):
    import imageio_ffmpeg
    design=DepthDesignV2()
    sheet=Image.new('RGB',(810,480*math.ceil(len(SCENES)/3)),BG)
    for i,(a,b,name) in enumerate(SCENES):
        image=design.render((a+b)/2)
        image.save(FOLDER/f'qa_v2_{name}.jpg',quality=95)
        sheet.paste(image.resize((270,480)),((i%3)*270,(i//3)*480))
    sheet.save(FOLDER/'storyboard_v2.jpg',quality=95)
    design.render(0).save(FOLDER/'qa_v2_inicio.jpg',quality=95)
    if storyboard_only:return
    output=FOLDER/'profundidad_danos_cortes_3d_maqueta_sin_voz_v2.mp4'
    writer=imageio_ffmpeg.write_frames(str(output),(1080,1920),fps=30,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',macro_block_size=2,quality=8,ffmpeg_log_level='error',output_params=['-movflags','+faststart','-preset','veryfast','-threads','2'])
    writer.send(None)
    try:
        for frame in range(DURATION*30):
            writer.send(design.render(frame/30).tobytes())
            if frame%300==0:print(f'Profiles / perspective depth: {frame/30:g}/{DURATION} s',flush=True)
    finally:writer.close()
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(output),'-f','null','-'],capture_output=True,check=True)
    metadata=dict(status='silent_draft_not_for_publication',width=1080,height=1920,fps=30,motion_sampling_fps=30,duration_seconds=DURATION,frames=DURATION*30,audio=None,full_decode='passed',sha256=sha256(output.read_bytes()).hexdigest(),catalog_sha256=HASH,scenes=SCENES,opening='original catalog projections west-east and south-north',profile_records=len(design.known),unknown_depth_count=1,maximum_selected_depth_km=design.maximum,selected_deep_events=0,hypothetical_depths_km=[500,150,10],hypothetical_horizontal_distance_km=HORIZONTAL_DISTANCE,visual_license='CC BY-SA 2.0',pending='new voice, synchronization, captions and final audio/rights/source review')
    (FOLDER/'draft_metadata_v2.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    print(output.resolve(),flush=True)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--storyboard-only',action='store_true')
    export(p.parse_args().storyboard_only)
