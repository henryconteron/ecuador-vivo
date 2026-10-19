"""Local four-date diagnostic with service lineage; not a forest classifier."""
import json
import numpy as np
from shapely.geometry import shape
from tools.parcelas.process_api import DATES, PILOT, ROOT, build_request, inspect, output_folder, source_product
from tools.parcelas.radar_series import summarize_series, temporal_gaps
from tools.parcelas.catalog import validate_parcel


def main():
    destination = PILOT / 'serie-api-trazable'
    if destination.exists():
        raise ValueError('Output exists; do not overwrite')
    parcel = json.loads((ROOT/'_local/parcelas/referencias/cersgis-16579443/parcela-piloto.geojson').read_text())
    validate_parcel(parcel)
    geometry = shape(parcel['features'][0]['geometry'])
    catalogs = ['catalogo-corte2020', 'catalogo-202503']
    items = [item for name in catalogs for item in json.loads((PILOT/name/'catalog-items.geojson').read_text())['features']]
    observations, arrays, masks, groups = [], [], [], set()
    for day in DATES:
        folder = output_folder(day)
        if json.loads((folder/'request.json').read_text()) != build_request(day):
            raise ValueError('Saved request differs from reviewed processing contract')
        report, data, valid = inspect(day, write=False)
        saved = json.loads((folder/'inspection.json').read_text())
        if saved['sha256'] != report['sha256']:
            raise ValueError('Archive changed after inspection')
        product = source_product(report['metadata'])
        matches = [item for item in items if item['id'] == product and item.get('collection') == 'sentinel-1-grd']
        if len(matches) != 1:
            raise ValueError('Service product does not match unique catalog entry')
        item = matches[0]
        properties = item['properties']
        if not properties['datetime'].startswith(day) or not shape(item['geometry']).covers(geometry):
            raise ValueError('Wrong acquisition day or incomplete scene footprint')
        key = tuple(properties.get(k) for k in ('platform','sar:instrument_mode','sat:relative_orbit','sat:orbit_state'))
        if None in key or not {'VV','VH'}.issubset(properties.get('sar:polarizations', [])):
            raise ValueError('Incomplete acquisition properties')
        groups.add(key)
        observations.append({'date':day, 'product':product, 'sha256':report['sha256'],
            'usable_centres':report['usable_centres'], 'local_incidence_range_degrees':report['incidence_range_degrees']})
        arrays.append(data)
        masks.append(valid)
    if len(groups) != 1:
        raise ValueError('Do not combine acquisition groups')
    common = np.logical_and.reduce(masks)
    if not common.any():
        raise ValueError('No common valid support')
    stats = {band:summarize_series([data[index] for data in arrays],common)
             for index,band in enumerate(('VV','VH'))}
    report = {'status':'diagnostic_not_compliance', 'observations':observations,
        'acquisition_group':list(next(iter(groups))), 'common_centres':int(common.sum()),
        'results':stats, 'gaps_over_30_days':temporal_gaps(DATES), 'interpolation':'none',
        'crop_before_2021':'unknown', 'deforestation_assessment':'not_performed',
        'grid':{'epsg':32630,'bbox':[528200,754180,529640,755420],'spacing_m':20},
        'limits':['Ghana reference, not Ecuador validation', 'Small sample, speckle, moisture and terrain confounding',
                  'shadowMask does not exclude all layover', 'No independent scientific accuracy validation']}
    lines = ['# Ecuador Vivo · serie radar con procedencia', '',
        '**Diagnóstico técnico, no certificación ni conclusión de deforestación.**', '',
        'Referencia pública CERSGIS 352, Ghana. Cacao observado en marzo de 2025; uso en 2020 desconocido.', '',
        'Cuatro descargas API: ID de producto del servicio contrastado con catálogo y cobertura de la parcela.',
        'Mismo Sentinel-1A, IW, órbita relativa 45, ascendente, VV/VH. Gamma0 terreno, DEM Copernicus 30.',
        'Grilla exacta de 20 m; no equivale a exactitud de 20 m. Sin filtro speckle ni interpolación temporal.',
        f'Soporte válido común: {int(common.sum())} centros; no son observaciones independientes.', '',
        '| Fecha | VV · dB de media lineal | VH · dB de media lineal |', '|---|---:|---:|']
    for i,day in enumerate(DATES):
        lines.append(f"| {day} | {stats['VV'][i]['db_of_mean_linear']:.3f} | {stats['VH'][i]['db_of_mean_linear']:.3f} |")
    lines.extend(['', 'Se promedia potencia lineal antes de aplicar 10 log10; no media de dB.', '',
        '**Faltan 1.524 días entre enero de 2021 y marzo de 2025. No se supone estabilidad entre fechas.**', '',
        'Las diferencias pueden incluir humedad, estructura, speckle y terreno. No detectan por sí solas tala.',
        'Pendiente ampliar serie y validar con cambios conocidos independientes; este piloto no valida Ecuador.', '',
        'Fuentes: Copernicus Sentinel-1 GRD y CERSGIS v2.0 (DOI 10.5281/zenodo.16579443, CC BY 4.0).'])
    destination.mkdir()
    (destination/'serie.json').write_text(json.dumps(report,indent=2,allow_nan=False),encoding='utf-8')
    (destination/'INFORME.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
