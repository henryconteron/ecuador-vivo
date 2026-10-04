"""Decode every encoded frame and verify publication properties, not just inputs."""
import argparse
from array import array
from hashlib import sha256
import json
from pathlib import Path
import subprocess

import imageio_ffmpeg


def verify(folder):
    folder=Path(folder)
    video=folder/"andes_pulso_reel_1900_2025.mp4"
    expected=json.loads((folder/"video_metadata.json").read_text())
    video_hash=sha256(video.read_bytes()).hexdigest()
    if video_hash!=expected["video_sha256"]:
        raise ValueError("Video hash does not match the exported artifact.")
    reader=imageio_ffmpeg.read_frames(str(video))
    actual=next(reader)
    try:
        count=sum(1 for _ in reader)
    finally:
        reader.close()
    if tuple(actual["size"])!=(1080,1920) or actual["fps"]!=30 or count!=expected["frames"] or abs(actual["duration"]-expected["duration_seconds"])>.04:
        raise ValueError(f"Encoded video mismatch: {actual}, decoded frames={count}")
    if "h264" not in actual["codec"]:
        raise ValueError(f"Unexpected codec: {actual['codec']}")
    # Independent full FFmpeg decode: errors must remain visible and fail verification.
    exe=imageio_ffmpeg.get_ffmpeg_exe()
    audio_report={"present":False}
    if expected.get("audio","none")!="none":
        decoded=subprocess.run([exe,"-v","error","-i",str(video),"-map","0:a:0","-vn","-ac","1","-ar","16000","-f","s16le","-"],capture_output=True,check=True)
        samples=array("h",decoded.stdout)
        duration=len(samples)/16000
        peak=max(abs(x) for x in samples) if samples else 0
        if peak<100 or abs(duration-expected["duration_seconds"])>.12:
            raise ValueError("Narration is absent, silent or out of sync with video duration.")
        audio_report=dict(present=True,decoded_duration_seconds=duration,peak_pcm=peak,scene_checks=[])
        if expected.get("audio_source_sha256"):
            import numpy as np
            source=folder/"voz_elevenlabs_original.mp3"
            if sha256(source.read_bytes()).hexdigest()!=expected["audio_source_sha256"]:
                raise ValueError("The original narration was changed after export.")
            source_pcm=subprocess.run([exe,"-v","error","-i",str(source),"-vn","-ac","1","-ar","16000","-f","s16le","-"],capture_output=True,check=True)
            reference=np.frombuffer(source_pcm.stdout,dtype="<i2").astype(float)
            encoded=np.asarray(samples[:len(reference)],dtype=float)
            if len(encoded)!=len(reference):
                raise ValueError("The encoded narration is shorter than the original take.")
            correlation=float(np.corrcoef(reference,encoded)[0,1])
            if not np.isfinite(correlation) or correlation<.98:
                raise ValueError(f"Narration timing or waveform changed: correlation={correlation}")
            audio_report.update(source_pcm_correlation=correlation,source_duration_seconds=len(reference)/16000,
                                original_take_preserved=True)
        # Verify audible content in each explanatory scene, not only somewhere in the file.
        for scene in expected.get("scenes",[]):
            if scene["kind"] in ["year","hold"]:
                continue
            start=int(scene["start_frame"]/30*16000)
            stop=int((scene["start_frame"]+scene["frames"])/30*16000)
            segment=samples[start:stop]
            energy=sum(x*x for x in segment)/max(1,len(segment))
            if energy<100:
                raise ValueError(f"No audible narration in {scene['kind']}")
            audio_report["scene_checks"].append(scene["kind"])
    result=subprocess.run([exe,"-v","error","-xerror","-i",str(video),"-f","null","-"],capture_output=True,text=True,check=True)
    if result.stderr.strip():
        raise ValueError(result.stderr)
    samples=[]
    for sample in expected.get("qa_samples",[]):
        samples.append((sample["second"],sample["label"]))
    if expected.get("opening")=="map-first":
        samples.append((0,"inicio"))
    labels={"intro":"inicio","purpose":"mensaje","guide":"guia","depth":"profundidad","profile":"perfiles","action":"preparacion","end":"cierre"}
    for scene in expected.get("scenes",[]):
        label=labels.get(scene["kind"])
        if scene["kind"]=="year" and scene["year"] in [1960,2016,2025]:
            label=str(scene["year"])
        if label:
            samples.append(((scene["start_frame"]+scene["frames"]//2)/expected["fps"],label))
    if not samples:  # Preserved v1 exports predate per-scene metadata.
        samples=[(1,"inicio"),(5,"guia"),(25,"medio"),(41.9,"2016"),(46.3,"2025"),(53,"cierre")]
    for second,label in samples:
        subprocess.run([exe,"-v","error","-ss",str(second),"-i",str(video),"-frames:v","1","-y",str(folder/f"codificado_{label}.jpg")],check=True)
    report=dict(width=actual["size"][0],height=actual["size"][1],fps=actual["fps"],duration_seconds=actual["duration"],
                codec=actual["codec"],decoded_frames=count,full_decode_errors=0,video_sha256=video_hash,audio=audio_report)
    (folder/"encoded_verification.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder",type=Path)
    verify(parser.parse_args().folder)
