"""Provisional system voice + original piedmont 3D, preserving silent V2."""
from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess
import wave
from PIL import Image, ImageDraw

from prepare_depth_episode import FOLDER, HASH
from reel_depth_damage_v2 import DepthDesignV2, SCENES as V2_SCENES
from reel_depth_damage import shell, paragraph
from reel_design import BG, LINE, GOLD, TEAL, MUTED, write, panel
from piedmont_animation import render_piedmont

AUDIO=FOLDER/'audio_provisional_v3'
OUTPUT=FOLDER/'profundidad_danos_voz_provisional_v3.mp4'
FPS=30
VOICE='Microsoft Helena Desktop (es-ES)'


def narration_parts():
    parts=(FOLDER/'guion_elevenlabs_v2.txt').read_text(encoding='utf-8').strip().split('\n\n')
    if len(parts)!=10: raise ValueError('Review script segmentation')
    shallow,comparison=parts[4].split('Mira los tres trayectos.',1)
    parts=parts[:4]+[shallow.strip(),'Mira los tres trayectos.'+comparison]+parts[5:]
    return {name.replace('_',''):text for (_,_,name),text in zip(V2_SCENES,parts)}


def wave_seconds(path):
    with wave.open(str(path),'rb') as audio:
        return audio.getnframes()/audio.getframerate()


def timeline_for(durations):
    scenes=[]; start=0
    for a,b,name in V2_SCENES:
        # No sentence is cut to fit the old silent edit. At least 0.35s intro
        # and 0.55s outro; rounded to full frames for sample-accurate edit.
        seconds=max(b-a,durations[name.replace('_','')]+.9)
        end=start+math.ceil(seconds*FPS)/FPS
        scenes.append((start,end,name)); start=end
    return scenes


def prepare_voice():
    AUDIO.mkdir(parents=True,exist_ok=True)
    parts=narration_parts()
    (AUDIO/'narration.json').write_text(json.dumps(parts,ensure_ascii=False,indent=2),encoding='utf-8')
    subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(Path(__file__).with_name('synthesize_depth_preview.ps1')),'-OutputDirectory',str(AUDIO)],check=True)
    durations={name:wave_seconds(AUDIO/f'voz_{name}.wav') for name in parts}
    scenes=timeline_for(durations)
    # PCM concatenation with planned silence, avoiding encoder gaps/cuts.
    with wave.open(str(AUDIO/'guion_completo_provisional.wav'),'wb') as destination:
        first=True
        for start,end,name in scenes:
            key=name.replace('_','')
            with wave.open(str(AUDIO/f'voz_{key}.wav'),'rb') as source:
                params=(source.getnchannels(),source.getsampwidth(),source.getframerate())
                if first: destination.setnchannels(params[0]); destination.setsampwidth(params[1]); destination.setframerate(params[2]); expected=params; first=False
                if params!=expected or params[1]!=2: raise ValueError('Expected uniform 16-bit PCM')
                lead=round(.35*params[2]); count=round((end-start)*params[2])
                tail=count-lead-source.getnframes()
                if tail<0: raise ValueError('Narration exceeds scene')
                destination.writeframes(b'\0'*(lead*params[0]*params[1]))
                destination.writeframes(source.readframes(source.getnframes()))
                destination.writeframes(b'\0'*(tail*params[0]*params[1]))
    manifest=dict(voice=VOICE,status='provisional_internal_review_not_publication',rate=0,scenes=scenes,
                  duration_seconds=scenes[-1][1],script_sha256=sha256((FOLDER/'guion_elevenlabs_v2.txt').read_bytes()).hexdigest(),
                  segments=[dict(scene=name,start=start,end=end,speech_start=start+.35,speech_seconds=durations[name.replace('_','')],
                                 file=f'voz_{name.replace("_","")}.wav',sha256=sha256((AUDIO/f'voz_{name.replace("_","")}.wav').read_bytes()).hexdigest()) for start,end,name in scenes])
    (AUDIO/'timeline.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Voice ready: {scenes[-1][1]:.2f}s; 11 complete segments.',flush=True)
    return manifest


class DepthDesignV3(DepthDesignV2):
    def __init__(self,scenes):
        super().__init__(); self.scenes=scenes; self.duration=scenes[-1][1]

    def amazon_v3(self,elapsed,duration):
        im=shell('Piedemonte amazónico · 1987','Secuencia del 5 de marzo, fecha local · entorno del Reventador')
        d=ImageDraw.Draw(im)
        panel(d,(90,420,930,518),GOLD)
        write(d,(120,444),'Caso principal USGS: 7,2 mw · 10 km',32,GOLD)
        im.paste(render_piedmont(elapsed/duration),(90,552))
        d=ImageDraw.Draw(im)
        d.rounded_rectangle((90,552,930,1190),radius=15,outline=LINE,width=2)
        self.locator(im,self.cases['reventador'],(690,1250))
        paragraph(d,(110,1230),'Deslizamientos y flujos documentados por IG-EPN. Las pendientes y la saturación fueron claves.',31,width=545,spacing=45)
        write(d,(690,1460),'Epicentro USGS',23,MUTED)
        paragraph(d,(110,1480),'No atribuimos todo el desastre a la profundidad.',29,GOLD,width=800)
        return im

    def render(self,second):
        a,b,name=next(s for s in self.scenes if s[0]<=second<s[1]); elapsed=second-a
        if name in ('pregunta_cortes','leer_cortes'): im=self.profiles(elapsed,name=='leer_cortes')
        elif name in ('profundo','intermedio','superficial'): im=self.depth_scene(name,elapsed)
        elif name=='comparacion': im=self.comparison_v2(elapsed)
        elif name in ('pedernales','quito'): im=self.archive(name,elapsed)
        elif name=='reventador': im=self.amazon_v3(elapsed,b-a)
        else: im=getattr(self,{'factores':'factors','cierre':'closing'}[name])(elapsed)
        d=ImageDraw.Draw(im)
        d.rectangle((90,213,930,240),fill=BG)
        write(d,(90,217),'VOZ PROVISIONAL · NO PUBLICAR',17,TEAL)
        if name=='cierre':
            d.rectangle((90,1530,930,1585),fill=BG)
            write(d,(100,1534),'Voz de referencia · faltan subtítulos finales.',28,GOLD)
        d.line((90,1690,930,1690),fill=LINE,width=4)
        d.line((90,1690,90+840*second/self.duration,1690),fill=GOLD,width=4)
        return im


def export(storyboard_only=False,regenerate_voice=False):
    import imageio_ffmpeg
    manifest=prepare_voice() if regenerate_voice or not (AUDIO/'timeline.json').exists() else json.loads((AUDIO/'timeline.json').read_text(encoding='utf-8'))
    if manifest['script_sha256']!=sha256((FOLDER/'guion_elevenlabs_v2.txt').read_bytes()).hexdigest(): raise ValueError('Regenerate voice for modified script')
    design=DepthDesignV3(manifest['scenes'])
    sheet=Image.new('RGB',(810,1920),BG)
    for i,(a,b,name) in enumerate(design.scenes):
        im=design.render((a+b)/2); im.save(FOLDER/f'qa_v3_{name}.jpg',quality=95)
        sheet.paste(im.resize((270,480)),((i%3)*270,(i//3)*480))
    sheet.save(FOLDER/'storyboard_v3.jpg',quality=95)
    a,b,_=next(s for s in design.scenes if s[2]=='reventador')
    for i,q in enumerate((.10,.26,.56,.94)):
        design.render(a+(b-a)*q).save(FOLDER/f'qa_v3_ladera_{i}.jpg',quality=95)
    if storyboard_only:return
    frames=round(design.duration*FPS)
    # Audio is already padded to scene lengths; do not -shortest away any words.
    writer=imageio_ffmpeg.write_frames(str(OUTPUT),(1080,1920),fps=FPS,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',macro_block_size=2,quality=8,
            ffmpeg_log_level='error',audio_path=str(AUDIO/'guion_completo_provisional.wav'),audio_codec='aac',
            output_params=['-movflags','+faststart','-preset','veryfast','-threads','2','-b:a','160k'])
    writer.send(None)
    try:
        for frame in range(frames):
            writer.send(design.render(frame/FPS).tobytes())
            if frame%300==0:print(f'Voz y piedemonte 3D: {frame/FPS:g}/{design.duration:.2f}s',flush=True)
    finally:writer.close()
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(OUTPUT),'-f','null','-'],check=True,capture_output=True)
    metadata=dict(status='provisional_voice_draft_not_publication',sha256=sha256(OUTPUT.read_bytes()).hexdigest(),frames=frames,fps=FPS,width=1080,height=1920,duration_seconds=design.duration,
                  voice=VOICE,scenes=design.scenes,catalog_sha256=HASH,full_decode='passed',visual_license='CC BY-SA 2.0',audio_rights='system voice internal preview; not relicensed under CC BY-SA',
                  animation='original 3D conceptual relief; not a reconstruction, DEM, landslide or shaking model',pending='final chosen voice, subtitles, listening review and publication rights')
    (FOLDER/'draft_metadata_v3.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    print(OUTPUT.resolve(),flush=True)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--storyboard-only',action='store_true'); parser.add_argument('--regenerate-voice',action='store_true')
    args=parser.parse_args(); export(args.storyboard_only,args.regenerate_voice)
