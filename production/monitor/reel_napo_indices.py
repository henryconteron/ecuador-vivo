"""Index-first river story: real 2019, 2024 and 2026 acquisitions, no AI imagery."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image, ImageDraw

from reel_napo_ndwi import fit_map, export, CAPTION, WIDTH, HEIGHT
from reel_design import CREDIT_NAME, CREDIT_SPECIALTY
from reel_territory import INK, LINE, MUTED, GOLD, LIME, PAPER, text, paragraph, card

FOLDER = Path("artifacts/rios_napo_indices_v3")
PREVIOUS_EVIDENCE = Path("artifacts/rios_napo_indices_v2")
YEARS = (2019, 2024, 2026)
DATES = {2019: "11 JUL 2019", 2024: "08 AGO 2024", 2026: "29 JUL 2026"}
MAP = (90, 405, 930, 1245)
SCRIPT = {
    "hook": "Puedo hacer que un píxel de este río se vea más azul sin añadir una sola gota. ¿Truco? No. Es la misma fecha. Cambió el cálculo.",
    "challenge": "Y eso importa cuando comparamos el Jatunyacu en dos mil diecinueve y dos mil veinticuatro. Parece una pregunta sencilla: ¿dónde está el agua? Pero una imagen no siempre nos lo pone fácil.",
    "rgb": "Un banco claro y una superficie de agua pueden confundirse en la imagen. Para investigar esa duda, podemos mirar luz que nuestros ojos no ven.",
    "ndwi": "Sentinel dos registra luz verde e infrarrojo cercano. El agua suele reflejar poco en este último. N D W I contrasta ambos: verde menos infrarrojo cercano, dividido por su suma. El resultado es un contraste, no una cantidad de agua.",
    "mndwi": "¿Y si cambiamos la banda infrarroja? Así se forma M N D W I: verde frente a infrarrojo de onda corta. Xu propuso esta modificación en un estudio con Landsat para reducir confusiones con otras superficies. Aquí la aplicamos a Sentinel dos.",
    "test": "Ahora revelamos el truco: N D W I a la izquierda; M N D W I a la derecha. Misma escena de dos mil veinticuatro, misma paleta y píxeles válidos. Cambió el contraste entre bandas. No apareció agua nueva.",
    "pixel": "En el píxel marcado, N D W I da aproximadamente cero coma veinticuatro; M N D W I, cero coma treinta y nueve. No significa más agua. Son cálculos distintos sobre el mismo lugar, que también puede mezclar agua y orilla.",
    "choice": "Elegimos M N D W I para explorar estos encuadres y conservamos N D W I y color natural para contrastar. Es una decisión educativa: no podemos declarar un ganador por exactitud sin muestras independientes.",
    "scale": "Hay otra trampa: el zoom. La banda de onda corta tiene muestreo de veinte metros; verde e infrarrojo cercano, de diez. Aquí promediamos a veinte antes de comparar. Agrandar los píxeles no descubre un arroyo escondido dentro de ellos.",
    "comparefirst": "Once de julio de dos mil diecinueve. Este es nuestro punto de partida: la misma curva del Jatunyacu, observada con M N D W I.",
    "comparemiddle": "Ocho de agosto de dos mil veinticuatro. Detengámonos aquí. Sigue la señal azul frente a las islas y las orillas. Señala lugares para investigar; todavía no mide cuánto se desplazó el cauce.",
    "comparerecent": "Veintinueve de julio de dos mil veintiséis. Otra instantánea. Son tres observaciones, no una película continua ni una tendencia validada.",
    "napo": "En el Napo, aguas abajo de Puerto Napo, repetimos la pregunta. ¿Cambió el agua presente ese día, la orilla o ambas? Estos sectores no representan todos los ríos de la provincia.",
    "quality": "Agosto de dos mil veinticuatro ofrecía mejor cobertura útil que julio en esta búsqueda. La trama marca datos descartados, no agua ni tierra. Y no hemos igualado la lluvia reciente ni el caudal: eso también puede cambiar lo que vemos.",
    "limits": "¿Podemos culpar a la minería? No con estos cálculos solos. Ninguno mide mercurio ni demuestra la causa. Harían falta otras evidencias y, para medir cambios del cauce, más fechas y validación independiente.",
    "end": "El misterio del azul tenía una respuesta: cambió la forma de medir. El misterio del río exige más trabajo. Un índice nos ayuda a hacer mejores preguntas; la evidencia decide hasta dónde podemos responder.",
}
TITLES = {
    "hook": ("¿Más azul significa más agua?", "La misma escena · Jatunyacu · 08 AGO 2024"),
    "challenge": ("Parece una pregunta sencilla.", "Jatunyacu · 2019 / 2024 · imágenes reales"),
    "ndwi": ("Primero: NDWI.", "McFeeters (1996) · verde frente a NIR"),
    "mndwi": ("¿Y si cambiamos una banda?", "Xu (2006): Landsat · aquí adaptado a Sentinel-2"),
    "test": ("Dos índices. El mismo río.", "Jatunyacu · 08 AGO 2024 · prueba a 20 m"),
    "pixel": ("De un píxel a un número.", "08 AGO 2024 · ejemplo real, no etiqueta de campo"),
    "choice": ("Elegir, no exagerar.", "MNDWI principal · NDWI y RGB como contraste"),
    "scale": ("Más zoom no es más detalle.", "Comparación a 20 m · sin inventar resolución"),
    "comparefirst": ("2019 / 2024 / 2026", "Jatunyacu · MNDWI · punto de partida: 2019"),
    "comparemiddle": ("Detengámonos en 2024.", "Jatunyacu · MNDWI · observa agua, islas y orillas"),
    "comparerecent": ("La observación de 2026.", "Jatunyacu · MNDWI · tres instantáneas, no tendencia"),
    "rgb": ("¿Agua, arena o una mezcla?", "Jatunyacu · color natural · 08 AGO 2024"),
    "napo": ("También cambia la mirada", "Napo aguas abajo de Puerto Napo · MNDWI"),
    "quality": ("Sin datos no hay conclusión.", "Nubes, fechas y caudal forman parte de la historia"),
    "limits": ("Una señal no explica la causa.", "Agua superficial no es minería ni contaminación"),
    "end": ("Un misterio resuelto. Otro abierto.", "El cálculo explica el azul; no explica todo el río"),
}


def active_year(fraction):
    # 2024 receives a longer hold. Hard cuts preserve the measured geography.
    fraction = fraction % 1
    return 2019 if fraction < .25 else 2024 if fraction < .65 else 2026


def load_evidence(folder):
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("recipe") != "aligned20m_v2" or [d[:10] for d in manifest["dates"]] != ["2019-07-11", "2024-08-08", "2026-07-29"]:
        raise ValueError("Wrong reviewed recipe / dates")
    if manifest["formulas"] != {"ndwi": "(B3-B8)/(B3+B8)", "mndwi": "(B3-B11)/(B3+B11)"}:
        raise ValueError("Unreviewed index definitions")
    if not manifest["qa"]["all_three_dates_and_both_indices"] or manifest["qa"]["accepted_scl"] != [4, 5, 6]:
        raise ValueError("Unreviewed QA")
    for row in manifest["scenes"]:
        if sha256((folder / row["crop_file"]).read_bytes()).hexdigest() != row["crop_sha256"]:
            raise ValueError("Source crop changed")
    for name, digest in manifest["images_sha256"].items():
        if sha256((folder / name).read_bytes()).hexdigest() != digest:
            raise ValueError("Derived image changed")
    for area in manifest["regions"].values():
        if area["common_valid_fraction"] < .55:
            raise ValueError("Too little common support")
    return manifest


def copy_evidence(source, destination):
    """Copy only checksum-verified generated scientific evidence, never old media."""
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError("New editorial version must not overwrite the previous folder")
    manifest = load_evidence(source)
    destination.mkdir(parents=True, exist_ok=True)
    names = ["manifest.json", "selection_2024.json"] + list(manifest["images_sha256"])
    names += [row["crop_file"] for row in manifest["scenes"]]
    names += [row["id"] + ".stac.json" for row in manifest["scenes"]]
    for name in names:
        if Path(name).name != name:
            raise ValueError("Evidence path must be a filename")
        target = destination / name
        if target.exists() and sha256(target.read_bytes()).hexdigest() != sha256((source / name).read_bytes()).hexdigest():
            raise ValueError("Refusing to replace conflicting scientific evidence")
        shutil.copy2(source / name, target)


class Design:
    def __init__(self, folder, manifest):
        self.folder, self.manifest = folder, manifest
        self.maps, self.ratios, self.cache = {}, {}, {}
        for area in manifest["regions"]:
            for year in YEARS:
                for mode in ("rgb", "ndwi", "mndwi"):
                    with Image.open(folder / f"{area}_{year}_{mode}.png") as image:
                        self.maps[area, year, mode], self.ratios[area] = fit_map(image.convert("RGBA"))

    def shell(self, kind):
        image = Image.new("RGB", (WIDTH, HEIGHT), INK)
        d = ImageDraw.Draw(image)
        text(d, (90, 142), "ANDES PULSO / ECUADOR VIVO", 25, LIME)
        text(d, (90, 184), "RÍOS DE NAPO · ÍNDICES CON EVIDENCIA", 24, MUTED)
        title, detail = TITLES[kind]
        text(d, (90, 250), title, 43, PAPER, True)
        text(d, (90, 330), detail, 25, MUTED)
        text(d, (90, 1621), CREDIT_NAME, 28, PAPER)
        text(d, (90, 1659), CREDIT_SPECIALTY, 23, MUTED)
        text(d, (90, 1723), "VISTA PREVIA · VOZ SINTÉTICA DE REFERENCIA", 22, GOLD)
        text(d, (90, 1765), "Contains modified Copernicus Sentinel data (2019, 2024, 2026)", 20, MUTED)
        return image

    @staticmethod
    def scene_year(kind):
        return {"comparefirst": 2019, "comparemiddle": 2024, "comparerecent": 2026}.get(kind)

    def legend(self, d, mode):
        if mode == "rgb":
            text(d, (90, 1320), "B4/B3/B2 · media a 20 m · ajuste fijo 0–0,3", 26, LIME)
            return
        stops = np.array([[116, 70, 46], [220, 199, 157], [242, 237, 212], [47, 141, 184], [7, 61, 105]])
        for x in range(560):
            color = tuple(int(np.interp(x / 559 * 4, np.arange(5), stops[:, c])) for c in range(3))
            d.line((270 + x, 1320, 270 + x, 1334), fill=color)
        text(d, (90, 1317), "ÍNDICES" if "/" in mode else mode.upper(), 25, LIME, width=165)
        for x, label in ((257, "−1"), (538, "0"), (811, "+1")):
            text(d, (x, 1340), label, 22, PAPER, width=70)

    def map(self, image, area, year, mode, *, other_mode=None, other_year=None):
        d = ImageDraw.Draw(image)
        surface = self.maps[area, year, mode].copy()
        if other_mode or other_year:
            right = self.maps[area, other_year or year, other_mode or mode]
            surface.paste(right.crop((420, 0, 840, 840)), (420, 0))
        image.paste(surface, MAP[:2])
        d.rectangle(MAP, outline=LINE, width=2)
        if other_mode or other_year:
            d.line((510, MAP[1], 510, MAP[3]), fill=GOLD, width=3)
        labels = ((110, mode.upper()), (650, other_mode.upper())) if other_mode else (
            ((110, DATES[year]), (650, DATES[other_year])) if other_year else ((110, DATES[year]),))
        for x, label in labels:
            d.rounded_rectangle((x - 6, 418, x + 245, 465), 6, fill=INK)
            text(d, (x, 427), label, 26, GOLD, width=246)
        length = 1000 / 20 * self.ratios[area]
        d.rectangle((105, 1170, 130 + length, 1230), fill=INK)
        d.line((120, 1215, 120 + length, 1215), fill=PAPER, width=3)
        text(d, (120, 1176), "≈ 1 km", 24, PAPER)
        d.rounded_rectangle((850, 485, 920, 531), 5, fill=INK)
        text(d, (863, 492), "N ↑", 24, PAPER, width=50)
        support = self.manifest["regions"][area]["common_valid_fraction"] * 100
        if other_mode:
            text(d, (90, 1270), f"Ambos a 20 m · QA común {support:.1f}% · trama = sin datos", 25, MUTED)
            self.legend(d, "ndwi / mndwi")
        elif other_year:
            text(d, (90, 1270), f"Color natural · QA común {support:.1f}% · trama = sin datos", 25, MUTED)
            self.legend(d, mode)
        else:
            for i, value in enumerate(YEARS):
                x = 90 + i * 280
                d.rounded_rectangle((x, 1260, x + 260, 1300), 8, fill=LINE if value == year else INK, outline=GOLD if value == year else LINE)
                text(d, (x + 20, 1267), DATES[value], 22, GOLD if value == year else MUTED, width=240)
            self.legend(d, mode)

    def formula(self, image, modified):
        d = ImageDraw.Draw(image)
        name, infrared = ("MNDWI", "SWIR") if modified else ("NDWI", "NIR")
        card(d, (90, 435, 930, 1055), LIME)
        text(d, (140, 475), name, 77, GOLD, True)
        text(d, (155, 663), "VERDE − " + infrared, 62, PAPER)
        d.line((150, 775, 860, 775), fill=LIME, width=4)
        text(d, (155, 817), "VERDE + " + infrared, 62, PAPER)
        text(d, (140, 965), "Reflectancias · no colores de una captura", 29, MUTED)
        text(d, (105, 1110), "B3: verde · 10 m", 31, LIME)
        text(d, (105, 1160), "B11: onda corta · 20 m" if modified else "B8: infrarrojo cercano · 10 m", 31, GOLD)
        paragraph(d, (105, 1235), "El agua absorbe en el infrarrojo. El contraste ayuda a distinguirla, pero no equivale a una clasificación validada.", 29, 810, MUTED)

    def base(self, kind, year, phase):
        image = self.shell(kind)
        d = ImageDraw.Draw(image)
        if kind == "challenge":
            self.map(image, "jatunyacu_detail", 2019, "rgb", other_year=2024)
        elif kind == "hook":
            mode = "ndwi" if phase < .5 else "mndwi"
            self.map(image, "jatunyacu_detail", 2024, mode)
            d.rounded_rectangle((110, 485, 430, 541), 8, fill=INK)
            text(d, (125, 497), "LECTURA A" if phase < .5 else "LECTURA B", 30, GOLD, width=290)
        elif kind == "rgb":
            self.map(image, "jatunyacu_detail", 2024, "rgb")
        elif kind in ("ndwi", "mndwi"):
            self.formula(image, kind == "mndwi")
        elif kind == "test":
            self.map(image, "jatunyacu_detail", 2024, "ndwi", other_mode="mndwi")
        elif kind == "pixel":
            point = self.manifest["illustrative_pixel"]
            surface = self.maps["jatunyacu_detail", 2024, "rgb"].resize((390, 390), Image.Resampling.NEAREST)
            image.paste(surface, (90, 435))
            x, y = point["local_col_row"]
            area = self.manifest["regions"]["jatunyacu_detail"]
            cx, cy = 90 + (x + .5) / area["width"] * 390, 435 + (y + .5) / area["height"] * 390
            d.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), outline=GOLD, width=3)
            text(d, (525, 448), "REFLECTANCIAS", 28, LIME)
            for i, (heading, value) in enumerate((("VERDE", point["green"]), ("NIR", point["nir"]), ("SWIR", point["swir"]))):
                yy = 520 + i * 100
                text(d, (525, yy), heading, 27, MUTED)
                text(d, (525, yy + 35), f"{value:.4f}".replace(".", ","), 40, PAPER)
            for i, (heading, value, bands) in enumerate((("NDWI", point["ndwi"], "(VERDE − NIR) / (VERDE + NIR)"),
                                                       ("MNDWI", point["mndwi"], "(VERDE − SWIR) / (VERDE + SWIR)"))):
                yy = 860 + i * 210
                card(d, (90, yy, 930, yy + 190), LIME)
                text(d, (138, yy + 24), f"{heading} ≈ {value:.2f}".replace(".", ","), 43, GOLD)
                text(d, (138, yy + 100), bands, 28, PAPER)
            paragraph(d, (105, 1290), "SCL = 6 (agua, clasificación auxiliar). Puede ser mixto; no es una etiqueta de campo validada.", 26, 805, MUTED)
        elif kind.startswith("compare") or kind == "napo":
            self.map(image, "napo" if kind == "napo" else "jatunyacu_detail", year,
                     "mndwi")
        elif kind == "scale":
            self.map(image, "tena", 2024, "ndwi")
            d.rounded_rectangle((110, 485, 690, 550), 8, fill=INK)
            text(d, (125, 499), "TENA · esta comparación es de 20 m", 26, GOLD, width=565)
        else:
            entries = {
                "choice": [("MNDWI · LECTURA PRINCIPAL", "Para explorar agua en estos cauces amplios."),
                           ("NDWI + RGB · CONTRASTE", "Comprobar contexto y posibles confusiones."),
                           ("NO ES UN GANADOR UNIVERSAL", "Sin etiquetas independientes, no hay exactitud medida.")],
                "quality": [("2024 · 08 DE AGOSTO", "Julio tenía cobertura útil insuficiente en varios sectores."),
                            ("MÁSCARA COMÚN · 3 FECHAS", "La trama oculta datos descartados; no los rellenamos."),
                            ("CAUDAL NO CONTROLADO", "Meses próximos no garantizan la misma lluvia ni nivel.")],
                "limits": [("AGUA PRESENTE ESE DÍA", "No necesariamente la geometría permanente del cauce."),
                           ("NO MIDE CONTAMINACIÓN", "Mercurio y minería requieren otras evidencias."),
                           ("FALTA VALIDACIÓN INDEPENDIENTE", "Más fechas, hidrología y revisión de campo.")],
                "end": [("UN CONTRASTE ESPECTRAL", "NDWI: verde / NIR · MNDWI: verde / SWIR."),
                        ("TRES INSTANTÁNEAS", "2019 / 2024 / 2026 · no una tendencia validada."),
                        ("MIRAR CON EVIDENCIA", "Índice + RGB + fechas + calidad + verificación.")],
            }[kind]
            for i, (heading, detail) in enumerate(entries):
                y = 430 + i * 262
                card(d, (90, y, 930, y + 237), LIME)
                text(d, (138, y + 26), heading, 28, GOLD)
                paragraph(d, (138, y + 90), detail, 33, 757, PAPER)
            paragraph(d, (110, 1250), "Copernicus Sentinel / Earth Search. McFeeters (1996), Xu (2006). Fuentes y método completos junto al video.", 27, 790, MUTED)
        return image

    def render(self, kind, fraction, caption, progress):
        year = self.scene_year(kind) or active_year(fraction)
        key = (kind, fraction >= .5 if kind == "hook" else year if kind.startswith("compare") or kind == "napo" else None)
        if key not in self.cache:
            self.cache[key] = self.base(kind, year, fraction)
        image = self.cache[key].copy()
        d = ImageDraw.Draw(image)
        card(d, CAPTION, GOLD)
        bottom = paragraph(d, (138, 1402), caption, 31, 757, PAPER, leading=1.23)
        if bottom > CAPTION[3] - 10:
            raise ValueError("Caption overflows safe area")
        d.line((90, 1598, 90 + round(840 * progress), 1598), fill=LIME, width=4)
        return image

    def comparison_sheet(self):
        """Readable full-frame 3 dates x RGB/NDWI/MNDWI; no geography stretching."""
        sheet = Image.new("RGB", (2700, 3010), INK)
        d = ImageDraw.Draw(sheet)
        text(d, (90, 45), "JATUNYACU · TRES FECHAS / TRES LECTURAS", 48, PAPER, width=2500)
        text(d, (90, 110), "20 m · misma paleta −1 a +1 · máscara común · no una clasificación de agua", 33, MUTED, width=2500)
        for row, mode in enumerate(("rgb", "ndwi", "mndwi")):
            for col, year in enumerate(YEARS):
                x, y = 50 + col * 900, 200 + row * 900
                text(d, (x, y), f"{DATES[year]} / {mode.upper()}", 34, GOLD, width=870)
                sheet.paste(self.maps["jatunyacu_detail", year, mode], (x, y + 55))
        text(d, (90, 2960), "Contains modified Copernicus Sentinel data (2019, 2024, 2026) · Henry Conteron", 29, MUTED, width=2500)
        sheet.save(self.folder / "comparacion_jatunyacu_indices_2019_2024_2026.jpg", quality=96)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, default=FOLDER)
    parser.add_argument("--storyboard-only", action="store_true")
    parser.add_argument("--silent", action="store_true")
    parser.add_argument("--reuse-evidence-from", type=Path, default=PREVIOUS_EVIDENCE)
    args = parser.parse_args()
    if not (args.folder / "manifest.json").exists():
        copy_evidence(args.reuse_evidence_from, args.folder)
    evidence = load_evidence(args.folder)
    Design(args.folder, evidence).comparison_sheet()
    print(export(args.folder, args.silent, args.storyboard_only, design_type=Design,
                 evidence_loader=load_evidence, script=SCRIPT, stem="rios_napo_2019_2024_2026_v3", tag="indices"))
