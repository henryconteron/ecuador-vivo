"""Validated CSV geography and explicit metrics: records are not populations."""
from __future__ import annotations

import io
import json

import numpy as np
import pandas as pd

from comparison_maps import normalized
from maqueta import MAIN_BOX, GALAPAGOS_BOX
from data import province_boundaries
from model import default_project

CATEGORY_COLORS = ['#58e2cc', '#ffd568', '#ff647c', '#74bdf7', '#c4a3ff', '#f5f7fa']


def read_csv(payload):
    if len(payload) > 20 * 1024 * 1024:
        raise ValueError('El CSV supera 20 MiB. Filtra primero el área o periodo para no saturar el editor.')
    for encoding in ('utf-8-sig', 'cp1252'):
        try:
            frame = pd.read_csv(io.BytesIO(payload), sep=None, engine='python', encoding=encoding)
            if len(frame) > 100000:
                raise ValueError('Limita el CSV a 100.000 filas por proyecto.')
            if frame.empty or not len(frame.columns):
                raise ValueError('El CSV está vacío.')
            return frame
        except UnicodeDecodeError:
            continue
    raise ValueError('No se pudo leer el CSV. Usa UTF-8 y separador coma o punto y coma.')


def _numeric(series):
    return pd.to_numeric(series.astype(str).str.strip().str.replace(',', '.', regex=False), errors='coerce')


def prepare_csv(frame, *, kind, latitude=None, longitude=None, category=None,
                province=None, value=None, period=None, allow_invalid=False):
    if kind not in ('points', 'polygons'):
        raise ValueError('Elige puntos o provincias.')
    result = pd.DataFrame(index=frame.index)
    result['period'] = frame[period].fillna('').astype(str).str.strip() if period else 'Todos los registros'
    invalid = result['period'].eq('')
    if kind == 'points':
        if not latitude or not longitude or latitude == longitude:
            raise ValueError('Selecciona dos columnas distintas para latitud y longitud WGS84.')
        result['lat'], result['lon'] = _numeric(frame[latitude]), _numeric(frame[longitude])
        invalid |= ~result.lat.between(-90, 90) | ~result.lon.between(-180, 180)
        in_frame = pd.Series(False, index=frame.index)
        for west, south, east, north in (MAIN_BOX, GALAPAGOS_BOX):
            in_frame |= result.lon.between(west, east) & result.lat.between(south, north)
        # This editor's two geographic windows cover Ecuador + its archipelago.
        # Out-of-window rows must not inflate metrics for invisible points.
        invalid |= ~in_frame
        result['category'] = frame[category].fillna('').astype(str).str.strip() if category else 'Registros'
        invalid |= result.category.eq('')
    else:
        if not province or not value:
            raise ValueError('Selecciona provincia y columna numérica.')
        names = {normalized(f['properties']['shapeName']): f['properties']['shapeName'] for f in province_boundaries()}
        result['area'] = frame[province].map(lambda name: names.get(normalized(name)))
        result['value'] = _numeric(frame[value])
        invalid |= result.area.isna() | ~np.isfinite(result.value)
    rejected = int(invalid.sum())
    if rejected and not allow_invalid:
        raise ValueError(f'{rejected} fila(s) tienen coordenadas, provincia, valor o periodo inválidos, o están fuera del encuadre Ecuador/Galápagos. Corrige el CSV o autoriza excluirlas explícitamente.')
    result = result[~invalid].copy()
    if result.empty:
        raise ValueError('No quedan registros válidos.')
    if kind == 'polygons' and result.duplicated(['area', 'period']).any():
        raise ValueError('Hay varias filas para una misma provincia y periodo. Agrega los valores antes de importar; el editor no adivina si debe sumarlos o promediarlos.')
    categories = sorted(result.category.unique()) if kind == 'points' else []
    if len(categories) > 6:
        raise ValueError('Filtra hasta seis categorías por video para que la leyenda sea legible.')
    # ISO dates/year strings sort chronologically; other labels remain lexical
    # and can be reordered in the UI. No invented dates or sampling intervals.
    periods = sorted(result.period.unique())
    records = json.loads(result.to_json(orient='records', double_precision=12))
    return {'map_kind': kind, 'records': records, 'periods': periods,
            'category_colors': dict(zip(categories, CATEGORY_COLORS)),
            'mode': 'nacional', 'area': 'Ecuador', 'parameter': 'CSV_RECORDS',
            'years': [], 'first_month': 1, 'last_month': 1, 'receipts': [],
            'source': 'CSV geográfico del usuario', 'rejected_rows': rejected,
            'input_rows': len(frame), 'valid_rows': len(result)}


def spatial_summary(output, config):
    frame = pd.DataFrame(output['records'])
    periods = output['periods']
    kind = output['map_kind']
    if kind == 'points':
        ranking = frame.category.value_counts()
        ranks = [{'name': str(name), 'value': int(count)} for name, count in ranking.items()]
        units = 'registros'
        cards = [
            {'value': str(len(frame)), 'label': 'Registros válidos', 'sub': 'No son individuos únicos'},
            {'value': str(len(ranking)), 'label': 'Categorías', 'sub': 'Según tu columna CSV'},
            {'value': str(len(periods)), 'label': 'Periodos', 'sub': 'Según tu archivo'},
            {'value': str(output.get('rejected_rows', 0)), 'label': 'Filas excluidas', 'sub': 'Con autorización explícita'},
        ]
        notes = ['Un punto representa un registro del archivo, no una población.',
                 'La falta de registros NO demuestra ausencia de la especie.',
                 'El muestreo y sus sesgos condicionan lo que vemos.',
                 'Revisa permisos y coordenadas sensibles antes de publicar.']
    else:
        rows = frame[frame.period == periods[-1]].sort_values('value', ascending=False)
        ranks = [{'name': str(row.area), 'value': float(row.value)} for row in rows.itertuples()]
        units = config.get('units', '')
        cards = [
            {'value': str(len(rows)), 'label': 'Provincias con dato', 'sub': periods[-1]},
            {'value': str(len(periods)), 'label': 'Periodos', 'sub': 'Valores originales del CSV'},
            {'value': f'{rows.value.max():.1f}', 'label': 'Mayor valor', 'sub': units},
            {'value': f'{rows.value.min():.1f}', 'label': 'Menor valor', 'sub': units},
        ]
        notes = ['Valor por provincia y periodo, sin interpolación espacial.',
                 'No se suman ni promedian columnas sin un método declarado.',
                 'Provincias sin dato quedan sin color, no se convierten en cero.']
    copy = {'subtitle': config.get('variable', 'Datos geográficos') + ' · Ecuador',
            'section_1': 'LOS DATOS EN CIFRAS', 'section_1_note': 'Archivo geográfico validado',
            'section_2': 'REGISTROS POR CATEGORÍA' if kind == 'points' else 'VALORES POR PROVINCIA',
            'section_2_note': 'Todos los registros' if kind == 'points' else periods[-1],
            'section_3': 'MÉTODO Y LÍMITES' if len(ranks) <= 12 else f'PROVINCIAS 13–{len(ranks)}',
            'section_3_note': 'Sin inventar cobertura', 'rank_axis_label': units,
            'footer': config.get('citation', output['source']), 'footer_2': 'Coordenadas WGS84 / límites geoBoundaries'}
    if not config.get('endcard_auto_text', True):
        copy['subtitle'] = config.get('endcard_subtitle') or copy['subtitle']
    return {'comparison_cards': cards, 'comparison_copy': copy, 'geographic_records': True, 'map_kind': kind,
            'rank_label': f'{len(frame)} registros · {len(ranks)} categorías' if kind == 'points' else f'{len(ranks)} provincias con dato',
            'province_rank': ranks, 'city_rank': ranks, 'comparison_notes': notes if len(ranks) <= 12 else [],
            'aggregate_units': units, 'units': units, 'aggregation': 'count_records' if kind == 'points' else 'original_csv_values',
            'scope': 'Ecuador', 'cadence': 'Periodos del CSV', 'decimals': 0 if kind == 'points' else 1,
            'warnings': notes, 'extreme_method': 'Valores del CSV; no extremos meteorológicos ni estimación de población.'}


def render_spatial_endcard(output, config):
    from endcard import compose_endcard
    summary = spatial_summary(output, config)
    project = default_project()
    project.update(config)
    project.update(source='local', units=summary['units'], endcard_auto_text=True,
                   endcard_aggregation='mean', endcard_aggregation_mode='manual')
    return compose_endcard(project, summary), summary
