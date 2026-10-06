/* Ecuador Vivo: numeric climate data, not a rendered video.
 * Paste into the Earth Engine Code Editor. Run creates Tasks; start them manually.
 * One GeoTIFF per month + one provenance CSV. Maximum 12 months per execution.
 * Native grid retained. A missing/duplicate source day blocks all export tasks.
 * Locally syntax-checked; authenticated Earth Engine execution still to verify.
 */
var PRODUCT = 'temperature'; // 'temperature', 'rain_v2', 'rain_v3'
var YEAR = 2024;
var FIRST_MONTH = 1;
var MONTHS = 1; // Start with one; 12 for the full year.
var MODE = 'daily'; // 'daily': bands per day; 'monthly': sum/mean + valid_days.
var FOLDER = 'EcuadorVivo_Datos';
// Editorial rectangle, not the national administrative polygon. Includes neighbors.
var BBOX = [-81.5, -5.2, -75.0, 1.8];
var products = {
  temperature: {id: 'ECMWF/ERA5_LAND/DAILY_AGGR', band: 'temperature_2m',
    units: 'degC', offset: -273.15, aggregation: 'mean',
    url: 'https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_DAILY_AGGR'},
  rain_v2: {id: 'UCSB-CHG/CHIRPS/DAILY', band: 'precipitation',
    units: 'mm/day', offset: 0, aggregation: 'sum',
    url: 'https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY'},
  rain_v3: {id: 'UCSB-CHC/CHIRPS/V3/DAILY_SAT', band: 'precipitation',
    units: 'mm/day', offset: 0, aggregation: 'sum',
    url: 'https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHC_CHIRPS_V3_DAILY_SAT'}
};
function integer(n) { return typeof n === 'number' && isFinite(n) && Math.floor(n) === n; }
if (!products[PRODUCT] || !integer(YEAR) || YEAR < 1950 ||
    !integer(FIRST_MONTH) || FIRST_MONTH < 1 || FIRST_MONTH > 12 ||
    !integer(MONTHS) || MONTHS < 1 || MONTHS > 12 || FIRST_MONTH + MONTHS > 13 ||
    (MODE !== 'daily' && MODE !== 'monthly')) {
  throw new Error('Revisa PRODUCT, YEAR, FIRST_MONTH, MONTHS y MODE.');
}
var config = products[PRODUCT];
var region = ee.Geometry.Rectangle(BBOX, 'EPSG:4326', false);
var start = ee.Date.fromYMD(YEAR, FIRST_MONTH, 1);
var end = start.advance(MONTHS, 'month');
var source = ee.ImageCollection(config.id).filterDate(start, end).select(config.band)
  .sort('system:time_start');
print('Ultima fecha global publicada (no garantiza cobertura local por pixel)',
  ee.ImageCollection(config.id).aggregate_max('system:time_start'));
var expected = ee.List.sequence(0, end.difference(start, 'day').subtract(1)).map(function (i) {
  return start.advance(i, 'day').format('YYYY-MM-dd');
});
var actual = source.aggregate_array('system:time_start').map(function (ms) {
  return ee.Date(ms).format('YYYY-MM-dd');
});
ee.Dictionary({expected: expected, actual: actual}).evaluate(function (dates, error) {
  if (error || !dates || JSON.stringify(dates.expected) !== JSON.stringify(dates.actual)) {
    print('NO se crean tareas. Faltan fechas o hay duplicados; elige meses completos publicados.', error || dates);
    return;
  }
  ee.Image(source.first()).projection().evaluate(function (projection, projectionError) {
    if (projectionError || !projection || !projection.crs || !projection.transform) {
      print('NO se crean tareas: falta proyeccion.', projectionError); return;
    }
    createTasks(projection);
  });
});

function createTasks(projection) {
  var records = [];
  var preview;
  for (var i = 0; i < MONTHS; i++) {
    var begin = start.advance(i, 'month');
    var finish = begin.advance(1, 'month');
    var expectedDays = finish.difference(begin, 'day');
    var subset = source.filterDate(begin, finish);
    var values = subset.map(function (image) {
      return image.add(config.offset).rename('value').toFloat()
        .copyProperties(image, ['system:time_start'])
        .set('system:index', ee.Date(image.get('system:time_start')).format('YYYYMMdd'));
    });
    var exportImage;
    if (MODE === 'daily') {
      exportImage = values.toBands();
    } else {
      var count = values.count().rename('valid_days');
      var summary = config.aggregation === 'sum' ? values.sum() : values.mean();
      exportImage = summary.rename('value').updateMask(count.eq(expectedDays)).addBands(count);
    }
    exportImage = exportImage.toFloat().setDefaultProjection(projection.crs, projection.transform);
    var label = YEAR + '_' + ('0' + (FIRST_MONTH + i)).slice(-2);
    var prefix = PRODUCT + '_' + MODE + '_' + label;
    Export.image.toDrive({image: exportImage.clip(region).unmask(-9999, false),
      description: prefix, fileNamePrefix: prefix, folder: FOLDER, region: region,
      crs: projection.crs, crsTransform: projection.transform,
      maxPixels: 1e9, fileFormat: 'GeoTIFF',
      formatOptions: {cloudOptimized: true, noData: -9999}});
    records.push(ee.Feature(null, {
      output_prefix: prefix, source: config.id, source_url: config.url,
      start_inclusive: begin.format('YYYY-MM-dd'), end_exclusive: finish.format('YYYY-MM-dd'),
      expected_days: expectedDays, actual_images: subset.size(),
      units: MODE === 'monthly' && config.aggregation === 'sum' ? 'mm/month' : config.units,
      operation: MODE === 'daily' ? 'one band per date' : config.aggregation,
      band_names: exportImage.bandNames().join('|'),
      source_ids: subset.aggregate_array('system:index').join('|'),
      bbox: JSON.stringify(BBOX), native_crs: projection.crs,
      native_transform: JSON.stringify(projection.transform), no_data: -9999,
      requested_at_utc: new Date().toISOString(),
      note: 'Rectangular download window; mask to administrative boundary before national statistics.'
    }));
    if (i === 0) preview = ee.Image(values.first());
  }
  var tag = PRODUCT + '_' + MODE + '_' + YEAR + '_m' + FIRST_MONTH + '_n' + MONTHS;
  Export.table.toDrive({collection: ee.FeatureCollection(records), folder: FOLDER,
    description: tag + '_manifest', fileNamePrefix: tag + '_manifest', fileFormat: 'CSV'});
  Map.centerObject(region, 6);
  Map.addLayer(preview.clip(region), PRODUCT === 'temperature' ?
    {min: 0, max: 35, palette: ['313695', '74add1', 'ffffbf', 'f46d43', 'a50026']} :
    {min: 0, max: 120, palette: ['102b36', '207ea1', '38b9bc', 'f5df80', 'b74362']},
    'Vista del primer dia; exportacion conserva valores');
  print('Tareas preparadas. Ejecuta primero un mes y su manifest en Tasks.');
}
