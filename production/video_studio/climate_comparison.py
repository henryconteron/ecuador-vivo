"""Transparent temporal and spatial summaries for the local climate prototype."""

from __future__ import annotations

import calendar
import datetime as dt
import json
import sys
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.io import MemoryFile
from rasterio.transform import xy

REPO_ROOT = Path(__file__).resolve().parents[2]
VIDEO_STUDIO = REPO_ROOT / "production" / "video_studio"
if str(VIDEO_STUDIO) not in sys.path:
    sys.path.insert(0, str(VIDEO_STUDIO))

from data import _polygon_stats, boundary, province_boundaries  # noqa: E402
from endcard import CAPITALS  # noqa: E402
from model import STORE as VIDEO_STORE  # noqa: E402
from providers import (  # noqa: E402
    CHIRPS_PRODUCTS,
    POWER_VARIABLES,
    download_chirps_v3,
    download_power_regional,
)


MONTH_LABELS = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic",
}
CHIRPS_PARAMETER = "CHIRPS_PRECTOT"


def year_range(year: int, first_month: int, last_month: int, *, today=None):
    """Return the requested full-month interval, clipped only at today."""
    current = today or dt.date.today()
    if not 1 <= int(first_month) <= int(last_month) <= 12:
        raise ValueError("El mes inicial debe ser anterior o igual al mes final.")
    start = dt.date(int(year), int(first_month), 1)
    end = dt.date(int(year), int(last_month), calendar.monthrange(int(year), int(last_month))[1])
    if start > current:
        raise ValueError(f"El periodo de {year} todavía no ha comenzado.")
    return start, min(end, current)


def cached_power_download(start, end, parameter, *, progress=None):
    """Reuse an exact local download receipt before making another API call."""
    start = start.isoformat() if isinstance(start, dt.date) else str(start)
    end = end.isoformat() if isinstance(end, dt.date) else str(end)
    downloads = VIDEO_STORE / "downloads"
    if downloads.exists():
        for manifest_path in sorted(downloads.glob("nasa-power-*/metadata.json"), reverse=True):
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                period = manifest.get("requested_period", {})
                if (manifest.get("parameter") == parameter
                        and period.get("start") == start
                        and period.get("end") == end):
                    folder = manifest_path.parent
                    tif = next(folder.glob("nasa-power-*.tif"), None)
                    archive = next(folder.glob("nasa-power-*.zip"), None)
                    csv_path = next(folder.glob("nasa-power-*.csv"), None)
                    if tif and archive and csv_path:
                        return {
                            "provider": "NASA POWER (copia local verificada)",
                            "parameter": parameter,
                            "parameter_name": manifest.get("parameter_name", parameter),
                            "units": manifest.get("units", ""),
                            "start": start,
                            "end": end,
                            "count": len(manifest.get("returned_dates", [])),
                            "missing_dates": manifest.get("missing_dates", []),
                            "manifest": manifest,
                            "manifest_path": str(manifest_path),
                            "tiff_path": str(tif),
                            "csv_path": str(csv_path),
                            "zip_path": str(archive),
                        }
            except (OSError, ValueError, TypeError, json.JSONDecodeError):
                continue
    return download_power_regional(start, end, parameter, progress=progress)


def cached_chirps_download(start, end, product="final_era5", *, progress=None):
    """Reuse a matching local CHIRPS package before requesting daily tiles."""
    start = start.isoformat() if isinstance(start, dt.date) else str(start)
    end = end.isoformat() if isinstance(end, dt.date) else str(end)
    downloads = VIDEO_STORE / "downloads"
    if downloads.exists():
        for manifest_path in sorted(downloads.glob("chirps-v3-*/metadata.json"), reverse=True):
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                period = manifest.get("requested_period", {})
                archive = manifest_path.parent / f"chirps-v3-{product}-{start.replace('-', '')}-{end.replace('-', '')}.zip"
                if (manifest.get("product") == product
                        and period.get("start") == start
                        and period.get("end") == end
                        and archive.exists()):
                    entries = [
                        {"date": item["date"], "path": str(manifest_path.parent / item["package_file"])}
                        for item in manifest.get("files", [])
                    ]
                    return {
                        "provider": "CHIRPS v3 (copia local verificada)",
                        "product": product,
                        "product_label": manifest.get("product_label", product),
                        "start": start,
                        "end": end,
                        "count": len(entries),
                        "entries": entries,
                        "manifest": manifest,
                        "manifest_path": str(manifest_path),
                        "zip_path": str(archive),
                        "units": "mm/día",
                    }
            except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
                continue
    return download_chirps_v3(start, end, product, progress=progress)


def _raster_dates(source):
    dates = []
    for index in range(1, source.count + 1):
        label = source.descriptions[index - 1]
        if not label:
            label = source.tags(index).get("DESCRIPTION", "")
        try:
            dates.append(dt.date.fromisoformat(label[:10]))
        except (TypeError, ValueError):
            dates.append(None)
    return dates


def _monthly_grid(source, indexes, parameter):
    data = source.read(indexes=indexes, masked=True).astype("float64")
    values = np.ma.filled(data, np.nan)
    values[~np.isfinite(values) | (values <= -900)] = np.nan
    if parameter in ('PRECTOTCORR', CHIRPS_PARAMETER):
        values[values < 0] = np.nan  # negative precipitation is invalid, not negative rain
    count = np.isfinite(values).sum(axis=0)
    if parameter in ("PRECTOTCORR", CHIRPS_PARAMETER):
        grid = np.nansum(values, axis=0)
    else:
        grid = np.nanmean(values, axis=0)
    # A missing daily pixel is not zero rain or a complete monthly mean.
    grid[count != len(indexes)] = np.nan
    return grid.astype("float32")


def display_units(parameter, *, period_total=False):
    """Units for the value actually shown, not just the daily source field."""
    if parameter in ("PRECTOTCORR", CHIRPS_PARAMETER):
        return "mm del periodo" if period_total else "mm/mes"
    return POWER_VARIABLES[parameter]["units"]


def _stats_for_features(grid, source, features):
    profile = {
        "driver": "GTiff", "width": source.width, "height": source.height,
        "count": 1, "dtype": "float32", "crs": source.crs,
        "transform": source.transform, "nodata": -9999.0,
    }
    raster = np.where(np.isfinite(grid), grid, profile["nodata"]).astype("float32")
    with MemoryFile() as memory:
        with memory.open(**profile) as monthly:
            monthly.write(raster, 1)
            return _polygon_stats(monthly, 1, features, reject_negative=(
                # Precipitation and wind speed cannot be negative; temperature can.
                False
            ))


def _find_feature(features, requested):
    normalized = str(requested).strip().casefold()
    for feature in features:
        props = feature.get("properties", {})
        name = props.get("shapeName") or props.get("name") or ""
        if str(name).strip().casefold() == normalized:
            return feature
    raise ValueError(f"No encontré el límite territorial de {requested}.")


def _city_coordinates(name):
    for city, longitude, latitude in CAPITALS:
        if city.casefold() == name.casefold():
            return float(longitude), float(latitude)
    raise ValueError("La localidad no está en el catálogo de puntos disponibles.")


def summarize_raster_months(path, parameter, year, first_month, last_month, *, mode="nacional", area="Ecuador"):
    """Compute monthly means/sums on the delivered native POWER raster.

    Rain uses a sum over daily cells, then a spatial area-weighted mean. Other
    intensive variables use a temporal average, then the same spatial mean.
    Incomplete months remain blank rather than being extrapolated.
    """
    if parameter not in POWER_VARIABLES:
        raise ValueError("Variable NASA POWER desconocida.")
    start, end = year_range(year, first_month, last_month)
    months = list(range(int(first_month), int(last_month) + 1))
    with rasterio.open(path) as source:
        dates = _raster_dates(source)
        known_dates = [day for day in dates if day is not None]
        if len(known_dates) != len(set(known_dates)):
            raise ValueError('Hay fechas duplicadas en el ráster; no se acumularán dos veces.')
        feature_list = province_boundaries()
        if mode == "provincia":
            targets = [_find_feature(feature_list, area)]
        elif mode == "nacional":
            targets = [boundary()["features"][0]]
        elif mode == "ranking":
            targets = feature_list
        else:
            targets = []

        records = []
        for month in months:
            month_start = dt.date(int(year), month, 1)
            month_end = dt.date(int(year), month, calendar.monthrange(int(year), month)[1])
            expected_start = month_start
            expected_end = month_end
            expected_days = calendar.monthrange(int(year), month)[1]
            indexes = [index for index, day in enumerate(dates, start=1)
                       if day and day.year == int(year) and day.month == month
                       and expected_start <= day <= expected_end]
            returned_days = len(indexes)
            coverage = returned_days / expected_days
            complete = returned_days == expected_days
            if not indexes:
                continue
            grid = _monthly_grid(source, indexes, parameter)

            if mode == "ciudad":
                lon, lat = _city_coordinates(area)
                row, col = source.index(lon, lat)
                values = [float(grid[row, col])] if np.isfinite(grid[row, col]) else []
                value = values[0] if values and complete else None
                point_lon, point_lat = xy(source.transform, row, col, offset="center")
                records.append({
                    "year": int(year), "month": month, "month_label": MONTH_LABELS[month],
                    "area": area, "value": value, "units": display_units(parameter),
                    "days_with_data": returned_days, "days_expected": expected_days,
                    "coverage": coverage, "cell_lon": float(point_lon),
                    "cell_lat": float(point_lat), "complete": complete,
                })
                continue

            stats = _stats_for_features(grid, source, targets)
            for name, stat in stats.items():
                value = stat["mean"] if complete else None
                records.append({
                    "year": int(year), "month": month, "month_label": MONTH_LABELS[month],
                    "area": name, "value": value,
                    "units": display_units(parameter),
                    "days_with_data": returned_days, "days_expected": expected_days,
                    "coverage": coverage, "complete": complete,
                })
    return pd.DataFrame.from_records(records)


def summarize_chirps_month(download, year, month, *, mode="nacional", area="Ecuador"):
    """Sum one complete CHIRPS daily month, then summarize its native grid."""
    entries = sorted(download.get("entries", []), key=lambda item: item["date"])
    month_start = dt.date(int(year), int(month), 1)
    expected_days = calendar.monthrange(int(year), int(month))[1]
    if len(entries) != expected_days or len({item['date'] for item in entries}) != expected_days or any(
        dt.date.fromisoformat(item["date"]).year != int(year)
        or dt.date.fromisoformat(item["date"]).month != int(month)
        for item in entries
    ):
        raise ValueError("CHIRPS requiere todas las fechas del mes seleccionado; no se rellenan huecos.")

    with rasterio.open(entries[0]["path"]) as first:
        profile = first.profile.copy()
        profile.update(count=len(entries), dtype="float32", nodata=-9999.0)
        arrays = []
        for entry in entries:
            with rasterio.open(entry["path"]) as daily:
                if (daily.shape != first.shape or daily.transform != first.transform
                        or daily.crs != first.crs):
                    raise ValueError("Los rásteres diarios CHIRPS no comparten la misma grilla.")
                values = daily.read(1, masked=True).astype("float32").filled(np.nan)
                values[(values <= -900) | ~np.isfinite(values)] = np.nan
                arrays.append(values)
        dates = [dt.date.fromisoformat(entry["date"]) for entry in entries]
        feature_list = province_boundaries()
        if mode == "provincia":
            targets = [_find_feature(feature_list, area)]
        elif mode == "nacional":
            targets = [boundary()["features"][0]]
        elif mode == "ranking":
            targets = feature_list
        else:
            targets = []
        with MemoryFile() as memory:
            with memory.open(**profile) as source:
                for index, values in enumerate(arrays, start=1):
                    source.write(np.where(np.isfinite(values), values, -9999.0), index)
                    source.set_band_description(index, dates[index - 1].isoformat())
                grid = _monthly_grid(source, list(range(1, len(entries) + 1)), CHIRPS_PARAMETER)
                if mode == "ciudad":
                    lon, lat = _city_coordinates(area)
                    row, col = source.index(lon, lat)
                    value = float(grid[row, col]) if np.isfinite(grid[row, col]) else None
                    point_lon, point_lat = xy(source.transform, row, col, offset="center")
                    return pd.DataFrame.from_records([{
                        "year": int(year), "month": int(month), "month_label": MONTH_LABELS[month],
                        "area": area, "value": value, "units": display_units(CHIRPS_PARAMETER),
                        "days_with_data": expected_days, "days_expected": expected_days,
                        "coverage": 1.0, "cell_lon": float(point_lon),
                        "cell_lat": float(point_lat), "complete": True,
                    }])
                stats = _stats_for_features(grid, source, targets)
    return pd.DataFrame.from_records([
        {
            "year": int(year), "month": int(month), "month_label": MONTH_LABELS[month],
            "area": name, "value": stat["mean"], "units": display_units(CHIRPS_PARAMETER),
            "days_with_data": expected_days, "days_expected": expected_days,
            "coverage": 1.0, "complete": True,
        }
        for name, stat in stats.items()
    ])


def annual_rank(monthly_frames, parameter, *, years_included=(), months_expected=()):
    """Rank provincial period values using each month's documented statistic."""
    if not monthly_frames:
        return pd.DataFrame()
    monthly = pd.concat(monthly_frames, ignore_index=True)
    if monthly.duplicated(['year', 'month', 'area']).any():
        raise ValueError('Hay meses provinciales duplicados; corrige la tabla antes de ordenar el ranking.')
    expected_months = list(months_expected) or sorted(monthly["month"].unique().tolist())
    included_years = list(years_included) or sorted(monthly["year"].unique().tolist())
    areas = sorted({
        str(feature.get("properties", {}).get("shapeName", ""))
        for feature in province_boundaries()
        if feature.get("properties", {}).get("shapeName")
    } or set(monthly["area"].unique().tolist()))
    rows = []
    for year in included_years:
        for area in areas:
            available = monthly[(monthly["year"] == year) & (monthly["area"] == area)]
            available = available[available["month"].isin(expected_months)]
            subset = available
            if "complete" in subset:
                subset = subset[subset["complete"].fillna(False)]
            subset = subset[subset["value"].notna()]
            ready = set(subset["month"].astype(int)) == set(expected_months)
            days = int(available["days_with_data"].sum()) if not available.empty else 0
            expected_days = int(available["days_expected"].sum()) if not available.empty else 0
            if ready and expected_months:
                if parameter in ("PRECTOTCORR", CHIRPS_PARAMETER):
                    value = float(subset["value"].sum())
                    statistic = "suma de acumulados espaciales mensuales completos"
                else:
                    weights = subset["days_with_data"].astype(float)
                    value = float(np.average(subset["value"], weights=weights))
                    statistic = "media temporal ponderada por días"
            else:
                value = np.nan
                statistic = "incompleto: faltan meses o días"
            rows.append({
                "year": int(year), "area": area, "value": value,
                "months_with_data": int(subset["month"].nunique()),
                "months_expected": len(expected_months),
                "days_with_data": days, "days_expected": expected_days,
                "complete": bool(ready), "statistic": statistic,
            })
    result = pd.DataFrame.from_records(rows)
    result["units"] = display_units(parameter, period_total=(parameter in ("PRECTOTCORR", CHIRPS_PARAMETER)))
    return result.sort_values(["year", "value"], ascending=[True, False])


def parse_cpc_index(text, column):
    """Read NOAA CPC whitespace tables (season/year/value) into dated rows."""
    frame = pd.read_csv(StringIO(str(text)), sep=r"\s+", engine="python")
    normalized = {str(name).strip().upper(): name for name in frame.columns}
    season_col = normalized.get("SEAS")
    year_col = normalized.get("YR")
    value_col = normalized.get(column.upper())
    if not season_col or not year_col or not value_col:
        raise ValueError(f"La tabla NOAA no contiene las columnas SEAS, YR, {column}.")
    months = {"DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6,
              "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12}
    frame["season"] = frame[season_col].astype(str).str.upper()
    frame["year"] = pd.to_numeric(frame[year_col], errors="coerce")
    frame["value"] = pd.to_numeric(frame[value_col], errors="coerce")
    frame["month"] = frame["season"].map(months)
    frame["date"] = pd.to_datetime({"year": frame["year"], "month": frame["month"], "day": 15}, errors="coerce")
    return frame.dropna(subset=["date", "value"])[["date", "season", "value"]].sort_values("date")


def ee_climate_script(
    date, *, show_sst=True, show_anomaly=False, show_wind=True,
    show_air_temp=True, show_rain=False,
):
    """Build a ready-to-paste Earth Engine script for an Ecuador–Pacific scene."""
    day = dt.date.fromisoformat(str(date))
    next_day = day + dt.timedelta(days=1)
    lines = [
        "// Ecuador Vivo · Océano–atmósfera en una escena",
        f"var day = '{day.isoformat()}';",
        f"var nextDay = '{next_day.isoformat()}';",
        "var region = ee.Geometry.Rectangle([-92, -8, -72, 7]);",
        "Map.centerObject(region, 4);",
        "Map.setOptions('SATELLITE');",
    ]
    if show_sst or show_anomaly:
        lines.extend([
            "var oisst = ee.ImageCollection('NOAA/CDR/OISST/V2_1')",
            "  .filterDate(day, nextDay).first();",
        ])
    if show_sst:
        lines.extend([
            "var sst = oisst.select('sst').multiply(0.01).rename('SST_C');",
            "Map.addLayer(sst.clip(region), {min: 18, max: 31,",
            "  palette: ['173f8a','31b8d4','f4e85b','f36b38','bd1746']},",
            "  'Temperatura superficial del mar (°C)');",
        ])
    if show_anomaly:
        lines.extend([
            "var anom = oisst.select('anom').multiply(0.01).rename('SST_anomaly_C');",
            "Map.addLayer(anom.clip(region), {min: -3, max: 3,",
            "  palette: ['2459a6','88c4de','f5f4ed','f5a15b','bd2543']},",
            "  'Anomalía diaria de TSM (°C)');",
        ])
    if show_rain:
        lines.extend([
            "var rain = ee.ImageCollection('UCSB-CHC/CHIRPS/V3/DAILY_RNL')",
            "  .filterDate(day, nextDay).first().select('precipitation');",
            "Map.addLayer(rain.clip(region), {min: 0, max: 80,",
            "  palette: ['091b3a','1676b8','32c7cf','f0e65a','f26b38','b9164b']},",
            "  'Precipitación diaria CHIRPS v3 · mm/día');",
        ])
    if show_wind or show_air_temp:
        lines.extend([
            "var era = ee.ImageCollection('ECMWF/ERA5/HOURLY')",
            "  .filterDate(ee.Date(day).advance(12, 'hour'), ee.Date(day).advance(13, 'hour')).first();",
        ])
    if show_air_temp:
        lines.extend([
            "var ecuador = ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017')",
            "  .filter(ee.Filter.eq('country_na', 'Ecuador'));",
            "var airTemp = era.select('temperature_2m').subtract(273.15).rename('air_temperature_C');",
            "Map.addLayer(airTemp.clip(ecuador.geometry()), {min: 5, max: 31,",
            "  palette: ['253494','2c7fb8','7fcdbb','ffffbf','fdae61','d7191c']},",
            "  'Temperatura del aire en Ecuador · ERA5 · °C');",
        ])
    if show_wind:
        lines.extend([
            "var u = era.select('u_component_of_wind_10m');",
            "var v = era.select('v_component_of_wind_10m');",
            "var speed = u.hypot(v).rename('wind_speed_m_s');",
            "var longitudes = ee.List.sequence(-91, -73, 2);",
            "var latitudes = ee.List.sequence(-7, 5, 2);",
            "var arrowGrid = ee.FeatureCollection(longitudes.map(function(lon) {",
            "  return latitudes.map(function(lat) { return ee.Feature(ee.Geometry.Point([lon, lat])); });",
            "}).flatten());",
            "var windSamples = ee.Image.cat([u, v, speed]).sampleRegions({",
            "  collection: arrowGrid, scale: 27830, geometries: true, tileScale: 2});",
            "var arrows = windSamples.map(function(feature) {",
            "  var uValue = ee.Number(feature.get('u_component_of_wind_10m'));",
            "  var vValue = ee.Number(feature.get('v_component_of_wind_10m'));",
            "  var lon = ee.Number(feature.geometry().coordinates().get(0));",
            "  var lat = ee.Number(feature.geometry().coordinates().get(1));",
            "  var dx = uValue.multiply(0.10).divide(lat.multiply(Math.PI / 180).cos());",
            "  var dy = vValue.multiply(0.10);",
            "  var endLon = lon.add(dx); var endLat = lat.add(dy);",
            "  var angle = vValue.atan2(uValue); var head = 0.12;",
            "  var leftLon = endLon.subtract(angle.add(2.55).cos().multiply(head).divide(lat.multiply(Math.PI / 180).cos()));",
            "  var leftLat = endLat.subtract(angle.add(2.55).sin().multiply(head));",
            "  var rightLon = endLon.subtract(angle.subtract(2.55).cos().multiply(head).divide(lat.multiply(Math.PI / 180).cos()));",
            "  var rightLat = endLat.subtract(angle.subtract(2.55).sin().multiply(head));",
            "  var shaft = ee.Geometry.LineString([[lon, lat], [endLon, endLat]]);",
            "  var headLeft = ee.Geometry.LineString([[endLon, endLat], [leftLon, leftLat]]);",
            "  var headRight = ee.Geometry.LineString([[endLon, endLat], [rightLon, rightLat]]);",
            "  return ee.FeatureCollection([ee.Feature(shaft), ee.Feature(headLeft), ee.Feature(headRight)])",
            "    .flatten().map(function(segment) { return segment.set('speed_ms', feature.get('wind_speed_m_s')); });",
            "}).flatten();",
            "Map.addLayer(arrows.style({color: 'ffffff', width: 1.4}), {}, 'Dirección del viento ERA5 · 10 m');",
            "Map.addLayer(speed.clip(region), {min: 0, max: 12,",
            "  palette: ['173f8a','49c7d3','f8df65','e95448']}, 'Rapidez del viento · m/s', false);",
            "// u y v son vectores hacia el este/norte. ERA5 es una reanálisis de ~31 km,",
            "// no una observación de una estación ni viento a escala de calle.",
        ])
    lines.append("// Para exportar, deja activa una sola capa y ejecuta esta tarea desde Tasks.")
    export_candidates = [
        (show_rain, "rain.clip(region)", "EcuadorVivo_lluvia_CHIRPS", 5566),
        (show_sst, "sst.clip(region)", "EcuadorVivo_SST", 27830),
        (show_anomaly, "anom.clip(region)", "EcuadorVivo_anomalia_TSM", 27830),
        (show_air_temp, "airTemp.clip(ecuador.geometry())", "EcuadorVivo_temperatura_aire", 27830),
        (show_wind, "speed.clip(region)", "EcuadorVivo_viento_ERA5", 27830),
    ]
    selected_export = next((item for item in export_candidates if item[0]), None)
    if selected_export:
        _, image_expression, description, scale = selected_export
        lines.extend([
            f"Export.image.toDrive({{image: {image_expression}, description: '{description}_' + day,",
            f"  folder: 'EcuadorVivo_Clima', region: region, scale: {scale}, maxPixels: 1e13}});",
            "// Ajusta image/description/scale si deseas exportar otra variable.",
        ])
    else:
        lines.append("// Activa al menos una capa antes de crear una tarea de exportación.")
    lines.append("// Comprueba la fecha disponible en el catálogo antes de iniciar la exportación.")
    return "\n".join(lines) + "\n"
