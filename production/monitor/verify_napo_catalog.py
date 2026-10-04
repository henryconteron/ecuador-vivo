"""Check encoded V5 properties and actual consecutive 3D-motion frames."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageChops


def verify(folder):
    folder = Path(folder)
    video = folder/"napo_1900_2026_fallas_3d_maqueta_sin_voz_v5.mp4"
    expected = json.loads((folder/"draft_metadata_v5.json").read_text(encoding="utf-8"))
    if sha256(video.read_bytes()).hexdigest() != expected["sha256"]:
        raise ValueError("Exported video hash mismatch")
    frames, duration = imageio_ffmpeg.count_frames_and_secs(str(video))
    reader = imageio_ffmpeg.read_frames(str(video))
    try:
        metadata = next(reader)
    finally:
        reader.close()
    if frames != 3930 or abs(duration-131) > .04:
        raise ValueError("Incorrect encoded frame count/duration")
    if metadata["size"] != (1080, 1920) or metadata["fps"] != 30 or "h264" not in metadata["codec"]:
        raise ValueError("Incorrect encoded size/fps/codec")
    if metadata.get("audio_codec"):
        raise ValueError("This draft must remain silent")
    # Decode selected frames from the actual file in one pass, not source renders.
    picks = [0, 315, 1185, 1365, 1890, 2430, 2431, 2730, 2731, 3030, 3031, 3900]
    expression = "+".join(f"eq(n,{index})" for index in picks)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(video),
                    "-vf", f"select='{expression}'", "-vsync", "0", "-q:v", "2", "-y",
                    str(folder/"qa_v5_encoded_%02d.jpg")], check=True, capture_output=True)
    pairs = [(6, 7, "normal"), (8, 9, "inversa"), (10, 11, "desgarre")]
    motion = {}
    for a, b, kind in pairs:
        with Image.open(folder/f"qa_v5_encoded_{a:02d}.jpg") as first:
            with Image.open(folder/f"qa_v5_encoded_{b:02d}.jpg") as second:
                delta = ImageChops.difference(first.crop((120, 520, 935, 1010)),
                                             second.crop((120, 520, 935, 1010)))
                if delta.getbbox() is None:
                    raise ValueError(f"Repeated motion frame: {kind}")
                motion[kind] = "consecutive encoded block-region frames differ"
    report = {"sha256": expected["sha256"], "frames": frames, "duration_seconds": duration,
              "size": metadata["size"], "fps": metadata["fps"], "codec": metadata["codec"],
              "audio": None, "encoded_frame_indices": picks, "motion_checks": motion,
              "full_decode": expected["full_decode"], "status": "silent_draft_not_for_publication"}
    (folder/"verification_v5.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    verify(parser.parse_args().folder)
