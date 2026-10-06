/* Ecuador Vivo · “La lluvia que ya cayó en 2026”.
 * Pegar en https://code.earthengine.google.com/ con un proyecto habilitado.
 *
 * IMERG V07 sigue actualizándose durante 2026. Por eso este borrador usa
 * productos provisionales y cierra el periodo en 2026-09-01: enero–agosto
 * completo, sin fingir que el año ya terminó. La banda precipitation es una
 * tasa en mm/h; cada imagen dura 30 minutos y se convierte a mm/día con
 * sum(mm/h) * 0.5 h.
 */
var source = 'NASA/GPM_L3/IMERG_V07';
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
  .filter(ee.Filter.eq('status', 'provisional')).select('precipitation');
var boundary = ee.FeatureCollection(boundaryAsset)
  .filter(ee.Filter.eq('shapeGroup', 'ECU'));

function dailyImage(day) {
  day = ee.Date(day);
  var halfHourly = sourceCollection.filterDate(day, day.advance(1, 'day'));
  return halfHourly.sum().multiply(0.5).rename('rain_mm_day')
    .setDefaultProjection(ee.Image(sourceCollection.first()).projection()).set({
    'system:time_start': day.millis(),
    'date': day.format('YYYY-MM-dd'),
    'interval_count': halfHourly.size(),
    'unit': 'mm/day',
    'status_used': 'provisional',
    'derivation': 'sum(IMERG precipitation mm/h) * 0.5 h'
  });
}

var days = ee.List.sequence(0, expectedDays - 1);
var daily = ee.ImageCollection(days.map(function (offset) {
  return dailyImage(start.advance(offset, 'day'));
}));
var hillshade = ee.Terrain.hillshade(ee.Image(dem).select('elevation'))
  .visualize({min: 60, max: 255, palette: ['173431', '2d5d54', 'b9c8b0']});
var palette = ['102b5c', '155fa0', '36a9c9', '7bd38f', 'e8e76a', 'f5b44e', 'd95b45'];
var rainMin = 0;
var rainMax = 120;
var frames = daily.map(function (image) {
  var rain = image.select('rain_mm_day').resample('bilinear').visualize({
    min: rainMin, max: rainMax, palette: palette, opacity: 0.86
  });
  return hillshade.blend(rain).clip(region).set({
    'system:time_start': image.get('system:time_start'),
    'date': image.get('date'),
    'interval_count': image.get('interval_count')
  });
});

ee.Dictionary({
  boundary_count: boundary.size(),
  daily_count: daily.size(),
  interval_counts: daily.aggregate_array('interval_count'),
  first_date: daily.first().get('date'),
  last_date: daily.sort('system:time_start', false).first().get('date')
}).evaluate(function (metadata, failure) {
  var intervals = metadata && metadata.interval_counts;
  var all48 = Array.isArray(intervals) && intervals.length === expectedDays &&
    intervals.every(function (value) { return value === 48; });
  if (failure || !metadata || metadata.boundary_count !== 1 ||
      metadata.daily_count !== expectedDays || !all48 ||
      metadata.first_date !== '2026-01-01' || metadata.last_date !== '2026-08-31') {
    print('No se crearon tareas: faltan días o intervalos provisionales IMERG.', failure || metadata);
    return;
  }
  var receipt = {
    schema_version: 1,
    case_id: 'ecuador-lluvia-2026-enero-agosto',
    source: source,
    source_url: 'https://developers.google.com/earth-engine/datasets/catalog/NASA_GPM_L3_IMERG_V07',
    doi: 'https://doi.org/10.5067/GPM/IMERG/3B-HH/07',
    period: ['2026-01-01', '2026-08-31'],
    source_band: 'precipitation',
    source_units: 'mm/h',
    interval_minutes: 30,
    status_used: 'provisional',
    derivation: 'daily accumulation = sum(rate_mm_per_hour) * 0.5 hour',
    output_units: 'mm/day',
    grid_native_m: 11132,
    daily_images: expectedDays,
    interval_count_per_day: 48,
    region_bbox: [-81.5, -5.2, -75.0, 1.8],
    terrain_context: dem,
    note: '2026 is a year-to-date provisional window; do not label it as a complete annual total.',
    license_note: 'NASA-produced GPM data are freely available for public use; retain citation.'
  };
  print('Recibo 2026 (conservar junto al video)', receipt);
  Export.video.toDrive({
    collection: frames,
    description: 'ecuador_lluvia_2026_enero_agosto',
    fileNamePrefix: 'ecuador_lluvia_2026_enero_agosto',
    folder: 'EcuadorVivo',
    region: region,
    dimensions: videoDimensions,
    framesPerSecond: framesPerSecond,
    crs: exportCrs,
    maxPixels: maxPixels
  });
  Export.table.toDrive({
    collection: ee.FeatureCollection([ee.Feature(null, {receipt: JSON.stringify(receipt)})]),
    description: 'ecuador_lluvia_2026_enero_agosto_receipt',
    fileNamePrefix: 'ecuador_lluvia_2026_enero_agosto_receipt',
    folder: 'EcuadorVivo',
    fileFormat: 'GeoJSON'
  });
  Map.centerObject(boundary, 7);
  Map.addLayer(daily.first(), {min: rainMin, max: rainMax, palette: palette}, 'Primer día 2026 · mm/día', true);
  Map.addLayer(ee.Image(dem), {min: 0, max: 5000, palette: ['0b2830', '567a63', 'e9d9ae', 'ffffff']}, 'Relieve SRTM', true);
  print('Tareas creadas:', 'ecuador_lluvia_2026_enero_agosto y su recibo');
});
