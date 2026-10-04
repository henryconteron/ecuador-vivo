"""Code-native Napo/Tena editorial storyboard with pinned IG-EPN evidence.

Exports a clearly labeled SILENT DRAFT. A new narration and real subtitle
alignment are required before publication. No seismic measurements are simulated.
"""
import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw

from export_video import WIDTH, HEIGHT, font
from reel_design import CREDIT_NAME, CREDIT_SPECIALTY

INK = "#102b28"
PANEL = "#1b3b34"
LINE = "#36594b"
PAPER = "#f1e8cd"
MUTED = "#b4c8b5"
LIME = "#c6df7e"
GOLD = "#ffcf76"
BOX = (90, 430, 930, 1225)
EXTENT = (-78.75, -76.95, -1.65, .10)
SCENES = [(0, 9, "mapa"), (9, 21, "boletines"), (21, 34, "proceso"),
          (34, 48, "profundidad"), (48, 64, "conceptos"), (64, 80, "cierre")]


def text(draw, xy, value, size=32, fill=PAPER, serif=False, width=None):
    width = width or 930 - xy[0]
    face = font(size, serif)
    if draw.textlength(value, font=face) > width:
        raise ValueError(f"Text exceeds content width: {value}")
    draw.text(xy, value, font=face, fill=fill)


def paragraph(draw, xy, value, size=32, width=760, fill=MUTED, leading=1.28):
    lines = []
    current = ""
    for word in value.split():
        trial = (current + " " + word).strip()
        if current and draw.textlength(trial, font=font(size)) > width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    for index, line in enumerate(lines):
        text(draw, (xy[0], xy[1] + index * round(size * leading)), line, size, fill, width=width)
    return xy[1] + len(lines) * round(size * leading)


def card(draw, box, accent=LIME):
    draw.rounded_rectangle(box, radius=24, fill=PANEL, outline=LINE, width=2)
    draw.line((box[0]+24, box[1]+20, box[0]+24, box[3]-20), fill=accent, width=4)


def project(lon, lat):
    west, east, south, north = EXTENT
    x0, y0, x1, y1 = BOX
    return (x0+(lon-west)/(east-west)*(x1-x0), y0+(north-lat)/(north-south)*(y1-y0))


def depth_y(depth, top=650, bottom=1130):
    if not math.isfinite(depth) or not 0 <= depth <= 30:
        raise ValueError("Depth is outside the fixed 0–30 km axis")
    return top+depth/30*(bottom-top)


class TerritoryDesign:
    def __init__(self, folder):
        self.folder = Path(folder)
        self.audit = json.loads((self.folder / "source_audit.json").read_text(encoding="utf-8"))
        boundaries = self.folder / "ecuador_adm1_reference.geojson"
        evidence = self.folder / "igepn_official_case.html"
        if sha256(boundaries.read_bytes()).hexdigest() != self.audit["boundary_sha256"]:
            raise ValueError("Boundary evidence hash mismatch")
        if sha256(evidence.read_bytes()).hexdigest() != self.audit["evidence_sha256"]:
            raise ValueError("Official evidence hash mismatch")
        from prepare_territory import BulletinParser, parse_bulletin
        parser = BulletinParser()
        parser.feed(evidence.read_text(encoding="utf-8"))
        cases = [parse_bulletin(m) for m in parser.messages if self.audit["case_id"] in m["text"]]
        saved = json.loads((self.folder / "igepn_2026_case.json").read_text(encoding="utf-8"))
        if {r["status"]: r for r in cases} != {r["status"]: r for r in saved}:
            raise ValueError("Case values differ from the official source snapshot")
        if len(cases) != 2 or len({r["id"] for r in cases}) != 1:
            raise ValueError("Expected two versions of one earthquake")
        self.before = next(r for r in cases if r["status"] == "PRELIMINAR")
        self.after = next(r for r in cases if r["status"] == "REVISADO")
        if any(not 0 <= r["depth_km"] <= 30 for r in cases):
            raise ValueError("Extend the fixed depth axes for this case")
        self.features = json.loads(boundaries.read_text(encoding="utf-8"))["features"]
        self.cache = {}

    def shell(self, number, title, subtitle):
        image = Image.new("RGB", (WIDTH, HEIGHT), INK)
        d = ImageDraw.Draw(image)
        # Decorative editorial geometry, not topographic contours or seismic signals.
        for y in range(95, 1600, 125):
            d.line((65, y, 957, y), fill="#15322d", width=1)
        text(d, (90, 145), "ANDES PULSO", 27, LIME)
        text(d, (90, 195), "MEMORIA SÍSMICA / 01 · TENA Y SU ENTORNO", 24, MUTED)
        text(d, (90, 256), title, 60, PAPER, True)
        text(d, (90, 341), subtitle, 27, MUTED)
        text(d, (90, 1615), CREDIT_NAME, 28)
        text(d, (90, 1657), CREDIT_SPECIALTY, 23, MUTED)
        text(d, (90, 1700), "BORRADOR VISUAL · SIN LOCUCIÓN · NO PUBLICAR", 22, GOLD)
        for index in range(6):
            x = 90+index*142
            d.rounded_rectangle((x, 1558, x+126, 1564), radius=3,
                                fill=LIME if index <= number else LINE)
        return image

    def map_image(self):
        result = self.shell(0, "Este dato cambió.", "16 JUN 2026 · IG-EPN · un caso real, no sismicidad en vivo")
        d = ImageDraw.Draw(result)
        surface = Image.new("RGB", (BOX[2]-BOX[0], BOX[3]-BOX[1]), "#243d33")
        land = ImageDraw.Draw(surface)
        for feature in self.features:
            name = feature["properties"]["shapeName"]
            geometry = feature["geometry"]
            polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
            for polygon in polygons:
                points = [(project(lon, lat)[0]-BOX[0], project(lon, lat)[1]-BOX[1]) for lon, lat in polygon[0]]
                land.polygon(points, fill="#507749" if name == "Napo" else "#28483c",
                             outline=LIME if name == "Napo" else "#668268", width=3 if name == "Napo" else 1)
                for hole in polygon[1:]:
                    land.polygon([(project(lon, lat)[0]-BOX[0], project(lon, lat)[1]-BOX[1]) for lon, lat in hole], fill="#243d33")
        result.paste(surface, BOX[:2])
        d.rectangle(BOX, outline=LINE, width=2)
        for lon in (-78.5, -78, -77.5):
            x, _ = project(lon, 0)
            d.line((x, BOX[1], x, BOX[3]), fill="#55725a", width=1)
            text(d, (x-35, 1236), f"{abs(lon):g}° O", 22)
        for lat in (-.5, -1, -1.5):
            _, y = project(-78, lat)
            d.line((BOX[0], y, BOX[2], y), fill="#55725a", width=1)
        text(d, (690, 477), "N ↑", 27, LIME)
        text(d, (490, 700), "NAPO", 50, PAPER, True)
        text(d, (126, 535), "PICHINCHA", 22, MUTED)
        text(d, (699, 565), "ORELLANA", 22, MUTED)
        text(d, (690, 1155), "PASTAZA", 22, MUTED)
        row = self.after
        x, y = project(row["longitude"], row["latitude"])
        d.ellipse((x-13, y-13, x+13, y+13), fill=GOLD, outline=PAPER, width=2)
        d.line((x+17, y, x+53, y, x+53, y-63), fill=PAPER, width=2)
        text(d, (x+65, y-96), "Epicentro", 27)
        text(d, (x+65, y-60), "revisado", 27, GOLD)
        text(d, (120, 1269), "Punto = epicentro; no área de daños", 27, GOLD)
        text(d, (120, 1310), "Napo resaltado = referencia territorial, no peligro", 23, MUTED)
        text(d, (120, 1348), "Límites: geoBoundaries · referencia 2011", 22, MUTED)
        card(d, (90, 1390, 930, 1514), GOLD)
        text(d, (130, 1410), "¿Cambió el sismo…", 36, PAPER, True)
        text(d, (130, 1460), "o cambió lo que sabemos de él?", 36, GOLD, True)
        return result

    def bulletins(self):
        image = self.shell(1, "Un sismo. Dos boletines.", "Mismo ID: igepn2026lsvn · valores de cada versión")
        d = ImageDraw.Draw(image)
        for row, y, color in [(self.before, 455, MUTED), (self.after, 885, LIME)]:
            card(d, (90, y, 930, y+375), color)
            text(d, (135, y+32), row["status"], 31, color)
            value = f"{row['depth_km']:g}"
            text(d, (130, y+95), value, 134, PAPER, True)
            text(d, (390, y+177), "km de profundidad", 32, color)
            text(d, (135, y+297), f"Magnitud publicada: {row['magnitude']:.1f} M".replace(".", ","), 31, MUTED)
        paragraph(d, (110, 1345), "Cambió la estimación. No son dos terremotos ni un foco que se desplazó.", 36, 780, GOLD)
        return image

    def process(self):
        image = self.shell(2, "No vemos la ruptura.", "La localizamos a partir de señales registradas")
        d = ImageDraw.Draw(image)
        for i, (heading, detail) in enumerate([
            ("REGISTRAR", "Los instrumentos registran el movimiento del suelo."),
            ("ESTIMAR", "El análisis permite calcular dónde comenzó la ruptura."),
            ("REVISAR", "Al revisar los datos, una solución puede ajustarse.")]):
            y = 470+i*288
            card(d, (90, y, 930, y+233))
            text(d, (130, y+29), f"0{i+1}", 47, LIME, True)
            text(d, (245, y+33), heading, 35)
            paragraph(d, (245, y+99), detail, 31, 620)
        card(d, (90, 1380, 930, 1514), GOLD)
        paragraph(d, (130, 1406), "Proceso conceptual: no son señales medidas de este evento.", 30, 740, GOLD)
        return image

    def depth(self):
        image = self.shell(3, "Epicentro ≠ hipocentro.", "Dos estimaciones · ejes fijos de profundidad: 0–30 km")
        d = ImageDraw.Draw(image)
        for row, x, color in [(self.before, 90, MUTED), (self.after, 530, LIME)]:
            card(d, (x, 475, x+400, 1220), color)
            text(d, (x+47, 510), row["status"], 26, color, width=340)
            text(d, (x+48, 570), "SUPERFICIE", 24, MUTED, width=340)
            top, bottom = 650, 1130
            d.line((x+70, top, x+355, top), fill=PAPER, width=3)
            for km in (0, 10, 20, 30):
                y = top+km/30*(bottom-top)
                d.line((x+70, y, x+355, y), fill=LINE, width=1)
                text(d, (x+38, y+5), str(km), 21, MUTED, width=320)
            cx = x+212
            hy = depth_y(row["depth_km"], top, bottom)
            for y in range(top+15, round(hy)-20, 22):
                d.line((cx, y, cx, min(y+10, hy-20)), fill=color, width=3)
            d.ellipse((cx-10, top-10, cx+10, top+10), fill=PAPER)
            d.ellipse((cx-14, hy-14, cx+14, hy+14), fill=GOLD, outline=PAPER, width=2)
            text(d, (x+252, hy-15), f"{row['depth_km']:g} km", 28, GOLD, width=130)
        paragraph(d, (110, 1270), "Arriba: epicentro. Abajo: hipocentro, donde comenzó la ruptura.", 35, 780, PAPER)
        paragraph(d, (110, 1390), "Esquemas de profundidad, no cortes de la falla ni un foco en movimiento.", 29, 780, MUTED)
        return image

    def concepts(self):
        image = self.shell(4, "El punto no lo dice todo.", "Tres conceptos que conviene separar")
        d = ImageDraw.Draw(image)
        for i, (heading, detail, color) in enumerate([
            ("MAGNITUD", "Describe el tamaño del sismo.", GOLD),
            ("INTENSIDAD", "Describe la sacudida en un lugar; puede variar entre sitios.", LIME),
            ("DAÑO", "También depende de la vulnerabilidad de las construcciones.", PAPER)]):
            y = 475+i*288
            card(d, (90, y, 930, y+230), color)
            text(d, (135, y+35), heading, 43, color, True)
            paragraph(d, (135, y+112), detail, 34, 735)
        paragraph(d, (110, 1380), "No mostramos intensidades ni daños medidos en Tena para este caso.", 30, 780, MUTED)
        return image

    def closing(self):
        image = self.shell(5, "Lee mejor el boletín.", "Cambió el reporte, no el sismo.")
        d = ImageDraw.Draw(image)
        for i, (title, detail) in enumerate([
            ("FECHA", "¿Cuándo ocurrió? Este caso: 16/06/2026."),
            ("FUENTE", "Busca el boletín original del IG-EPN."),
            ("ESTADO", "¿Dice preliminar o revisado?")]):
            y = 455+i*235
            card(d, (90, y, 930, y+188))
            text(d, (135, y+22), title, 36, LIME)
            paragraph(d, (135, y+89), detail, 30, 735)
        text(d, (110, 1220), "Entender para prepararnos.", 49, GOLD, True)
        paragraph(d, (110, 1320), "Caso: IG-EPN · boletines oficiales 11946 y 11947. Conceptos: USGS. Mapa: geoBoundaries.", 29, 780)
        paragraph(d, (110, 1430), "Un caso de 2026, no un catálogo completo ni una predicción.", 29, 780, GOLD)
        return image

    def render(self, second):
        number = next(i for i, (start, end, _) in enumerate(SCENES) if start <= second < end)
        if number not in self.cache:
            self.cache[number] = [self.map_image, self.bulletins, self.process, self.depth, self.concepts, self.closing][number]()
        image = self.cache[number].copy()
        d = ImageDraw.Draw(image)
        start = SCENES[number][0]
        elapsed = second-start
        # Editorial reveals only: estimated coordinates/depths never move.
        reveal_boxes = {
            1: [(3.0, (90, 885, 930, 1260)), (6.0, (90, 1330, 930, 1500))],
            2: [(3.0, (90, 758, 930, 991)), (6.0, (90, 1046, 930, 1279))],
            4: [(3.0, (90, 763, 930, 993)), (6.0, (90, 1051, 930, 1281))],
            5: [(2.5, (90, 690, 930, 878)), (5.0, (90, 925, 930, 1113))],
        }
        for reveal_at, box in reveal_boxes.get(number, []):
            phase = max(0, min(1, (elapsed-reveal_at)/.45))
            if phase < 1:
                image.paste(Image.blend(Image.new("RGB", (box[2]-box[0], box[3]-box[1]), INK),
                                        image.crop(box), phase), box[:2])
        # A reading-progress indicator is editorial, never a seismic waveform.
        d = ImageDraw.Draw(image)
        d.line((90, 1528, 90+840*second/80, 1528), fill=LIME, width=4)
        return image


def export(folder, preview=True):
    import imageio_ffmpeg
    folder = Path(folder)
    design = TerritoryDesign(folder)
    for start, end, name in SCENES:
        design.render((start+end)/2).save(folder / f"qa_{name}.jpg", quality=95)
    sheet = Image.new("RGB", (720, 1280), INK)
    for number, (start, end, _) in enumerate(SCENES):
        sheet.paste(design.render((start+end)/2).resize((240, 426)), ((number % 3)*240, (number//3)*426))
    sheet = sheet.crop((0, 0, 720, 852))
    sheet.save(folder / "storyboard.jpg", quality=95)
    design.render(13).save(folder / "portada_borrador.jpg", quality=96)
    if not preview:
        print("Storyboard exported:", folder.resolve())
        return
    output = folder / "napo_tena_maqueta_sin_voz_v2.mp4"
    fps = 30
    writer = imageio_ffmpeg.write_frames(str(output), (WIDTH, HEIGHT), fps=fps, codec="libx264",
                                       pix_fmt_in="rgb24", pix_fmt_out="yuv420p", macro_block_size=2,
                                       quality=8, ffmpeg_log_level="error",
                                       output_params=["-movflags", "+faststart", "-preset", "veryfast", "-threads", "2"])
    writer.send(None)
    try:
        for frame in range(0, 80*fps, 3):
            rendered = design.render(frame/fps).tobytes()
            for _ in range(3):
                writer.send(rendered)
            if frame % (10*fps) == 0:
                print(f"Draft rendered: {frame/fps:g}/80 seconds", flush=True)
    finally:
        writer.close()
    # Full decode, not just a successful encoder exit.
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(output),
                    "-f", "null", "-"], capture_output=True, check=True)
    result = {"status": "silent_visual_draft_not_for_publication", "width": WIDTH, "height": HEIGHT,
              "duration_seconds": 80, "fps": fps, "frames_expected": 2400,
              "full_decode": "passed", "audio": None, "subtitle_alignment": "pending_new_voice",
              "scientific_data": "two official bulletin versions of one IG-EPN event",
              "animation": "editorial panel reveals; no moving or pulsing scientific symbols",
              "case_id": design.after["id"], "sha256": sha256(output.read_bytes()).hexdigest(),
              "scenes": SCENES, "credit": CREDIT_NAME+", "+CREDIT_SPECIALTY.lower()}
    (folder / "draft_metadata_v2.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Silent draft verified:", output.resolve(), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--storyboard-only", action="store_true")
    args = parser.parse_args()
    export(args.folder, not args.storyboard_only)
