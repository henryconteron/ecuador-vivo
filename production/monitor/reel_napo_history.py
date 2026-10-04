"""Historical selection → 2026 question → reviewed IG-EPN case. Silent draft."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw

from prepare_napo_history import load_history
from reel_territory import (TerritoryDesign, BOX, WIDTH, HEIGHT, INK, LINE,
                            MUTED, GOLD, LIME, PAPER, text, paragraph, card, project)

SCENES = [(0, 18, "historia_1987"), (18, 36, "mapa_historico"),
          (36, 42, "pregunta_2026"), (42, 51, "mapa_2026"),
          (51, 61, "boletines"), (61, 70, "proceso"),
          (70, 83, "profundidad"), (83, 96, "conceptos"), (96, 109, "cierre")]
DURATION = SCENES[-1][1]


def historical_count(elapsed):
    return min(4, max(1, int(elapsed // 4.5)+1))


class NapoHistoryDesign(TerritoryDesign):
    def __init__(self, folder):
        super().__init__(folder)
        self.history = load_history(folder)
        self.mapped_history = [r for r in self.history if r["latitude"] is not None]
        if len(self.mapped_history) != 4:
            raise ValueError("Expected four explicitly selected historical epicenters")

    def shell(self, number, title, subtitle):
        image = super().shell(0, title, subtitle)
        d = ImageDraw.Draw(image)
        d.rectangle((80, 190, 945, 240), fill=INK)
        text(d, (90, 195), "MEMORIA SÍSMICA / 01 · NAPO: ANTES Y AHORA", 24, MUTED)
        d.rectangle((80, 1545, 945, 1580), fill=INK)
        return image

    def history_1987(self):
        image = self.shell(0, "Napo tiene memoria.", "05 MAR 1987 · fecha local · nororiente del Ecuador")
        d = ImageDraw.Draw(image)
        for row, y in zip(self.history[:2], (455, 835)):
            card(d, (90, y, 930, y+325), GOLD)
            text(d, (135, y+30), f"{row['local_time']} · UTC−5", 33, MUTED)
            text(d, (130, y+100), str(row["magnitude"]).replace(".", ","), 126, PAPER, True)
            text(d, (395, y+170), "Ms", 46, GOLD)
            text(d, (135, y+265), "Magnitud de ondas superficiales", 28, MUTED)
        paragraph(d, (110, 1220), "Dos terremotos. Sus efectos incluyeron grandes deslizamientos y flujos de escombros.", 36, 780, PAPER)
        paragraph(d, (110, 1380), "Napo tenía otros límites en 1987. No situamos estos epicentros sin coordenadas verificadas.", 28, 780, GOLD)
        text(d, (110, 1480), "Fuente: IG-EPN · reconstrucción histórica de 1987", 25, MUTED)
        return image

    def reference_map(self, image):
        surface = Image.new("RGB", (BOX[2]-BOX[0], BOX[3]-BOX[1]), "#243d33")
        d = ImageDraw.Draw(surface)
        for feature in self.features:
            geometry = feature["geometry"]
            napo = feature["properties"]["shapeName"] == "Napo"
            polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
            for polygon in polygons:
                points = [(project(lon, lat)[0]-BOX[0], project(lon, lat)[1]-BOX[1]) for lon, lat in polygon[0]]
                d.polygon(points, fill="#507749" if napo else "#28483c",
                          outline=LIME if napo else "#668268", width=3 if napo else 1)
                for hole in polygon[1:]:
                    d.polygon([(project(lon, lat)[0]-BOX[0], project(lon, lat)[1]-BOX[1]) for lon, lat in hole], fill="#243d33")
        image.paste(surface, BOX[:2])
        d = ImageDraw.Draw(image)
        d.rectangle(BOX, outline=LINE, width=2)
        text(d, (730, 470), "N ↑", 28, LIME)
        text(d, (490, 690), "NAPO", 46, PAPER, True)
        text(d, (135, 520), "PICHINCHA", 21, MUTED)
        text(d, (700, 570), "ORELLANA", 21, MUTED)
        text(d, (700, 1160), "PASTAZA", 21, MUTED)

    def history_map(self, count):
        image = self.shell(1, "La historia continúa.", "Selección documentada: 2023–2025 · NO es todo el catálogo")
        self.reference_map(image)
        d = ImageDraw.Draw(image)
        offsets = [(35, -38), (-90, -10), (-75, 40), (36, -38)]
        for index, row in enumerate(self.mapped_history[:count]):
            x, y = project(row["longitude"], row["latitude"])
            dx, dy = offsets[index]
            d.ellipse((x-9, y-9, x+9, y+9), fill=GOLD, outline=PAPER, width=2)
            d.line((x+dx*.15, y+dy*.15, x+dx, y+dy), fill=PAPER, width=2)
            d.ellipse((x+dx-18, y+dy-18, x+dx+18, y+dy+18), fill=INK, outline=GOLD, width=2)
            text(d, (x+dx-7, y+dy-13), str(index+1), 22, GOLD, width=30)
        text(d, (110, 1245), "Puntos = epicentros · tamaño fijo, no magnitud", 26, GOLD)
        row = self.mapped_history[count-1]
        date = "/".join(reversed(row["date"].split("-")))
        card(d, (90, 1300, 930, 1444), GOLD)
        text(d, (130, 1320), f"{count:02d} / {date} · {row['magnitude']:g} {row['type']}".replace(".", ","), 39, PAPER, True)
        text(d, (130, 1382), f"Profundidad: {row['depth_km']:g} km · fuente: IG-EPN".replace(".", ","), 30, MUTED)
        text(d, (110, 1453), "MLv y Mw: escalas distintas; no hacemos un ranking", 25, MUTED)
        text(d, (110, 1493), "Límites: referencia 2011 · Napo resaltado ≠ peligro", 24, MUTED)
        return image

    def question(self):
        image = self.shell(2, "¿Y en 2026?", "Del pasado a los registros de este año")
        d = ImageDraw.Draw(image)
        text(d, (110, 540), "2026", 195, GOLD, True)
        card(d, (90, 870, 930, 1265), LIME)
        paragraph(d, (135, 930), "¿Se sigue moviendo la Tierra en Napo?", 66, 720, PAPER)
        paragraph(d, (110, 1360), "Respondemos con un boletín real, no con una predicción.", 34, 780, MUTED)
        return image

    def render(self, second):
        number = next(i for i, (start, end, _) in enumerate(SCENES) if start <= second < end)
        name = SCENES[number][2]
        elapsed = second-SCENES[number][0]
        count = historical_count(elapsed)
        key = (name, count if name == "mapa_historico" else 0)
        if key not in self.cache:
            makers = {"historia_1987": self.history_1987, "pregunta_2026": self.question,
                      "mapa_2026": self.map_image, "boletines": self.bulletins,
                      "proceso": self.process, "profundidad": self.depth,
                      "conceptos": self.concepts, "cierre": self.closing}
            self.cache[key] = self.history_map(count) if name == "mapa_historico" else makers[name]()
        image = self.cache[key].copy()
        reveals = {
            "historia_1987": [(3, (90, 835, 930, 1160))],
            "boletines": [(3, (90, 885, 930, 1260)), (6, (90, 1330, 930, 1500))],
            "proceso": [(2, (90, 758, 930, 991)), (4, (90, 1046, 930, 1279))],
            "conceptos": [(3, (90, 763, 930, 993)), (6, (90, 1051, 930, 1281))],
            "cierre": [(2.5, (90, 690, 930, 878)), (5, (90, 925, 930, 1113))],
        }
        for at, box in reveals.get(name, []):
            phase = max(0, min(1, (elapsed-at)/.45))
            if phase < 1:
                image.paste(Image.blend(Image.new("RGB", (box[2]-box[0], box[3]-box[1]), INK), image.crop(box), phase), box[:2])
        d = ImageDraw.Draw(image)
        d.line((90, 1528, 90+840*second/DURATION, 1528), fill=LIME, width=4)
        for index in range(len(SCENES)):
            x = 90+index*94
            d.rounded_rectangle((x, 1558, x+80, 1564), radius=3, fill=LIME if index <= number else LINE)
        return image


def export(folder, storyboard_only=False):
    import imageio_ffmpeg
    folder = Path(folder)
    design = NapoHistoryDesign(folder)
    sheet = Image.new("RGB", (720, 1278), INK)
    for i, (start, end, name) in enumerate(SCENES):
        second = end-.5 if name == "mapa_historico" else (start+end)/2
        frame = design.render(second)
        frame.save(folder / f"qa_v3_{name}.jpg", quality=95)
        sheet.paste(frame.resize((240, 426)), ((i%3)*240, (i//3)*426))
    sheet.save(folder / "storyboard_v3.jpg", quality=95)
    design.render(39).save(folder / "portada_borrador_v3.jpg", quality=95)
    if storyboard_only:
        print("Historical storyboard verified:", folder.resolve())
        return
    output = folder / "napo_historia_2026_maqueta_sin_voz_v3.mp4"
    fps = 30
    writer = imageio_ffmpeg.write_frames(str(output), (WIDTH, HEIGHT), fps=fps, codec="libx264",
                                        pix_fmt_in="rgb24", pix_fmt_out="yuv420p", macro_block_size=2,
                                        quality=8, ffmpeg_log_level="error",
                                        output_params=["-movflags", "+faststart", "-preset", "veryfast", "-threads", "2"])
    writer.send(None)
    try:
        for frame in range(0, DURATION*fps, 3):
            raw = design.render(frame/fps).tobytes()
            for _ in range(3):
                writer.send(raw)
            if frame % (10*fps) == 0:
                print(f"Historical draft: {frame/fps:g}/{DURATION} seconds", flush=True)
    finally:
        writer.close()
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(output), "-f", "null", "-"], capture_output=True, check=True)
    metadata = {"status": "silent_draft_not_for_publication", "duration_seconds": DURATION,
                "width": WIDTH, "height": HEIGHT, "fps": fps, "audio": None,
                "full_decode": "passed", "scenes": SCENES,
                "sha256": sha256(output.read_bytes()).hexdigest(),
                "historical_selection": "two 1987 events described, four 2023–2025 epicenters mapped",
                "current_case": design.after["id"], "catalog_completeness": "not claimed",
                "pending": "new narration, timing and subtitles; source recheck before publication"}
    (folder / "draft_metadata_v3.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Silent historical draft verified:", output.resolve(), flush=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--storyboard-only", action="store_true")
    args = parser.parse_args()
    export(args.folder, args.storyboard_only)
