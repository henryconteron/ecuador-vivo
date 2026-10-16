"""Bounded Blender render worker. One scratch PNG, explicit cancellation, CFR."""
import hashlib
import json
import os
from pathlib import Path
from queue import Queue,Empty
import shutil
import subprocess
import sys
from threading import Thread
import time
import traceback
from PIL import Image
import imageio_ffmpeg
from studio_blender import blender_executable,job_root,recipe_identity,validate_recipe,_write


def movie_writer(path,size):
    return imageio_ffmpeg.write_frames(str(path),size,fps=30,codec='libx264',
        pix_fmt_in='rgb24',pix_fmt_out='yuv420p',macro_block_size=1,
        output_params=['-crf','18','-movflags','+faststart'],ffmpeg_log_level='error')


def execute(job,engine):
    job=Path(job).resolve()
    if job!=job_root(job.name):raise ValueError('El job Blender está fuera de su almacén.')
    if Path(engine).resolve()!=blender_executable().resolve():raise ValueError('Motor Blender no verificado.')
    request=json.loads((job/'request.json').read_text(encoding='utf-8'))
    recipe=validate_recipe(request['recipe']);mode=request['mode']
    if mode not in ('poster','preview','final') or job.name!=recipe_identity(recipe)+'-'+mode:
        raise ValueError('El job no coincide con la receta.')
    process=None;writer=None;started=time.monotonic();frames=0
    total=1 if mode=='poster' else round(recipe['duration']*30)
    size=(1080,900) if mode=='final' else (640,534)
    def status(state,message,progress=0):
        _write(job/'status.json',dict(state=state,message=message,progress=progress,pid=os.getpid(),updated=time.time()))
    try:
        status('running','Construyendo escena Blender')
        process=subprocess.Popen([str(engine),'--background','--factory-startup','--disable-autoexec',
            '--threads','4','--python-exit-code','1','--python',str(Path(__file__).with_name('blender_orographic.py')),'--',str(job)],
            cwd=Path(engine).parent,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
            text=True,encoding='utf-8',errors='replace',bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        messages=Queue(maxsize=1024)
        def collect():
            for line in process.stdout:messages.put(line)
            messages.put(None)
        Thread(target=collect,daemon=True).start()
        if mode!='poster':
            writer=movie_writer(job/'video.partial.mp4',size)
            writer.send(None)
        done=False
        with (job/'blender.log').open('w',encoding='utf-8') as log:
            while True:
                if (job/'cancel.request').exists():raise InterruptedError('Render 3D cancelado.')
                if time.monotonic()-started>3600:raise TimeoutError('El render 3D superó una hora; reduce duración o usa previsualización.')
                try:line=messages.get(timeout=.5)
                except Empty:continue
                if line is None:break
                if log.tell()<10*1024*1024:log.write(line);log.flush()
                if line.strip()=='EV_DONE':done=True
                if not line.startswith('EV_FRAME:'):continue
                index=int(line.split(':',1)[1])
                if index!=frames or frames>=total:raise ValueError('Blender entregó una secuencia de cuadros inválida.')
                with Image.open(job/'frame.png') as image:
                    if image.size!=size:raise ValueError('Blender cambió la resolución solicitada.')
                    pixels=image.convert('RGB')
                    try:
                        if writer is not None:writer.send(pixels.tobytes())
                        if mode=='poster' or index==min(total-1,round(total*.65)-1):
                            shutil.copyfile(job/'frame.png',job/'poster.png')
                    finally:pixels.close()
                frames+=1;status('running',f'Renderizando cuadro {frames} de {total}',frames/total)
                process.stdin.write('EV_ACK\n');process.stdin.flush()
        if process.wait(timeout=30)!=0 or not done or frames!=total:raise ValueError('Blender no completó todos los cuadros; consulta su log.')
        if writer is not None:writer.close();writer=None;os.replace(job/'video.partial.mp4',job/'video.mp4')
        files={}
        for name in ('poster.png','scene.blend')+(() if mode=='poster' else ('video.mp4',)):
            with (job/name).open('rb') as stream:files[name]=hashlib.file_digest(stream,'sha256').hexdigest()
        _write(job/'receipt.json',dict(engine='Blender',version='4.5.4 LTS',recipe_sha256=recipe_identity(recipe),
            frames=frames,fps=30,size=list(size),duration=frames/30 if mode!='poster' else 0,
            render_seconds=round(time.monotonic()-started,3),files=files,
            scientific_status='Ilustración conceptual, no pronóstico, DEM ni simulación microfísica.'))
        status('complete','Recurso 3D listo',1)
    except InterruptedError as error:status('cancelled',str(error))
    except Exception as error:
        traceback.print_exc();status('failed',str(error))
    finally:
        if process is not None:
            if process.poll() is None:
                process.terminate()
                try:process.wait(timeout=10)
                except subprocess.TimeoutExpired:process.kill();process.wait(timeout=10)
            if process.stdout:process.stdout.close()
            if process.stdin:process.stdin.close()
        if writer is not None:writer.close()
        # Only these owned scratch outputs, never a user-selected directory.
        for name in ('frame.png','video.partial.mp4'):
            (job/name).unlink(missing_ok=True)


if __name__=='__main__':execute(sys.argv[1],sys.argv[2])
