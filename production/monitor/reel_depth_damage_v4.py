"""Real cases, documented felt effects and an original 3D explanatory story."""
from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess
import wave
from PIL import Image, ImageDraw
from prepare_depth_story_v4 import V4
from prepare_depth_episode import HASH
from reel_depth_damage_v2 import DepthDesignV2
from reel_depth_damage_v3 import VOICE, wave_seconds
from reel_depth_damage import shell, paragraph
from reel_design import BG, TEXT, MUTED, GOLD, TEAL, LINE, panel, write
from depth_story_3d import render_source, render_relocation, render_piedmont_orbit

NAMES=('pregunta','lectura','bolivia','mecanismo','loreto','sentido','pedernales','pelileo','reventador','factores','cierre')
FPS=30
AUDIO=V4/'audio_provisional'
OUTPUT=V4/'profundidad_casos_reales_3d_voz_provisional_v4.mp4'
SCRIPT=V4/'guion_elevenlabs_v4.txt'


def narration_parts():
    parts=SCRIPT.read_text(encoding='utf-8').strip().split('\n\n')
    if len(parts)!=len(NAMES): raise ValueError('Scene/script mismatch')
    return dict(zip(NAMES,parts))


def timeline_for(durations):
    start=0; scenes=[]
    for name in NAMES:
        length=max(14 if name=='pregunta' else 6,durations[name]+1.15)
        end=start+math.ceil(length*FPS)/FPS
        scenes.append((start,end,name)); start=end
    return scenes


def prepare_voice():
    AUDIO.mkdir(parents=True,exist_ok=True)
    parts=narration_parts()
    (AUDIO/'narration.json').write_text(json.dumps(parts,ensure_ascii=False,indent=2),encoding='utf-8')
    subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(Path(__file__).with_name('synthesize_depth_story_v4.ps1')),'-OutputDirectory',str(AUDIO)],check=True)
    durations={k:wave_seconds(AUDIO/f'voz_{k}.wav') for k in parts}; scenes=timeline_for(durations)
    segments=[]
    with wave.open(str(AUDIO/'guion_completo_provisional.wav'),'wb') as dest:
        expected=None
        for start,end,name in scenes:
            with wave.open(str(AUDIO/f'voz_{name}.wav'),'rb') as source:
                params=(source.getnchannels(),source.getsampwidth(),source.getframerate())
                if expected is None:
                    expected=params; dest.setnchannels(params[0]); dest.setsampwidth(params[1]); dest.setframerate(params[2])
                if params!=expected or params[1]!=2: raise ValueError('Expected uniform PCM16')
                lead=round(.35*params[2]); tail=round((end-start)*params[2])-lead-source.getnframes()
                if tail<0: raise ValueError('Cut narration')
                dest.writeframes(b'\0'*(lead*params[0]*params[1])); dest.writeframes(source.readframes(source.getnframes())); dest.writeframes(b'\0'*(tail*params[0]*params[1]))
            segments.append(dict(scene=name,start=start,end=end,speech_start=start+.35,speech_seconds=durations[name],file=f'voz_{name}.wav',sha256=sha256((AUDIO/f'voz_{name}.wav').read_bytes()).hexdigest()))
    marks=json.loads((AUDIO/'word_marks.json').read_text(encoding='utf-8-sig'))
    cues={}
    targets={'mecanismo':['La ruptura','Su energía','Si lo demás','Pero estamos'], 'reventador':['La sacudida','Hubo grandes','Esta animación'], 'pedernales':['El Instituto','Esta fotografía']}
    for name,phrases in targets.items():
        cues[name]={}
        for phrase in phrases:
            position=parts[name].index(phrase)
            candidates=[m for m in marks[name] if m['Character']>=position]
            if not candidates: raise ValueError('Missing voice word marker')
            cues[name][phrase]=candidates[0]['Seconds']+.35
    manifest=dict(voice=VOICE,status='provisional_internal_review_not_publication',scenes=scenes,segments=segments,duration_seconds=scenes[-1][1],script_sha256=sha256(SCRIPT.read_bytes()).hexdigest(),cues=cues,
                  synchronization='System.Speech SpeakProgress audio positions, not words-per-second estimates')
    (AUDIO/'timeline.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Complete provisional voice: {scenes[-1][1]:.2f}s',flush=True)
    return manifest


class DepthDesignV4(DepthDesignV2):
    def __init__(self,scenes,cues=None):
        super().__init__(); self.scenes=scenes; self.duration=scenes[-1][1]; self.cues=cues or {}
        self.evidence=json.loads((V4/'source_audit_v4.json').read_text(encoding='utf-8'))
        if self.evidence['catalog_sha256']!=HASH: raise ValueError('Opening catalogue changed')
        records=list(self.evidence['sources'].values())+[c['source'] for c in self.evidence['cases'].values()]
        for record in records:
            if sha256((V4/record['file']).read_bytes()).hexdigest()!=record['sha256']: raise ValueError('Primary evidence changed')

    def source_scene(self,key,elapsed,duration):
        case=self.evidence['cases'][key]; depth=case['depth_km']
        title,subtitle,kind,color,report,citation={
            'bolivia':('¿Tan profundo… y hubo daños?','Bolivia · 9 jun 1994 · caso adicional fuera del corte', 'PROFUNDO · 300–700 km','#ce95c9',
                'La Paz: ventanas rotas en edificios altos. Profundo no significa inofensivo.','USGS · boletín histórico, p. 34'),
            'loreto':('A 135 km también hubo daño.','Lagunas, Loreto · 26 may 2019 · caso adicional', 'INTERMEDIO · 70–300 km','#e89772',
                'Lagunas / Yurimaguas: sacudida fuerte y colapsos. VII Mercalli Modificada.','IGP · informe mayo 2019, pp. 5 y 8'),
            'pedernales':('Ahora, cerca de la superficie.','Pedernales · 16 abr 2016 · fecha local','SUPERFICIAL · 0–70 km',GOLD,
                'IX EMS-98 en sectores de Pedernales y Chamanga. No en toda la región.','USGS: parámetros · IG-EPN: efectos')
        }[key]
        im=shell(title,subtitle); d=ImageDraw.Draw(im)
        panel(d,(90,405,930,501),color)
        write(d,(117,419),kind,26,color)
        value=f'{depth:g}'.replace('.',','); mag=f'{case["magnitude"]:g}'.replace('.',',')
        write(d,(117,459),f'{value} km  ·  M {mag}  ·  {case["provider"].split(",")[0]}',26)
        im.paste(render_source(depth,elapsed,color),(90,523))
        d=ImageDraw.Draw(im); panel(d,(90,1240,930,1578),color)
        write(d,(120,1263),'EFECTOS DOCUMENTADOS',26,color)
        paragraph(d,(120,1313),report,35,width=765,spacing=47)
        write(d,(120,1482),citation,24,MUTED)
        write(d,(120,1529),'El esquema no reproduce la sacudida real.',24,MUTED)
        return im

    def mechanism(self,elapsed):
        im=shell('¿Cómo llega hasta arriba?','La ruptura genera ondas; el trayecto modifica la sacudida.')
        d=ImageDraw.Draw(im); panel(d,(90,405,930,498),TEAL)
        write(d,(120,431),'FUENTE HIPOTÉTICA · NO OTRO CASO REAL',28,TEAL)
        im.paste(render_source(350,elapsed,TEAL,True),(90,523))
        d=ImageDraw.Draw(im); panel(d,(90,1240,930,1575),TEAL)
        marks=self.cues.get('mecanismo',{})
        stage=0 if elapsed<marks.get('Su energía',6) else 1 if elapsed<marks.get('Si lo demás',12) else 2
        titles=['1 · La energía se reparte.','2 · Parte se atenúa en el recorrido.','3 · Importa la distancia a la ruptura.']
        paragraph(d,(120,1260),titles[stage],37,width=770,spacing=50)
        paragraph(d,(120,1380),'Más lejos suele haber menos sacudida si lo demás es comparable.',34,GOLD,width=765,spacing=47)
        write(d,(120,1532),'USGS · propagación y distancia',25,MUTED)
        return im

    def felt(self,elapsed):
        im=shell('Un evento. Distintos efectos.','Loreto 2019 · magnitud e intensidad no son lo mismo.')
        d=ImageDraw.Draw(im)
        panel(d,(90,420,930,645),GOLD)
        write(d,(120,448),'MAGNITUD · EL EVENTO',28,GOLD)
        write(d,(120,505),'M 8,0',68,serif=True)
        write(d,(415,535),'IGP · no cambia por ciudad',28,MUTED)
        for i,(title,value,scale,effect,source) in enumerate([
            ('Lagunas / Yurimaguas','VII','Mercalli Modificada','Sacudida fuerte y colapsos.','IGP · informe mayo 2019'),
            ('Tena / Puyo','IV','EMS-98 · preliminar','Reportes de percepción en Ecuador.','IG-EPN · Informe Especial 12-2019')]):
            y=685+i*345; accent=GOLD if i==0 else TEAL
            panel(d,(90,y,930,y+310),accent)
            write(d,(120,y+20),title,35,accent)
            write(d,(120,y+88),value,64,serif=True)
            write(d,(335,y+109),scale,27)
            write(d,(120,y+201),effect,29)
            write(d,(120,y+257),source,24,MUTED)
        paragraph(d,(100,1415),'Intensidad = efectos en un sitio. Escalas distintas: no comparar los números directamente.',30,GOLD,width=800,spacing=42)
        return im

    def coast(self,elapsed,duration):
        if elapsed<self.cues.get('pedernales',{}).get('Esta fotografía',duration*.55): return self.source_scene('pedernales',elapsed,duration)
        im=self.archive('pedernales',elapsed)
        d=ImageDraw.Draw(im); d.rectangle((90,1400,930,1578),fill=BG); panel(d,(90,1400,930,1578),GOLD)
        paragraph(d,(120,1420),'IG-EPN: IX EMS-98 en sectores de Pedernales y Chamanga. Profundidad ≠ explicación completa del daño.',30,width=770,spacing=42)
        return im

    def pelileo(self,elapsed):
        im=shell('Sierra · Pelileo, 1949','5 ago · un desastre que cambió la ubicación de la ciudad.')
        d=ImageDraw.Draw(im); panel(d,(90,405,930,501),GOLD)
        write(d,(117,429),'M estimada 6,8  ·  profundidad <15 km',32,GOLD)
        im.paste(render_relocation(elapsed),(90,523)); d=ImageDraw.Draw(im)
        panel(d,(90,1240,930,1578),GOLD)
        paragraph(d,(120,1263),'El impacto no cabe en un solo número: Pelileo se reconstruyó en otro lugar.',37,width=765,spacing=51)
        write(d,(120,1448),'IG-EPN · revisión histórica del terremoto',26,MUTED)
        paragraph(d,(120,1490),'6,8 estimada de intensidades; no se etiqueta Mw.',26,MUTED,width=760,spacing=36)
        return im

    def amazon_story(self,elapsed,duration):
        im=shell('Amazonía · cuando falla la ladera.','Reventador · secuencia del 5 mar 1987, fecha local.')
        d=ImageDraw.Draw(im); panel(d,(90,405,930,501),GOLD)
        write(d,(117,430),'Caso principal USGS: 7,2 mw · 10 km',31,GOLD)
        marks=self.cues.get('reventador',{})
        shock=marks.get('La sacudida',duration*.30); effects=marks.get('Hubo grandes',duration*.62); explanation=marks.get('Esta animación',duration*.76)
        # One-way geological process, tied to actual spoken word timestamps.
        import numpy as np
        q=float(np.interp(elapsed,[0,shock,effects,explanation,duration],[0,.18,.34,.74,1]))
        im.paste(render_piedmont_orbit(q),(90,523)); d=ImageDraw.Draw(im)
        panel(d,(90,1240,930,1578),TEAL)
        paragraph(d,(120,1264),'IG-EPN documenta deslizamientos y flujos sobre pendientes pronunciadas y terrenos saturados.',35,width=765,spacing=47)
        write(d,(120,1470),'El relieve y el agua también importan.',29,GOLD)
        write(d,(120,1529),'Modelo propio: no reconstrucción de 1987.',24,MUTED)
        return im

    def render(self,second):
        a,b,name=next(s for s in self.scenes if s[0]<=second<s[1]); elapsed=second-a
        if name in ('pregunta','lectura'): im=self.profiles(elapsed,name=='lectura')
        elif name in ('bolivia','loreto'): im=self.source_scene(name,elapsed,b-a)
        elif name=='mecanismo': im=self.mechanism(elapsed)
        elif name=='sentido': im=self.felt(elapsed)
        elif name=='pedernales': im=self.coast(elapsed,b-a)
        elif name=='pelileo': im=self.pelileo(elapsed)
        elif name=='reventador': im=self.amazon_story(elapsed,b-a)
        elif name=='factores':
            im=self.factors(elapsed); d=ImageDraw.Draw(im); d.rectangle((90,1530,930,1585),fill=BG)
            write(d,(100,1540),'Casos distintos: no aíslan el efecto de la profundidad.',26,MUTED)
        else:
            im=self.closing(elapsed); d=ImageDraw.Draw(im)
            d.rectangle((90,1240,930,1585),fill=BG)
            paragraph(d,(100,1240),'Fuentes primarias: USGS, IG-EPN e IGP. Fotografía real: Micaela Ayala V. / ANDES. Animaciones 3D propias.',29,MUTED,width=815,spacing=41)
            paragraph(d,(100,1420),'Montaje visual CC BY-SA 2.0. Voz provisional para revisión; faltan voz y subtítulos finales.',29,GOLD,width=815,spacing=41)
        d=ImageDraw.Draw(im); d.rectangle((90,213,930,240),fill=BG)
        write(d,(90,217),'VOZ PROVISIONAL · NO PUBLICAR',17,TEAL)
        d.line((90,1690,930,1690),fill=LINE,width=4); d.line((90,1690,90+840*second/self.duration,1690),fill=GOLD,width=4)
        return im


def export(storyboard_only=False,regenerate_voice=False):
    import imageio_ffmpeg
    manifest=prepare_voice() if regenerate_voice or not (AUDIO/'timeline.json').exists() else json.loads((AUDIO/'timeline.json').read_text(encoding='utf-8'))
    if manifest['script_sha256']!=sha256(SCRIPT.read_bytes()).hexdigest(): raise ValueError('Regenerate modified voice')
    design=DepthDesignV4(manifest['scenes'],manifest.get('cues')); sheet=Image.new('RGB',(810,480*math.ceil(len(NAMES)/3)),BG)
    for i,(a,b,name) in enumerate(design.scenes):
        im=design.render((a+b)/2); im.save(V4/f'qa_{name}.jpg',quality=95)
        sheet.paste(im.resize((270,480)),((i%3)*270,(i//3)*480))
    sheet.save(V4/'storyboard_v4.jpg',quality=95)
    for name in ('bolivia','loreto','pedernales','reventador'):
        a,b,_=next(s for s in design.scenes if s[2]==name)
        for j,q in enumerate((.08,.28,.58,.94)): design.render(a+(b-a)*q).save(V4/f'qa_{name}_{j}.jpg',quality=95)
    if storyboard_only: return
    count=round(design.duration*FPS)
    writer=imageio_ffmpeg.write_frames(str(OUTPUT),(1080,1920),fps=FPS,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',macro_block_size=2,quality=8,
        ffmpeg_log_level='error',audio_path=str(AUDIO/'guion_completo_provisional.wav'),audio_codec='aac',output_params=['-movflags','+faststart','-preset','veryfast','-threads','2','-b:a','160k'])
    writer.send(None)
    try:
        for i in range(count):
            writer.send(design.render(i/FPS).tobytes())
            if i%300==0: print(f'V4 real cases / 3D: {i/FPS:g}/{design.duration:.2f}s',flush=True)
    finally: writer.close()
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(OUTPUT),'-f','null','-'],check=True,capture_output=True)
    meta=dict(status='provisional_internal_review_not_publication',sha256=sha256(OUTPUT.read_bytes()).hexdigest(),frames=count,fps=FPS,width=1080,height=1920,
        duration_seconds=design.duration,voice=VOICE,scenes=design.scenes,catalog_sha256=HASH,full_decode='passed',script_sha256=manifest['script_sha256'],
        visual_license='CC BY-SA 2.0',audio_rights='system voice internal review, not relicensed',pending='final licensed voice, subtitles and human listening review')
    (V4/'draft_metadata_v4.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    print(OUTPUT.resolve(),flush=True)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--storyboard-only',action='store_true'); p.add_argument('--regenerate-voice',action='store_true')
    args=p.parse_args(); export(args.storyboard_only,args.regenerate_voice)
