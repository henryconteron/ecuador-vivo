"""Audit independent references without confusing coarse labels with parcel truth."""
import csv
import hashlib
import io
import json
from urllib.request import Request, urlopen
from shapely.geometry import Point, shape, mapping
from shapely.ops import unary_union
from tools.parcelas.process_api import ROOT

REQUIRED=('human_interpreted','independent','parcel_boundary_verified','change_date_verified')


def assess_reference(reference):
    missing=[key for key in REQUIRED if reference.get(key) is not True]
    return {'usable_for_parcel_change_validation':not missing,'missing':missing,
            'compliance_decision':'not_performed'}


def main():
    folder=ROOT/'_local/parcelas/validacion/referencias-wri-ecuador'
    if folder.exists():
        raise ValueError('Output exists; preserve original audit')
    url='https://zenodo.org/records/15224684/files/validation_2001_2022.csv?download=1'
    with urlopen(Request(url,headers={'User-Agent':'EcuadorVivo-reference-audit/0.1'}),timeout=45) as response:
        raw=response.read(1_000_001)
    if len(raw)>1_000_000 or hashlib.md5(raw).hexdigest() != 'bc804d30187986108e17cbbf75b9082f':
        raise ValueError('Reference file does not match pinned published version')
    national_path=ROOT/'production/video_studio/reference_data/ecuador-national.geojson'
    country=unary_union([shape(f['geometry']) for f in json.loads(national_path.read_text())['features']])
    if not country.is_valid:
        raise ValueError('Invalid country boundary')
    rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    selected=[]
    for row in rows:
        point=Point(float(row['Longitude']),float(row['Latitude']))
        if country.covers(point):
            selected.append({'type':'Feature','geometry':mapping(point),'properties':{
                **row,'reference_support':'approximately 1 km interpretation unit, NOT cadastral parcel',
                'event_date':'unknown','parcel_boundary':'not_available',
                'source':'WRI and Google DeepMind validation set, Zenodo 15224684 v3 (CC BY 4.0)'}})
    gate=assess_reference({'human_interpreted':True,'independent':True,
        'parcel_boundary_verified':False,'change_date_verified':False})
    result={'source':url,'version':'Zenodo 15224684 v3','license':'CC BY 4.0',
        'sha256':hashlib.sha256(raw).hexdigest(),'published_md5':'bc804d30187986108e17cbbf75b9082f',
        'global_rows':len(rows),'ecuador_point_count':len(selected),
        'ecuador_boundary_sha256':hashlib.sha256(national_path.read_bytes()).hexdigest(),
        'boundary_source':'geoBoundaries gbOpen ADM0, academic reference, not cadastral authority',
        'gate':gate,'period':'2001-2022 aggregate; no precise event dates',
        'status':'candidate_cases_for_manual_review_not_validated_parcels',
        'sampling_warning':'This subset is not a representative Ecuador accuracy sample; no stable negative controls inferred.'}
    folder.mkdir(parents=True)
    (folder/'validation_2001_2022.csv').write_bytes(raw)
    (folder/'candidatos-ecuador.geojson').write_text(json.dumps({'type':'FeatureCollection','features':selected},indent=2),encoding='utf-8')
    (folder/'auditoria.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    lines=['# Ecuador Vivo · auditoría de referencias independientes','',
        f'{len(rows)} muestras globales de validación; {len(selected)} centros dentro de la referencia nacional de Ecuador.', '',
        'Fuente: WRI / Google DeepMind, interpretaciones visuales de imágenes de muy alta resolución, revisadas por otros intérpretes.',
        'Se conserva el conjunto de VALIDACIÓN; no se descargó ni mezcló el conjunto de entrenamiento.', '',
        '**Son centros de unidades de aproximadamente 1 km, NO polígonos de fincas ni fechas de tala.**',
        'Etiquetas del motor principal agregadas para 2001–2022; las secundarias tienen menor control de calidad.',
        'No convertirlas a cuadrados y llamarlas parcelas verificadas. No emplearlas para declarar cumplimiento después de 2020.', '',
        '## Casos ecuatorianos para revisión', '', '| ID | Clase interpretada | Confianza | Ruido |', '|---|---|---|---|']
    for feature in selected:
        p=feature['properties']; lines.append(f'| {p["ID"]} | {p["Driver_primary"]} | {p["Confidence_primary"]} | {p["Noise"]} |')
    lines += ['', '## Decisión', '',
        'Referencia humana útil para proponer casos, pero INSUFICIENTE para validar cambios a escala de parcela y fecha exacta.',
        'La selección geográfica usa geoBoundaries existente, no límites oficiales/catastrales. No se reporta exactitud nacional.',
        'Siguiente requisito: interpretar secuencias fechadas independientes en áreas autorizadas y registrar cambio/estabilidad, incertidumbre y perímetro.', '',
        '## Fuentes', '', '- https://zenodo.org/records/15224684 (v3 fijada, CC BY 4.0)',
        '- https://doi.org/10.1088/1748-9326/add606',
        '- https://arxiv.org/abs/2201.11192 (ReforesTree: biomasa en seis sitios ecuatorianos, no historial de deforestación)',
        '- https://ecuador.mapbiomas.org/iniciativas-y-productos/cobertura-y-uso-del-suelo/cobertura-30m/ (producto clasificado; contraste auxiliar, no verdad independiente)', '',
        'No se han publicado coordenadas, contactado productores ni descargado rásteres globales.']
    (folder/'AUDITORIA.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'global_rows':len(rows),'ecuador_candidates':len(selected),'gate':gate}))


if __name__=='__main__':
    main()
