"""Detección del tipo de variable y del cálculo temporal que le corresponde.

Regla física que aplica todo el cierre de métricas:
* magnitudes *por intervalo* (lluvia en mm/día, energía diaria) → se SUMAN;
* magnitudes *intensivas* (temperatura, índices, viento, %, W/m²,
  anomalías) → se PROMEDIAN; sumarlas no tiene sentido físico;
* direcciones (grados de viento) → no admiten promedio aritmético.

``detect_profile`` lee unidades y nombre científico de la variable del
proyecto. Si no reconoce nada devuelve el perfil ``generic`` con promedio (la
opción segura) y una advertencia visible en el recibo.
"""

import re
import unicodedata


def _norm(text):
    text = unicodedata.normalize('NFKD', str(text or '').lower())
    return ''.join(c for c in text if not unicodedata.combining(c))


def _unit_key(units):
    u = _norm(units).replace(' ', '').replace('º', '°').replace('^', '')
    return u.replace('m²', 'm2').replace('m-2', 'm2').replace('·', '')


# Cadencia del proyecto → fragmentos que identifican «por intervalo».
_PER_INTERVAL = {
    'Diaria': ('/dia', '/d', 'perday', '/day', 'diario'),
    'Mensual': ('/mes', '/month', 'permonth', 'mensual'),
    'Anual': ('/ano', '/year', '/yr', 'peryear', 'anual'),
}


def _profile(kind, aggregation, *, unit='', decimals=1, signed=False,
             intensive=False, supported=True, warnings=(), peak_word='mayor'):
    return {
        'kind': kind,
        'aggregation': aggregation,
        'accumulated_unit': unit,
        'decimals': decimals,
        'signed': signed,          # puede tomar valores negativos legítimos
        'intensive': intensive,    # sumar es físicamente incorrecto
        # La tarjeta actual resume una única magnitud escalar por fecha. Una
        # dirección requiere media circular (o componentes u/v), por lo que
        # no debe pasar silenciosamente por el promedio aritmético.
        'supported': supported,
        'warnings': list(warnings),
        'peak_word': peak_word,
    }


def detect_profile(project):
    # Editorial copy is mutable presentation, never physical metadata. A title
    # mentioning "anomaly" must not turn a rainfall total into a temporal mean.
    text = _norm(project.get('variable', ''))
    units = _unit_key(project.get('units', ''))
    cadence = project.get('cadence', 'Diaria')

    # 1) Anomalías: siempre intensivas y con signo.
    if 'anomal' in text or 'desviacion' in text:
        return _profile('anomaly', 'mean', unit=project.get('units', ''),
                        decimals=2, signed=True, intensive=True)

    # 2) Direcciones: no se promedian.
    if units in ('°', 'deg', 'grados') or 'direccion' in text:
        return _profile('direction', 'mean', unit=project.get('units', ''),
                        decimals=0, intensive=True, supported=False,
                        warnings=['Las direcciones (grados) no admiten promedio '
                                  'aritmético: usa componentes u/v o una media '
                                  'circular antes de importar.'])

    # 3) Precipitación u otras cantidades por intervalo.
    is_rain_word = bool(re.search(r'lluvia|precip|rain|pluvio', text))
    if units.startswith('mm') or (is_rain_word and units in ('', 'mm')):
        if re.search(r'/h|/hr|/s|/min|h-1|s-1|min-1', units):
            return _profile('precipitation_rate', 'mean',
                            unit=project.get('units', ''), decimals=1,
                            intensive=True,
                            warnings=['Tasa de precipitación: no se acumula sin '
                                      'integrar la duración de cada intervalo.'])
        per = _PER_INTERVAL.get(cadence, ())
        if units == 'mm' or any(units.endswith(tag) for tag in per):
            return _profile('precipitation', 'sum', unit='mm', decimals=1)
        return _profile('precipitation_rate', 'mean',
                        unit=project.get('units', ''), decimals=1,
                        intensive=True,
                        warnings=[f'Las unidades «{project.get("units")}» no '
                                  f'coinciden con la cadencia «{cadence}»; se '
                                  'promedia en vez de acumular.'])
    if re.search(r'mj/m2|j/m2', units) and any(
            units.endswith(t) for t in _PER_INTERVAL.get(cadence, ())):
        return _profile('energy', 'sum', unit=units.split('/')[0] + '/m²',
                        decimals=1)

    # 4) Temperatura.
    if re.search(r'^(°|)c$|°c|degc|celsius|°f|^k$|kelvin', units) or 'temperatura' in text:
        return _profile('temperature', 'mean', unit=project.get('units', ''),
                        decimals=1, signed=True, intensive=True)

    # 5) Índices espectrales (NDVI, NDWI, MNDWI, NDMI, EVI…).
    if re.search(r'\b(ndvi|ndwi|mndwi|ndmi|evi|savi|nbr|ndti)\b|indice', text):
        return _profile('index', 'mean', unit=project.get('units', ''),
                        decimals=2, signed=True, intensive=True)

    # 6) Viento (rapidez).
    if re.search(r'm/s|ms-1|km/h|kmh-1|kt|knot|nudo|mph', units) or 'viento' in text:
        return _profile('wind_speed', 'mean', unit=project.get('units', ''),
                        decimals=1, intensive=True)

    # 7) Porcentajes (nubosidad, humedad, cobertura…).
    if units == '%' or 'fraccion' in text or 'humedad' in text:
        return _profile('percent', 'mean', unit=project.get('units', '') or '%',
                        decimals=1, intensive=True)

    # 8) Flujos / radiación / presión.
    if re.search(r'w/m2|hpa|kpa|pa$', units):
        return _profile('flux', 'mean', unit=project.get('units', ''),
                        decimals=1, intensive=True)

    return _profile('generic', 'mean', unit=project.get('units', ''),
                    decimals=1, signed=True, intensive=True,
                    warnings=['Variable no reconocida: se usa promedio temporal, '
                              'la opción segura. Revisa el cálculo antes de publicar.'])


def resolve_aggregation(project):
    """Operación temporal efectiva: automática o elegida a mano.

    En modo manual se rechaza *sumar* una magnitud intensiva, porque la cifra
    resultante no tiene significado físico.
    """
    profile = detect_profile(project)
    if not profile['supported']:
        raise ValueError(
            'El cierre numérico no admite direcciones: prepara componentes '
            'u/v o una media circular antes de importar la serie.'
        )
    mode = project.get('endcard_aggregation_mode', 'auto')
    if mode == 'auto':
        return profile['aggregation'], profile
    chosen = project.get('endcard_aggregation', 'mean')
    if chosen == 'sum' and profile['intensive']:
        raise ValueError(
            f'No se puede sumar una variable de tipo «{profile["kind"]}» '
            f'({project.get("units", "sin unidades")}): usa «Promediar».'
        )
    return chosen, profile


RAIN_SECTION_2 = '¿DÓNDE LLOVIÓ MÁS?'
SECTION_2_TITLES = {
    'temperature': '¿DÓNDE HIZO MÁS CALOR?',
    'anomaly': '¿DÓNDE FUE MÁS ANÓMALO?',
    'wind_speed': '¿DÓNDE SOPLÓ MÁS FUERTE?',
}


def section_2_title(project, profile):
    """Sustituye solo el texto de fábrica de lluvia; un título editado se respeta."""
    title = project.get('endcard_section_2', RAIN_SECTION_2)
    if title.strip().upper() != RAIN_SECTION_2 or profile['kind'] == 'precipitation':
        return title
    return SECTION_2_TITLES.get(profile['kind'], '¿DÓNDE FUE MÁS ALTO?')


_COPY = {
    'precipitation': {
        'variable': 'la lluvia',
        'date_label': 'Mayor promedio espacial',
        'period_sum': 'Mes más lluvioso',
        'period_mean': 'Mes con mayor promedio',
        'average': ('Promedio espacial', 'del período'),
        'maximum': ('Máximo por píxel', 'registrado'),
        'rank_question': '¿DÓNDE LLOVIÓ MÁS?',
        'period_suffix': 'lluvia',
    },
    'temperature': {
        'variable': 'la temperatura',
        'date_label': 'Mayor temperatura media',
        'period_sum': 'Período con mayor suma',
        'period_mean': 'Mes más cálido',
        'average': ('Temperatura media', 'espacial'),
        'maximum': ('Máxima por píxel', 'registrada'),
        'rank_question': '¿DÓNDE HIZO MÁS CALOR?',
        'period_suffix': 'temperatura',
    },
    'anomaly': {
        'variable': 'la anomalía',
        'date_label': 'Mayor promedio espacial',
        'period_sum': 'Período con mayor suma',
        'period_mean': 'Período con mayor anomalía',
        'average': ('Anomalía media', 'espacial'),
        'maximum': ('Máximo por píxel', 'registrado'),
        'rank_question': '¿DÓNDE FUE MÁS ANÓMALO?',
        'period_suffix': 'anomalía',
    },
    'index': {
        'variable': 'el índice',
        'date_label': 'Mayor promedio espacial',
        'period_sum': 'Período con mayor suma',
        'period_mean': 'Período con mayor promedio',
        'average': ('Promedio espacial', 'del índice'),
        'maximum': ('Máximo por píxel', 'registrado'),
        'rank_question': '¿DÓNDE FUE MAYOR?',
        'period_suffix': 'índice',
    },
    'wind_speed': {
        'variable': 'el viento',
        'date_label': 'Mayor velocidad media',
        'period_sum': 'Período con mayor suma',
        'period_mean': 'Mes con más viento',
        'average': ('Velocidad media', 'espacial'),
        'maximum': ('Máxima por píxel', 'registrada'),
        'rank_question': '¿DÓNDE SOPLÓ MÁS FUERTE?',
        'period_suffix': 'velocidad del viento',
    },
    'percent': {
        'variable': 'la cobertura',
        'date_label': 'Mayor promedio espacial',
        'period_sum': 'Período con mayor suma',
        'period_mean': 'Período con mayor promedio',
        'average': ('Promedio espacial', 'del período'),
        'maximum': ('Máximo por píxel', 'registrado'),
        'rank_question': '¿DÓNDE FUE MAYOR?',
        'period_suffix': 'cobertura',
    },
    'flux': {
        'variable': 'el flujo',
        'date_label': 'Mayor promedio espacial',
        'period_sum': 'Período con mayor suma',
        'period_mean': 'Período con mayor promedio',
        'average': ('Promedio espacial', 'del período'),
        'maximum': ('Máximo por píxel', 'registrado'),
        'rank_question': '¿DÓNDE FUE MAYOR?',
        'period_suffix': 'flujo',
    },
    'generic': {
        'variable': 'la variable',
        'date_label': 'Mayor promedio espacial',
        'period_sum': 'Período con mayor suma',
        'period_mean': 'Período con mayor promedio',
        'average': ('Promedio espacial', 'del período'),
        'maximum': ('Máximo por píxel', 'registrado'),
        'rank_question': '¿DÓNDE FUE MAYOR?',
        'period_suffix': 'variable',
    },
}


def endcard_copy(project, summary, profile=None):
    """Create scientifically matched display labels for the automatic card."""
    profile = profile or detect_profile(project)
    kind = _COPY.get(profile['kind'], _COPY['generic'])
    cadence = project.get('cadence', 'Diaria')
    year = summary.get('year')
    if year is not None:
        section_one = f'{year} EN CIFRAS'
        subtitle = f'Así se comportó {kind["variable"]} en Ecuador durante {year}.'
    else:
        section_one = 'PERÍODO EN CIFRAS'
        subtitle = f'Así varió {kind["variable"]} en el período observado.'

    if cadence == 'Anual':
        period_label = ('Año con mayor acumulado' if summary.get('aggregation') == 'sum'
                        else 'Año con mayor promedio')
    elif cadence == 'Por observación':
        period_label = 'Observaciones válidas'
    else:
        period_label = (kind['period_sum'] if summary.get('aggregation') == 'sum'
                        else kind['period_mean'])
    if cadence == 'Diaria':
        date_label = kind['date_label']
    elif cadence == 'Mensual':
        date_label = 'Mes con mayor promedio espacial'
    elif cadence == 'Anual':
        date_label = 'Año con mayor promedio espacial'
    elif cadence == 'Por observación':
        date_label = 'Observación con mayor promedio espacial'
    else:
        date_label = 'Observación con mayor promedio espacial'

    measure = project.get('variable') or project.get('title') or 'Variable'
    location = 'en Ecuador' if summary.get('national_extent') else 'en el encuadre seleccionado'
    unit = project.get('units', '').strip()
    rank_title = kind['rank_question']
    if profile['kind'] == 'index':
        rank_title = f'¿DÓNDE FUE MAYOR {measure.upper()}?'
    elif profile['kind'] == 'percent':
        text = _norm(' '.join(str(project.get(k, '')) for k in
                              ('variable', 'title', 'description')))
        if 'humedad' in text:
            rank_title = '¿DÓNDE HUBO MÁS HUMEDAD?'
        elif 'nube' in text or 'nubosidad' in text:
            rank_title = '¿DÓNDE HUBO MÁS NUBOSIDAD?'
        elif 'cobertura' in text:
            rank_title = '¿DÓNDE HUBO MÁS COBERTURA?'
        else:
            rank_title = f'¿DÓNDE FUE MAYOR {measure.upper()}?'
    if not project.get('endcard_auto_text', True):
        rank_title = section_2_title(project, profile)
    source = (
        'CHIRPS v2 · resolución nativa ≈ 5,6 km'
        if project.get('source') == 'chirps'
        else (project.get('citation') or 'Fuente según el GeoTIFF importado')
    )
    domain = (
        'Ecuador continental · ranking provincial: 24 provincias'
        if summary.get('ranking_kind') == 'provinces'
        and len(summary.get('province_rank', [])) == 24
        else (summary.get('scope') or 'Encuadre seleccionado')
    )
    aggregation = summary.get('aggregation', profile['aggregation'])
    aggregate_units = summary.get('aggregate_units') or (
        project.get('endcard_accumulated_units', unit)
        if aggregation == 'sum' else unit
    )
    if aggregation == 'sum':
        axis_label = (f'Acumulado en {year}' if year
                      else 'Acumulado del período')
    else:
        axis_label = f'Promedio de {measure}'
    if aggregate_units:
        axis_label += f' ({aggregate_units})'

    maximum_labels = kind['maximum']
    if summary.get('extreme_method') == 'display_grid':
        maximum_labels = ('Máximo en rejilla', 'del mapa')
    elif summary.get('extreme_method') == 'mixed':
        maximum_labels = ('Máximo estimado', 'método mixto')
    copy = {
        'subtitle': (subtitle.replace('en Ecuador', location)
                     if summary.get('national_extent') is not True
                     else subtitle),
        'section_1': section_one,
        'section_1_note': f'Así cambió {kind["variable"]} {location}.',
        'section_2': rank_title,
        'section_2_note': (
            f'Provincias · {"acumulado temporal" if aggregation == "sum" else "promedio temporal"} · ranking 1–12'
        ),
        'section_3': 'PROVINCIAS 13–24',
        'section_3_note': 'Continuación del ranking provincial.',
        'date_label': date_label,
        'period_label': period_label,
        'average_labels': kind['average'],
        'maximum_labels': maximum_labels,
        'rank_axis_label': axis_label,
        'footer': source,
        'footer_2': domain,
    }
    if not project.get('endcard_auto_text', True):
        date_manual = project.get('endcard_date_metric_label', '').strip()
        period_manual = project.get('endcard_period_metric_label', '').strip()
        average_manual = project.get('endcard_average_metric_label', '').strip()
        maximum_manual = project.get('endcard_maximum_metric_label', '').strip()
        axis_manual = project.get('endcard_rank_axis_label', '').strip()
        copy.update({
            'section_1': project.get('endcard_section_1', copy['section_1']),
            'section_1_note': project.get('endcard_section_1_note', copy['section_1_note']),
            'section_2': project.get('endcard_section_2', copy['section_2']),
            'section_2_note': project.get('endcard_section_2_note', copy['section_2_note']),
            'section_3': project.get('endcard_section_3', copy['section_3']),
            'section_3_note': project.get('endcard_section_3_note', copy['section_3_note']),
            'date_label': date_manual or copy['date_label'],
            'period_label': period_manual or copy['period_label'],
            'average_labels': (average_manual or 'Promedio espacial', ''),
            'maximum_labels': (maximum_manual or 'Máximo por píxel', ''),
            'rank_axis_label': axis_manual or copy['rank_axis_label'],
            'footer': project.get('endcard_footer', copy['footer']),
            'footer_2': project.get('endcard_footer_2', copy['footer_2']),
        })
    return copy
