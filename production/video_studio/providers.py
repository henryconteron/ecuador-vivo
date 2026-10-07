"""Download adapters for documented, free-to-access climate data products.

The adapters keep the original source files and query details beside every
derived raster/CSV.  They deliberately do not interpolate station readings or
fill missing observations.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
import json
import math
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
from rasterio.windows import from_bounds

from data import store_upload
from model import ROOT, STORE


INAMHI_BASE = "https://inamhi.gob.ec/api_rest/"
INAMHI_APP_ID = "vs_1d_inh"
INAMHI_VIEWER_URL = "https://inamhi.gob.ec/ddia/visor"
INAMHI_STATIONS_URL = (
    INAMHI_BASE
    + "station_information/estaciones/visores/diarios/?"
    + urllib.parse.urlencode({"id_aplicacion": INAMHI_APP_ID})
)
INAMHI_PARAMETERS_URL = INAMHI_BASE + "station_information/parametros/"
INAMHI_DAILY_URL = INAMHI_BASE + "station_data_daily/data"
INAMHI_PUBLIC_ACCESS_URL = "https://www.inamhi.gob.ec/info-liberada/"

POWER_DAILY_URL = "https://power.larc.nasa.gov/api/temporal/daily/regional"
POWER_DOCS_URL = "https://power.larc.nasa.gov/docs/services/api/temporal/daily/"

CHIRPS3_INFO_URL = "https://chc.ucsb.edu/data/chirps3"
CHIRPS3_ROOT = "https://data.chc.ucsb.edu/products/CHIRPS/v3.0/"

# The acquisition rectangle includes the continental territory and the large
# Galápagos islands. The renderer still clips the main map to Ecuador's border.
ECUADOR_DATA_BBOX = (-92.5, -5.5, -75.0, 2.0)
ECUADOR_MAP_BBOX = (-81.5, -5.2, -75.0, 1.8)

CHIRPS_PRODUCTS = {
    "prelim": {
        "label": "CHIRPS v3 preliminar · satélite IMERG",
        "path": "daily/prelim/sat/{year}/chirps-v3.0.prelim.{date}.tif",
        "minimum_date": dt.date(2001, 1, 1),
        "method": (
            "Producto preliminar diario basado en la partición satelital IMERG; "
            "puede actualizarse cuando se publique el producto final."
        ),
        "resolution": "CHIRPS v3 · 0,05° (~5,6 km)",
    },
    "final_sat": {
        "label": "CHIRPS v3 final · partición satelital IMERG",
        "path": "daily/final/sat/cogs/{year}/chirps-v3.0.sat.{date}.cog",
        "minimum_date": dt.date(2001, 1, 1),
        "method": (
            "Estimación diaria derivada del total pentadal CHIRPS v3; las "
            "proporciones diarias usan IMERG Late V07."
        ),
        "resolution": "CHIRPS v3 · 0,05° (~5,6 km)",
    },
    "final_rnl": {
        "label": "CHIRPS v3 final · partición de reanálisis ERA5",
        "path": "daily/final/rnl/cogs/{year}/chirps-v3.0.rnl.{date}.cog",
        "minimum_date": dt.date(1981, 1, 1),
        "method": (
            "Estimación diaria derivada del total pentadal CHIRPS v3; las "
            "proporciones diarias usan ERA5."
        ),
        "resolution": "CHIRPS v3 · 0,05° (~5,6 km)",
    },
}

POWER_VARIABLES = {
    "PRECTOTCORR": {
        "label": "Precipitación corregida",
        "units": "mm/día",
        "legend": "PRECIPITACIÓN DIARIA",
        "kind": "precipitation",
        "title": "PRECIPITACIÓN EN ECUADOR",
        "scale_note": "Escala fija · NASA POWER",
        "stops": [0, 1, 5, 10, 20, 40, 70, 120],
    },
    "T2M": {
        "label": "Temperatura media del aire a 2 m",
        "units": "°C",
        "legend": "TEMPERATURA MEDIA",
        "kind": "temperature",
        "title": "TEMPERATURA EN ECUADOR",
        "scale_note": "Escala fija · NASA POWER",
        "stops": [0, 5, 10, 15, 20, 25, 30, 35],
    },
    "T2M_MAX": {
        "label": "Temperatura máxima del aire a 2 m",
        "units": "°C",
        "legend": "TEMPERATURA MÁXIMA",
        "kind": "temperature",
        "title": "TEMPERATURA MÁXIMA EN ECUADOR",
        "scale_note": "Escala fija · NASA POWER",
        "stops": [0, 5, 10, 15, 20, 25, 30, 40],
    },
    "T2M_MIN": {
        "label": "Temperatura mínima del aire a 2 m",
        "units": "°C",
        "legend": "TEMPERATURA MÍNIMA",
        "kind": "temperature",
        "title": "TEMPERATURA MÍNIMA EN ECUADOR",
        "scale_note": "Escala fija · NASA POWER",
        "stops": [-5, 0, 5, 10, 15, 20, 25, 30],
    },
    "WS10M": {
        "label": "Velocidad media del viento a 10 m",
        "units": "m/s",
        "legend": "VELOCIDAD DEL VIENTO",
        "kind": "wind_speed",
        "title": "VIENTO EN ECUADOR",
        "scale_note": "Escala fija · NASA POWER",
        "stops": [0, 1, 2, 3, 5, 7, 10, 15],
    },
    "RH2M": {
        "label": "Humedad relativa a 2 m",
        "units": "%",
        "legend": "HUMEDAD RELATIVA",
        "kind": "percent",
        "title": "HUMEDAD EN ECUADOR",
        "scale_note": "Escala fija · NASA POWER",
        "stops": [0, 15, 30, 45, 60, 75, 90, 100],
    },
}


def _as_date(value):
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value))


def _checked_range(start, end, *, maximum_days, minimum_date=dt.date(1981, 1, 1)):
    first, last = _as_date(start), _as_date(end)
    if first > last:
        raise ValueError("La fecha inicial debe ser anterior o igual a la final.")
    if first < minimum_date:
        raise ValueError(f"La fuente no ofrece datos antes de {minimum_date.isoformat()}.")
    if last > dt.date.today():
        raise ValueError("No se permiten fechas futuras.")
    count = (last - first).days + 1
    if count > maximum_days:
        raise ValueError(f"Este conector permite hasta {maximum_days} fechas por descarga.")
    return first, last, [first + dt.timedelta(days=i) for i in range(count)]


def _request_bytes(url, *, method="GET", body=None, headers=None, timeout=60):
    request_headers = {
        "User-Agent": "EcuadorVivo-VideoStudio/1.0 (local scientific data workflow)",
        "Accept": "application/json, text/csv, image/tiff, */*",
    }
    if headers:
        request_headers.update(headers)
    request = urllib.request.Request(url, data=body, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        message = error.read(1200).decode("utf-8", "replace")
        raise ValueError(
            f"La fuente respondió HTTP {error.code}. "
            "Comprueba si ese producto/fecha está publicado. "
            + message[:500]
        ) from error
    except (urllib.error.URLError, TimeoutError) as error:
        raise ValueError(f"No se pudo conectar con la fuente: {error}") from error


def _request_json(url, *, method="GET", payload=None, timeout=45):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    content = _request_bytes(url, method=method, body=body, headers=headers, timeout=timeout)
    try:
        return json.loads(content.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("La respuesta de la fuente no llegó como JSON válido.") from error


def _new_download_dir(prefix):
    folder = STORE / "downloads" / f"{prefix}-{dt.datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:8]}"
    folder.mkdir(parents=True, exist_ok=False)
    return folder


def _write_json(path, payload):
    Path(path).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _bundle(folder, bundle_name, members):
    target = folder / bundle_name
    temporary = target.with_suffix(target.suffix + ".part")
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, arcname in members:
            archive.write(path, arcname=arcname)
    temporary.replace(target)
    return target


def chirps_v3_url(day, product):
    """Return an official CHIRPS v3 daily file URL for one date."""
    if product not in CHIRPS_PRODUCTS:
        raise ValueError("Selecciona un producto CHIRPS v3 reconocido.")
    day = _as_date(day)
    metadata = CHIRPS_PRODUCTS[product]
    if day < metadata["minimum_date"]:
        raise ValueError(
            f"{metadata['label']} comienza el {metadata['minimum_date'].isoformat()}."
        )
    if day > dt.date.today():
        raise ValueError("No se permiten fechas futuras.")
    relative = metadata["path"].format(year=day.year, date=day.strftime("%Y.%m.%d"))
    return CHIRPS3_ROOT + relative


def _chirps_clip_tiff(url, clip_bbox):
    """Read a small Ecuador window from a remote CHIRPS GeoTIFF/COG."""
    virtual_path = "/vsicurl/" + url
    try:
        with rasterio.Env(
            GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
            CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.cog",
            GDAL_HTTP_MAX_RETRY="2",
            GDAL_HTTP_RETRY_DELAY="1",
        ):
            with rasterio.open(virtual_path) as source:
                if source.count < 1 or not source.crs:
                    raise ValueError("El ráster CHIRPS no tiene banda o CRS legible.")
                window = from_bounds(*clip_bbox, transform=source.transform)
                window = window.round_offsets().round_lengths()
                col0 = max(0, int(window.col_off))
                row0 = max(0, int(window.row_off))
                col1 = min(source.width, int(window.col_off + window.width))
                row1 = min(source.height, int(window.row_off + window.height))
                if col1 <= col0 or row1 <= row0:
                    raise ValueError("La ventana solicitada no cruza el ráster fuente.")
                clipped_window = rasterio.windows.Window(
                    col0, row0, col1 - col0, row1 - row0
                )
                values = source.read(1, window=clipped_window).astype("float32")
                source_nodata = source.nodata
                if source_nodata is not None:
                    values[~np.isfinite(values)] = -9999.0
                    values[np.isclose(values, source_nodata)] = -9999.0
                else:
                    values[~np.isfinite(values)] = -9999.0
                    values[np.isclose(values, -9999.0)] = -9999.0
                if not np.any((values != -9999.0) & np.isfinite(values)):
                    raise ValueError("El archivo CHIRPS no contiene valores válidos en Ecuador.")
                profile = source.profile.copy()
                profile.update(
                    driver="GTiff",
                    width=values.shape[1],
                    height=values.shape[0],
                    count=1,
                    dtype="float32",
                    nodata=-9999.0,
                    transform=source.window_transform(clipped_window),
                    compress="deflate",
                    tiled=False,
                )
    except rasterio.errors.RasterioError as error:
        raise ValueError(
            "No se pudo leer el GeoTIFF remoto de CHIRPS. Puede que aún no esté "
            "publicado o que el servidor esté temporalmente fuera de servicio."
        ) from error

    with MemoryFile() as memory:
        with memory.open(**profile) as clipped:
            clipped.write(values, 1)
        return memory.read()


def download_chirps_v3(start, end, product="prelim", *, progress=None):
    """Download/crop a daily CHIRPS v3 series and prepare it for the editor.

    The product is clipped to an Ecuador-plus-Galápagos bounding rectangle.
    The video renderer applies the national outline later. 31-day packages
    limit network and disk use; long animations can still use the editor's
    existing on-demand CHIRPS path or be assembled in month-sized packages.
    """
    if product not in CHIRPS_PRODUCTS:
        raise ValueError("Selecciona un producto CHIRPS v3 reconocido.")
    minimum_date = CHIRPS_PRODUCTS[product]["minimum_date"]
    first, last, days = _checked_range(
        start, end, maximum_days=31, minimum_date=minimum_date
    )
    folder = _new_download_dir("chirps-v3")
    entries = []
    members = []
    manifest_files = []
    for index, day in enumerate(days, start=1):
        url = chirps_v3_url(day, product)
        payload = _chirps_clip_tiff(url, ECUADOR_DATA_BBOX)
        digest = hashlib.sha256(payload).hexdigest()
        local_tif = store_upload(f"chirps-v3-{product}-{day.isoformat()}.tif", payload)
        package_tif = folder / f"chirps-v3-{product}-{day:%Y%m%d}.tif"
        package_tif.write_bytes(payload)
        entries.append({
            "date": day.isoformat(),
            "band": 1,
            "path": str(local_tif),
            "source_url": url,
            "artifact_sha256": digest,
        })
        members.append((package_tif, package_tif.name))
        manifest_files.append({
            "date": day.isoformat(),
            "url": url,
            "package_file": package_tif.name,
            "clipped_geotiff_sha256": digest,
        })
        if progress:
            progress(index, len(days), day.isoformat())

    product_info = CHIRPS_PRODUCTS[product]
    manifest = {
        "provider": "Climate Hazards Center, University of California Santa Barbara",
        "dataset": "CHIRPS v3 daily",
        "product": product,
        "product_label": product_info["label"],
        "daily_method_note": product_info["method"],
        "citation": "Climate Hazards Center (CHC), UC Santa Barbara. CHIRPS v3 daily.",
        "source_url": CHIRPS3_INFO_URL,
        "retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "requested_period": {"start": first.isoformat(), "end": last.isoformat()},
        "spatial_resolution": product_info["resolution"],
        "units": "mm/day",
        "clip_bbox_wgs84": list(ECUADOR_DATA_BBOX),
        "files": manifest_files,
        "interpretation": (
            "Los productos diarios de CHIRPS v3 se derivan de los acumulados "
            "pentadales; no representan necesariamente una ventana diaria "
            "uniforme de observación de todos los pluviómetros."
        ),
        "license_note": "El CHC declara CHIRPS como dominio público en la medida permitida por la ley.",
    }
    manifest_path = folder / "metadata.json"
    _write_json(manifest_path, manifest)
    members.append((manifest_path, "metadata.json"))
    zip_path = _bundle(
        folder,
        f"chirps-v3-{product}-{first:%Y%m%d}-{last:%Y%m%d}.zip",
        members,
    )
    return {
        "provider": "CHIRPS v3",
        "product": product,
        "product_label": product_info["label"],
        "start": first.isoformat(),
        "end": last.isoformat(),
        "count": len(entries),
        "entries": entries,
        "manifest": manifest,
        "manifest_path": str(manifest_path),
        "zip_path": str(zip_path),
        "source_url": CHIRPS3_INFO_URL,
        "citation": f"{product_info['label']} · CHC/UCSB",
        "units": "mm/día",
        "variable": "Precipitación CHIRPS v3",
        "legend": "LLUVIA ACUMULADA",
        "resolution_note": product_info["resolution"],
        "note": product_info["method"],
        "data_bbox": list(ECUADOR_DATA_BBOX),
    }


def power_daily_regions(bbox=ECUADOR_DATA_BBOX):
    """Split a regional extent into legal POWER requests with a small overlap.

    The API accepts regional rectangles no wider than 10 degrees and rejects
    rectangles narrower than 2 degrees. A 0.625-degree overlap preserves the
    native longitude grid across split boundaries; duplicate grid cells are
    removed after retrieval.
    """
    west, south, east, north = (float(value) for value in bbox)
    if west >= east or south >= north:
        raise ValueError("El área NASA POWER debe tener límites válidos.")

    def split_axis(low, high):
        span = high - low
        if span < 2:
            raise ValueError("NASA POWER requiere áreas de al menos 2° por lado.")
        if span <= 10:
            return [(low, high)]
        overlap = 0.625
        count = math.ceil((span - overlap) / (10 - overlap))
        step = (span - overlap) / count
        intervals = []
        for index in range(count):
            start = low + index * step
            finish = high if index == count - 1 else low + (index + 1) * step + overlap
            intervals.append((start, min(finish, high)))
        if any((finish - start) > 10.000001 for start, finish in intervals):
            raise ValueError("No se pudo dividir el área en solicitudes POWER válidas.")
        return intervals

    longitude_parts = split_axis(west, east)
    latitude_parts = split_axis(south, north)
    return [
        (part_west, part_south, part_east, part_north)
        for part_south, part_north in latitude_parts
        for part_west, part_east in longitude_parts
    ]


def power_daily_url(start, end, parameter, bbox=ECUADOR_DATA_BBOX):
    """Build a one-variable NASA POWER daily regional request for one legal tile."""
    if parameter not in POWER_VARIABLES:
        raise ValueError("Selecciona una variable NASA POWER admitida.")
    first, last, _ = _checked_range(start, end, maximum_days=366)
    west, south, east, north = bbox
    if (east - west) > 10 or (north - south) > 10:
        raise ValueError("Divide áreas mayores a 10° en varias solicitudes NASA POWER.")
    if (east - west) < 2 or (north - south) < 2:
        raise ValueError("NASA POWER requiere áreas de al menos 2° por lado.")
    query = urllib.parse.urlencode({
        "latitude-min": f"{south:g}",
        "latitude-max": f"{north:g}",
        "longitude-min": f"{west:g}",
        "longitude-max": f"{east:g}",
        "parameters": parameter,
        "community": "SB",
        "start": first.strftime("%Y%m%d"),
        "end": last.strftime("%Y%m%d"),
        "format": "CSV",
        "time-standard": "UTC",
    })
    return f"{POWER_DAILY_URL}?{query}"


def parse_power_regional_csv(text, parameter, start=None, end=None):
    """Parse NASA POWER regional CSV rows without converting missing values to 0."""
    if parameter not in POWER_VARIABLES:
        raise ValueError("Variable NASA POWER desconocida.")
    lines = str(text).lstrip("\ufeff").splitlines()
    header_index = next(
        (i for i, line in enumerate(lines) if line.strip().upper().startswith("LAT,LON,YEAR,MO,DY,")),
        None,
    )
    if header_index is None:
        raise ValueError("La respuesta CSV de NASA POWER no contiene la tabla regional esperada.")
    rows = []
    first = _as_date(start) if start is not None else None
    last = _as_date(end) if end is not None else None
    reader = csv.DictReader(lines[header_index:])
    for source_row in reader:
        row = {str(key).strip().upper(): str(value or "").strip() for key, value in source_row.items()}
        try:
            day = dt.date(int(row["YEAR"]), int(row["MO"]), int(row["DY"]))
            lat, lon = float(row["LAT"]), float(row["LON"])
            value = float(row[parameter])
        except (KeyError, TypeError, ValueError) as error:
            continue
        if (first is not None and day < first) or (last is not None and day > last):
            continue
        if not math.isfinite(value) or value <= -900:
            value = None
        rows.append({"date": day.isoformat(), "lat": lat, "lon": lon, "value": value})
    if not rows:
        raise ValueError("NASA POWER no devolvió observaciones dentro del periodo elegido.")
    return rows


def _power_geotiff_bytes(rows, parameter):
    day_keys = sorted({row["date"] for row in rows})
    lons = sorted({round(float(row["lon"]), 7) for row in rows})
    lats = sorted({round(float(row["lat"]), 7) for row in rows})
    if len(lons) < 2 or len(lats) < 2:
        raise ValueError("La grilla regional devuelta por NASA POWER es incompleta.")
    dx_values = np.diff(lons)
    dy_values = np.diff(lats)
    dx = float(np.median(dx_values))
    dy = float(np.median(dy_values))
    if dx <= 0 or dy <= 0:
        raise ValueError("No se pudo identificar el espaciado de la grilla NASA POWER.")
    lon_index = {value: index for index, value in enumerate(lons)}
    lat_index = {value: index for index, value in enumerate(reversed(lats))}
    array = np.full((len(day_keys), len(lats), len(lons)), -9999.0, dtype="float32")
    day_index = {day: index for index, day in enumerate(day_keys)}
    for row in rows:
        if row["value"] is None:
            continue
        lon = round(float(row["lon"]), 7)
        lat = round(float(row["lat"]), 7)
        array[day_index[row["date"]], lat_index[lat], lon_index[lon]] = float(row["value"])
    if any(not np.any(array[index] != -9999.0) for index in range(len(day_keys))):
        missing = [day_keys[i] for i in range(len(day_keys)) if not np.any(array[i] != -9999.0)]
        raise ValueError("NASA POWER no tiene celdas válidas para: " + ", ".join(missing[:10]))

    transform = from_origin(lons[0] - dx / 2, lats[-1] + dy / 2, dx, dy)
    with MemoryFile() as memory:
        with memory.open(
            driver="GTiff",
            width=len(lons),
            height=len(lats),
            count=len(day_keys),
            crs="EPSG:4326",
            transform=transform,
            dtype="float32",
            nodata=-9999.0,
            compress="deflate",
        ) as destination:
            for index, day in enumerate(day_keys, start=1):
                destination.write(array[index - 1], index)
                destination.set_band_description(index, day)
            destination.update_tags(
                AREA_OR_POINT="Point",
                source="NASA POWER regional daily API",
                parameter=parameter,
                spatial_resolution=f"{dy:g} x {dx:g} degrees",
            )
        return memory.read(), day_keys, dx, dy


def download_power_regional(start, end, parameter, *, progress=None):
    """Download NASA POWER daily regional grid, GeoTIFF, CSV and receipt."""
    if parameter not in POWER_VARIABLES:
        raise ValueError("Selecciona una variable NASA POWER admitida.")
    first, last, _ = _checked_range(start, end, maximum_days=366)
    regions = power_daily_regions(ECUADOR_DATA_BBOX)
    requests = []
    source_rows = {}
    for index, region in enumerate(regions, start=1):
        url = power_daily_url(first, last, parameter, bbox=region)
        raw = _request_bytes(url, timeout=180)
        text = raw.decode("utf-8-sig", "replace")
        rows_for_region = parse_power_regional_csv(text, parameter, first, last)
        requests.append({
            "region": list(region),
            "url": url,
            "bytes": raw,
            "sha256": hashlib.sha256(raw).hexdigest(),
        })
        for row in rows_for_region:
            key = (row["date"], round(row["lat"], 7), round(row["lon"], 7))
            if key in source_rows:
                previous = source_rows[key]["value"]
                current = row["value"]
                if previous is not None and current is not None and not math.isclose(
                    previous, current, rel_tol=1e-6, abs_tol=1e-6
                ):
                    raise ValueError(
                        "NASA POWER devolvió valores distintos en la zona de solape "
                        f"({row['date']}, {row['lat']}, {row['lon']}); revisa antes de unir."
                    )
                if previous is None and current is not None:
                    source_rows[key] = row
            else:
                source_rows[key] = row
        if progress:
            progress(index, len(regions), f"Región {index}/{len(regions)}")
    rows = list(source_rows.values())
    rows.sort(key=lambda row: (row["date"], row["lat"], row["lon"]))
    if not rows:
        raise ValueError("NASA POWER no devolvió observaciones dentro del periodo elegido.")
    info = POWER_VARIABLES[parameter]
    tiff_bytes, dates, dx, dy = _power_geotiff_bytes(rows, parameter)
    imported_tiff = store_upload(
        f"nasa-power-{parameter}-{first:%Y%m%d}-{last:%Y%m%d}.tif",
        tiff_bytes,
    )
    raster_digest = hashlib.sha256(tiff_bytes).hexdigest()
    source_urls = [item["url"] for item in requests]
    entries = [
        {
            "date": day,
            "band": index,
            "path": str(imported_tiff),
            "source_url": source_urls,
            "artifact_sha256": raster_digest,
        }
        for index, day in enumerate(dates, start=1)
    ]
    folder = _new_download_dir("nasa-power")
    csv_path = folder / f"nasa-power-{parameter}-{first:%Y%m%d}-{last:%Y%m%d}.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["LAT", "LON", "YEAR", "MO", "DY", parameter])
        writer.writeheader()
        for row in rows:
            day = dt.date.fromisoformat(row["date"])
            writer.writerow({
                "LAT": row["lat"], "LON": row["lon"], "YEAR": day.year,
                "MO": day.month, "DY": day.day,
                parameter: "-999" if row["value"] is None else row["value"],
            })
    source_csv_paths = []
    for index, item in enumerate(requests, start=1):
        source_csv_path = folder / f"source-region-{index:02d}.csv"
        source_csv_path.write_bytes(item["bytes"])
        source_csv_paths.append(source_csv_path)
    tiff_path = folder / f"nasa-power-{parameter}-{first:%Y%m%d}-{last:%Y%m%d}.tif"
    tiff_path.write_bytes(tiff_bytes)
    day_set = set(dates)
    requested_days = [first + dt.timedelta(days=i) for i in range((last - first).days + 1)]
    missing_days = [day.isoformat() for day in requested_days if day.isoformat() not in day_set]
    manifest = {
        "provider": "NASA POWER · NASA Langley Research Center",
        "dataset": "POWER Daily API · Regional",
        "parameter": parameter,
        "parameter_name": info["label"],
        "units": info["units"],
        "citation": "NASA POWER, NASA Langley Research Center. Daily Regional API.",
        "source_url": POWER_DOCS_URL,
        "request_urls": source_urls,
        "source_csv_sha256": [item["sha256"] for item in requests],
        "source_regions_wgs84": [item["region"] for item in requests],
        "merged_csv_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
        "retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "requested_period": {"start": first.isoformat(), "end": last.isoformat()},
        "returned_dates": dates,
        "derived_geotiff_sha256": raster_digest,
        "missing_dates": missing_days,
        "spatial_resolution_degrees": {"latitude": dy, "longitude": dx},
        "clip_bbox_wgs84": list(ECUADOR_DATA_BBOX),
        "api_extent_note": (
            "La cobertura se obtuvo en varias solicitudes porque la API regional "
            "limita cada rectángulo a 10°; las zonas solapadas se deduplicaron "
            "y se verificaron antes de crear la grilla unificada."
        ),
        "time_standard": "UTC",
        "native_resolution_note": (
            "La API regional reporta una grilla cercana a 0.5° x 0.625° "
            "(aprox. 50–60 km); los valores meteorológicos proceden de MERRA-2."
        ),
        "interpretation": (
            "Estimación de grilla para contexto regional; no es una lectura de "
            "pluviómetro/estación INAMHI ni tiene precisión para calles o "
            "microclimas. Las estadísticas por provincias pequeñas requieren revisión."
        ),
    }
    manifest_path = folder / "metadata.json"
    _write_json(manifest_path, manifest)
    zip_path = _bundle(
        folder,
        f"nasa-power-{parameter}-{first:%Y%m%d}-{last:%Y%m%d}.zip",
        [
            *((path, path.name) for path in source_csv_paths),
            (csv_path, csv_path.name),
            (tiff_path, tiff_path.name),
            (manifest_path, "metadata.json"),
        ],
    )
    if progress:
        progress(len(dates), len(dates), dates[-1])
    return {
        "provider": "NASA POWER",
        "parameter": parameter,
        "parameter_name": info["label"],
        "start": first.isoformat(),
        "end": last.isoformat(),
        "count": len(dates),
        "missing_dates": missing_days,
        "entries": entries,
        "manifest": manifest,
        "manifest_path": str(manifest_path),
        "csv_path": str(csv_path),
        "tiff_path": str(tiff_path),
        "zip_path": str(zip_path),
        "source_url": source_urls[0] if len(source_urls) == 1 else source_urls,
        "request_urls": source_urls,
        "citation": manifest["citation"],
        "units": info["units"],
        "variable": info["label"],
        "title": info["title"],
        "legend": info["legend"],
        # The editor's storage kind is continuous/categorical. Keep the
        # scientific profile separate so it cannot leak into model validation.
        "kind": "continuous",
        "profile_kind": info["kind"],
        "stops": list(info["stops"]),
        "scale_note": info["scale_note"],
        "resolution_note": manifest["native_resolution_note"],
        "note": manifest["interpretation"],
        "data_bbox": list(ECUADOR_DATA_BBOX),
    }


def inamhi_stations():
    """List stations exposed by the official INAMHI daily viewer API.

    The current repository snapshot enriches the API IDs with station names,
    canton/province and coordinates where available; any live station not in
    that snapshot remains selectable by its official code.
    """
    response = _request_json(INAMHI_STATIONS_URL)
    if isinstance(response, dict):
        response = response.get("results", response.get("data", []))
    if not isinstance(response, list):
        raise ValueError("El catálogo diario de INAMHI devolvió un formato inesperado.")

    local = {}
    path = ROOT / "data" / "geojson" / "estaciones-inamhi.geojson"
    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            for feature in payload.get("features", []):
                properties = feature.get("properties", {})
                station_id = str(properties.get("id_estacion", ""))
                coordinates = (feature.get("geometry") or {}).get("coordinates", [])
                local[station_id] = {
                    "name": properties.get("nombre", ""),
                    "code": properties.get("codigo", ""),
                    "category": properties.get("categoria", ""),
                    "state": properties.get("estado", ""),
                    "owner": properties.get("propietario", ""),
                    "province": properties.get("provincia", ""),
                    "canton": properties.get("canton", ""),
                    "altitude_m": properties.get("altitud_m"),
                    "longitude": coordinates[0] if len(coordinates) >= 2 else None,
                    "latitude": coordinates[1] if len(coordinates) >= 2 else None,
                }
        except (OSError, json.JSONDecodeError, TypeError):
            local = {}

    result = []
    for item in response:
        if not isinstance(item, dict) or item.get("id_estacion") is None:
            continue
        station_id = str(item["id_estacion"])
        known = local.get(station_id, {})
        longitude = known.get("longitude")
        latitude = known.get("latitude")
        try:
            if longitude is None:
                longitude = float(item["longitud"])
            if latitude is None:
                latitude = float(item["latitud"])
        except (KeyError, TypeError, ValueError):
            longitude = latitude = None
        result.append({
            "id": int(item["id_estacion"]),
            "code": known.get("code") or str(item.get("codigo", "")),
            "name": known.get("name") or str(item.get("nombre", "")),
            "province": known.get("province", ""),
            "canton": known.get("canton", ""),
            "category": known.get("category", ""),
            "state": item.get("estado_transmision") or known.get("state", ""),
            "owner": item.get("propietario") or known.get("owner", ""),
            "longitude": longitude,
            "latitude": latitude,
            "altitude_m": known.get("altitude_m", item.get("altitud")),
        })
    return sorted(result, key=lambda row: (
        row["province"] or "ZZZ", row["canton"] or "ZZZ",
        row["name"] or row["code"], row["code"],
    ))


def inamhi_parameters(station_id):
    """Return measured variable/statistic choices for one live INAMHI station."""
    query = urllib.parse.urlencode({
        "id_estacion": int(station_id),
        "id_aplicacion": INAMHI_APP_ID,
    })
    response = _request_json(INAMHI_PARAMETERS_URL + "?" + query)
    if isinstance(response, dict):
        response = response.get("results", response.get("data", []))
    if not isinstance(response, list):
        raise ValueError("INAMHI devolvió un catálogo de variables no reconocido.")
    options = []
    for group in response:
        if not isinstance(group, dict):
            continue
        for parameter in group.get("params", []) or []:
            code = parameter.get("nemonico")
            if not code:
                continue
            options.append({
                "code": str(code),
                "name": str(group.get("name_param", parameter.get("descripcion_parametro", "Variable"))),
                "units": str(parameter.get("simbolo_unidad", group.get("simbolo_unidad", ""))),
                "statistic": str(parameter.get("estadistico", "")),
                "description": str(parameter.get("descripcion_parametro", "")),
                "latest": str(parameter.get("fecha_ultimo_dato", ""))[:10],
            })
    return sorted(options, key=lambda row: (row["name"], row["statistic"], row["code"]))


def download_inamhi_daily(station, parameter, start, end):
    """Download a station daily series; preserve gaps and the API's real dates."""
    first, last, requested_days = _checked_range(start, end, maximum_days=31)
    code = str(parameter.get("code", "")).strip()
    if not code:
        raise ValueError("Selecciona una variable diaria válida de INAMHI.")
    if not station or station.get("id") is None:
        raise ValueError("Selecciona una estación INAMHI.")
    payload = {
        "start_date": first.isoformat(),
        "end_date": last.isoformat(),
        "id_estacion": int(station["id"]),
        "table_names": [code],
    }
    response = _request_json(
        INAMHI_DAILY_URL,
        method="POST",
        payload=payload,
        timeout=60,
    )
    if isinstance(response, list):
        response = next(
            (
                item for item in response
                if isinstance(item, dict) and item.get("nemonico") == code
            ),
            {},
        )
    if not isinstance(response, dict):
        raise ValueError("La API diaria de INAMHI devolvió un formato inesperado.")
    raw_rows = response.get("data", [])
    if not isinstance(raw_rows, list):
        raise ValueError("La serie diaria de INAMHI no contiene una tabla reconocible.")

    rows = []
    returned_raw_dates = []
    for row in raw_rows:
        if not isinstance(row, dict):
            continue
        raw_date = str(row.get("fecha_toma_dato", ""))
        try:
            day = dt.date.fromisoformat(raw_date[:10])
            value = float(row.get("valor"))
        except (TypeError, ValueError):
            continue
        returned_raw_dates.append(day.isoformat())
        if not first <= day <= last or not math.isfinite(value):
            continue
        rows.append({
            "date": day.isoformat(),
            "station_id": int(station["id"]),
            "station_code": station.get("code", ""),
            "station_name": station.get("name", ""),
            "province": station.get("province", ""),
            "canton": station.get("canton", ""),
            "longitude": station.get("longitude"),
            "latitude": station.get("latitude"),
            "altitude_m": station.get("altitude_m"),
            "variable": parameter.get("name", ""),
            "statistic": parameter.get("statistic", ""),
            "parameter_code": code,
            "value": value,
            "units": parameter.get("units", ""),
        })
    rows.sort(key=lambda row: row["date"])
    if not rows:
        raw_bounds = (
            f"La respuesta entregó fechas {min(returned_raw_dates)}–{max(returned_raw_dates)}. "
            if returned_raw_dates else ""
        )
        raise ValueError(
            "INAMHI no devolvió observaciones dentro del periodo solicitado. "
            + raw_bounds
            + "La API pública del visor puede limitar la consulta a una ventana reciente."
        )

    observed = {row["date"] for row in rows}
    missing = [day.isoformat() for day in requested_days if day.isoformat() not in observed]
    folder = _new_download_dir("inamhi")
    safe_station = (station.get("code") or str(station["id"])).replace("/", "-")
    csv_path = folder / f"inamhi-{safe_station}-{first:%Y%m%d}-{last:%Y%m%d}.csv"
    fields = [
        "date", "station_id", "station_code", "station_name", "province", "canton",
        "longitude", "latitude", "altitude_m", "variable", "statistic",
        "parameter_code", "value", "units",
    ]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    query_url = INAMHI_DAILY_URL + " · POST"
    manifest = {
        "provider": "Instituto Nacional de Meteorología e Hidrología del Ecuador (INAMHI)",
        "dataset": "Visor diario de estaciones meteorológicas e hidrológicas",
        "citation": "INAMHI · datos diarios observados en estación; revisar control de calidad de la institución.",
        "source_url": INAMHI_VIEWER_URL,
        "public_access_notice": INAMHI_PUBLIC_ACCESS_URL,
        "api_endpoint": INAMHI_DAILY_URL,
        "request_body": payload,
        "retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "requested_period": {"start": first.isoformat(), "end": last.isoformat()},
        "returned_date_span_before_filter": (
            {"start": min(returned_raw_dates), "end": max(returned_raw_dates)}
            if returned_raw_dates else None
        ),
        "returned_rows_in_requested_period": len(rows),
        "missing_dates": missing,
        "station": station,
        "parameter": parameter,
        "quality_control_note": (
            "La respuesta de esta consulta no incluyó una bandera de control de calidad; "
            "no se asigna ni se infiere una. El valor 0 se conserva como observación válida."
        ),
        "spatial_note": (
            "Son observaciones puntuales de una estación. No equivalen al promedio "
            "de una provincia ni a una superficie espacial interpolada."
        ),
        "license_note": (
            "INAMHI anuncia acceso público gratuito a información hidrometeorológica; "
            "el endpoint no devuelve una licencia explícita. Mantener atribución y "
            "verificar condiciones vigentes antes de redistribuir el archivo."
        ),
    }
    manifest_path = folder / "metadata.json"
    _write_json(manifest_path, manifest)
    zip_path = _bundle(
        folder,
        f"inamhi-{safe_station}-{first:%Y%m%d}-{last:%Y%m%d}.zip",
        [(csv_path, csv_path.name), (manifest_path, "metadata.json")],
    )
    return {
        "provider": "INAMHI",
        "station": station,
        "parameter": parameter,
        "start": first.isoformat(),
        "end": last.isoformat(),
        "count": len(rows),
        "rows": rows,
        "missing_dates": missing,
        "returned_date_span_before_filter": manifest["returned_date_span_before_filter"],
        "request_url": query_url,
        "manifest": manifest,
        "manifest_path": str(manifest_path),
        "csv_path": str(csv_path),
        "zip_path": str(zip_path),
    }
