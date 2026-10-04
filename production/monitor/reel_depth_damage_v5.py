"""GPU wave demonstration with original story and timed provisional subtitles."""
from functools import lru_cache
from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess
import wave
import numpy as np
from PIL import Image,ImageDraw
from prepare_depth_story_v5 import V5
from prepare_depth_story_v4 import V4
from reel_depth_damage_v4 import DepthDesignV4
from reel_depth_damage_v3 import wave_seconds,VOICE
from reel_depth_damage import shell,paragraph
from reel_design import BG,GOLD,TEAL,TEXT,MUTED,LINE,write,panel
from export_video import font
from seismic_gpu import SeismicGPU,COLORS,displacement

NAMES=('pregunta','particula','p','s','love','rayleigh','bolivia','loreto','sentido','pedernales','pelileo','reventador','cierre')
SCRIPT=V5/'guion_elevenlabs_v5.txt'
AUDIO=V5/'audio_provisional'
OUTPUT=V5/'ondas_profundidad_3d_voz_provisional_v5.mp4'
FPS=30


def narration_parts():
    parts=SCRIPT.read_text(encoding='utf-8').strip().split('\n\n')
    if len(parts)!=len(NAMES):raise ValueError('Script/scene mismatch')
    return dict(zip(NAMES,parts))


def prepare_voice():
    AUDIO.mkdir(parents=True,exist_ok=True);parts=narration_parts()
    (AUDIO/'narration.json').write_text(json.dumps(parts,ensure_ascii=False,indent=2),encoding='utf-8')
    subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(Path(__file__).with_name('synthesize_depth_story_v4.ps1')),'-OutputDirectory',str(AUDIO)],check=True)
    durations={name:wave_seconds(AUDIO/f'voz_{name}.wav') for name in NAMES}; scenes=[];start=0;segments=[]
    marks=json.loads((AUDIO/'word_marks.json').read_text(encoding='utf-8-sig'));captions=[]
    with wave.open(str(AUDIO/'guion_completo_provisional.wav'),'wb') as dest:
        dest.setnchannels(1);dest.setsampwidth(2);dest.setframerate(16000)
        for name in NAMES:
            end=start+math.ceil((durations[name]+.95)*FPS)/FPS;scenes.append((start,end,name))
            with wave.open(str(AUDIO/f'voz_{name}.wav')) as source:
                if source.getframerate()!=16000 or source.getnchannels()!=1 or source.getsampwidth()!=2:raise ValueError('Expected PCM16 16kHz')
                lead=round(.25*16000);tail=round((end-start)*16000)-lead-source.getnframes()
                if tail<0:raise ValueError('Voice cut')
                dest.writeframes(b'\0'*(lead*2));dest.writeframes(source.readframes(source.getnframes()));dest.writeframes(b'\0'*(tail*2))
            segments.append(dict(scene=name,start=start,end=end,speech_start=start+.25,speech_seconds=durations[name],file=f'voz_{name}.wav',sha256=sha256((AUDIO/f'voz_{name}.wav').read_bytes()).hexdigest()))
            words=marks[name]
            if words[-1]['Seconds']>=durations[name]:raise ValueError('Invalid speech clock')
            for i in range(0,len(words),6):
                first=words[i];next_word=words[i+6] if i+6<len(words) else None
                char_end=next_word['Character'] if next_word else len(parts[name])
                # SpeakProgress excludes leading inverted punctuation; keep it.
                char_start=0 if i==0 else first['Character']
                text=parts[name][char_start:char_end].strip()
                captions.append(dict(scene=name,start=start+.25+first['Seconds'],end=start+.25+(next_word['Seconds'] if next_word else durations[name]),text=text))
            start=end
    cues={}
    targets={'pedernales':['Esta foto','Cerca de'], 'reventador':['Las lluvias','La sacudida','Aquí la amenaza']}
    for name,phrases in targets.items():
        cues[name]={}
        for phrase in phrases:
            pos=parts[name].index(phrase);mark=next(m for m in marks[name] if m['Character']>=pos)
            cues[name][phrase]=.25+mark['Seconds']
    manifest=dict(voice=VOICE,status='provisional_internal_review_not_publication',scenes=scenes,segments=segments,cues=cues,captions=captions,
        duration_seconds=scenes[-1][1],script_sha256=sha256(SCRIPT.read_bytes()).hexdigest(),caption_method='System.Speech word positions; provisional, replace with final voice')
    (AUDIO/'timeline.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    def stamp(t):
        ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
    srt='\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}' for i,c in enumerate(captions))
    (V5/'subtitulos_provisionales_v5.srt').write_text(srt,encoding='utf-8')
    print(f'Voice and {len(captions)} caption cues: {start:.2f}s',flush=True)
    return manifest


class DepthDesignV5(DepthDesignV4):
    def __init__(self,manifest):
        super().__init__(manifest['scenes']);self.manifest=manifest;self.cues=manifest['cues']
        self.gpu=SeismicGPU((840,830))
        self.audit=json.loads((V5/'source_audit_v5.json').read_text(encoding='utf-8'))
        for record in self.audit['sources'].values():
            if sha256((V5/record['file']).read_bytes()).hexdigest()!=record['sha256']:raise ValueError('Wave source changed')
        if sha256((V4/'source_audit_v4.json').read_bytes()).hexdigest()!=self.audit['historical_evidence_sha256']:raise ValueError('Historical evidence changed')

    @lru_cache(maxsize=32)
    def stage(self,title,subtitle):
        im=shell(title,subtitle);d=ImageDraw.Draw(im)
        d.rectangle((90,213,930,240),fill=BG);write(d,(90,217),'VOZ PROVISIONAL · NO PUBLICAR',17,TEAL)
        return im

    def waves(self,name,elapsed):
        kind='p' if name=='particula' else name
        titles={
            'particula':('La onda viaja. La roca oscila.','Sigue la partícula amarilla, no el frente de onda.'),
            'p':('P · comprimir y estirar.','Primarias · oscilación paralela al avance'),
            's':('S · moverse de través.','Secundarias · oscilación perpendicular al avance'),
            'love':('Love · de lado a lado.','Superficiales · movimiento horizontal transversal'),
            'rayleigh':('Rayleigh · una pequeña elipse.','Superficiales · movimiento vertical y horizontal')}
        im=self.stage(*titles[name]).copy();hero,anchor=self.gpu.wave(kind,elapsed)
        # Crop only the empty upper viewport, never the model or particle trail.
        im.paste(hero.crop((0,115,840,830)),(90,440));d=ImageDraw.Draw(im)
        color=tuple(round(c*255) for c in COLORS[kind])
        write(d,(98,404),'PROPAGACIÓN →',24,MUTED)
        # Large material-particle close-up, synchronized to the exact same field.
        cx,cy=762,1250;r=57
        d.ellipse((cx-85,cy-80,cx+85,cy+80),fill='#1b303c',outline=LINE,width=2)
        samples=[]
        for t in np.linspace(elapsed-3,elapsed,100):
            u=displacement(kind,np.array([[0,0,1.35]]),t)[0]
            samples.append((cx+u[0]*130 if kind in ('p','rayleigh') else cx+u[2]*130 if kind=='love' else cx,cy-u[1]*130))
        d.line(samples,fill=color,width=3)
        x,y=samples[-1];d.ellipse((x-8,y-8,x+8,y+8),fill=GOLD)
        write(d,(98,1186),'MATERIAL',25,GOLD)
        paragraph(d,(98,1227),{'particula':'No se traslada con la onda.','p':'Paralelo ↔','s':'Perpendicular ↕','love':'Horizontal ↔','rayleigh':'Elíptico'}[name],35,width=530,spacing=47)
        if name=='love':write(d,(98,1300),'Sin desplazamiento vertical.',27,color)
        write(d,(98,1350),'Movimiento exagerado · esquema, no registro',24,MUTED)
        return im

    def depth_case(self,name,elapsed):
        c=self.evidence['cases'][name]
        title={'bolivia':'631 km… y hubo daños.','loreto':'135 km. También hubo colapsos.','pedernales':'Cerca de la superficie.'}[name]
        subtitle={'bolivia':'Bolivia · 1994 · caso adicional fuera del corte','loreto':'Loreto, Perú · 2019 · solución IGP, no mezclada con USGS','pedernales':'Pedernales · 2016 · fecha local'}[name]
        im=self.stage(title,subtitle).copy();hero,anchors=self.gpu.depth(c['depth_km'],elapsed);im.paste(hero,(90,440));d=ImageDraw.Draw(im)
        value=f'{c["depth_km"]:g}'.replace('.',',');mag=f'{c["magnitude"]:g}'.replace('.',',')
        write(d,(98,403),f'M {mag}  /  {value} km  /  {c["provider"].split(",")[0]}',29,GOLD)
        for key,label in [(0,'0 km'),(70,'70'),(300,'300'),(700,'700')]:
            x,y=anchors[key];d.text((90+x-14,440+y),label,font=font(23),fill=MUTED,anchor='rm')
        write(d,(98,1140),'Profundidad bajo la superficie (km)',24,MUTED)
        x,y=anchors['epicenter']
        d.text((90+x+18,440+y-43),'Epicentro',font=font(27),fill=TEAL)
        fx,fy=anchors['focus'];label_y=max(fy-15,y+35)
        if label_y>fy:
            d.line((90+fx,440+fy,90+fx+35,440+label_y+14,90+fx+45,440+label_y+14),fill=GOLD,width=2)
        d.text((90+fx+48,440+label_y),'Foco',font=font(27),fill=GOLD)
        paragraph(d,(98,1220),{'bolivia':'La Paz: ventanas rotas en edificios altos.','loreto':'Lagunas / Yurimaguas: sacudida fuerte y colapsos.','pedernales':'La distancia a la ruptura también cuenta.'}[name],33,width=805,spacing=44)
        write(d,(98,1350),'Vista transparente conceptual · no sacudida medida',23,MUTED)
        return im

    def coast_v5(self,elapsed):
        # Switch to evidence when the narrator says "Esta foto"; then back to mechanism.
        cues=self.cues['pedernales']
        if elapsed<cues['Esta foto'] or elapsed>=cues['Cerca de']:return self.depth_case('pedernales',elapsed)
        im=self.stage('Esta imagen sí es del desastre.','Pedernales · Ecuador · 2016').copy();d=ImageDraw.Draw(im)
        im.paste(self.photos['pedernales'],(90,484))
        write(d,(98,1110),'FOTOGRAFÍA REAL · 18 ABR 2016',26,TEAL)
        write(d,(98,1155),'Micaela Ayala V. / ANDES',29)
        write(d,(98,1200),'CC BY-SA 2.0 · original completo, sin recorte',25,MUTED)
        paragraph(d,(98,1270),'No deducimos un tipo de onda a partir de esta foto.',34,GOLD,width=805,spacing=45)
        return im

    def render(self,second):
        a,b,name=next(s for s in self.scenes if s[0]<=second<s[1]);elapsed=second-a
        if name=='pregunta':
            im=self.profiles(elapsed,False);d=ImageDraw.Draw(im)
            d.rectangle((90,242,930,395),fill=BG)
            paragraph(d,(90,242),'Estos puntos no dicen cuánto temblará tu casa.',45,TEXT,width=840,spacing=53)
            write(d,(90,361),'¿Qué nos falta para entenderlos?',29,GOLD)
            # Preserve both data panels; clear former footer for subtitles.
            d.rectangle((90,1400,930,1590),fill=BG)
            write(d,(98,1389),'USGS · 1900–2025 · mismos cortes, mismos datos',24,MUTED)
        elif name in ('particula','p','s','love','rayleigh'):im=self.waves(name,elapsed)
        elif name in ('bolivia','loreto'):im=self.depth_case(name,elapsed)
        elif name=='pedernales':im=self.coast_v5(elapsed)
        elif name=='sentido':
            im=self.felt(elapsed);d=ImageDraw.Draw(im);d.rectangle((90,1380,930,1590),fill=BG)
            write(d,(98,1384),'Dos escalas distintas · no comparar números sin contexto',24,MUTED)
        elif name=='pelileo':
            im=self.pelileo(elapsed);d=ImageDraw.Draw(im);d.rectangle((90,1215,930,1590),fill=BG)
            paragraph(d,(98,1235),'La destrucción obligó a reconstruir la ciudad en otro sitio.',35,GOLD,width=805,spacing=48)
            write(d,(98,1350),'IG-EPN · 6,8 estimada de intensidades; no Mw',24,MUTED)
        elif name=='reventador':
            im=self.stage('El peligro también baja por la ladera.','Reventador · secuencia del 5 mar 1987, fecha local').copy()
            cues=self.cues['reventador'];q=float(np.interp(elapsed,[0,cues['Las lluvias'],cues['La sacudida'],cues['Aquí la amenaza'],b-a],[0,.10,.18,.75,1]))
            hero,phase=self.gpu.piedmont(q,elapsed);im.paste(hero,(90,440));d=ImageDraw.Draw(im)
            write(d,(98,404),['LLUVIA PREVIA','SACUDIDA','DESLIZAMIENTO','MATERIAL EN EL CAUCE'][phase],28,GOLD)
            paragraph(d,(98,1235),'Pendiente + agua + sacudida: una cadena de efectos.',35,GOLD,width=805,spacing=48)
            write(d,(98,1350),'IG-EPN · esquema propio, no reconstrucción de 1987',23,MUTED)
        else:
            im=self.stage('Entender no es predecir.','Es prepararnos mejor.').copy();d=ImageDraw.Draw(im)
            for i,(title,detail) in enumerate([('DÓNDE','Distancia a la ruptura'),('QUÉ TERRENO','Suelo, pendiente, agua'),('CÓMO CONSTRUIMOS','Respuesta de la estructura')]):
                y=450+i*220;write(d,(98,y),title,35,TEAL);write(d,(98,y+66),detail,34)
                d.line((98,y+150,910,y+150),fill=LINE,width=2)
            paragraph(d,(98,1175),'Tena: ¿qué es una falla?',47,GOLD,width=805,spacing=57)
            write(d,(98,1350),'Fuentes: USGS · IG-EPN · IGP · EarthScope',24,MUTED)
        d=ImageDraw.Draw(im);d.rectangle((90,213,930,240),fill=BG);write(d,(90,217),'VOZ PROVISIONAL · NO PUBLICAR',17,TEAL)
        # Full spoken text in short, timed captions; reserved lower safe zone.
        caption=next((c for c in self.manifest['captions'] if c['start']<=second<c['end']),None)
        if caption:
            d.rounded_rectangle((90,1430,930,1578),radius=16,fill='#192e39')
            paragraph(d,(114,1443),caption['text'],35,TEXT,width=790,spacing=45)
        d.line((90,1690,930,1690),fill=LINE,width=4);d.line((90,1690,90+840*second/self.duration,1690),fill=GOLD,width=4)
        return im


def export(storyboard_only=False,regenerate_voice=False):
    import imageio_ffmpeg
    m=prepare_voice() if regenerate_voice or not (AUDIO/'timeline.json').exists() else json.loads((AUDIO/'timeline.json').read_text(encoding='utf-8'))
    if m['script_sha256']!=sha256(SCRIPT.read_bytes()).hexdigest():raise ValueError('Regenerate voice')
    design=DepthDesignV5(m);sheet=Image.new('RGB',(810,480*math.ceil(len(NAMES)/3)),BG)
    for i,(a,b,name) in enumerate(design.scenes):
        im=design.render((a+b)/2);im.save(V5/f'qa_{name}.jpg',quality=95);sheet.paste(im.resize((270,480)),((i%3)*270,(i//3)*480))
    sheet.save(V5/'storyboard_v5.jpg',quality=95)
    if storyboard_only:return
    frames=round(design.duration*FPS)
    writer=imageio_ffmpeg.write_frames(str(OUTPUT),(1080,1920),fps=FPS,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',macro_block_size=2,quality=8,
        audio_path=str(AUDIO/'guion_completo_provisional.wav'),audio_codec='aac',ffmpeg_log_level='error',output_params=['-movflags','+faststart','-preset','veryfast','-threads','2','-b:a','160k'])
    writer.send(None)
    try:
        for i in range(frames):
            writer.send(design.render(i/FPS).tobytes())
            if i%300==0:print(f'V5 GPU waves: {i/FPS:g}/{design.duration:.2f}s',flush=True)
    finally:writer.close()
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(OUTPUT),'-f','null','-'],check=True,capture_output=True)
    meta=dict(status='provisional_internal_review_not_publication',sha256=sha256(OUTPUT.read_bytes()).hexdigest(),frames=frames,fps=FPS,width=1080,height=1920,
        duration_seconds=design.duration,voice=VOICE,scenes=design.scenes,script_sha256=m['script_sha256'],gpu=design.gpu.renderer,
        full_decode='passed',visual_license='CC BY-SA 2.0',audio_rights='system voice internal review, not relicensed',captions='timed provisional captions burned in and SRT',pending='final voice with compatible rights, retiming and human listening/scientific review')
    (V5/'draft_metadata_v5.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8');print(OUTPUT.resolve(),flush=True)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--storyboard-only',action='store_true');p.add_argument('--regenerate-voice',action='store_true')
    args=p.parse_args();export(args.storyboard_only,args.regenerate_voice)
