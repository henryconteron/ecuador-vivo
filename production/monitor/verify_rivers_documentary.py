"""Verify the actual encoded documentary, not only its storyboard."""
from hashlib import sha256
import json
import re
import subprocess
import wave

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw

from reel_rivers_documentary import BEATS, Design, FOLDER, FPS, BG, PAPER, font


def main():
    video=FOLDER/"que_le_paso_al_rio_v8.mp4"
    metadata=json.loads((FOLDER/"video_metadata.json").read_text(encoding="utf-8"))
    sources=json.loads((FOLDER/"sources_manifest.json").read_text(encoding="utf-8"))
    if sha256(video.read_bytes()).hexdigest()!=metadata["video_sha256"]:
        raise ValueError("Encoded video changed")
    if sha256((FOLDER/"sources_manifest.json").read_bytes()).hexdigest()!=metadata["source_manifest_sha256"]:
        raise ValueError("Evidence manifest changed")
    for row in sources["images"]:
        if sha256((FOLDER/row["file"]).read_bytes()).hexdigest()!=row["sha256"]:raise ValueError(row["file"])
    for file,digest in sources["local_files"].items():
        if sha256((FOLDER/file).read_bytes()).hexdigest()!=digest:raise ValueError(file)
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    # Demux info is taken from the encoded file, not assumed from the renderer.
    probe=subprocess.run([ff,"-hide_banner","-i",str(video)],capture_output=True,text=True)
    if not re.search(r"Video: h264.*1920x1080.*30 fps",probe.stderr):
        raise ValueError("Actual video dimensions/codec/rate differ")
    if "Audio: aac" not in probe.stderr:raise ValueError("Encoded narration absent")
    decoded=subprocess.run([ff,"-v","error","-i",str(video),"-map","0:v:0","-an","-progress","pipe:1","-f","null","-"],capture_output=True,text=True,check=True)
    frames=[int(n) for n in re.findall(r"^frame=(\d+)$",decoded.stdout,re.M)]
    if not frames or frames[-1]!=metadata["frames"] or decoded.stderr.strip():
        raise ValueError("Full video decode failed or frame count differs")
    print(f"Full decode passed: {frames[-1]} frames",flush=True)
    audio=subprocess.run([ff,"-v","error","-i",str(video),"-vn","-ar","16000","-ac","1","-f","f32le","-"],capture_output=True,check=True)
    samples=np.frombuffer(audio.stdout,dtype="<f4")
    if abs(len(samples)/16000-metadata["duration_seconds"])>.15:raise ValueError("Audio/video length differs")
    scene_reports=[]
    sheet=Image.new("RGB",(1600,2250),BG)
    # Check subtitle bounds with the real service timing, and sample every encoded shot.
    design=Design()
    for i,(beat,scene) in enumerate(zip(BEATS,metadata["scenes"])):
        with wave.open(str(FOLDER/f"voz_{scene['kind']}.wav")) as stream:
            voice_seconds=stream.getnframes()/stream.getframerate()
        if voice_seconds>scene["frames"]/FPS:raise ValueError("Voice clipped: "+scene["kind"])
        start=scene["start_frame"]/FPS
        segment=samples[round(start*16000):round((start+voice_seconds)*16000)]
        rms=float(np.sqrt(np.mean(segment**2)))
        if rms<.001:raise ValueError("Silent encoded narration: "+scene["kind"])
        timing=json.loads((FOLDER/f"times_{scene['kind']}.json").read_text(encoding="utf-8"))
        last=timing["words"][-1]
        tail=samples[round((start+last["start"])*16000):round((start+last["end"])*16000)]
        if not tail.size or np.sqrt(np.mean(tail**2))<.001:raise ValueError("Final word missing: "+scene["kind"])
        for cue in scene["cues"]:design.render(beat,.6,cue["text"])
        timestamp=start+scene["frames"]/FPS*.55
        target=FOLDER/f"encoded_{scene['kind']}.jpg"
        subprocess.run([ff,"-v","error","-y","-ss",str(timestamp),"-i",str(video),"-frames:v","1","-q:v","2",str(target)],check=True)
        with Image.open(target) as image:
            if image.size!=(1920,1080):raise ValueError("Encoded dimensions changed")
            sheet.paste(image.resize((400,225),Image.Resampling.LANCZOS),((i%4)*400,(i//4)*250))
            ImageDraw.Draw(sheet).text(((i%4)*400+8,(i//4)*250+227),scene["kind"],font=font(17),fill=PAPER)
        scene_reports.append(dict(shot=scene["kind"],audio_rms=rms,audio_seconds=voice_seconds,final_word_signal=True,caption_bounds_passed=True))
    sheet.save(FOLDER/"storyboard_encoded.jpg",quality=92)
    report=dict(status="technical-verification-passed; human scientific/editorial final review recommended",video_sha256=metadata["video_sha256"],
        decoded_frames=frames[-1],expected_frames=metadata["frames"],duration_seconds=metadata["duration_seconds"],
        dimensions=[1920,1080],fps=30,audio_seconds=len(samples)/16000,scene_checks=scene_reports,
        limitations="Shot samples inspected separately; automated timing and signal checks do not constitute full human listening or scientific peer review")
    (FOLDER/"verification.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("All 35 shots: narration, last-word signal, caption bounds and encoded image checked",flush=True)


if __name__=="__main__":main()
