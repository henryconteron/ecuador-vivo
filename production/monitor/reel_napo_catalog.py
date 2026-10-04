"""Map-first 1900–2025 USGS / 2026 IG-EPN reel with original 3D fault examples."""
from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw

from prepare_napo_catalog import REGION, load_catalog
from prepare_napo_fault import load_fault_evidence
from fault_blocks import render_blocks
from reel_napo_fault import NapoFaultDesign, ZOOM_EXTENT, locate, smooth
from reel_territory import TerritoryDesign, WIDTH, HEIGHT, BOX, INK, LINE, PAPER, GOLD, LIME, MUTED, text, paragraph, card

SCENES = [(0, 24, "mapa_historico"), (24, 30, "pregunta_2026"), (30, 40, "mapa_2026"),
          (40, 46, "zoom_tena"), (46, 58, "que_es_falla"), (58, 69, "bloqueo"),
          (69, 79, "deslizamiento"), (79, 89, "normal"), (89, 99, "inversa"),
          (99, 109, "desgarre"), (109, 119, "contexto_local"), (119, 131, "cierre")]
DURATION = SCENES[-1][1]


def historical_year(elapsed):
    if elapsed < 4:
        return min(1955, 1900+math.floor(max(0, elapsed)/4*55))
    if elapsed < 10:
        return 1955+math.floor((elapsed-4)/6*32)
    if elapsed < 12:
        return 1987
    if elapsed < 20:
        return min(2025, 1988+math.floor((elapsed-12)/8*38))
    return 2025


def camera(phase):
    phase = smooth(phase)
    return tuple(a+(b-a)*phase for a, b in zip(REGION, ZOOM_EXTENT))


class CatalogFaultDesign(NapoFaultDesign):
    def __init__(self, folder):
        TerritoryDesign.__init__(self, folder)
        self.history, self.history_audit = load_catalog(folder)
        self.cities, second = load_fault_evidence(folder)
        self.current = [self.after, second]
        self.map_cache, self.static = {}, {}
        if any(r["utc_time"] < "2026-01-01" for r in self.current):
            raise ValueError("Current IG-EPN scenes must not overlap historical USGS period")

    def map_frame_v5(self, name, elapsed):
        historic, zoom = name == "mapa_historico", name == "zoom_tena"
        extent = camera(elapsed/3.6) if zoom else REGION
        title = "Napo y su entorno." if historic else "Tena: bajo el mapa." if zoom else "2026: sí hay registros."
        subtitle = "USGS · consulta 1900–2025 · magnitud publicada ≥ 4" if historic else "Acercamiento geográfico · no ampliación de una zona de daño" if zoom else "IG-EPN · dos boletines revisados, no todo el catálogo de 2026"
        image = self.shell(0, title, subtitle)
        image.paste(self.base_map(extent), BOX[:2])
        d = ImageDraw.Draw(image)
        if historic:
            year = historical_year(elapsed)
            rows = [r for r in self.history if r["year"] <= year]
            for row in rows:
                x, y = locate(row["longitude"], row["latitude"], extent)
                d.ellipse((x-5, y-5, x+5, y+5), fill=GOLD, outline="#263c31", width=1)
            if year == 1987:
                main = next(r for r in rows if r["id"] == "usp000330w")
                x, y = locate(main["longitude"], main["latitude"], extent)
                # Highlight an identified historical case; ring is not damage or wave propagation.
                d.ellipse((x-13, y-13, x+13, y+13), outline=PAPER, width=3)
            d.rounded_rectangle((110, 447, 367, 577), radius=16, fill=INK)
            text(d, (125, 455), str(year), 83, GOLD, True)
        else:
            rows = self.current if zoom else self.current[:min(2, int(elapsed//5)+1)]
            for index, row in enumerate(rows):
                x, y = locate(row["longitude"], row["latitude"], extent)
                d.ellipse((x-9, y-9, x+9, y+9), fill=GOLD, outline=PAPER, width=2)
                dx, dy = [(45, 24), (-45, 35)][index]
                d.line((x+dx*.2, y+dy*.2, x+dx, y+dy), fill=PAPER, width=2)
                d.ellipse((x+dx-17, y+dy-17, x+dx+17, y+dy+17), fill=INK, outline=GOLD, width=2)
                text(d, (x+dx-7, y+dy-14), str(index+1), 22, GOLD, width=30)
        self.city_points(image, extent)
        d = ImageDraw.Draw(image)
        d.rectangle(BOX, outline=LINE, width=2)
        text(d, (825, 455), "N ↑", 27, LIME, width=90)
        lat = (extent[2]+extent[3])/2
        length = 20/(111.32*math.cos(math.radians(lat)))/(extent[1]-extent[0])*(BOX[2]-BOX[0])
        d.line((120, 1187, 120+length, 1187), fill=PAPER, width=3)
        text(d, (120, 1154), "≈ 20 km", 22, PAPER)
        self.legend(d)
        card(d, (90, 1330, 930, 1465), GOLD)
        if historic:
            text(d, (130, 1347), f"{len(rows)} registros acumulados · USGS", 35, PAPER, True)
            if year < 1927:
                detail = "Sin registros aquí ≠ ausencia de sismos."
            elif year == 1987:
                detail = "05 MAR, hora local · caso resaltado: 7,2 mw"
            else:
                detail = "Ventana regional: también incluye provincias vecinas."
            text(d, (130, 1405), detail, 27, MUTED)
        elif zoom:
            text(d, (130, 1347), "Nos detenemos en Tena.", 38, PAPER, True)
            text(d, (130, 1405), "¿Qué ocurre cuando se mueve una falla?", 29, GOLD)
        else:
            row = rows[-1]
            date = "/".join(reversed(row["local_time"][:10].split("-")))
            text(d, (130, 1348), f"{len(rows):02d} / {date} · {row['magnitude']:g} {row['magnitude_type']}".replace(".", ","), 38, PAPER, True)
            text(d, (130, 1405), "Cerca de Tena · fuente IG-EPN, no USGS", 28, MUTED)
        text(d, (110, 1486), "Napo resaltado · referencia 2011 · localidades: GeoNames", 23, MUTED)
        return image

    def diagram_frame(self, name, elapsed):
        types = {
            "normal": ("Falla normal.", "Extensión · el bloque de techo desciende", "normal", "EL BLOQUE SOBRE EL PLANO BAJA", "Mira cómo las capas dejan de coincidir a ambos lados."),
            "inversa": ("Falla inversa.", "Compresión · el bloque de techo asciende", "inversa", "EL BLOQUE SOBRE EL PLANO SUBE", "El movimiento ocurre a lo largo del plano inclinado."),
            "desgarre": ("Falla de desgarre.", "También llamada transcurrente · movimiento lateral", "desgarre", "LOS BLOQUES SE DESLIZAN DE LADO", "En este ejemplo no hay desplazamiento vertical."),
            "que_es_falla": ("¿Qué es una falla?", "Fractura o zona de fracturas con desplazamiento", "desgarre", "NO ES SIMPLEMENTE UNA GRIETA", "Los bloques se han desplazado uno respecto al otro."),
            "bloqueo": ("Un tramo bloqueado.", "La fricción puede bloquear; la roca acumula deformación", "desgarre", "DEFORMACIÓN Y ENERGÍA ACUMULADA", "Un tramo puede permanecer bloqueado. No está deslizando libremente."),
            "deslizamiento": ("Cuando desliza de golpe.", "Parte de la energía se propaga como ondas sísmicas", "desgarre", "DESLIZAMIENTO REPENTINO → SISMO", "No todo movimiento de una falla es repentino: también existe deslizamiento lento."),
        }
        title, subtitle, kind, heading, detail = types[name]
        if name == "bloqueo":
            phase = 0
        elif name == "deslizamiento":
            phase = (elapsed-2)/.55
        else:
            phase = (elapsed-1.5)/3.2
        if name not in self.static:
            background = self.shell(4, title, subtitle)
            d = ImageDraw.Draw(background)
            text(d, (135, 1170), "Esquema 3D conceptual · sin escala espacial ni temporal", 25, MUTED)
            text(d, (135, 1210), "No es la geometría de una falla bajo Tena.", 26, MUTED)
            card(d, (90, 1280, 930, 1489), GOLD)
            text(d, (130, 1304), heading, 29, GOLD)
            paragraph(d, (130, 1365), detail, 29, 740, PAPER)
            self.static[name] = background
        image = self.static[name].copy()
        render_blocks(image, kind, phase, locked=name == "bloqueo")
        if name == "bloqueo":
            d = ImageDraw.Draw(image)
            # Qualitative editorial loading indicator, not an observed stress measurement.
            d.rounded_rectangle((180, 905, 490, 948), radius=8, fill=INK, outline=LINE, width=2)
            load = smooth(elapsed/8)
            d.rounded_rectangle((190, 915, 191+290*load, 938), radius=5, fill=GOLD)
            text(d, (190, 963), "Esfuerzo: ilustrativo, sin unidades", 20, MUTED, width=340)
        return image

    def closing_v5(self):
        image = self.closing_fault()
        d = ImageDraw.Draw(image)
        d.rectangle((90, 1410, 930, 1510), fill=INK)
        paragraph(d, (110, 1420), "Historia 1900–2025: USGS. Casos 2026 y contexto local: IG-EPN. Conceptos: USGS. Mapa: geoBoundaries / GeoNames.", 26, 780, MUTED)
        return image

    def render(self, second):
        number = next(i for i, (a, b, _) in enumerate(SCENES) if a <= second < b)
        name = SCENES[number][2]
        elapsed = second-SCENES[number][0]
        if name.startswith("mapa") or name == "zoom_tena":
            key = (name, historical_year(elapsed) if name == "mapa_historico" else min(1, int(elapsed//5)) if name == "mapa_2026" else round(min(elapsed, 3.6), 2))
            if key not in self.cache:
                self.cache[key] = self.map_frame_v5(name, elapsed)
                if len(self.cache) > 8:
                    del self.cache[next(iter(self.cache))]
            image = self.cache[key].copy()
        elif name in ("que_es_falla", "bloqueo", "deslizamiento", "normal", "inversa", "desgarre"):
            image = self.diagram_frame(name, elapsed)
        else:
            if name not in self.static:
                self.static[name] = {"pregunta_2026": self.question, "contexto_local": self.local_context, "cierre": self.closing_v5}[name]()
            image = self.static[name].copy()
        d = ImageDraw.Draw(image)
        d.line((90, 1528, 90+840*second/DURATION, 1528), fill=LIME, width=4)
        step = 840/len(SCENES)
        for index in range(len(SCENES)):
            x = 90+index*step
            d.rounded_rectangle((x, 1558, x+step-12, 1564), radius=3, fill=LIME if index <= number else LINE)
        return image


def export(folder, storyboard_only=False):
    import imageio_ffmpeg
    folder = Path(folder)
    design = CatalogFaultDesign(folder)
    sheet = Image.new("RGB", (720, 426*math.ceil(len(SCENES)/3)), INK)
    for i, (start, end, name) in enumerate(SCENES):
        second = end-.5 if name in ("mapa_historico", "zoom_tena") else (start+end)/2
        frame = design.render(second)
        frame.save(folder / f"qa_v5_{name}.jpg", quality=95)
        sheet.paste(frame.resize((240, 426)), ((i%3)*240, (i//3)*426))
    sheet.save(folder / "storyboard_v5.jpg", quality=95)
    design.render(10.5).save(folder / "qa_v5_1987.jpg", quality=95)
    design.render(0).save(folder / "qa_v5_1900.jpg", quality=95)
    if storyboard_only:
        print("Catalog and 3D-fault storyboard exported:", folder.resolve())
        return
    output = folder / "napo_1900_2026_fallas_3d_maqueta_sin_voz_v5.mp4"
    writer = imageio_ffmpeg.write_frames(str(output), (WIDTH, HEIGHT), fps=30, codec="libx264",
                                        pix_fmt_in="rgb24", pix_fmt_out="yuv420p", macro_block_size=2,
                                        quality=8, ffmpeg_log_level="error",
                                        output_params=["-movflags", "+faststart", "-preset", "veryfast", "-threads", "2"])
    writer.send(None)
    try:
        for frame in range(DURATION*30):
            writer.send(design.render(frame/30).tobytes())
            if frame % 300 == 0:
                print(f"Catalog / 3D-fault draft: {frame/30:g}/{DURATION} seconds", flush=True)
    finally:
        writer.close()
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(output), "-f", "null", "-"], capture_output=True, check=True)
    metadata = {"status": "silent_draft_not_for_publication", "width": WIDTH, "height": HEIGHT,
                "duration_seconds": DURATION, "fps": 30, "motion_sampling_fps": 30,
                "audio": None, "full_decode": "passed", "sha256": sha256(output.read_bytes()).hexdigest(),
                "scenes": SCENES, "historical_source": "USGS", "historical_query_period": "1900–2025 UTC",
                "historical_events": len(design.history), "first_available": design.history_audit["earliest_record"],
                "region": REGION, "minimum_reported_magnitude": 4,
                "current_source": "IG-EPN", "current_selection": [r["id"] for r in design.current],
                "combination": "separate non-overlapping periods/scenes; not a unified catalog or rate comparison",
                "fault_examples": "normal, reverse and strike-slip; actual block/layer motion; schematic not local faults",
                "pending": "new voice, synchronization, subtitles and final source/visual/audio review"}
    (folder / "draft_metadata_v5.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Silent catalog / 3D-fault draft verified:", output.resolve(), flush=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--storyboard-only", action="store_true")
    args = parser.parse_args()
    export(args.folder, args.storyboard_only)
