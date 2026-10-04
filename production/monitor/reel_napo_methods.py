"""Original curiosity-first river video: observations, methods, then evidence.

Free installed reference narration; no voice imitation or automatic publication.
Preserves all previous episodes. Six-band methods are computed from native data.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from reel_napo_indices import Design as PreviousDesign, DATES, YEARS, MAP
from reel_napo_ndwi import fit_map, export, WIDTH, HEIGHT
from reel_design import CREDIT_NAME, CREDIT_SPECIALTY
from reel_territory import INK, LINE, MUTED, GOLD, LIME, PAPER, text, paragraph, card

FOLDER = Path("artifacts/rios_napo_metodos_v4")
SCRIPT = {
    "hook": "Mira esta curva del Jatunyacu. Dos mil diecinueve a la izquierda; dos mil veinticuatro a la derecha. ¿Dónde pondrías la orilla? Parece fácil. Pero ahora cambiaremos el cálculo, sin cambiar de fecha. Y no todos los métodos señalarán lo mismo.",
    "reveal": "Aquí está la trampa. N D W I y M N D W I miran la misma escena de dos mil veinticuatro, pero resaltan el río de manera diferente. Un azul más intenso no significa más agua. El satélite no pintó el río: nosotros elegimos cómo interpretar la luz.",
    "questions": "Entonces, ¿qué índice es mejor? Antes hay que elegir la pregunta. ¿Queremos localizar agua, saber si un lecho queda expuesto, o investigar sedimentos dentro del agua? Son tres problemas distintos. Un único número no resuelve los tres.",
    "ndwi": "Empecemos por el agua. Sentinel dos registra verde e infrarrojo cercano. El agua suele reflejar poco en ese infrarrojo. N D W I resta infrarrojo al verde y divide por su suma. Es un contraste espectral, no profundidad, caudal ni litros.",
    "mndwi": "M N D W I cambia el infrarrojo cercano por onda corta. Puede ayudar a separar agua de otras superficies. Pero el agua poco profunda, las sombras y los píxeles que mezclan orilla y río siguen siendo difíciles. No basta con que el mapa se vea bonito.",
    "awei": "Feyisa y sus colegas propusieron A W E I, con variantes para entornos con y sin sombras. Combinan varias bandas con pesos distintos. Aquí mostramos la variante para sombras. No es una mejora garantizada: nuestra máscara también puede descartar agua oscura antes de compararla.",
    "agreement": "Probemos los cuatro detectores sobre dos mil veinticuatro. Azul: todos superan el umbral; ámbar: discrepan. Cero es un umbral exploratorio, no calibrado aquí. Y cuatro votos no son cuatro testigos independientes: comparten bandas y pueden equivocarse juntos.",
    "comparefirst": "Ahora volvamos al paisaje, sin índices. Once de julio de dos mil diecinueve: mismo encuadre y ajuste visual. Este punto de partida no representa un río intacto ni todo el año.",
    "comparemiddle": "Ocho de agosto de dos mil veinticuatro. Mira los bancos claros, los brazos de agua y las orillas. Esta es la imagen que merece detenerse a observar. Podemos señalar diferencias, pero aún no separar cuánto corresponde al nivel del agua y cuánto a cambios del cauce.",
    "comparerecent": "Veintinueve de julio de dos mil veintiséis. La observación más reciente de esta selección, no una cámara en vivo. Tres fechas nos muestran momentos; no nos cuentan todo lo que ocurrió entre ellos.",
    "change": "En coral marcamos píxeles que pasan de cuatro detectores positivos a ninguno entre dos mil diecinueve y dos mil veinticuatro. Es una pérdida candidata de señal de agua. No significa automáticamente lecho seco, erosión medida ni minería. El ámbar conserva los casos dudosos.",
    "dry": "¿Se está secando el río? Para responder necesitamos muchas fechas, agua y sedimento clasificados con referencias independientes, y lluvia o niveles del río. Una poza puede seguir teniendo agua aunque no haya flujo continuo. Una nube tampoco cuenta como un día seco.",
    "vegetation": "Aguas abajo, en el Napo, añadimos N D V I para explorar vegetación. Ayuda a contextualizar las márgenes, no a identificar minería. Para distinguir agua poco profunda, sedimento y vegetación, una clasificación multibanda validada es una opción que debemos probar localmente.",
    "sediment": "¿Y si el agua transporta más sedimento? Aquí N D T I contrasta rojo y verde, solamente en agua candidata. El gris queda fuera de esa selección; la trama significa sin datos. Es una señal óptica, no una concentración ni un análisis de mercurio. Fondo, atmósfera y píxeles mixtos también influyen.",
    "mining": "La relación entre minería aluvial y sedimentos está documentada en investigaciones tropicales. Pero eso no demuestra la causa en estos píxeles del Napo. Haría falta localizar intervenciones independientes, contrastar antes y después, aguas arriba y abajo, y revisar crecidas y otras explicaciones.",
    "validation": "La literatura ofrece una ruta. Cavallo y sus colegas estudiaron dos tramos del Mingardo, en Italia, con clasificación multibanda y referencias de alta resolución. No trasladamos su resultado a Napo: necesitamos nuestras propias etiquetas y pruebas separadas para comparar métodos.",
    "end": "La respuesta no es encontrar el índice con el azul más convincente. Es elegir qué queremos medir, comprobar dónde falla y buscar evidencia que pueda contradecirnos. Nuestros ríos no necesitan un filtro espectacular: necesitan preguntas que podamos responder con rigor.",
    "sources": "Las adquisiciones, fórmulas, fuentes y limitaciones acompañan este video. Son imágenes reales de Copernicus Sentinel dos. La narración es una voz sintética de referencia; la versión final todavía requiere revisión científica y de subtítulos.",
}
TITLES = {
    "hook": ("¿Dónde pondrías la orilla?", "Jatunyacu · 2019 / 2024 · imágenes reales"),
    "reveal": ("Mismo río. Otro resultado.", "08 AGO 2024 · NDWI / MNDWI · no agua nueva"),
    "questions": ("¿Mejor para qué?", "Agua, lecho expuesto y sedimentos son preguntas distintas"),
    "ndwi": ("Primero: detectar agua.", "NDWI · McFeeters (1996) · verde frente a NIR"),
    "mndwi": ("Cambiemos una banda.", "MNDWI · Xu (2006) · verde frente a SWIR1"),
    "awei": ("¿Y las sombras?", "AWEIsh · Feyisa et al. (2014) · aplicado a Sentinel-2"),
    "agreement": ("No todos están de acuerdo.", "Cuatro detectores · umbrales cero no calibrados"),
    "comparefirst": ("Volvamos al paisaje: 2019.", "Jatunyacu · 11 JUL 2019 · color natural"),
    "comparemiddle": ("Detengámonos en 2024.", "Jatunyacu · 08 AGO 2024 · color natural"),
    "comparerecent": ("Una ventana a 2026.", "Jatunyacu · 29 JUL 2026 · no es una vista en vivo"),
    "change": ("Cambios que investigar.", "2019 → 2024 · señal candidata, no causa demostrada"),
    "dry": ("Una poza no es un caudal.", "Agua visible ≠ flujo continuo · sin datos ≠ seco"),
    "vegetation": ("Más allá del azul.", "Napo · 08 AGO 2024 · RGB / NDVI"),
    "sediment": ("¿Qué viaja dentro del agua?", "Jatunyacu · 08 AGO 2024 · NDTI, no concentración"),
    "mining": ("La causa exige otra prueba.", "Dethier et al. (2023) · contexto tropical, no prueba local"),
    "validation": ("¿Cómo elegir un ganador?", "Cavallo et al. (2025) · dos tramos en Italia, no Napo"),
    "end": ("Menos filtros. Más evidencia.", "La pregunta determina el método"),
    "sources": ("Puedes comprobarlo.", "Fuentes y observaciones trazables junto al video"),
}


def load_evidence(folder):
    folder = Path(folder)
    m = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if m.get("recipe") != "native20m_methods_video_v4" or m["dates"] != ["2019-07-11", "2024-08-08", "2026-07-29"]:
        raise ValueError("Unreviewed video recipe or dates")
    if m["winner"] is not None or m["threshold_status"] != "exploratory-not-locally-calibrated":
        raise ValueError("Unvalidated winner or threshold claim")
    if m["formulas"]["aweinsh"] != "4*(B3-B11)-0.25*B8-2.75*B12":
        raise ValueError("Incorrect AWEInsh bands")
    files = {"source_manifest.json": m["source_manifest_sha256"], **m["images_sha256"]}
    for row in m["sources"]:
        files[row["local_file"]] = row["native_sha256"]
        files[row["id"] + ".stac.json"] = row["stac_sha256"]
    for name, expected in files.items():
        if Path(name).name != name or sha256((folder / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Evidence checksum/path mismatch: " + name)
    return m


class Design(PreviousDesign):
    def __init__(self, folder, manifest):
        self.folder, self.manifest = Path(folder), manifest
        self.maps, self.ratios, self.cache = {}, {}, {}
        for name in manifest["images_sha256"]:
            area, year, mode = name.rsplit("_", 2)
            with Image.open(self.folder / name) as image:
                self.maps[area, int(year), mode[:-4]], self.ratios[area] = fit_map(image.convert("RGBA"))

    @staticmethod
    def scene_year(kind):
        return {"comparefirst": 2019, "comparemiddle": 2024, "comparerecent": 2026}.get(kind, 2024)

    def shell(self, kind):
        image = Image.new("RGB", (WIDTH, HEIGHT), INK)
        d = ImageDraw.Draw(image)
        text(d, (90, 142), "ANDES PULSO / ECUADOR VIVO", 25, LIME)
        text(d, (90, 184), "NAPO · UN RÍO, TRES PREGUNTAS", 24, MUTED)
        title, detail = TITLES[kind]
        text(d, (90, 250), title, 43, PAPER, True)
        text(d, (90, 330), detail, 24, MUTED)
        text(d, (90, 1621), CREDIT_NAME, 28, PAPER)
        text(d, (90, 1659), CREDIT_SPECIALTY, 23, MUTED)
        text(d, (90, 1723), "VISTA PREVIA · VOZ SINTÉTICA DE REFERENCIA", 22, GOLD)
        text(d, (90, 1765), "Contains modified Copernicus Sentinel data (2019, 2024, 2026)", 20, MUTED)
        return image

    def legend(self, d, mode):
        labels = {
            "agreement": "Azul: 4/4 · ámbar: 1–3/4 · oscuro: 0/4",
            "change": "Coral: pérdida · verde: aparición · ámbar: duda",
            "ndti": "NDTI −1/+1 · gris: fuera del agua candidata",
            "ndvi": "NDVI −1/+1 · verde: mayor contraste de verdor",
            "rgb/ndvi": "RGB / NDVI −1/+1 · verde: mayor contraste de verdor",
            "aweish": "AWEIsh · color fijo −1/+1, NO rango normalizado",
        }
        if mode in labels:
            text(d, (90, 1314), labels[mode], 26, LIME)
            extra = {"change": "Azul: señal estable · oscuro: 0/4 en ambas fechas",
                     "ndti": "(B4 − B3) / (B4 + B3) · no unidades de turbidez",
                     "aweish": "B2 + 2,5B3 − 1,5(B8 + B11) − 0,25B12"}.get(mode)
            if extra:
                text(d, (90, 1348), extra, 24, MUTED)
            return
        super().legend(d, mode)

    def map(self, image, area, year, mode, *, other_mode=None, other_year=None):
        # Retain fixed geometry/scale; draw a mode-correct legend after old helper.
        super().map(image, area, year, mode, other_mode=other_mode, other_year=other_year)
        if other_mode == "ndvi" or mode in ("agreement", "change", "ndti", "aweish"):
            d = ImageDraw.Draw(image)
            d.rectangle((90, 1305, 930, 1375), fill=INK)
            self.legend(d, "rgb/ndvi" if other_mode else mode)
        if mode == "change":
            d = ImageDraw.Draw(image)
            d.rectangle((104, 418, 390, 465), fill=INK)
            text(d, (110, 427), "2019 → 2024", 26, GOLD)

    def cards(self, image, rows, citation):
        d = ImageDraw.Draw(image)
        for i, (heading, detail) in enumerate(rows):
            y = 430 + i * 262
            card(d, (90, y, 930, y + 237), LIME)
            text(d, (138, y + 26), heading, 28, GOLD)
            bottom = paragraph(d, (138, y + 90), detail, 32, 757, PAPER)
            if bottom > y + 220:
                raise ValueError("Card body overflows")
        paragraph(d, (110, 1250), citation, 25, 790, MUTED)

    def base(self, kind, year, phase):
        image = self.shell(kind)
        if kind == "hook":
            self.map(image, "jatunyacu_detail", 2019, "rgb", other_year=2024)
        elif kind == "reveal":
            self.map(image, "jatunyacu_detail", 2024, "ndwi", other_mode="mndwi")
        elif kind in ("ndwi", "mndwi"):
            self.formula(image, kind == "mndwi")
        elif kind in ("awei", "agreement", "sediment", "change"):
            self.map(image, "jatunyacu_detail", 2024,
                     {"awei": "aweish", "agreement": "agreement", "sediment": "ndti", "change": "change"}[kind])
        elif kind.startswith("compare"):
            self.map(image, "jatunyacu_detail", year, "rgb")
        elif kind == "vegetation":
            self.map(image, "napo", 2024, "rgb", other_mode="ndvi")
        else:
            entries, citation = {
                "questions": ([("01 · ¿DÓNDE HAY AGUA?", "NDWI / MNDWI / AWEI: detectores que hay que evaluar."),
                               ("02 · ¿QUEDA LECHO EXPUESTO?", "Agua + sedimento + vegetación + muchas fechas."),
                               ("03 · ¿CAMBIÓ LO QUE TRANSPORTA?", "Señales ópticas del agua + muestreo y calibración.")],
                              "No existe aquí un ganador validado. Una señal no determina la causa."),
                "dry": ([("AGUA VISIBLE ≠ FLUJO", "Las pozas pueden persistir sin conexión continua."),
                         ("TRES FECHAS ≠ DURACIÓN", "No calculamos días secos ni tendencia de sequía."),
                         ("TRAMA ≠ LECHO SECO", "QA conservadora; sin observación no hay diagnóstico.")],
                        "Cavallo et al. (2025). Las fechas no igualan caudal ni lluvia antecedente."),
                "mining": ([("RELACIÓN DOCUMENTADA", "Minería aluvial y sedimentos en ríos tropicales."),
                            ("PRUEBA LOCAL PENDIENTE", "Intervenciones independientes + controles espaciales y temporales."),
                            ("NO ES UN ANÁLISIS QUÍMICO", "Sin NTU, mg/L, mercurio ni atribución de responsabilidades.")],
                           "Dethier et al. (2023), Nature · doi:10.1038/s41586-023-06309-9. Lobo et al. (2018): calibración con muestreo."),
                "validation": ([("MULTIBANDA + REFERENCIAS", "Separar agua poco profunda, agua profunda, sedimento y vegetación."),
                                ("ENTRENAR ≠ EVALUAR", "Reservar referencias independientes antes de ajustar los métodos."),
                                ("ITALIA ≠ NAPO", "Un caso publicado orienta; no valida nuestros píxeles.")],
                               "Cavallo et al. (2025), Journal of Hydrology · doi:10.1016/j.jhydrol.2025.133416. No modelo entrenado en este video."),
                "end": ([("AGUA", "Comparar detectores y revisar píxeles mixtos."),
                         ("LECHO Y VEGETACIÓN", "Clasificar superficies y seguirlas en el tiempo."),
                         ("SEDIMENTOS Y CAUSAS", "Calibración local + evidencia que pueda refutar la hipótesis.")],
                        "Ventanas locales: Tena, Jatunyacu, Napo y Misahuallí. No toda la provincia. Comparación a 20 m; ampliar no crea detalle."),
                "sources": ([("NDWI / MNDWI / AWEI", "McFeeters (1996), Xu (2006), Feyisa et al. (2014)."),
                             ("CAUCES Y SEDIMENTOS", "Cavallo et al. (2025), Lobo et al. (2018), Dethier et al. (2023)."),
                             ("OBSERVACIONES REALES", "Copernicus Sentinel-2 / Earth Search. 11 JUL 2019 · 08 AGO 2024 · 29 JUL 2026.")],
                            "Método, adquisiciones, bibliografía y límites: NAPO_RIOS_METODOS_V4.md. Umbrales exploratorios, no validación de campo."),
            }[kind]
            self.cards(image, entries, citation)
        return image

    def comparison_sheet(self):
        sheet = Image.new("RGB", (2700, 4810), INK)
        d = ImageDraw.Draw(sheet)
        text(d, (90, 40), "JATUNYACU · CAMBIAR LA PREGUNTA, NO SOLO EL COLOR", 42, PAPER, width=2500)
        text(d, (90, 104), "20 m · tres adquisiciones · QA común · umbral 0 exploratorio · sin ganador validado", 31, MUTED, width=2500)
        for row, mode in enumerate(("rgb", "mndwi", "aweish", "agreement", "ndti")):
            for col, year in enumerate(YEARS):
                x, y = 50 + col * 900, 200 + row * 900
                text(d, (x, y), f"{DATES[year]} / {mode.upper()}", 32, GOLD, width=870)
                sheet.paste(self.maps["jatunyacu_detail", year, mode], (x, y + 55))
        paragraph(d, (90, 4710), "Acuerdo: azul 4/4, ámbar discrepancia, oscuro 0/4. NDTI: gris fuera de agua candidata. Trama sin datos. AWEI: color −1/+1 editorial, no rango normalizado. Copernicus / Henry Conteron.", 27, 2500, MUTED)
        sheet.save(self.folder / "comparacion_metodos_2019_2024_2026.jpg", quality=96)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, default=FOLDER)
    parser.add_argument("--storyboard-only", action="store_true")
    parser.add_argument("--silent", action="store_true")
    args = parser.parse_args()
    manifest = load_evidence(args.folder)
    Design(args.folder, manifest).comparison_sheet()
    print(export(args.folder, args.silent, args.storyboard_only, design_type=Design,
                 evidence_loader=load_evidence, script=SCRIPT, stem="rios_napo_metodos_v4", tag="metodos"))
