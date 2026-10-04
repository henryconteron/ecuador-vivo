"""Map-first edit synchronized to a user-supplied continuous narration.

No speech synthesis, audio acceleration, cuts, or remote audio upload.
"""
import argparse
from array import array
from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess

import pandas as pd
from PIL import ImageDraw

from reel_design import (WIDTH,HEIGHT,BG,TEAL,MUTED,MAP,CREDIT,write,base_map,render_map,
                         guide_card,depth_card,profile_card,action_card,closing_card,
                         animate_card,depth_counts)

FPS=30


def decode_audio(audio):
    import imageio_ffmpeg
    result=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),"-v","error","-i",str(audio),
                           "-vn","-ac","1","-ar","16000","-f","s16le","-"],capture_output=True,check=True)
    samples=array("h",result.stdout)
    if not samples or max(abs(x) for x in samples)<100:
        raise ValueError("The supplied narration is empty or silent.")
    return len(samples)/16000


def timeline(first,last,cues,audio_duration,tail=5):
    ordered=[cues[k] for k in ["archive_complete","guide_start","depth_start","profile_start","action_start","end_start"]]
    if not all(math.isfinite(t) for t in ordered+[audio_duration,tail,cues["scope_start"]]):
        raise ValueError("Audio durations and cues must be finite.")
    if not 0<cues["scope_start"]<ordered[0] or not all(a<b for a,b in zip(ordered,ordered[1:])) or ordered[-1]>=audio_duration or tail<0:
        raise ValueError("Audio cues must be ordered and lie within the supplied narration.")
    if last<first:
        raise ValueError("Invalid archive period.")
    boundaries=[round(t*FPS) for t in ordered]
    if not all(a<b for a,b in zip(boundaries,boundaries[1:])):
        raise ValueError("Each explanation needs at least one encoded frame.")
    year_end,guide,depth,profile,action,end=boundaries
    years=last-first+1
    if year_end<years:
        raise ValueError("The map needs at least one frame per year.")
    # Integer partition: every closed year is included, no drift or missing years.
    plan=[("year",year,((i+1)*year_end)//years-(i*year_end)//years) for i,year in enumerate(range(first,last+1))]
    plan.extend([("hold",last,guide-year_end),("guide",None,depth-guide),("depth",None,profile-depth),
                 ("profile",None,action-profile),("action",None,end-action),
                 ("end",None,math.ceil((audio_duration+tail)*FPS)-end)])
    return plan


def export_reel(folder,dynamic=False):
    import imageio_ffmpeg
    folder=Path(folder)
    manifest=json.loads((folder/"manifest.json").read_text(encoding="utf-8"))
    cues=json.loads((folder/"audio_cues.json").read_text(encoding="utf-8"))
    audio=folder/"voz_elevenlabs_original.mp3"
    duration=decode_audio(audio)
    if sha256((folder/"catalog.csv").read_bytes()).hexdigest()!=manifest["csv_sha256"] or not all(manifest["checks"].values()):
        raise ValueError("Catalog does not match the audited snapshot.")
    df=pd.read_csv(folder/"catalog.csv")
    df.time=pd.to_datetime(df.time,utc=True,format="ISO8601")
    if len(df)!=manifest["exported_count"]:
        raise ValueError("Record count mismatch.")
    plan=timeline(manifest["first"],manifest["last"],cues,duration)
    total=sum(n for _,_,n in plan)
    motion=None
    if dynamic:
        from reel_motion import MotionDesign
        motion=MotionDesign(folder,df,manifest)
    base=base_map(manifest["first"],manifest["last"],manifest["minimum"])
    draw=ImageDraw.Draw(base)
    draw.rectangle((90,178,930,220),fill=BG)
    write(draw,(90,184),"01 / OBSERVA EL ARCHIVO",25,fill=MUTED)
    visual=folder/"visual_sin_audio.mp4"
    output=folder/"andes_pulso_reel_1900_2025.mp4"
    writer=imageio_ffmpeg.write_frames(str(visual),(WIDTH,HEIGHT),fps=FPS,codec="libx264",pix_fmt_in="rgb24",pix_fmt_out="yuv420p",
                                     quality=8,macro_block_size=2,output_params=["-movflags","+faststart","-profile:v","high","-level","4.1"],ffmpeg_log_level="error")
    writer.send(None)
    scenes=[]
    count=0
    try:
        for kind,year,repeat in plan:
            if kind in ["year","hold"]:
                image=render_map(base,df[df.time.dt.year<=year],year)
                draw=ImageDraw.Draw(image)
                draw.rectangle((90,1248,930,1295),fill=BG)
                message=("Archivo histórico · no son sismos en curso" if count/FPS<cues["scope_start"] else
                         "Continente, océano y vecinos · sin Galápagos" if kind=="year" else "Más registros ≠ más peligro")
                write(draw,(90,1255),message,29,fill=TEAL)
            elif kind=="guide":
                image=guide_card()
            elif kind=="depth":
                image=depth_card()
                draw=ImageDraw.Draw(image)
                draw.rectangle((90,178,930,220),fill=BG)
                write(draw,(90,184),"03 / LA OTRA DIMENSIÓN",25,fill=MUTED)
            elif kind=="profile":
                image=profile_card(df)
                write(ImageDraw.Draw(image),(90,1389),"Proyección regional · no es un corte de falla",23,fill=MUTED)
            elif kind=="action":
                image=action_card()
            else:
                image=closing_card(manifest,tagline=True)
            scenes.append(dict(kind=kind,year=year,start_frame=count,frames=repeat))
            if kind!="year" or year in [1900,1906,1960,2016,2025]:
                proof=(motion.render(image,kind,year,(count+repeat/2)/FPS,count/FPS,(count+repeat/2)/total) if motion else
                       animate_card(image,kind,.5,(count+repeat/2)/total))
                proof.save(folder/f"qa_{kind}_{year or 0}.jpg",quality=93)
            if kind=="year" and year==2025:
                poster=motion.render(image,kind,year,count/FPS,count/FPS,count/total) if motion else image
                poster.save(folder/"portada.jpg",quality=95)
            step=1 if motion else 3
            for offset in range(0,repeat,step):
                frame=(motion.render(image,kind,year,(count+offset)/FPS,count/FPS,(count+offset)/total) if motion else
                       animate_card(image,kind,offset/repeat,(count+offset)/total)).tobytes()
                for _ in range(min(step,repeat-offset)):
                    writer.send(frame)
            count+=repeat
            if year and year%25==0:
                print(f"Rendered through {year}",flush=True)
    finally:
        writer.close()
    # Preserve the full continuous take at its original speed and time origin.
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),"-v","error","-y","-i",str(visual),"-i",str(audio),
                    "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k","-ar","48000",
                    "-af",f"apad=whole_dur={count/FPS}","-t",str(count/FPS),"-movflags","+faststart",str(output)],
                   capture_output=True,text=True,check=True)
    metadata=dict(width=WIDTH,height=HEIGHT,fps=FPS,frames=count,duration_seconds=count/FPS,codec="H.264",pixel_format="yuv420p",
                  audio="AAC · user-supplied ElevenLabs narration · Emilio",audio_source_sha256=sha256(audio.read_bytes()).hexdigest(),
                  audio_source_duration_seconds=duration,audio_speed=1,audio_cuts=0,video_sha256=sha256(output.read_bytes()).hexdigest(),
                  csv_sha256=manifest["csv_sha256"],scenes=scenes,depth_counts=depth_counts(df),depth_max_km=float(df.depth.max()),
                  credit=CREDIT,version=6 if dynamic else 5,opening="map-first",audio_cues=cues,
                  dynamic_edit=bool(dynamic),burned_in_captions=bool(dynamic),
                  subtitle_timing="Local word timestamps, approximate; displayed spelling checked against script" if dynamic else None,
                  caption_box=[90,1430,930,1590] if dynamic else None,
                  scientific_motion="None: no symbol pulsing or movement, fixed coordinates, depth and magnitude scales")
    if dynamic:
        metadata["qa_samples"]=[dict(second=second,label=label) for second,label in [
            (1,"gancho"),(35,"advertencia"),(51.7,"epicentro"),(54.7,"magnitud"),
            (56.6,"no_danos"),(60.7,"color_claro"),(62.6,"color_oscuro"),
            (72,"hipocentro"),(74.7,"epicentro_esquema"),(78.5,"flecha_profundidad"),
            (86,"perfil_oeste"),(90,"perfil_norte"),(97.7,"maximo"),
            (103,"sin_profundidad"),(110,"no_prediccion"),(114.4,"conversa"),
            (115.9,"practica"),(117.4,"kit"),(120,"mensaje_final"),(124,"fuentes")]]
    (folder/"video_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in metadata.items() if k not in ["scenes","audio_cues"]},indent=2),flush=True)
    return output


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder",type=Path)
    parser.add_argument("--dynamic",action="store_true",help="Narration-driven shots, reveals and burned-in word-timed captions")
    args=parser.parse_args()
    print(export_reel(args.folder,args.dynamic))
