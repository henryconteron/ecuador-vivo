"""Narrated, visually edited science Reel from an audited USGS snapshot."""
import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess
import wave

import pandas as pd

from reel_design import (WIDTH, HEIGHT, MAP, SAFE_RIGHT, CREDIT, write, base_map, render_map,
                         intro_card, closing_card, depth_card, profile_card, depth_counts,
                         profile_point, text_card, purpose_card, action_card, animate_card)

FPS = 30
YEAR_FRAMES = 9


def narration(df):
    counts=depth_counts(df)
    return {
        "intro":"¿Dónde empieza un terremoto? Un punto en el mapa no cuenta toda la historia.",
        "purpose":"Posición: epicentro. Tamaño: magnitud. Color: profundidad. Tres pistas, pero ninguna es un semáforo de peligro. Los puntos se acumulan: no son simultáneos.",
        "guide":"Claro: más superficial. Oscuro: más profundo. Kilómetros, no peligro. Mayor círculo: mayor magnitud, no mayor área de daños. Dos claves distintas.",
        "depth":"El epicentro está en superficie. El hipocentro es donde comienza la ruptura. La distancia hacia abajo es la profundidad. Setenta y trescientos kilómetros separan superficiales, intermedios y profundos.",
        "history":"Ahora sí: viajemos por el archivo de Ecuador y sus zonas vecinas. Al principio aparecen pocos puntos. ¿Había pocos sismos? No podemos concluirlo: los registros históricos son incompletos. Más adelante se acumulan muchos más. También cambió nuestra capacidad de observarlos. Más registros, por sí solos, no demuestran más peligro. Recuerda: vemos epicentros estimados, no el área de daños, ni el lugar del próximo terremoto.",
        "profile":f"Miremos de lado: oeste a este, y sur a norte. Proyectamos toda la región, no cortamos una falla. La profundidad aumenta hacia abajo. Máximo de esta selección: {df.depth.max():g} kilómetros. Hay {counts['unknown']} registro sin profundidad: no lo ponemos a cero.",
        "action":"El mapa no basta. Conversa en familia, practica simulacros y prepara un kit de emergencia. Conciencia sísmica: información más acción.",
        "end":"Aprender del pasado no es predecir el futuro. Este archivo es incompleto y revisable. No todas sus magnitudes son del mismo tipo. Fuentes y límites en la descripción.",
    }


def timeline(first,last,audio_frames=None):
    audio_frames=audio_frames or {}
    def duration(kind,seconds):
        return max(seconds*FPS,audio_frames.get(kind,0))
    return [(kind,None,duration(kind,seconds)) for kind,seconds in [("intro",7),("purpose",9),("guide",10),("depth",12)]]+[
        ("year",year,YEAR_FRAMES) for year in range(first,last+1)]+[
        ("hold",last,3*FPS)]+[(kind,None,duration(kind,seconds)) for kind,seconds in [("profile",14),("action",10),("end",14)]]


def synthesize_audio(folder,script):
    """Use an installed Spanish system voice, never a cloned presenter voice."""
    (folder/"narration.json").write_text(json.dumps(script,ensure_ascii=False,indent=2),encoding="utf-8")
    result=subprocess.run(["pwsh","-NoProfile","-File",str(Path(__file__).with_name("synthesize_reel.ps1")),
                           "-OutputDirectory",str(folder.resolve())],capture_output=True,text=True,check=True)
    print(result.stdout.strip(),flush=True)
    durations={}
    for kind in script:
        with wave.open(str(folder/f"voz_{kind}.wav")) as stream:
            durations[kind]=stream.getnframes()/stream.getframerate()
    return {kind:math.ceil((seconds+.5)*FPS) for kind,seconds in durations.items()}


def mux_audio(folder,visual,output,scenes):
    import imageio_ffmpeg
    exe=imageio_ffmpeg.get_ffmpeg_exe()
    groups=[]
    for scene in scenes:
        if scene["kind"] in ["year","hold"]:
            if not groups or groups[-1][0]!="history":
                groups.append(["history",0])
            groups[-1][1]+=scene["frames"]
        else:
            groups.append([scene["kind"],scene["frames"]])
    args=[exe,"-v","error","-y","-i",str(visual)]
    filters=[]
    for index,(kind,frames) in enumerate(groups,1):
        args.extend(["-i",str(folder/f"voz_{kind}.wav")])
        duration=frames/FPS
        filters.append(f"[{index}:a]aresample=48000,apad=whole_dur={duration},atrim=duration={duration},asetpts=PTS-STARTPTS[a{index}]")
    filters.append("".join(f"[a{index}]" for index in range(1,len(groups)+1))+f"concat=n={len(groups)}:v=0:a=1,alimiter=limit=0.9[audio]")
    args.extend(["-filter_complex",";".join(filters),"-map","0:v:0","-map","[audio]","-c:v","copy",
                 "-c:a","aac","-b:a","160k","-movflags","+faststart",str(output)])
    subprocess.run(args,capture_output=True,text=True,check=True)


def export_reel(folder,silent=False):
    import imageio_ffmpeg
    folder=Path(folder)
    manifest=json.loads((folder/"manifest.json").read_text(encoding="utf-8"))
    csv=(folder/"catalog.csv").read_bytes()
    if sha256(csv).hexdigest()!=manifest["csv_sha256"] or not all(manifest["checks"].values()):
        raise ValueError("Catalog does not match the audited snapshot.")
    df=pd.read_csv(folder/"catalog.csv")
    df.time=pd.to_datetime(df.time,utc=True,format="ISO8601")
    if len(df)!=manifest["exported_count"]:
        raise ValueError("Record count mismatch.")
    script=narration(df)
    audio_frames={} if silent else synthesize_audio(folder,script)
    if audio_frames.get("history",0)>(manifest["last"]-manifest["first"]+1)*YEAR_FRAMES+3*FPS:
        raise ValueError("History narration is too long; shorten the script, never cut it off.")
    first,last,minimum=(manifest[k] for k in ["first","last","minimum"])
    plan=timeline(first,last,audio_frames)
    total=sum(n for _,_,n in plan)
    base=base_map(first,last,minimum)
    output=folder/"andes_pulso_reel_1900_2025.mp4"
    visual=output if silent else folder/"visual_sin_audio.mp4"
    writer=imageio_ffmpeg.write_frames(str(visual),(WIDTH,HEIGHT),fps=FPS,codec="libx264",pix_fmt_in="rgb24",pix_fmt_out="yuv420p",
              quality=8,macro_block_size=2,output_params=["-movflags","+faststart","-profile:v","high","-level","4.1"],ffmpeg_log_level="error")
    writer.send(None)
    frames=0
    scenes=[]
    try:
        for kind,year,repeat in plan:
            if kind in ["intro","guide"]:
                image=intro_card(first,last,minimum,second=kind=="guide")
            elif kind=="purpose":
                image=purpose_card()
            elif kind=="depth":
                image=depth_card()
            elif kind=="profile":
                image=profile_card(df)
            elif kind=="action":
                image=action_card()
            elif kind=="end":
                image=closing_card(manifest)
            else:
                image=render_map(base,df[df.time.dt.year<=year],year)
            if kind=="intro":
                image.save(folder/"portada.jpg",quality=95)
            if kind!="year" or year in [1900,1906,1960,2016,2025]:
                animate_card(image,kind,.5,(frames+repeat/2)/total).save(folder/f"qa_{kind}_{year or 0}.jpg",quality=92)
            scenes.append(dict(kind=kind,year=year,start_frame=frames,frames=repeat))
            for offset in range(0,repeat,3):
                frame=animate_card(image,kind,offset/repeat,(frames+offset)/total).tobytes()
                for _ in range(min(3,repeat-offset)):
                    writer.send(frame)
            frames+=repeat
            if year and year%25==0:
                print(f"Rendered through {year}",flush=True)
    finally:
        writer.close()
    if not silent:
        mux_audio(folder,visual,output,scenes)
    metadata=dict(width=WIDTH,height=HEIGHT,fps=FPS,frames=frames,duration_seconds=frames/FPS,codec="H.264",pixel_format="yuv420p",
                  audio="none" if silent else "AAC · Spanish synthetic narration · Microsoft Pablo",
                  video_sha256=sha256(output.read_bytes()).hexdigest(),csv_sha256=manifest["csv_sha256"],scenes=scenes,
                  depth_counts=depth_counts(df),depth_max_km=float(df.depth.max()),credit=CREDIT,version=3)
    (folder/"video_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in metadata.items() if k!="scenes"},indent=2),flush=True)
    return output


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder",type=Path)
    parser.add_argument("--silent",action="store_true",help="Skip Windows speech synthesis and export without narration.")
    options=parser.parse_args()
    print(export_reel(options.folder,options.silent))
