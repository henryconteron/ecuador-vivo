"""Prepare a completed local render as a reviewable Andes Pulso case draft."""
import csv
import datetime as dt
import json
import os
import re
import shutil
import uuid
from pathlib import Path

from model import ROOT, STORE
from jobs import read_json, write_json
from variables import endcard_copy, resolve_aggregation

REGISTRY = ROOT / 'data' / 'cases' / 'registry.json'
MAX_INLINE_VIDEO_BYTES = 90 * 1024 * 1024


def default_case_id(project):
    """A stable readable case identifier users can edit before staging."""
    import unicodedata

    label = unicodedata.normalize('NFKD', str(project.get('variable', 'variable')))
    label = ''.join(char for char in label if not unicodedata.combining(char))
    label = re.sub(r'[^a-zA-Z0-9]+', '-', label.lower()).strip('-') or 'variable'
    dates = [row.get('date') for row in project.get('entries', [])
             if row.get('date')]
    start = project.get('start') or (min(dates) if dates else None)
    year = dt.date.fromisoformat(start).year if start else dt.date.today().year
    return f'{label}-ecuador-{year}'


def _csv_bytes(summary):
    from io import StringIO

    stream = StringIO(newline='')
    identity = ('category' if summary.get('map_kind') == 'points' else
                'province' if summary.get('map_kind') == 'polygons' else
                'territory_or_year' if summary.get('comparison_cards') else 'province')
    fields = ['rank', identity, 'value', 'units', 'valid_dates',
              'date_coverage_fraction']
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    for rank, row in enumerate(summary.get('province_rank', []), 1):
        writer.writerow({
            'rank': rank,
            identity: row['name'],
            'value': row['value'],
            'units': summary.get('aggregate_units', summary.get('units', '')),
            'valid_dates': row.get('days'),
            'date_coverage_fraction': row.get('coverage'),
        })
    return stream.getvalue().encode('utf-8-sig')


def _public_receipt(receipt):
    project = dict(receipt.get('project', {}))
    # Local absolute paths are not useful on the public site and can expose a
    # person's computer layout. The source hashes and URLs remain auditable.
    project.pop('entries', None)
    project.pop('comparison_data', None)
    project.pop('spatial_data', None)
    def without_local_paths(value):
        if isinstance(value, dict):
            return {key: without_local_paths(item) for key, item in value.items()
                    if not (isinstance(item, str) and (re.match(r'^[A-Za-z]:[\\/]', item) or item.startswith('/')))}
        if isinstance(value, list):
            return [without_local_paths(item) for item in value]
        return value
    project = without_local_paths(project)
    records = []
    for row in receipt.get('source_records', []):
        records.append({key: row[key] for key in (
            'date', 'band', 'sha256', 'source_url', 'native_crs',
            'embedded_scale', 'embedded_offset', 'province_mean_method',
            'provider', 'period', 'archive_sha256',
            'request_urls', 'source_csv_sha256', 'retrieved_utc',
        ) if key in row})
    return {
        'schema_version': 1,
        'case_id': '',
        'generated_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'project': project,
        'temporal_interpolation': receipt.get('temporal_interpolation'),
        'duration_seconds': receipt.get('duration_seconds'),
        'video_sha256': receipt.get('video_sha256'),
        'boundary_source': receipt.get('boundary_source'),
        'source_records': records,
        'endcard': receipt.get('endcard'),
        'galapagos': receipt.get('galapagos'),
        'render_type': receipt.get('render_type', 'raster_sequence'),
        'comparison': receipt.get('comparison'),
        'methodology': receipt.get('methodology'),
        'montage': without_local_paths(receipt.get('montage')),
    }


def prepare_case(job, case_id):
    """Copy one completed render into Git-tracked case/media folders.

    Existing cases are never overwritten. The returned registry record is a
    draft: committing and deploying the website remains an editorial action.
    """
    job = Path(job).resolve()
    if not job.is_relative_to((STORE / 'jobs').resolve()):
        raise ValueError('Carpeta de exportación fuera del estudio local.')
    if (not isinstance(case_id, str) or len(case_id) > 72
            or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', case_id)):
        raise ValueError('Usa un identificador corto en minúsculas separado por guiones.')

    state = read_json(job / 'status.json', {})
    receipt = read_json(job / 'receipt.json', {})
    video = job / 'ecuador-vivo.mp4'
    if state.get('state') != 'complete' or receipt.get('complete') is not True or not video.is_file():
        raise ValueError('Solo se pueden preparar exportaciones terminadas.')
    geographic = receipt.get('render_type') == 'geographic_csv'
    if geographic and not receipt.get('project', {}).get('share_spatial_records'):
        raise ValueError('Este video contiene datos geográficos del CSV. Revisa permisos y coordenadas sensibles y activa la autorización para compartirlos en el editor antes de preparar el caso web.')
    if video.stat().st_size > MAX_INLINE_VIDEO_BYTES:
        raise ValueError('El MP4 supera 90 MiB; usa un alojamiento de video o GitHub Release.')

    registry = read_json(REGISTRY, {})
    if not isinstance(registry.get('cases'), list):
        raise ValueError('El catálogo de casos no tiene el formato esperado.')
    if any(row.get('id') == case_id for row in registry['cases']):
        raise FileExistsError(f'Ya existe el caso «{case_id}» en Andes Pulso.')

    case_target = ROOT / 'data' / 'cases' / case_id
    media_target = ROOT / 'assets' / 'media' / 'andes-pulso' / case_id
    if case_target.exists() or media_target.exists():
        raise FileExistsError(f'Ya existe una carpeta para «{case_id}»; no se sobrescribió.')

    case_parent, media_parent = case_target.parent, media_target.parent
    case_parent.mkdir(parents=True, exist_ok=True)
    media_parent.mkdir(parents=True, exist_ok=True)
    nonce = uuid.uuid4().hex
    case_stage = case_parent / f'.{case_id}.{nonce}.tmp'
    media_stage = media_parent / f'.{case_id}.{nonce}.tmp'
    case_stage.mkdir()
    media_stage.mkdir()
    created_targets = []
    try:
        summary = receipt.get('endcard', {}).get('summary', {})
        project = receipt.get('project', {})
        if not summary:
            raise ValueError('El recibo no contiene métricas del cierre.')
        public_receipt = _public_receipt(receipt)
        public_receipt['case_id'] = case_id
        profile = resolve_aggregation(project)[1]
        copy = endcard_copy(project, summary, profile)
        copy.update(summary.get('comparison_copy', {}))

        (case_stage / 'receipt.json').write_text(
            json.dumps(public_receipt, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        public_summary = {
            'schema_version': 1,
            'case_id': case_id,
            'metric_definitions': {
                'spatial_mean': 'Promedio espacial ponderado por coseno de latitud en los píxeles válidos de cada fecha.',
                'province_rank': 'Promedio espacial sobre píxeles fuente nativos válidos dentro de cada polígono ADM1; en mapas regionales se limita al encuadre, y en el nacional incluye las 24 provincias. En CRS geográficos usa pesos aproximados cos(latitud). La serie temporal sigue la regla de agregación indicada.',
                'peak_pixel': summary.get('extreme_method'),
                'temporal_aggregation': summary.get('aggregation'),
            },
            'summary': summary,
            'display_copy': copy,
        }
        (case_stage / 'summary.json').write_text(
            json.dumps(public_summary, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        comparison = receipt.get('render_type') in ('climate_comparison', 'geographic_csv')
        metrics_name = 'metrics-records.csv' if geographic else 'metrics-periods.csv' if comparison else 'metrics-provinces.csv'
        (case_stage / metrics_name).write_bytes(_csv_bytes(summary))
        if comparison:
            shutil.copy2(job / 'comparison.csv', case_stage / 'comparison.csv')
            if (job / 'ranking-provincias.csv').is_file():
                shutil.copy2(job / 'ranking-provincias.csv', case_stage / 'ranking-provincias.csv')
        source_rows = public_receipt.get('source_records', [])
        with (case_stage / 'sources.csv').open('w', newline='', encoding='utf-8-sig') as handle:
            fields = ['date', 'band', 'source_url', 'sha256', 'native_crs', 'provider', 'period', 'archive_sha256']
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(source_rows)
        labels = project.get('period_labels', [])
        period_start = project.get('start') or (labels[0] if labels else source_rows[0].get('date', '') if source_rows else '')
        period_end = project.get('end') or (labels[-1] if labels else source_rows[-1].get('date', '') if source_rows else '')
        method = (
            f'# {copy["subtitle"]}\n\n'
            f'- Fuente declarada: {project.get("citation", "sin cita indicada")}\n'
            f'- Variable: {project.get("variable", "sin nombre")} ({project.get("units", "sin unidades")}).\n'
            f'- Frecuencia: {project.get("cadence", "no indicada")}; agregación aplicada: {summary.get("aggregation")}.\n'
            f'- Periodo: {period_start} – {period_end}.\n'
            f'- Alcance: {summary.get("scope", "encuadre indicado en el recibo")}.\n'
            f'- Máximo: {summary.get("extreme_method", "método no indicado")}.\n\n'
            'La página conserva también el recibo con huellas SHA-256 por observación. '
            'Los rásteres completos no se copian al repositorio web; se conservan sus '
            'fuentes, URLs, fechas y checksums para localizar y verificar los insumos.\n'
        )
        (case_stage / 'methodology.md').write_text(method, encoding='utf-8')

        shutil.copy2(video, media_stage / 'ecuador-vivo.mp4')
        poster = job / 'endcard.png'
        if not poster.is_file():
            frames = sorted(job.glob('frame-*.png'))
            poster = frames[0] if frames else None
        if poster:
            shutil.copy2(poster, media_stage / 'poster.png')

        title = project.get('title') or project.get('variable') or case_id
        english_variables = {
            'precipitation': 'Rainfall', 'precipitation_rate': 'Rainfall rate',
            'temperature': 'Temperature', 'wind_speed': 'Wind speed',
            'index': project.get('variable') or 'Spectral index',
            'anomaly': 'Anomaly', 'percent': 'Coverage', 'flux': 'Energy flux',
            'generic': project.get('variable') or 'Environmental variable',
        }
        copy_hook = copy.get('section_2', 'Explora los datos detrás del mapa.')
        record = {
            'id': case_id,
            'kind': profile['kind'],
            'status': 'draft',
            'title_es': title,
            'title_en': f'{english_variables.get(profile["kind"], "Environmental data")} across Ecuador',
            'hook_es': copy.get('subtitle', ''),
            'hook_en': f'{english_variables.get(profile["kind"], "The variable")} across Ecuador during the selected period.',
            'question_es': copy_hook,
            'question_en': 'Explore the provincial ranking and inspect the data and methods behind the video.',
            'period_es': f'{period_start} – {period_end}',
            'period_en': f'{period_start} – {period_end}',
            'territories': [summary['scope']] if comparison else ['Ecuador'] if summary.get('national_extent') else ['Encuadre del mapa'],
            'sources_es': project.get('citation') or 'Fuente declarada en el recibo',
            'sources_en': project.get('citation') or 'Source listed in the provenance receipt',
            'video': {
                'href': f'assets/media/andes-pulso/{case_id}/ecuador-vivo.mp4',
                'poster': (f'assets/media/andes-pulso/{case_id}/poster.png'
                           if (media_stage / 'poster.png').is_file() else None),
            },
            'summary_href': f'data/cases/{case_id}/summary.json',
            'limits_es': '; '.join(summary.get('warnings', [])) or
                         'Estimación espacial; consulta el recibo para método, alcance y límites de la fuente.',
            'limits_en': '; '.join(summary.get('warnings', [])) or
                         'Spatial estimate; see the receipt for method, extent, and source limitations.',
            'files': [
                {'label_es': 'Resumen de métricas', 'href': f'data/cases/{case_id}/summary.json'},
                {'label_es': 'Valores del cierre CSV' if comparison else 'Ranking provincial CSV', 'href': f'data/cases/{case_id}/{metrics_name}'},
                {'label_es': 'Recibo y trazabilidad', 'href': f'data/cases/{case_id}/receipt.json'},
                {'label_es': 'Fuentes por fecha CSV', 'href': f'data/cases/{case_id}/sources.csv'},
                {'label_es': 'Método', 'href': f'data/cases/{case_id}/methodology.md'},
            ],
        }
        if comparison:
            if geographic:
                record['kind'] = 'geographic_records'
                record['title_en'] = 'Geographic records across Ecuador'
                record['hook_en'] = 'Inspect the geographic records, their sources and interpretation limits.'
                record['question_en'] = 'What do the mapped records show, and what can they not demonstrate?'
            record['question_es'] = ('Registros geográficos del CSV; consulta procedencia, cobertura y límites de interpretación.' if geographic
                                     else 'Comparación de años con la misma ventana mensual; consulta los valores, fuentes y cobertura.')
            record['files'].append({'label_es': 'Registros geográficos CSV' if geographic else 'Comparación mensual CSV',
                                    'label_en': 'Geographic records CSV' if geographic else 'Monthly comparison CSV', 'href': f'data/cases/{case_id}/comparison.csv'})
            if (case_stage / 'ranking-provincias.csv').is_file():
                record['files'].append({'label_es': 'Ranking de todos los años CSV', 'label_en': 'Ranking for all years CSV', 'href': f'data/cases/{case_id}/ranking-provincias.csv'})
            public_summary['metric_definitions'] = receipt.get('methodology', {})
            public_summary['metric_definitions']['temporal_aggregation'] = receipt['comparison']['aggregation']
            (case_stage / 'summary.json').write_text(json.dumps(public_summary, ensure_ascii=False, indent=2), encoding='utf-8')

        case_stage.replace(case_target)
        created_targets.append(case_target)
        media_stage.replace(media_target)
        created_targets.append(media_target)
        registry['cases'].insert(0, record)
        registry['updated'] = dt.date.today().isoformat()
        write_json(REGISTRY, registry)
        return record
    except Exception:
        for stage in (case_stage, media_stage):
            if stage.exists():
                shutil.rmtree(stage)
        # Both destinations were checked as absent before staging; remove only
        # directories created by this transaction if a later step failed.
        for target in created_targets:
            if target.exists():
                shutil.rmtree(target)
        raise
