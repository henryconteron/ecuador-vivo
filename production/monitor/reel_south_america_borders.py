"""Render a source-traceable, silent vertical draft about South American borders.

This is an original editorial format inspired only by the general idea of a
year-by-year map. It does not reuse graphics, typography, flags, audio or
wording from any third-party video.

The input is the official CShapes 2.0 Shapefile. Its historical coverage ends
on 2019-12-31, so this renderer deliberately never labels a later year as
observed data. It maps country-period geometries, not lived histories,
territorial claims or legal conclusions.

Example:
    python reel_south_america_borders.py \
      _local/cshapes/source/CShapes-2.0.shp \
      --output _local/reels/sudamerica-fronteras-1886-2019.mp4
"""

from __future__ import annotations

import argparse
from datetime import date
from hashlib import sha256
import json
import subprocess
from pathlib import Path

import geopandas as gpd
from PIL import Image, ImageDraw

from export_video import WIDTH, HEIGHT, font


SOURCE_URL = "https://icr.ethz.ch/data/cshapes/CShapes-2.0.zip"
SOURCE_CITATION = (
    "Schvitz, G. et al. (2022). Mapping The International System, "
    "1886-2017: The CShapes 2.0 Dataset. Journal of Conflict Resolution, 66(1), 144-161."
)
SOURCE_LICENSE = "CC BY-NC-SA 4.0"
FIRST_YEAR, LAST_YEAR = 1886, 2019

# Panamá is retained because its separation changes Colombia's northern outline.
# French Guiana is retained as a dependent territory, as represented by CShapes.
REGION_NAMES = frozenset(
    {
        "Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador",
        "French Guyana", "Guyana", "Panama", "Paraguay", "Peru", "Surinam",
        "Uruguay", "Venezuela",
    }
)
DISPLAY_NAMES = {"French Guyana": "Guayana Francesa", "Surinam": "Surinam"}
COLORS = {
    "Argentina": "#e75f50", "Bolivia": "#e5b956", "Brazil": "#579c72",
    "Chile": "#d5846c", "Colombia": "#729ec7", "Ecuador": "#f0c66a",
    "French Guyana": "#ac83b7", "Guyana": "#76ab95", "Panama": "#ce8aa1",
    "Paraguay": "#b58f63", "Peru": "#8d80c4", "Surinam": "#60aeb1",
    "Uruguay": "#71a9cf", "Venezuela": "#dc985b",
}

INK, PAPER, MUTED, OCEAN, GRID, GOLD = (
    "#102523", "#f6f0df", "#bfd1c8", "#1c4a4a", "#35625d", "#f4c56c"
)
MAP = (72, 418, 1008, 1428)
EXTENT = (-84.8, -30.0, -59.5, 14.0)  # west, east, south, north


def write(draw: ImageDraw.ImageDraw, xy: tuple[float, float], value: str, size: int,
          fill: str = PAPER, serif: bool = False, right: int = 1000) -> None:
    face = font(size, serif)
    if xy[0] + draw.textlength(value, font=face) > right:
        raise ValueError(f"Text exceeds safe width: {value}")
    draw.text(xy, value, font=face, fill=fill)


def paragraph(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, size: int,
              width: int, fill: str = MUTED, leading: float = 1.25) -> int:
    lines: list[str] = []
    line = ""
    face = font(size)
    for word in value.split():
        trial = f"{line} {word}".strip()
        if line and draw.textlength(trial, font=face) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    gap = round(size * leading)
    for index, rendered in enumerate(lines):
        write(draw, (xy[0], xy[1] + index * gap), rendered, size, fill, right=xy[0] + width)
    return xy[1] + len(lines) * gap


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], accent: str = GOLD) -> None:
    draw.rounded_rectangle(box, radius=26, fill="#153431", outline=GRID, width=2)
    draw.rounded_rectangle((box[0], box[1] + 22, box[0] + 5, box[3] - 22), radius=2, fill=accent)


def project(lon: float, lat: float) -> tuple[float, float]:
    west, east, south, north = EXTENT
    x0, y0, x1, y1 = MAP
    return (
        x0 + (lon - west) / (east - west) * (x1 - x0),
        y0 + (north - lat) / (north - south) * (y1 - y0),
    )


def polygon_parts(geometry):
    if geometry.geom_type == "Polygon":
        return [geometry]
    if geometry.geom_type == "MultiPolygon":
        return list(geometry.geoms)
    return []


def load_periods(path: Path) -> gpd.GeoDataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    data = gpd.read_file(path)
    required = {"cntry_name", "gwsdate", "gwedate", "geometry"}
    absent = required.difference(data.columns)
    if absent:
        raise ValueError(f"CShapes fields absent: {', '.join(sorted(absent))}")
    data = data[data["cntry_name"].isin(REGION_NAMES)].copy()
    data["gwsdate"] = data["gwsdate"].dt.date
    data["gwedate"] = data["gwedate"].dt.date
    if data.empty:
        raise ValueError("No South American CShapes periods were found.")
    return data


def active_periods(periods: gpd.GeoDataFrame, year: int) -> gpd.GeoDataFrame:
    moment = date(year, 12, 31)
    active = periods[(periods["gwsdate"] <= moment) & (periods["gwedate"] >= moment)]
    if active.empty:
        raise ValueError(f"No active geometry at {year}.")
    return active


def transitions(periods: gpd.GeoDataFrame) -> list[tuple[date, str]]:
    found = {
        (row.gwsdate, row.cntry_name)
        for row in periods.itertuples()
        if date(FIRST_YEAR, 1, 1) < row.gwsdate <= date(LAST_YEAR, 12, 31)
    }
    return sorted(found)


def shell(chapter: str) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), INK)
    draw = ImageDraw.Draw(image)
    for y in range(92, 1740, 118):
        draw.line((56, y, 1024, y), fill="#132d2b", width=1)
    write(draw, (72, 108), "ECUADOR VIVO / ATLAS LATINOAMERICANO", 24, GOLD)
    write(draw, (72, 148), chapter, 23, MUTED)
    write(draw, (72, 1770), "Borrador visual · datos y límites en ecuadorvivo.org", 22, MUTED)
    return image


def map_surface(rows: gpd.GeoDataFrame) -> Image.Image:
    x0, y0, x1, y1 = MAP
    image = Image.new("RGB", (x1 - x0, y1 - y0), OCEAN)
    draw = ImageDraw.Draw(image)
    for row in rows.itertuples():
        color = COLORS.get(row.cntry_name, "#93a995")
        for geometry in polygon_parts(row.geometry):
            exterior = [project(lon, lat) for lon, lat in geometry.exterior.coords]
            exterior = [(round(x - x0), round(y - y0)) for x, y in exterior]
            draw.polygon(exterior, fill=color, outline="#1d3834", width=2)
            for interior in geometry.interiors:
                hole = [project(lon, lat) for lon, lat in interior.coords]
                draw.polygon([(round(x - x0), round(y - y0)) for x, y in hole], fill=OCEAN)
    return image


def draw_map(image: Image.Image, rows: gpd.GeoDataFrame) -> None:
    draw = ImageDraw.Draw(image)
    x0, y0, x1, y1 = MAP
    image.paste(map_surface(rows), (x0, y0))
    draw.rectangle(MAP, outline="#5e9184", width=2)
    for longitude in (-80, -70, -60, -50, -40):
        x, _ = project(longitude, 0)
        draw.line((x, y0, x, y1), fill="#38655f", width=1)
        write(draw, (x - 32, y1 + 10), f"{abs(longitude)}° O", 20, MUTED, right=x + 54)
    for latitude in (-50, -40, -30, -20, -10, 0, 10):
        _, y = project(-60, latitude)
        draw.line((x0, y, x1, y), fill="#38655f", width=1)
    write(draw, (x1 - 80, y0 + 26), "N ↑", 24, PAPER)
    labels = [("ECUADOR", -78.5, -1.4), ("BRASIL", -55.5, -11), ("PERÚ", -75, -10),
              ("ARGENTINA", -65, -38), ("CHILE", -71, -30), ("COLOMBIA", -73, 4)]
    for label, lon, lat in labels:
        x, y = project(lon, lat)
        face = font(21)
        draw.text((x, y), label, font=face, fill="#17342f", stroke_width=2, stroke_fill=PAPER)


def events_so_far(event_dates: list[tuple[date, str]], year: int) -> int:
    return sum(when.year <= year for when, _ in event_dates)


def event_for_year(event_dates: list[tuple[date, str]], year: int) -> str | None:
    names = sorted({DISPLAY_NAMES.get(name, name) for when, name in event_dates if when.year == year})
    return ", ".join(names) if names else None


def intro(rows: gpd.GeoDataFrame) -> Image.Image:
    image = shell("01 / UNA IMAGEN QUE PARECE QUIETA")
    draw = ImageDraw.Draw(image)
    write(draw, (72, 238), "Sudamérica no", 68, PAPER, True)
    write(draw, (72, 320), "siempre se vio así.", 68, GOLD, True)
    draw_map(image, rows)
    panel(draw, (72, 1490, 1008, 1660), GOLD)
    write(draw, (108, 1522), "1886–2019", 47, PAPER, True)
    paragraph(draw, (385, 1530), "No es una historia completa: es una secuencia de límites codificados.", 28, 560)
    return image


def timeline_frame(rows: gpd.GeoDataFrame, year: int, event_dates: list[tuple[date, str]]) -> Image.Image:
    image = shell("02 / FRONTERAS, AÑO POR AÑO")
    draw = ImageDraw.Draw(image)
    write(draw, (72, 232), "Los países parecen fijos.", 45, PAPER, True)
    write(draw, (72, 292), "Sus contornos, no siempre.", 42, GOLD, True)
    draw_map(image, rows)
    panel(draw, (72, 1490, 487, 1660), GOLD)
    write(draw, (108, 1513), str(year), 82, PAPER, True)
    write(draw, (108, 1612), "año del mapa", 23, MUTED)
    panel(draw, (514, 1490, 1008, 1660), "#75c5ad")
    count = events_so_far(event_dates, year)
    write(draw, (550, 1515), str(count), 55, PAPER, True)
    write(draw, (645, 1532), "cambios de período", 25, PAPER)
    write(draw, (550, 1580), "registrados en la selección", 23, MUTED)
    event = event_for_year(event_dates, year)
    if event:
        panel(draw, (72, 1684, 1008, 1750), "#75c5ad")
        write(draw, (108, 1703), f"Nuevo período: {event}", 25, PAPER)
    else:
        write(draw, (72, 1707), "Sin transición de período en este año dentro del conjunto.", 22, MUTED)
    return image


def limit_card() -> Image.Image:
    image = shell("03 / LO QUE EL MAPA SÍ Y NO DICE")
    draw = ImageDraw.Draw(image)
    write(draw, (72, 242), "Una frontera no es", 57, PAPER, True)
    write(draw, (72, 315), "toda una historia.", 57, GOLD, True)
    cards = [
        ("SÍ", "Geometrías históricas", "CShapes codifica períodos de fronteras y estatus."),
        ("NO", "Una sentencia territorial", "El video no resuelve reclamaciones ni sustituye archivos locales."),
        ("LÍMITE", "Cobertura hasta 2019", "No se presentan años posteriores como si fueran observados."),
    ]
    for index, (tag, title, detail) in enumerate(cards):
        y = 495 + index * 295
        panel(draw, (72, y, 1008, y + 246), GOLD if index == 0 else "#75c5ad")
        write(draw, (108, y + 29), tag, 25, GOLD if index == 0 else "#75c5ad")
        write(draw, (108, y + 78), title, 40, PAPER, True)
        paragraph(draw, (108, y + 142), detail, 27, 815)
    write(draw, (72, 1455), "Fuente: CShapes 2.0 · Schvitz et al. (2022)", 26, GOLD)
    paragraph(draw, (72, 1515), "Mira el método, los datos y la cita completa antes de reutilizar esta pieza.", 30, 870, PAPER)
    return image


def render(shapefile: Path, output: Path, fps: int = 24, quick: bool = False) -> dict:
    periods = load_periods(shapefile)
    event_dates = transitions(periods)
    opening = intro(active_periods(periods, FIRST_YEAR))
    closing = limit_card()
    years = list(range(FIRST_YEAR, LAST_YEAR + 1))
    frames_per_year = 2 if quick else 5
    output.parent.mkdir(parents=True, exist_ok=True)
    import imageio_ffmpeg
    writer = imageio_ffmpeg.write_frames(
        str(output), (WIDTH, HEIGHT), fps=fps, codec="libx264", pix_fmt_in="rgb24",
        pix_fmt_out="yuv420p", macro_block_size=2, quality=8, ffmpeg_log_level="error",
        output_params=["-movflags", "+faststart", "-preset", "veryfast", "-threads", "2"],
    )
    writer.send(None)
    frames = 0
    try:
        for _ in range(fps * 4):
            writer.send(opening.tobytes())
            frames += 1
        for year in years:
            frame = timeline_frame(active_periods(periods, year), year, event_dates).tobytes()
            for _ in range(frames_per_year):
                writer.send(frame)
                frames += 1
        for _ in range(fps * 5):
            writer.send(closing.tobytes())
            frames += 1
    finally:
        writer.close()
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(output), "-f", "null", "-"],
                   check=True, capture_output=True)
    result = {
        "status": "silent_visual_draft_not_for_publication",
        "title": "Sudamérica no siempre se vio así · 1886–2019",
        "coverage": {"first_year": FIRST_YEAR, "last_year": LAST_YEAR, "not_observed_after": LAST_YEAR},
        "dataset": {"name": "CShapes 2.0", "url": SOURCE_URL, "license": SOURCE_LICENSE,
                    "citation": SOURCE_CITATION, "source_sha256": sha256(shapefile.read_bytes()).hexdigest()},
        "scope": "South America plus Panama and French Guiana to preserve the regional periods represented by CShapes.",
        "limitation": "Historical GIS periods are not a complete account of territorial, legal, indigenous or lived histories.",
        "fps": fps, "frames": frames, "duration_seconds": round(frames / fps, 2),
        "output_sha256": sha256(output.read_bytes()).hexdigest(),
        "output": str(output),
        "transitions_in_selected_scope": len(event_dates),
    }
    output.with_suffix(".json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("shapefile", type=Path, help="Official CShapes 2.0 .shp file")
    parser.add_argument("--output", type=Path, default=Path("artifacts/sudamerica-fronteras-1886-2019.mp4"))
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--quick", action="store_true", help="Reduce map frames for a local QA draft")
    args = parser.parse_args()
    print(json.dumps(render(args.shapefile, args.output, args.fps, args.quick), ensure_ascii=False, indent=2))
