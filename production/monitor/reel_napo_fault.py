"""Map-first territorial reel: historical cases → 2026 → Tena → fault concept.

Maps contain source-pinned points. Moving blocks belong only to a labeled
conceptual diagram, never a reconstruction of a named local fault or earthquake.
"""
from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw

from prepare_napo_history import load_history
from prepare_napo_fault import load_fault_evidence
from export_video import font
from reel_territory import (TerritoryDesign, BOX, EXTENT, WIDTH, HEIGHT, INK,
                            PANEL, LINE, MUTED, GOLD, LIME, PAPER, text, paragraph, card)

CITY = "#9dd7dc"
ZOOM_EXTENT = (-78.18, -77.45, -1.34, -.67)
SCENES = [(0, 18, "mapa_historico"), (18, 24, "pregunta_2026"),
          (24, 34, "mapa_2026"), (34, 40, "zoom_tena"),
          (40, 53, "que_es_falla"), (53, 67, "bloqueo"),
          (67, 79, "deslizamiento"), (79, 89, "contexto_local"), (89, 100, "cierre")]
DURATION = SCENES[-1][1]


def clamp(value):
    return max(0., min(1., value))


def smooth(value):
    value = clamp(value)
    return value*value*(3-2*value)


def viewport(phase):
    phase = smooth(phase)
    return tuple(a+(b-a)*phase for a, b in zip(EXTENT, ZOOM_EXTENT))


def locate(lon, lat, extent=EXTENT):
    west, east, south, north = extent
    return (BOX[0]+(lon-west)/(east-west)*(BOX[2]-BOX[0]),
            BOX[1]+(north-lat)/(north-south)*(BOX[3]-BOX[1]))


def schematic_slip(second):
    """Illustrative displacement in pixels: NOT a local measurement or timescale."""
    return 52*smooth((second-2)/.6)


def arrow(d, start, end, color, width=6):
    d.line((*start, *end), fill=color, width=width)
    angle = math.atan2(end[1]-start[1], end[0]-start[0])
    points = [end] + [(end[0]-20*math.cos(angle+a), end[1]-20*math.sin(angle+a)) for a in (-.5, .5)]
    d.polygon(points, fill=color)


class NapoFaultDesign(TerritoryDesign):
    def __init__(self, folder):
        super().__init__(folder)
        self.history = [r for r in load_history(folder) if r["latitude"] is not None]
        self.cities, second = load_fault_evidence(folder)
        self.current = [self.after, second]
        self.map_cache = {}

    def shell(self, number, title, subtitle):
        image = super().shell(0, title, subtitle)
        d = ImageDraw.Draw(image)
        d.rectangle((80, 190, 945, 240), fill=INK)
        text(d, (90, 195), "MEMORIA SÍSMICA / 01 · NAPO: BAJO EL MAPA", 24, MUTED)
        d.rectangle((80, 1545, 945, 1580), fill=INK)
        return image

    def base_map(self, extent):
        key = tuple(round(v, 6) for v in extent)
        if key in self.map_cache:
            return self.map_cache[key].copy()
        surface = Image.new("RGB", (BOX[2]-BOX[0], BOX[3]-BOX[1]), "#243d33")
        d = ImageDraw.Draw(surface)
        for feature in self.features:
            napo = feature["properties"]["shapeName"] == "Napo"
            geometry = feature["geometry"]
            polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
            for polygon in polygons:
                def relative(ring):
                    return [(locate(lon, lat, extent)[0]-BOX[0], locate(lon, lat, extent)[1]-BOX[1]) for lon, lat in ring]
                d.polygon(relative(polygon[0]), fill="#507749" if napo else "#28483c",
                          outline=LIME if napo else "#668268", width=3 if napo else 1)
                for hole in polygon[1:]:
                    d.polygon(relative(hole), fill="#243d33")
        self.map_cache[key] = surface
        return surface.copy()

    def city_points(self, image, extent):
        d = ImageDraw.Draw(image)
        offsets = {"Tena": (17, 13), "Archidona": (17, -35), "Baeza": (17, -18), "El Chaco": (17, -18)}
        for row in self.cities:
            x, y = locate(row["longitude"], row["latitude"], extent)
            if not BOX[0]+12 <= x <= BOX[2]-170 or not BOX[1]+35 <= y <= BOX[3]-45:
                continue
            d.polygon([(x, y-7), (x+7, y), (x, y+7), (x-7, y)], fill=CITY, outline=INK)
            dx, dy = offsets[row["name"]]
            face = font(26)
            label_box = d.textbbox((x+dx, y+dy), row["name"], font=face)
            d.rounded_rectangle((label_box[0]-5, label_box[1]-3, label_box[2]+5, label_box[3]+4), radius=4, fill=INK)
            text(d, (x+dx, y+dy), row["name"], 26, CITY)

    def legend(self, d):
        d.ellipse((112, 1252, 128, 1268), fill=GOLD, outline=PAPER, width=1)
        text(d, (144, 1243), "Epicentro", 27, GOLD)
        d.polygon([(450, 1252), (458, 1260), (450, 1268), (442, 1260)], fill=CITY)
        text(d, (473, 1243), "Localidad de referencia", 27, CITY)
        text(d, (110, 1287), "Símbolos fijos: no magnitud, sacudida ni daños", 24, MUTED)

    def map_frame(self, name, elapsed):
        is_history = name == "mapa_historico"
        zoom = name == "zoom_tena"
        extent = viewport(elapsed/3.6) if zoom else EXTENT
        title = "Napo también tiembla." if is_history else "Tena: bajo el mapa." if zoom else "2026: sí hay registros."
        subtitle = "2023–2025 · casos seleccionados del IG-EPN, no catálogo completo" if is_history else "Acercamiento geográfico · no ampliación de una zona de daño" if zoom else "Dos casos revisados · selección, no todos los sismos de 2026"
        image = self.shell(0, title, subtitle)
        image.paste(self.base_map(extent), BOX[:2])
        d = ImageDraw.Draw(image)
        d.rectangle(BOX, outline=LINE, width=2)
        text(d, (825, 455), "N ↑", 27, LIME, width=90)
        if not zoom:
            text(d, (690, 1030), "NAPO", 42, PAPER, True)
        self.city_points(image, extent)
        d = ImageDraw.Draw(image)
        if is_history:
            count = min(4, int(elapsed//4.5)+1)
            rows = self.history[:count]
        elif zoom:
            rows = self.current
        else:
            rows = self.current[:min(2, int(elapsed//5)+1)]
        offsets = [(35, -38), (-90, -10), (-75, 40), (36, -38)] if is_history else [(45, 24), (-45, 35)]
        for index, row in enumerate(rows):
            x, y = locate(row["longitude"], row["latitude"], extent)
            d.ellipse((x-9, y-9, x+9, y+9), fill=GOLD, outline=PAPER, width=2)
            dx, dy = offsets[index]
            d.line((x+dx*.2, y+dy*.2, x+dx, y+dy), fill=PAPER, width=2)
            d.ellipse((x+dx-17, y+dy-17, x+dx+17, y+dy+17), fill=INK, outline=GOLD, width=2)
            text(d, (x+dx-7, y+dy-14), str(index+1), 22, GOLD, width=30)
        # Approximate ground-distance scale; changes with viewport, not with data.
        lat = (extent[2]+extent[3])/2
        length = 20/(111.32*math.cos(math.radians(lat)))/(extent[1]-extent[0])*(BOX[2]-BOX[0])
        d.line((120, 1187, 120+length, 1187), fill=PAPER, width=3)
        text(d, (120, 1154), "≈ 20 km", 22, PAPER)
        self.legend(d)
        card(d, (90, 1330, 930, 1465), GOLD)
        if zoom:
            text(d, (130, 1347), "Nos detenemos en Tena.", 38, PAPER, True)
            text(d, (130, 1405), "¿Qué ocurre cuando se mueve una falla?", 29, GOLD)
        else:
            row = rows[-1]
            date = "/".join(reversed(row.get("date", row.get("local_time", "")[:10]).split("-")))
            text(d, (130, 1348), f"{len(rows):02d} / {date} · {row['magnitude']:g} {row.get('type', row.get('magnitude_type'))}".replace(".", ","), 38, PAPER, True)
            detail = f"Profundidad: {row['depth_km']:g} km · informe IG-EPN" if is_history else "Boletín revisado · cerca de Tena · IG-EPN"
            text(d, (130, 1405), detail.replace(".", ","), 28, MUTED)
        text(d, (110, 1486), "Límites: geoBoundaries 2011 · localidades: GeoNames", 23, MUTED)
        return image

    def question(self):
        image = self.shell(1, "¿Y en 2026?", "Del mapa histórico a los reportes de este año")
        d = ImageDraw.Draw(image)
        text(d, (110, 535), "2026", 195, GOLD, True)
        card(d, (90, 855, 930, 1260), LIME)
        paragraph(d, (135, 920), "¿Se sigue moviendo la Tierra en Napo?", 66, 720, PAPER)
        paragraph(d, (110, 1370), "Veamos los registros. Luego, qué ocurre bajo el mapa.", 34, 780, MUTED)
        return image

    def rock_diagram(self, image, offset=0, strain=0, waves=False):
        d = ImageDraw.Draw(image)
        box = (135, 500, 890, 1130)
        d.rectangle(box, fill="#283f37", outline=LINE, width=2)
        cx = 510
        d.rectangle((135, 500, cx, 1130), fill="#3b5e46")
        d.rectangle((cx, 500, 890, 1130), fill="#254a48")
        # Marker lines are features in two conceptual rock blocks, not real roads.
        for y in (680, 850, 1010):
            left = [(x, y-offset-strain*45*(cx-x)/(cx-135)) for x in range(135, cx+1, 5)]
            right = [(x, y+offset+strain*45*(x-cx)/(890-cx)) for x in range(cx, 891, 5)]
            d.line(left, fill="#9ab580", width=7)
            d.line(right, fill="#7eafb0", width=7)
        d.line((cx, 500, cx, 1130), fill=GOLD, width=5)
        text(d, (170, 533), "BLOQUE A", 28, PAPER)
        text(d, (665, 533), "BLOQUE B", 28, PAPER)
        arrow(d, (255, 900), (255, 755), PAPER)
        arrow(d, (760, 755), (760, 900), PAPER)
        if waves:
            for radius in (85, 160, 245):
                d.arc((cx-radius, 850-radius, cx+radius, 850+radius), 120, 240, fill=GOLD, width=3)
                d.arc((cx-radius, 850-radius, cx+radius, 850+radius), -60, 60, fill=GOLD, width=3)
        text(d, (550, 1160), "Traza de falla", 30, GOLD)
        d.line((cx, 1130, cx, 1184, 533, 1184), fill=GOLD, width=2)
        text(d, (135, 1210), "Vista desde arriba · ejemplo de deslizamiento lateral", 26, MUTED)
        text(d, (135, 1248), "Esquema sin escala · NO representa una falla de Tena", 25, MUTED)

    def fault_frame(self, name, elapsed):
        if name == "que_es_falla":
            title, subtitle = "¿Qué es una falla?", "No basta con que una roca tenga una grieta"
            heading, detail = "FRACTURA + DESPLAZAMIENTO", "Una fractura o zona de fracturas donde bloques de roca se han desplazado entre sí."
            offset, strain = 40*smooth((elapsed-3)/1), 0
        elif name == "bloqueo":
            title, subtitle = "No siempre desliza.", "La fricción puede mantener bloqueada una parte de la falla"
            heading, detail = "EL ESFUERZO PUEDE ACUMULARSE", "Mientras continúa el movimiento tectónico, las rocas pueden deformarse sin deslizar en ese tramo."
            offset, strain = 0, smooth(elapsed/9)
        else:
            title, subtitle = "Cuando desliza de golpe.", "Parte de la energía acumulada se propaga como ondas sísmicas"
            heading, detail = "DESLIZAMIENTO REPENTINO → SISMO", "Hay desplazamiento a lo largo de la falla: no necesariamente una abertura gigante en la superficie."
            offset = schematic_slip(elapsed)
            strain = 1-clamp(offset/52)
        image = self.shell(4, title, subtitle)
        self.rock_diagram(image, offset, strain, name == "deslizamiento" and elapsed >= 2.6)
        d = ImageDraw.Draw(image)
        card(d, (90, 1300, 930, 1489), GOLD)
        text(d, (130, 1324), heading, 30, GOLD)
        paragraph(d, (130, 1380), detail, 29, 740, PAPER)
        return image

    def local_context(self):
        image = self.shell(7, "¿Y cerca de Tena?", "El contexto local necesita evidencia, no una línea inventada")
        d = ImageDraw.Draw(image)
        card(d, (90, 450, 930, 810), GOLD)
        text(d, (135, 485), "CASOS DE 2025", 35, GOLD)
        paragraph(d, (135, 563), "Para los sismos de enero y junio, el IG-EPN describe movimiento relacionado con el límite del bloque Norandino.", 38, 725, PAPER)
        card(d, (90, 855, 930, 1188), LIME)
        text(d, (135, 890), "SISTEMA DE FALLAS", 34, LIME)
        paragraph(d, (135, 968), "Chingual · Cosanga · Pallatanga · Puná", 43, 715, PAPER)
        paragraph(d, (110, 1255), "Eso no asigna automáticamente los casos de 2026 a una falla concreta.", 37, 780, GOLD)
        paragraph(d, (110, 1400), "Fuente: IG-EPN · informes 2025-002 y 2025-007. No dibujamos aquí su traza geológica.", 29, 780, MUTED)
        return image

    def closing_fault(self):
        image = self.shell(8, "Una falla no es una fecha.", "Entender el mecanismo ayuda; no predice el próximo sismo")
        d = ImageDraw.Draw(image)
        for i, (heading, detail) in enumerate([
            ("FALLA", "Una fractura o zona de fracturas con desplazamiento."),
            ("SISMO", "Un deslizamiento repentino puede liberar energía en ondas."),
            ("SIN PREDICCIÓN", "Este mapa no anuncia cuándo ocurrirá el próximo.")]):
            y = 460+i*278
            card(d, (90, y, 930, y+232), GOLD if i==0 else LIME)
            text(d, (135, y+28), heading, 37, GOLD if i==0 else LIME)
            paragraph(d, (135, y+104), detail, 33, 735, PAPER)
        text(d, (110, 1340), "Entender para prepararnos.", 46, GOLD, True)
        paragraph(d, (110, 1420), "Datos: IG-EPN · conceptos: USGS · mapa: geoBoundaries · localidades: GeoNames. Esquemas propios.", 27, 780, MUTED)
        return image

    def render(self, second):
        number = next(i for i, (start, end, _) in enumerate(SCENES) if start <= second < end)
        name = SCENES[number][2]
        elapsed = second-SCENES[number][0]
        if name.startswith("mapa") or name == "zoom_tena":
            phase = math.floor(elapsed*10)/10
            key = (name, min(3, int(elapsed//4.5)) if name == "mapa_historico" else min(1, int(elapsed//5)) if name == "mapa_2026" else min(3.6, phase))
            if key not in self.cache:
                self.cache[key] = self.map_frame(name, phase)
            image = self.cache[key].copy()
        elif name in ("que_es_falla", "bloqueo", "deslizamiento"):
            image = self.fault_frame(name, elapsed)
        else:
            if name not in self.cache:
                self.cache[name] = {"pregunta_2026": self.question, "contexto_local": self.local_context, "cierre": self.closing_fault}[name]()
            image = self.cache[name].copy()
        d = ImageDraw.Draw(image)
        d.line((90, 1528, 90+840*second/DURATION, 1528), fill=LIME, width=4)
        for index in range(len(SCENES)):
            x = 90+index*94
            d.rounded_rectangle((x, 1558, x+80, 1564), radius=3, fill=LIME if index <= number else LINE)
        return image


def export(folder, storyboard_only=False):
    import imageio_ffmpeg
    folder = Path(folder)
    design = NapoFaultDesign(folder)
    sheet = Image.new("RGB", (720, 1278), INK)
    for i, (start, end, name) in enumerate(SCENES):
        second = end-.5 if name in ("mapa_historico", "zoom_tena") else (start+end)/2
        frame = design.render(second)
        frame.save(folder / f"qa_v4_{name}.jpg", quality=95)
        sheet.paste(frame.resize((240, 426)), ((i%3)*240, (i//3)*426))
    sheet.save(folder / "storyboard_v4.jpg", quality=95)
    design.render(17.5).save(folder / "portada_borrador_v4.jpg", quality=95)
    if storyboard_only:
        print("Map-first fault storyboard exported:", folder.resolve())
        return
    output = folder / "napo_mapa_tena_fallas_maqueta_sin_voz_v4.mp4"
    writer = imageio_ffmpeg.write_frames(str(output), (WIDTH, HEIGHT), fps=30, codec="libx264",
                                        pix_fmt_in="rgb24", pix_fmt_out="yuv420p", macro_block_size=2,
                                        quality=8, ffmpeg_log_level="error",
                                        output_params=["-movflags", "+faststart", "-preset", "veryfast", "-threads", "2"])
    writer.send(None)
    try:
        for frame in range(0, DURATION*30, 3):
            raw = design.render(frame/30).tobytes()
            for _ in range(3):
                writer.send(raw)
            if frame % 300 == 0:
                print(f"Fault reel draft: {frame/30:g}/{DURATION} seconds", flush=True)
    finally:
        writer.close()
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(output), "-f", "null", "-"], capture_output=True, check=True)
    metadata = {"status": "silent_draft_not_for_publication", "duration_seconds": DURATION,
                "width": WIDTH, "height": HEIGHT, "fps": 30, "audio": None,
                "full_decode": "passed", "scenes": SCENES, "sha256": sha256(output.read_bytes()).hexdigest(),
                "opening": "historical map from frame zero; city diamonds distinct from epicenter circles",
                "history": "four selected 2023–2025 IG-EPN cases; no complete catalog claim",
                "current": [r["id"] for r in design.current],
                "zoom": "viewport changes, geographic source coordinates never change",
                "fault": "conceptual strike-slip diagram, not a Tena fault trace or 2026 reconstruction",
                "local_context": "2025-002 and 2025-007 reports, not fault assignment for 2026",
                "pending": "new narration, synchronization and subtitles; final review before publication"}
    (folder / "draft_metadata_v4.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Silent map-first fault draft verified:", output.resolve(), flush=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--storyboard-only", action="store_true")
    args = parser.parse_args()
    export(args.folder, args.storyboard_only)
