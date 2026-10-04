"""Source-pinned, map-first NDWI video. No synthetic satellite imagery.

Optional installed Microsoft Pablo narration is a reference take, not the
author's voice. Final publication still needs an editorial/scientific review.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw

from export_video import font
from reel_design import CREDIT_NAME, CREDIT_SPECIALTY
from reel_territory import INK, PANEL, LINE, MUTED, GOLD, LIME, PAPER, text, paragraph, card

WIDTH, HEIGHT, FPS = 1080, 1920, 30
MAP = (90, 395, 930, 1235)
CAPTION = (90, 1380, 930, 1578)
SCRIPT = {
    "hook": "¿Cambió el río, o cambió nuestra forma de mirarlo? Esto no es una ilustración: es el entorno del Jatunyacu visto por Sentinel dos, el veintinueve de julio de dos mil veintiséis.",
    "light": "Un satélite registra más que los colores que vemos. El agua suele reflejar poco infrarrojo cercano. Al contrastarlo con la luz verde, podemos resaltar una señal asociada al agua superficial.",
    "formula": "Este contraste se llama índice diferencial de agua normalizado: N D W I. Restamos infrarrojo cercano al verde y dividimos por su suma. No es una fotografía azul: es un cálculo sobre reflectancias.",
    "reveal": "Sobre la misma imagen, cambiamos de color natural a N D W I. La escala va de menos uno a más uno. Los valores altos aparecen azules. Eso ayuda a observar; no confirma por sí solo que cada píxel sea agua.",
    "compare": "Ahora volvemos al once de julio de dos mil diecinueve. Mismo encuadre, misma escala y solo píxeles utilizables en las dos fechas. Observa el río y sus márgenes. Son dos adquisiciones, no una película continua de siete años.",
    "napo": "Seguimos aguas abajo, hacia el Napo. Podemos localizar diferencias para revisarlas. Pero una crecida, un banco de arena, la erosión o una intervención humana pueden cambiar lo que vemos. Compartir mes no garantiza el mismo caudal.",
    "towns": "También miramos Tena y el entorno de Puerto Misahuallí. Cada píxel óptico abarca unos diez metros. En cauces estrechos puede mezclar agua, vegetación y orillas. Acercar la imagen no crea detalle nuevo.",
    "limits": "¿Y la minería? EcoCiencia y MAAP publicaron una investigación de Napo en dos mil veintiséis, con evidencia independiente de mayor resolución. No confundamos ese trabajo con nuestro índice: N D W I no mide mercurio ni demuestra la causa de un cambio.",
    "end": "La buena pregunta no es solo: ¿qué cambió? También: ¿cómo lo sabemos? Observa, contrasta fechas y calidad, y verifica con otras fuentes. Nuestros ríos merecen curiosidad, pero también evidencia.",
}
TITLES = {
    "hook": ("¿Cambió el río?", "Jatunyacu · imagen real de 2026"),
    "light": ("Ver lo invisible.", "Verde + infrarrojo cercano · no una curva medida"),
    "formula": ("Dos bandas. Un contraste.", "NDWI de McFeeters (1996) · agua superficial"),
    "reveal": ("La misma escena, otra lectura.", "2026 · RGB → NDWI · sin cambiar la geometría"),
    "compare": ("2019 / 2026", "Jatunyacu · dos adquisiciones, no una tendencia"),
    "napo": ("Sigamos hacia el Napo.", "Dos fechas · misma cuadrícula y ajuste visual"),
    "towns": ("No todos los ríos caben", "en un píxel · Tena / Puerto Misahuallí"),
    "limits": ("Una señal no es una causa.", "Índice, contexto independiente y límites"),
    "end": ("¿Cómo lo sabemos?", "Observar → contrastar → verificar"),
}


def load_evidence(folder):
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    expected = ["2019-07-11", "2026-07-29"]
    if [d[:10] for d in manifest["dates"]] != expected or manifest["formula"] != "(B3-B8)/(B3+B8)":
        raise ValueError("Unreviewed dates or index")
    if manifest["qa"]["accepted_scl"] != [4, 5, 6] or not manifest["qa"]["common_valid_support"]:
        raise ValueError("Unreviewed QA")
    for row in manifest["scenes"]:
        if sha256((folder / row["crop_file"]).read_bytes()).hexdigest() != row["crop_sha256"]:
            raise ValueError("Source crop has changed")
    for name, digest in manifest["images_sha256"].items():
        if sha256((folder / name).read_bytes()).hexdigest() != digest:
            raise ValueError("Derived image has changed: " + name)
    for area in ("jatunyacu", "napo", "tena", "misahualli"):
        if manifest["regions"][area]["common_valid_fraction"] < .55:
            raise ValueError("Too little paired QA support for the planned scene: " + area)
    return manifest


def fit_map(source):
    """Nearest display scaling with aspect preserved; never stretch a river."""
    target = Image.new("RGB", (840, 840), "#263832")
    d = ImageDraw.Draw(target)
    for y in range(0, 840, 16):
        for x in range(0, 840, 16):
            if (x // 16 + y // 16) % 2:
                d.rectangle((x, y, x + 15, y + 15), fill="#33463d")
    ratio = min(840 / source.width, 840 / source.height)
    size = (round(source.width * ratio), round(source.height * ratio))
    resized = source.resize(size, Image.Resampling.NEAREST)
    target.paste(resized, ((840 - size[0]) // 2, (840 - size[1]) // 2), resized)
    return target, ratio


class Design:
    def __init__(self, folder, manifest):
        self.folder, self.manifest, self.maps = folder, manifest, {}
        self.base_cache = {}
        self.ratios = {}
        for area in manifest["regions"]:
            for year in (2019, 2026):
                for mode in ("rgb", "ndwi"):
                    with Image.open(folder / f"{area}_{year}_{mode}.png") as image:
                        self.maps[area, year, mode], self.ratios[area] = fit_map(image.convert("RGBA"))

    def shell(self, kind):
        image = Image.new("RGB", (WIDTH, HEIGHT), INK)
        d = ImageDraw.Draw(image)
        text(d, (90, 142), "ANDES PULSO / ECUADOR VIVO", 25, LIME)
        text(d, (90, 184), "RÍOS DE NAPO · MIRAR CON EVIDENCIA", 24, MUTED)
        title, detail = TITLES[kind]
        text(d, (90, 254), title, 49, PAPER, True)
        text(d, (90, 330), detail, 27, MUTED)
        text(d, (90, 1621), CREDIT_NAME, 28, PAPER)
        text(d, (90, 1659), CREDIT_SPECIALTY, 23, MUTED)
        text(d, (90, 1723), "VISTA PREVIA · VOZ SINTÉTICA DE REFERENCIA", 22, GOLD)
        text(d, (90, 1765), "Contains modified Copernicus Sentinel data (2019, 2026)", 21, MUTED)
        return image

    def map_image(self, image, area, mode, phase=1, compare=False):
        d = ImageDraw.Draw(image)
        surface = self.maps[area, 2026, mode].copy()
        if compare:
            split = round(840 * max(0, min(1, phase)))
            surface.paste(self.maps[area, 2019, mode].crop((0, 0, split, 840)), (0, 0))
        image.paste(surface, MAP[:2])
        d.rectangle(MAP, outline=LINE, width=2)
        if compare:
            x = MAP[0] + split
            d.line((x, MAP[1], x, MAP[3]), fill=GOLD, width=4)
            for x0, label in ((110, "11 JUL 2019"), (678, "29 JUL 2026")):
                d.rounded_rectangle((x0 - 8, 412, x0 + 230, 455), 6, fill=INK)
                text(d, (x0, 418), label, 25, GOLD, width=240)
        else:
            d.rounded_rectangle((102, 411, 355, 455), 6, fill=INK)
            text(d, (112, 418), "29 JUL 2026", 25, GOLD)
        # Ground-distance scale of the native UTM grid, not the video's DPI.
        length = 1000 / 10 * self.ratios[area]
        d.rectangle((110, 1154, 130 + length, 1213), fill=INK)
        d.line((120, 1199, 120 + length, 1199), fill=PAPER, width=3)
        text(d, (120, 1162), "≈ 1 km", 24, PAPER)
        d.rounded_rectangle((850, 470, 920, 514), 5, fill=INK)
        text(d, (863, 476), "N ↑", 24, PAPER, width=50)
        support = self.manifest["regions"][area]["common_valid_fraction"] * 100
        text(d, (90, 1260), f"Soporte QA común: {support:.1f}% · trama = sin datos", 26, MUTED)
        if mode == "ndwi":
            stops = np.array([[116, 70, 46], [220, 199, 157], [242, 237, 212], [47, 141, 184], [7, 61, 105]])
            for x in range(560):
                rgb = tuple(int(np.interp(x / 559 * 4, np.arange(5), stops[:, c])) for c in range(3))
                d.line((235 + x, 1310, 235 + x, 1329), fill=rgb)
            for x, label in ((220, "−1"), (500, "0"), (778, "+1")):
                text(d, (x, 1336), label, 22, PAPER, width=65)
            text(d, (90, 1312), "NDWI", 24, LIME, width=130)
        else:
            text(d, (90, 1310), "Sentinel-2 L2A · B4/B3/B2 · entradas de 10 m", 26, LIME)

    def base(self, kind, fraction):
        image = self.shell(kind)
        d = ImageDraw.Draw(image)
        if kind in ("hook", "reveal", "compare", "napo", "towns"):
            area = "napo" if kind == "napo" else ("tena" if fraction < .5 else "misahualli") if kind == "towns" else "jatunyacu"
            mode = "ndwi" if kind == "compare" or (kind == "reveal" and fraction >= .45) else "rgb"
            self.map_image(image, area, mode, .5 + .4 * np.sin(fraction * np.pi * 2) if kind in ("compare", "napo") else 1,
                           compare=kind in ("compare", "napo"))
            if kind == "towns":
                d.rounded_rectangle((110, 470, 600, 516), 5, fill=INK)
                text(d, (122, 477), "TENA" if area == "tena" else "PUERTO MISAHUALLÍ", 27, GOLD)
        elif kind == "light":
            card(d, (90, 420, 930, 1080), LIME)
            for i, (label, band, detail) in enumerate([
                ("LUZ VERDE", "B3 · 10 m", "Una banda visible."),
                ("INFRARROJO CERCANO", "B8 · 10 m", "No lo vemos con nuestros ojos.")]):
                y = 495 + i * 255
                text(d, (130, y), label, 34, LIME if i == 0 else GOLD)
                text(d, (130, y + 63), band, 51, PAPER, True)
                text(d, (130, y + 150), detail, 30, MUTED)
            paragraph(d, (110, 1140), "El agua suele reflejar poco NIR. El contraste puede destacar agua superficial.", 38, 790, PAPER)
        elif kind == "formula":
            card(d, (90, 465, 930, 1065), LIME)
            text(d, (145, 520), "NDWI", 91, GOLD, True)
            text(d, (170, 700), "VERDE − NIR", 61, PAPER)
            d.line((165, 805, 845, 805), fill=LIME, width=4)
            text(d, (170, 849), "VERDE + NIR", 61, PAPER)
            paragraph(d, (110, 1160), "Con reflectancias no negativas y suma positiva: de −1 a +1. No calculamos desde los colores del RGB.", 34, 790, MUTED)
        else:
            entries = [("OBSERVAR", "Imágenes reales y un índice espectral."),
                       ("CONTRASTAR", "Fechas, nubes, resolución y caudal."),
                       ("VERIFICAR", "Otras imágenes y evidencia de campo.")] if kind == "end" else [
                       ("NDWI", "No mide mercurio ni confirma minería."),
                       ("MAAP #249 · 2026", "Investigación externa: EcoCiencia / MAAP."),
                       ("NO SON EL MISMO RESULTADO", "Su análisis no valida nuestros píxeles.")]
            for i, (heading, detail) in enumerate(entries):
                y = 450 + i * 258
                card(d, (90, y, 930, y + 220), LIME)
                text(d, (127, y + 29), heading, 31, GOLD)
                paragraph(d, (127, y + 100), detail, 33, 755, PAPER)
            paragraph(d, (110, 1245), "Datos: Copernicus Sentinel / Earth Search. NDWI: McFeeters (1996). Fuentes completas en la descripción.", 27, 790, MUTED)
        return image

    def render(self, kind, fraction, caption, progress):
        # Reuse static scene pixels; captions/progress do not change geography.
        key = None if kind in ("compare", "napo") else (kind, fraction >= .5 if kind == "towns" else fraction >= .45 if kind == "reveal" else False)
        if key is None:
            image = self.base(kind, fraction)
        else:
            if key not in self.base_cache:
                self.base_cache[key] = self.base(kind, fraction)
            image = self.base_cache[key].copy()
        d = ImageDraw.Draw(image)
        card(d, CAPTION, GOLD)
        paragraph(d, (138, 1402), caption, 31, 757, PAPER, leading=1.23)
        d.line((90, 1598, 90 + round(840 * progress), 1598), fill=LIME, width=4)
        return image


def pieces(value, maximum=19):
    words = value.split()
    return [" ".join(words[i:i + maximum]) for i in range(0, len(words), maximum)]


def timestamp(seconds):
    ms = round(seconds * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def export(folder, silent=False, storyboard_only=False, *, design_type=Design,
           evidence_loader=load_evidence, script=SCRIPT, stem="ndwi_napo_2019_2026", tag="ndwi",
           render_stride=3):
    if not isinstance(render_stride, int) or render_stride <= 0 or FPS % render_stride:
        raise ValueError("Render stride must be a positive divisor of FPS")
    import imageio_ffmpeg
    from reel_editorial import synthesize_audio, mux_audio
    folder = Path(folder)
    evidence = evidence_loader(folder)
    design = design_type(folder, evidence)
    (folder / "guion_elevenlabs.txt").write_text("\n\n".join(script.values()) + "\n", encoding="utf-8")
    (folder / "narration.json").write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
    narrated_frames = {} if silent or storyboard_only else synthesize_audio(folder, script)
    scenes, frame_start, subtitle_rows = [], 0, []
    for kind, narration in script.items():
        count = max(5 * FPS, narrated_frames[kind]) if kind in narrated_frames else round((len(narration.split()) / 2.3 + 1) * FPS)
        count += -count % render_stride
        scene = {"kind": kind, "year": getattr(design, "scene_year", lambda _: None)(kind),
                 "start_frame": frame_start, "frames": count}
        scenes.append(scene)
        captions = pieces(narration)
        weights = [len(c.split()) for c in captions]
        elapsed = 0
        for caption, weight in zip(captions, weights):
            duration = count / FPS * weight / sum(weights)
            subtitle_rows.append({"kind": kind, "start": frame_start / FPS + elapsed,
                                  "end": frame_start / FPS + elapsed + duration, "text": caption})
            elapsed += duration
        frame_start += count
    total = frame_start
    sheet = Image.new("RGB", (720, ((len(scenes) + 2) // 3) * 426), INK)
    for i, scene in enumerate(scenes):
        caption = next(r["text"] for r in subtitle_rows if r["kind"] == scene["kind"])
        image = design.render(scene["kind"], .58, caption, (scene["start_frame"] + scene["frames"] / 2) / total)
        image.save(folder / f"qa_{tag}_{scene['kind']}.jpg", quality=95)
        sheet.paste(image.resize((240, 426)), (i % 3 * 240, i // 3 * 426))
    sheet.save(folder / f"storyboard_{tag}.jpg", quality=95)
    srt = "\n\n".join(f"{i}\n{timestamp(r['start'])} --> {timestamp(r['end'])}\n{r['text']}" for i, r in enumerate(subtitle_rows, 1))
    (folder / "subtitulos_borrador.srt").write_text(srt + "\n", encoding="utf-8")
    if storyboard_only:
        return folder / f"storyboard_{tag}.jpg"
    visual = folder / f"{stem}_visual_sin_voz.mp4"
    writer = imageio_ffmpeg.write_frames(str(visual), (WIDTH, HEIGHT), fps=FPS, codec="libx264", pix_fmt_in="rgb24",
                                        pix_fmt_out="yuv420p", macro_block_size=2, quality=8, ffmpeg_log_level="error",
                                        output_params=["-movflags", "+faststart", "-preset", "veryfast", "-threads", "2"])
    writer.send(None)
    try:
        for scene in scenes:
            rows = [r for r in subtitle_rows if r["kind"] == scene["kind"]]
            for offset in range(0, scene["frames"], render_stride):
                seconds = (scene["start_frame"] + offset) / FPS
                caption = next((r["text"] for r in rows if r["start"] <= seconds < r["end"]), rows[-1]["text"])
                fraction = offset / scene["frames"]
                raw = design.render(scene["kind"], fraction, caption, seconds / (total / FPS)).tobytes()
                for _ in range(render_stride):
                    writer.send(raw)
            print("Rendered", tag, "scene:", scene["kind"], flush=True)
    finally:
        writer.close()
    output = visual if silent else folder / f"{stem}_vista_previa.mp4"
    if not silent:
        mux_audio(folder, visual, output, scenes)
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    decoded = subprocess.run([exe, "-v", "error", "-xerror", "-i", str(output), "-progress", "pipe:1",
                              "-nostats", "-f", "null", "-"], capture_output=True, text=True, check=True)
    decoded_counts = [int(line.split("=", 1)[1]) for line in decoded.stdout.splitlines() if line.startswith("frame=")]
    if not decoded_counts or decoded_counts[-1] != total or decoded.stderr.strip():
        raise ValueError("Full decode frame count or errors differ from the planned export")
    metadata_reader = imageio_ffmpeg.read_frames(str(output))
    actual = next(metadata_reader)
    metadata_reader.close()
    if actual["size"] != (WIDTH, HEIGHT) or actual["fps"] != FPS or abs(actual["duration"] - total / FPS) > .04:
        raise ValueError("Encoded video duration or format mismatch")
    for scene in scenes:
        second = (scene["start_frame"] + .58 * scene["frames"]) / FPS
        subprocess.run([exe, "-v", "error", "-ss", str(second), "-i", str(output), "-frames:v", "1", "-y",
                        str(folder / f"codificado_{tag}_{scene['kind']}.jpg")], capture_output=True, check=True)
    voice_report = {"present": not silent}
    if not silent:
        pcm = subprocess.run([exe, "-v", "error", "-i", str(output), "-map", "0:a:0", "-vn", "-ac", "1", "-ar", "16000",
                              "-f", "s16le", "-"], capture_output=True, check=True).stdout
        samples = np.frombuffer(pcm, dtype="<i2")
        if abs(samples.size / 16000 - total / FPS) > .12 or np.abs(samples.astype("int32")).max() < 100:
            raise ValueError("Missing or truncated narration")
        checked = []
        for scene in scenes:
            start = round(scene["start_frame"] / FPS * 16000)
            stop = round((scene["start_frame"] + scene["frames"]) / FPS * 16000)
            segment = samples[start:stop].astype("float64")
            if not segment.size or np.mean(segment * segment) < 100:
                raise ValueError("No audible narration in scene " + scene["kind"])
            checked.append(scene["kind"])
        voice_report.update(duration_seconds=samples.size / 16000, peak=int(np.abs(samples.astype("int32")).max()),
                            checked_scenes=checked)
    result = {"status": "narrated_preview_not_final_publication", "video": output.name,
              "sha256": sha256(output.read_bytes()).hexdigest(), "source_manifest_sha256": sha256((folder / "manifest.json").read_bytes()).hexdigest(),
              "width": WIDTH, "height": HEIGHT, "fps": FPS, "frames": total, "duration_seconds": total / FPS,
              "full_decode": "passed", "decoded_frames": decoded_counts[-1], "audio": voice_report, "scenes": scenes,
              "narrator": "none" if silent else "installed Microsoft Pablo; synthetic reference take; no paid service",
              "captions": "approximate word-count timing, manually review before final publication",
              "pending": "author's optional new voice take, subtitle alignment, scientific/editorial review"}
    (folder / "video_metadata.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--silent", action="store_true")
    parser.add_argument("--storyboard-only", action="store_true")
    args = parser.parse_args()
    print(export(args.folder, args.silent, args.storyboard_only))
