"""Local-only speech timing inspection using an isolated faster-whisper runtime."""
import argparse
import json
from pathlib import Path
import sys
import subprocess


def inspect_audio(audio,folder):
    # Kept out of the app environment: no changes to Streamlit dependencies.
    sys.path.insert(0,str(Path(__file__).parent/"artifacts"/"asr_runtime"))
    import numpy as np
    import imageio_ffmpeg
    from faster_whisper import WhisperModel
    decoded=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),"-v","error","-i",str(audio),
                            "-vn","-ac","1","-ar","16000","-f","f32le","-"],capture_output=True,check=True)
    waveform=np.frombuffer(decoded.stdout,dtype="<f4")
    model=WhisperModel("base",device="cpu",compute_type="int8",cpu_threads=4,
                       download_root=str(Path(__file__).parent/"artifacts"/"asr_models"))
    segments,info=model.transcribe(waveform,language="es",beam_size=5,word_timestamps=True,vad_filter=False)
    rows=[]
    for segment in segments:
        row=dict(start=segment.start,end=segment.end,text=segment.text,
                 words=[dict(start=w.start,end=w.end,text=w.word,probability=w.probability) for w in segment.words or []])
        rows.append(row)
        print(f"{segment.start:.2f}–{segment.end:.2f}: {segment.text}",flush=True)
    result=dict(method="local faster-whisper base int8; automatically estimated times",language=info.language,
                duration=info.duration,segments=rows)
    (Path(folder)/"audio_transcript.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio",type=Path)
    parser.add_argument("folder",type=Path)
    args=parser.parse_args()
    inspect_audio(args.audio,args.folder)
