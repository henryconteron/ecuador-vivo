/* Ecuador Vivo · mapa de calor atmosférico “El pulso térmico de Ecuador”.
 * Fuente: ERA5-Land Daily Aggregated, temperatura del aire a 2 m.
 * El periodo 2026-01-01–2026-08-31 evita presentar un año incompleto como
 * anual. La variable original está en kelvin y se convierte a °C.
 */
var source = 'ECMWF/ERA5_LAND/DAILY_AGGR';
var dem = 'USGS/SRTMGL1_003';
var boundaryAsset = 'WM/geoLab/geoBoundaries/600/ADM0';
var start = ee.Date('2026-01-01');
var end = ee.Date('2026-09-01');
var expectedDays = 243;
var framesPerSecond = 12;
var videoDimensions = 1080;
var exportCrs = 'EPSG:4326';
var maxPixels = 100000000;
var region = ee.Geometry.Rectangle([-81.5, -5.2, -75.0, 1.8], 'EPSG:4326', false);

var sourceCollection = ee.ImageCollection(source).filterDate(start, end)
  .select('temperature_2m');
var boundary = ee.FeatureCollection(boundaryAsset)
  .filter(ee.Filter.eq('shapeGroup', 'ECU'));
var heatPalette = [
  '16004d', '2636a6', '166ed1', '25c7e8', '55e59b', 'c8f23a',
  'fff04a', 'ffbd28', 'ff6b1a', 'ed2c3b', 'ad0f68', 'ff39d8'
];
var tempMin = 8;
var tempMax = 38;

var daily = sourceCollection.map(function (image) {
  var celsius = image.select('temperature_2m').subtract(273.15).rename('temperature_2m_c');
  return celsius.copyProperties(image, ['system:time_start', 'day', 'month', 'year'])
    .set({'unit': 'degC', 'source_units': 'K', 'derivation': 'temperature_2m - 273.15'});
});
var hillshade = ee.Terrain.hillshade(ee.Image(dem).select('elevation'))
  .visualize({min: 60, max: 255, palette: ['101329', '263a4d', 'a9b5c4']});
var frames = daily.map(function (image) {
  var heat = image.select('temperature_2m_c').resample('bilinear').visualize({
    min: tempMin, max: tempMax, palette: heatPalette, opacity: 0.88
  });
  return hillshade.blend(heat).clip(region).set({
    'system:time_start': image.get('system:time_start'),
    'date': ee.Date(image.get('system:time_start')).format('YYYY-MM-dd')
  });
});

ee.Dictionary({
  boundary_count: boundary.size(),
  daily_count: daily.size(),
  first_date: daily.first().get('system:time_start'),
  last_date: daily.sort('system:time_start', false).first().get('system:time_start')
}).evaluate(function (metadata, failure) {
  var firstDate = metadata && metadata.first_date ? new Date(metadata.first_date).toISOString().slice(0, 10) : null;
  var lastDate = metadata && metadata.last_date ? new Date(metadata.last_date).toISOString().slice(0, 10) : null;
  if (failure || !metadata || metadata.boundary_count !== 1 || metadata.daily_count !== expectedDays ||
      firstDate !== '2026-01-01' || lastDate !== '2026-08-31') {
    print('No se crearon tareas: ERA5-Land no devolvió los 243 días esperados.', failure || metadata);
    return;
  }
  var receipt = {
    schema_version: 1,
    case_id: 'ecuador-temperatura-2026-enero-agosto',
    source: source,
    source_url: 'https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_DAILY_AGGR',
    citation_doi: 'https://doi.org/10.24381/cds.68d2bb30',
    period: ['2026-01-01', '2026-08-31'],
    source_band: 'temperature_2m',
    source_units: 'K',
    output_units: 'degC',
    derivation: 'temperature_2m - 273.15',
    grid_native_m: 11132,
    daily_images: expectedDays,
    region_bbox: [-81.5, -5.2, -75.0, 1.8],
    terrain_context: dem,
    visual_range_degC: [tempMin, tempMax],
    note: 'Reanalysis of near-surface air temperature, not a thermometer at each pixel and not land-surface temperature.',
    copernicus_notice: 'Contains modified Copernicus Climate Change Service Information 2026; neither ECMWF nor the European Commission is responsible for use made of it.'
  };
  print('Recibo térmico (conservar junto al video)', receipt);
  Export.video.toDrive({
    collection: frames,
    description: 'ecuador_temperatura_2026_enero_agosto',
    fileNamePrefix: 'ecuador_temperatura_2026_enero_agosto',
    folder: 'EcuadorVivo',
    region: region,
    dimensions: videoDimensions,
    framesPerSecond: framesPerSecond,
    crs: exportCrs,
    maxPixels: maxPixels
  });
  Export.table.toDrive({
    collection: ee.FeatureCollection([ee.Feature(null, {receipt: JSON.stringify(receipt)})]),
    description: 'ecuador_temperatura_2026_enero_agosto_receipt',
    fileNamePrefix: 'ecuador_temperatura_2026_enero_agosto_receipt',
    folder: 'EcuadorVivo',
    fileFormat: 'GeoJSON'
  });
  Map.centerObject(boundary, 7);
  Map.addLayer(daily.first(), {min: tempMin, max: tempMax, palette: heatPalette}, 'Primer día 2026 · temperatura °C', true);
  Map.addLayer(ee.Image(dem), {min: 0, max: 5000, palette: ['101329', '40566b', 'ded7b1', 'ffffff']}, 'Relieve SRTM', true);
  print('Tareas creadas:', 'ecuador_temperatura_2026_enero_agosto y su recibo');
});
