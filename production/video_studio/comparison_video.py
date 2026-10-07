"""Social-video maquetas for verified climate comparisons."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import uuid

import imageio_ffmpeg
import numpy as np
import pandas as pd
from PIL import Image, ImageColor, ImageDraw

from jobs import write_json
from model import STORE, default_project
from maqueta import compose_final, gradient_text, fit_text
from render import fitted, font
from comparison_maps import draw_geographic_scene, map_steps, native_fields, scale_limits
from layout_engine import begin_layout


MONTH_LABELS = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic",
}
PALETTES = {
    "Andes pulso": ["#ff5e62", "#f5b84b", "#55e2cb"],
    "Océano": ["#47b9f1", "#56e3cf", "#f2cf5b"],
    "Tierra": ["#e26d5a", "#eeb95b", "#84d6a2"],
}


def _hex(value, fallback):
    try:
        return ImageColor.getrgb(value)
    except (TypeError, ValueError):
        return ImageColor.getrgb(fallback)


def _wrap(draw, text, selected_font, max_width, max_lines=2):
    words = str(text or "").split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and draw.textlength(candidate, font=selected_font) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while draw.textlength(lines[-1] + "…", font=selected_font) > max_width and lines[-1]:
            lines[-1] = lines[-1][:-1]
        lines[-1] += "…"
    return lines


def _heading(draw, text, y, color, *, size=72, max_width=930):
    selected = font(size, True)
    lines = _wrap(draw, text, selected, max_width, max_lines=2)
    for index, line in enumerate(lines):
        draw.text((72, y + index * int(size * 0.92)), line, font=selected, fill=color)
    return y + len(lines) * int(size * 0.92)


def _title_lines(draw, title):
    """Prefer two readable balanced lines over shrinking a long headline."""
    base = fit_text('display', 80, 10000, title)
    words = title.split()
    if draw.textlength(title, font=base) <= 930 or len(words) < 2:
        return [title]
    candidates = [(' '.join(words[:index]), ' '.join(words[index:])) for index in range(1, len(words))]
    return list(min(candidates, key=lambda lines: max(draw.textlength(line, font=base) for line in lines)))


def _source_label(output):
    source = str(output.get("source", ""))
    if source.startswith("CHIRPS"):
        return "CHIRPS v3 · lluvia diaria · ~5,6 km"
    if "POWER" in source:
        return "NASA POWER · grilla regional ~50–60 km"
    return source or "Fuente documentada en el recibo"


def _line_data(frame, output):
    valid = frame.dropna(subset=["value"]).copy()
    if valid.empty:
        raise ValueError("No hay meses completos para dibujar la comparación.")
    valid["month"] = pd.to_numeric(valid["month"], errors="coerce")
    valid["year"] = pd.to_numeric(valid["year"], errors="coerce")
    valid = valid.dropna(subset=["month", "year"])
    if "complete" in valid:
        valid = valid[valid["complete"].fillna(False)]
    if valid.empty:
        raise ValueError("No hay cobertura temporal completa; no se dibujarán valores interpolados.")
    return valid


def compose_comparison_frame(frame, output, config, *, progress=1.0, rank_frame=None):
    """Draw one 1080×1920 social-safe comparison frame from computed values."""
    from editorial import editorial_background, compose_editorial
    image = begin_layout(editorial_background(config), config, 'map')
    draw = ImageDraw.Draw(image)
    accent = _hex(config.get("accent"), "#55e2cb")
    white = _hex(config.get("text"), "#f4f8fb")
    muted = _hex(config.get("muted"), "#a6bdc7")
    palette = config.get('palette_colors') or PALETTES.get(config.get("palette"), PALETTES["Andes pulso"])
    line_colors = [_hex(color, "#55e2cb") for color in palette]
    dark_card = _hex(config.get("card"), "#0c2633")
    rule = _hex(config.get("rule"), "#285166")

    from editorial import draw_header, draw_footer
    draw_header(image, config)

    # The audiovisual body is always geographic. Scalar series/rankings belong
    # in the final metrics card, never as a fallback for missing source rasters.
    draw_geographic_scene(image, output, config, palette, progress=progress)

    source_text = config.get("citation") or _source_label(output)
    method = config.get("method") or (
        "Promedio espacial del polígono; sin rellenar fechas faltantes."
        if output.get("mode") != "ciudad"
        else "Celda de grilla más cercana; no representa una estación ni el microclima urbano."
    )
    draw_footer(image, config, source_text, method)
    return compose_editorial(image, config)


def _draw_series(draw, valid, output, config, colors, white, muted, rule,
                 variable, area, units, progress):
    months = list(range(int(output["first_month"]), int(output["last_month"]) + 1))
    if not months:
        raise ValueError("La comparación no contiene meses seleccionados.")
    position = min(len(months) - 1, max(0, int(float(progress) * len(months))))
    visible_month = months[position]
    years = [int(year) for year in output.get("years", [])]
    visible = valid[valid["month"] <= visible_month]
    values = visible["value"].astype(float).to_numpy()
    full_values = valid["value"].astype(float).to_numpy()
    low, high = float(np.nanmin(full_values)), float(np.nanmax(full_values))
    if str(output.get("parameter", "")).upper() in ("PRECTOTCORR", "CHIRPS_PRECTOT"):
        low = 0.0
    pad = max((high - low) * 0.12, abs(high) * 0.08, 0.25)
    if high <= low:
        high = low + 1.0
    y_min, y_max = (low, high + pad) if low == 0 else (low - pad, high + pad)

    draw.text((84, 458), f"{variable.upper()} · {area.upper()}", font=fitted(f"{variable.upper()} · {area.upper()}", 27, 880, True), fill=white)
    draw.rounded_rectangle((82, 506, 998, 574), radius=18, fill=rule)
    month_label = MONTH_LABELS.get(visible_month, str(visible_month))
    year_label = " / ".join(map(str, years))
    draw.text((108, 520), f"{month_label.upper()} · {year_label}", font=fitted(f"{month_label.upper()} · {year_label}", 29, 850, True), fill=white)

    x0, y0, x1, y1 = 172, 670, 944, 1248
    for tick in range(5):
        ratio = tick / 4
        y = y1 - ratio * (y1 - y0)
        value = y_min + ratio * (y_max - y_min)
        draw.line((x0, y, x1, y), fill=rule, width=2)
        label = f"{value:.1f}"
        draw.text((x0 - 18, y), label, font=font(19), fill=muted, anchor="rm")
    for index, month in enumerate(months):
        x = x0 + (x1 - x0) * index / max(1, len(months) - 1)
        label = MONTH_LABELS.get(month, str(month))
        draw.text((x, y1 + 22), label, font=font(20), fill=muted, anchor="mt")
    draw.text((x0, 1320), f"UNIDAD · {units or 'según la variable'}",
              font=font(21, True), fill=muted)

    for series_index, year in enumerate(years):
        rows = visible[visible["year"].astype(int) == year].sort_values("month")
        points = []
        last_month = None
        for _, row in rows.iterrows():
            if pd.isna(row["value"]):
                last_month = None
                continue
            month = int(row["month"])
            ratio = (float(row["value"]) - y_min) / (y_max - y_min)
            x = x0 + (x1 - x0) * (month - months[0]) / max(1, months[-1] - months[0])
            y = y1 - ratio * (y1 - y0)
            if last_month is not None and month == last_month + 1 and len(points) > 0:
                draw.line((points[-1][0], points[-1][1], x, y), fill=colors[series_index % len(colors)], width=7)
            draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill=colors[series_index % len(colors)], outline=white, width=2)
            points.append((x, y))
            last_month = month

    legend_y = 1386
    for index, year in enumerate(years):
        color = colors[index % len(colors)]
        x = 100 + (index % 3) * 294
        y = legend_y + (index // 3) * 40
        draw.ellipse((x, y, x + 18, y + 18), fill=color)
        current = valid[(valid["year"].astype(int) == year) & (valid["month"].astype(int) == visible_month)]
        reading = f"{current.iloc[0]['value']:.1f} {units}" if not current.empty else "sin dato completo"
        draw.text((x + 30, y - 5), f"{year} · {reading}", font=fitted(f"{year} · {reading}", 20, 250), fill=white)


def _draw_ranking(draw, rank_frame, years, output, config, colors, white, muted, rule):
    if rank_frame.empty:
        raise ValueError("No se generó un ranking provincial completo para la maqueta.")
    progress = min(0.999999, max(0.0, float(config.get("progress", 1.0))))
    if progress >= 0.999:
        year_index, year_progress = len(years) - 1, 1.0
    else:
        phase = progress * max(1, len(years))
        year_index = min(len(years) - 1, int(phase))
        year_progress = phase - year_index
    year = years[year_index]
    data = rank_frame[(rank_frame["year"].astype(int) == year) & rank_frame["value"].notna()]
    data = data.sort_values("value", ascending=False).head(24)
    if data.empty:
        raise ValueError(f"{year}: no hay valores completos para ordenar provincias.")
    comparable = rank_frame.dropna(subset=['value'])
    if 'complete' in comparable:
        comparable = comparable[comparable['complete'].fillna(False)]
    max_value = max(float(comparable['value'].max()), 0.0)
    min_value = min(float(comparable['value'].min()), 0.0)
    span = max(max_value - min_value, 1e-6)
    units = str(config.get("units", ""))
    draw.text((84, 458), f"PROVINCIAS · {output.get('first_month', 1):02d}–{output.get('last_month', 12):02d}", font=font(27, True), fill=white)
    draw.rounded_rectangle((82, 506, 998, 574), radius=18, fill=rule)
    draw.text((108, 520), f"RANKING · {year} · {len(data)} PROVINCIAS CON DATO", font=font(27, True), fill=white)
    x0, x1 = 332, 830
    zero = x0 + (x1 - x0) * (-min_value) / span
    chart_top, row_height = 614, 32
    reveal = max(1, min(len(data), int(np.ceil(year_progress * len(data)))))
    for index, (_, row) in enumerate(data.iterrows()):
        y = chart_top + index * row_height
        if y + row_height > 1424:
            break
        label = str(row["area"])
        draw.text((94, y), f"{index + 1:02d}", font=font(21, True), fill=muted)
        draw.text((143, y), label, font=fitted(label, 22, 170), fill=white)
        draw.line((x0, y + 13, x1, y + 13), fill=rule, width=3)
        if index < reveal:
            right = x0 + (x1 - x0) * (float(row['value']) - min_value) / span
            left, right_edge = sorted((zero, right))
            draw.rounded_rectangle((left, y + 3, max(left + 2, right_edge), y + 24), radius=5,
                                   fill=colors[index % len(colors)])
            reading = f"{float(row['value']):.1f} {units}".strip()
            draw.text((846, y), reading,
                      font=fitted(reading, 19, 148), fill=white)
    draw.text((94, 1408), f"{output.get('area', 'Ecuador')} · {units} · periodo completo, sin meses incompletos",
              font=fitted(f"{output.get('area', 'Ecuador')} · {units} · periodo completo, sin meses incompletos", 18, 870), fill=muted)


def render_preview(frame, output, config, *, rank_frame=None, progress=1.0):
    selected = dict(config)
    selected["progress"] = progress
    return compose_comparison_frame(frame, output, selected, progress=progress, rank_frame=rank_frame)


def comparison_summary(frame, output, config, *, rank_frame=None):
    """Use complete, identical month windows; never sum an intensive variable."""
    import calendar
    rain = str(output['parameter']).upper() in ('PRECTOTCORR', 'CHIRPS_PRECTOT')
    months = set(range(int(output['first_month']), int(output['last_month']) + 1))
    valid = _line_data(frame, output)
    if valid.duplicated(['year', 'month', 'area'] if 'area' in valid else ['year', 'month']).any():
        raise ValueError('Hay observaciones mensuales duplicadas; corrige la tabla antes de exportar.')
    periods = []
    if rank_frame is not None:
        selected = rank_frame.dropna(subset=['value']).copy()
        if 'complete' in selected:
            selected = selected[selected['complete'].fillna(False)]
        for _, row in selected.iterrows():
            periods.append({'name': f"{row['area']} · {int(row['year'])}", 'area': row['area'],
                            'year': int(row['year']), 'value': float(row['value'])})
    else:
        for year in sorted(output['years']):
            rows = valid[valid.year == year].sort_values('month')
            if set(rows.month.astype(int)) != months:
                raise ValueError(f'{year}: la ventana mensual está incompleta. No se exportará una comparación desigual.')
            weights = [calendar.monthrange(int(year), int(month))[1] for month in rows.month]
            value = float(rows.value.sum()) if rain else float(np.average(rows.value, weights=weights))
            periods.append({'name': str(year), 'year': int(year), 'area': output['area'], 'value': value})
    if not periods:
        raise ValueError('No hay periodos completos para construir el cierre.')
    units = 'mm' if rain else str(config.get('units', ''))
    method = 'Acumulado del periodo' if rain else 'Media temporal ponderada por días'
    ranked = sorted(periods, key=lambda row: row['value'], reverse=True)
    years = sorted(set(row['year'] for row in periods))
    if rank_frame is None:
        first, last = sorted(periods, key=lambda row: row['year'])[0], sorted(periods, key=lambda row: row['year'])[-1]
        delta = last['value'] - first['value']
        cards = [
            {'value': f"{first['value']:.1f} {units}", 'label': f"{first['year']} · periodo", 'sub': 'Acumulado' if rain else 'Media ponderada'},
            {'value': f"{last['value']:.1f} {units}", 'label': f"{last['year']} · periodo", 'sub': 'Acumulado' if rain else 'Media ponderada'},
            {'value': f'{0. if abs(delta) < .05 else delta:+.1f} {units}', 'label': 'Diferencia entre años', 'sub': f"{last['year']} - {first['year']}"},
            {'value': f"{len(months)} {'mes' if len(months) == 1 else 'meses'}", 'label': 'Ventana comparable', 'sub': f'{len(years)} años con datos'},
        ]
    else:
        cards = [
            {'value': f"{ranked[0]['value']:.1f} {units}", 'label': 'Mayor valor provincial', 'sub': ranked[0]['name']},
            {'value': f"{ranked[-1]['value']:.1f} {units}", 'label': 'Menor valor provincial', 'sub': ranked[-1]['name']},
            {'value': str(len(periods)), 'label': 'Provincia–año con dato', 'sub': 'Solo periodos completos'},
            {'value': f"{len(months)} {'mes' if len(months) == 1 else 'meses'}", 'label': 'Ventana comparable', 'sub': f'{len(years)} años con datos'},
        ]
    selected_year = years[-1]
    # One 24-row ranking at the end; all years remain in the CSV and receipt.
    closing_rank = [row for row in ranked if row['year'] == selected_year] if rank_frame is not None else ranked
    copy = {
        'subtitle': f"{config.get('variable', output['parameter'])} · {output['area']} · {min(years)}–{max(years)}",
        'section_1': 'COMPARACIÓN EN CIFRAS', 'section_1_note': method,
        'section_2': f'PROVINCIAS · {selected_year}' if rank_frame is not None else 'LOS AÑOS EN PERSPECTIVA',
        'section_2_note': 'Misma ventana temporal',
        'section_3': f'PROVINCIAS 13–{len(closing_rank)}' if len(closing_rank) > 12 else 'HALLAZGOS CLAVE',
        'section_3_note': 'Sin interpolar fechas ausentes',
        'rank_axis_label': f'{method} ({units})',
        'footer': config.get('citation') or _source_label(output),
        'footer_2': f"{output['first_month']:02d}–{output['last_month']:02d} · {output['area']}",
    }
    return {'comparison_cards': cards, 'comparison_copy': copy,
            'city_rank': closing_rank, 'province_rank': closing_rank,
            'rank_label': f'{len(closing_rank)} provincias · {selected_year}' if rank_frame is not None else f'{len(years)} años · {output["area"]}',
            'aggregate_units': units, 'units': units, 'aggregation': 'sum' if rain else 'mean',
            'scope': output['area'], 'cadence': 'Mensual', 'decimals': 1,
            'period_values': periods, 'years': years, 'months': sorted(months),
            'comparison_notes': [
                f"01 · {output['area']} · meses {min(months):02d}–{max(months):02d} en cada año.",
                '02 · Lluvia: suma de acumulados mensuales completos.' if rain else '02 · Media ponderada por los días de cada mes.',
                ('03 · Provincias incompletas excluidas; no se rellenan faltantes.' if rank_frame is not None
                 else '03 · Diferencias calculadas antes de redondear.'),
                '04 · Grilla regional; no equivale a una estación.',
                config.get('citation') or _source_label(output),
            ] if len(closing_rank) <= 12 else [],
            'warnings': ['Datos de grilla; no mediciones de estación. Solo periodos completos.'],
            'extreme_method': 'Extremos de promedios del periodo; no máximos diarios ni píxeles extremos.'}


def render_comparison_endcard(frame, output, config, *, rank_frame=None):
    if output.get('map_kind') in ('points', 'polygons'):
        from spatial_csv import render_spatial_endcard
        return render_spatial_endcard(output, config)
    from endcard import compose_endcard
    summary = comparison_summary(frame, output, config, rank_frame=rank_frame)
    if rank_frame is None:
        from editorial import comparison_findings
        summary['findings'] = comparison_findings(summary)
        if not config.get('endcard_auto_text', True):
            for calculated, manual in zip(summary['findings'], config.get('endcard_findings', [])):
                for key in ('title', 'body'):
                    if isinstance(manual.get(key), str) and manual[key].strip():
                        calculated[key] = manual[key].strip()
            if any(isinstance(item.get(key), str) and item[key].strip()
                   for item in config.get('endcard_findings', []) for key in ('title', 'body')):
                summary['warnings'].append('Hallazgos con texto manual: revisar que la interpretación corresponda a los datos.')
    project = default_project()
    project.update(config)
    project['title_gradient_1'] = config.get('title_gradient_1', '#26ede0')
    project['title_gradient_2'] = config.get('title_gradient_2', '#229ffa')
    project.update(source='local', variable=config.get('variable', output['parameter']), units=summary['units'], cadence='Mensual',
                   endcard_aggregation=summary['aggregation'], endcard_aggregation_mode='manual')
    if not config.get('endcard_auto_text', True):
        summary['comparison_copy']['subtitle'] = config.get('endcard_subtitle', '') or summary['comparison_copy']['subtitle']
        for key, value in config.get('endcard_copy', {}).items():
            if key in summary['comparison_copy'] and isinstance(value, str) and value.strip():
                summary['comparison_copy'][key] = value
    # The common compositor must consume this comparison's resolved copy, not
    # the map template's factory rain labels when manual overrides are enabled.
    project['endcard_auto_text'] = True
    image = compose_endcard(project, summary)
    return image, summary


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def create_comparison_job(frame, output, config, *, rank_frame=None, progress_callback=None, jobs_root=None):
    """Render maps, then the selected format/montage, preserving source receipts."""
    from storyboard import base_timing, assemble
    # Validate the actual geographic sources BEFORE creating a job or MP4.
    fields = None if output.get('map_kind') else native_fields(output)
    config = base_timing(config)
    config['scale_min'], config['scale_max'] = scale_limits(output, config, fields)
    steps = map_steps(output, config)
    fps = 30
    duration = max(1/30, min(3600, float(config.get("duration", 20))))
    total_frames = round(duration * fps)
    if total_frames < len(steps):
        raise ValueError('Aumenta la duración: debe caber al menos un fotograma por mapa original.')
    duration = total_frames / fps
    closing_enabled = config.get('endcard_enabled', True)
    closing_duration = round(float(config.get('endcard_duration', 6)) * fps) / fps if closing_enabled else 0
    closing_image, closing_summary = render_comparison_endcard(frame, output, config, rank_frame=rank_frame)
    jobs_root = Path(jobs_root) if jobs_root is not None else STORE / "jobs"
    jobs_root.mkdir(parents=True, exist_ok=True)
    job = jobs_root / ("comparacion-" + dt.datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8])
    job.mkdir()
    periods = [receipt for receipt in output.get("receipts", []) if receipt.get("start") and receipt.get("end")]
    period_start = min((receipt["start"] for receipt in periods), default=None if output.get('map_kind') else dt.date.today().isoformat())
    period_end = max((receipt["end"] for receipt in periods), default=None if output.get('map_kind') else dt.date.today().isoformat())
    project = {
        "name": config.get("name") or f"Comparación · {output.get('parameter')} · {output.get('area')}",
        "title": config.get("title", "Comparación climática"),
        "variable": config.get("variable", output.get("parameter", "Variable climática")),
        "units": config.get("units", ""),
        "citation": config.get("citation") or _source_label(output),
        "start": period_start,
        "end": period_end,
        "cadence": "Periodo del CSV" if output.get('map_kind') else "Mensual",
        "layout": "comparacion",
        "author": config.get("author", "Henry P. Conteron Moreta"),
        "description": config.get("subtitle", ""),
        "source": 'local',
        "period_labels": output.get('periods', []),
        "video_type": 'CSV geográfico' if output.get('map_kind') else 'Comparación climática',
    }
    write_json(job / "project.json", {**config, **project})
    write_json(job / "status.json", {"state": "running", "pid": os.getpid(), "progress": 0.0, "message": "Preparando maqueta de comparación", "updated": dt.datetime.now().timestamp()})
    csv_path = job / "comparison.csv"
    frame.to_csv(csv_path, index=False, encoding="utf-8-sig")
    if rank_frame is not None:
        rank_frame.to_csv(job / "ranking-provincias.csv", index=False, encoding="utf-8-sig")

    video_partial = job / "video-incompleto.mp4"
    writer = imageio_ffmpeg.write_frames(
        str(video_partial), (1080, 1920), fps=fps, codec="libx264",
        pix_fmt_in="rgb24", pix_fmt_out="yuv420p", macro_block_size=1,
        output_params=["-crf", "19", "-preset", "fast", "-movflags", "+faststart"],
    )
    writer.send(None)
    cached_phase = None
    pixels = None
    try:
        for index in range(total_frames):
            if (job / 'cancel.request').exists():
                raise InterruptedError('Exportación cancelada.')
            progress = index / max(1, total_frames - 1)
            phase = min(len(steps)-1, int(min(.999999, progress) * len(steps)))
            if phase != cached_phase:
                image = render_preview(frame, output, config, rank_frame=rank_frame, progress=progress)
                pixels = np.asarray(image)
                cached_phase = phase
            writer.send(pixels)
            if progress_callback and (index % max(1, fps) == 0 or index == total_frames - 1):
                progress_callback((index + 1) / total_frames)
        if closing_enabled:
            for _ in range(round(closing_duration * fps)):
                if (job / 'cancel.request').exists():
                    raise InterruptedError('Exportación cancelada.')
                writer.send(np.asarray(closing_image))
    except Exception as error:
        writer.close()
        write_json(job / "status.json", {
            "state": "cancelled" if isinstance(error, InterruptedError) else "failed", "progress": 0.0,
            "message": f"{type(error).__name__}: {error}",
            "updated": dt.datetime.now().timestamp(),
        })
        raise
    writer.close()
    final = job / "ecuador-vivo.mp4"
    if closing_enabled:
        closing_image.save(job / 'endcard.png')
    try:
        assembled, montage = assemble(job, video_partial, config, map_duration=duration,
            endcard_duration=closing_duration, status=lambda message: write_json(job/'status.json',
                {'state': 'running', 'pid': os.getpid(), 'progress': .95, 'message': message, 'updated': dt.datetime.now().timestamp()}))
        if (job/'cancel.request').exists():
            raise InterruptedError('Montaje cancelado antes de finalizar.')
        assembled.replace(final)
    except Exception as error:
        write_json(job/'status.json', {'state': 'cancelled' if isinstance(error, InterruptedError) else 'failed',
            'progress': .95, 'message': str(error), 'updated': dt.datetime.now().timestamp()})
        raise

    source_records = []
    for receipt in output.get("receipts", []):
        manifest = receipt.get("manifest", {})
        source_records.append({
            "provider": receipt.get("provider"),
            "sha256": _sha256(receipt['csv_path']) if receipt.get('csv_path') and Path(receipt['csv_path']).is_file() else None,
            "period": manifest.get("requested_period", {"start": receipt.get("start"), "end": receipt.get("end")}),
              "source_url": manifest.get("source_url") or manifest.get("provider_url"),
              "request_urls": manifest.get('request_urls', []),
              "source_csv_sha256": manifest.get('source_csv_sha256', []),
              "retrieved_utc": manifest.get('retrieved_utc'),
            "archive_sha256": _sha256(receipt["zip_path"]) if receipt.get("zip_path") and Path(receipt["zip_path"]).is_file() else None,
            "manifest_path_local": receipt.get("manifest_path"),
        })
    summary = {
        "type": "climate_comparison",
        "variable": config.get("variable", output.get("parameter")),
        "units": config.get("units", ""),
        "mode": output.get("mode"),
        "area": output.get("area"),
        "years": output.get("years", []),
        "months": [int(output.get("first_month", 1)), int(output.get("last_month", 12))],
        "aggregation": "sum of complete monthly spatial means" if str(output.get("parameter", "")).upper() in ("PRECTOTCORR", "CHIRPS_PRECTOT") else "day-weighted temporal mean of complete monthly spatial means",
        "values": json.loads(frame.to_json(orient="records")),
        "ranking": json.loads(rank_frame.to_json(orient="records")) if rank_frame is not None else [],
    }
    geographic_csv = output.get('map_kind') in ('points', 'polygons')
    if geographic_csv:
        summary = {'type': 'geographic_csv', 'representation': output['map_kind'],
                   'variable': config.get('variable'), 'units': config.get('units', ''),
                   'periods': output['periods'], 'records': json.loads(frame.to_json(orient='records')),
                   'input_rows': output.get('input_rows'), 'rejected_rows': output.get('rejected_rows', 0),
                   'aggregation': 'count of CSV records, not population' if output['map_kind'] == 'points' else 'original CSV values; no implicit aggregation'}
    if not (job / "preview.png").exists():
        render_preview(frame, output, config, rank_frame=rank_frame, progress=1.0).save(job / "preview.png")
    receipt = {
        "complete": True,
        "render_type": "geographic_csv" if geographic_csv else "climate_comparison",
        "duration_seconds": montage['duration_seconds'],
        "montage": montage,
        "endcard": {'enabled': closing_enabled, 'duration_seconds': closing_duration, 'summary': closing_summary},
        "fps": fps,
        "video_sha256": _sha256(final),
        "comparison_csv_sha256": _sha256(csv_path),
        "project": {**config, **project},
        "comparison": summary,
        "source_records": source_records,
        "methodology": {
            "map_representation": output.get('map_kind', 'raster'),
            "map_layout": config.get('map_layout', 'Dos mapas'),
            "map_steps": steps,
            "shared_color_scale": [config['scale_min'], config['scale_max']],
            "display_resampling": "bilinear, restricted to original valid cells" if config.get('map_smooth', True) else "nearest native cell",
            "map_source_rule": "Original source rasters, province polygons or geolocated CSV records; never a surface inferred from a scalar mean.",
            "coverage_rule": "Incomplete months and missing values are not interpolated or extrapolated.",
            "area_weighting": "Approximate cos(latitude) area weighting for geographic raster cells.",
            "city_rule": "Nearest grid cell to listed city coordinate; not an in-situ station measurement.",
        },
    }
    if geographic_csv:
        receipt['methodology'].update(
            coverage_rule='CSV rows are mapped individually; missing records do not demonstrate absence.',
            area_weighting='Not applied to imported CSV values.',
            city_rule='Explicit WGS84 coordinates supplied by the CSV; no nearest weather-grid sampling.',
            display_resampling='None: points or province polygons.',
        )
    write_json(job / "receipt.json", receipt)
    write_json(job / "status.json", {"state": "complete", "progress": 1.0, "message": "Comparación exportada", "updated": dt.datetime.now().timestamp()})
    return job
