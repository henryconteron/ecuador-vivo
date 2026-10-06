/* Ecuador Vivo · exportación del borrador “365 días de lluvia sobre Ecuador”.
 * Pegar en https://code.earthengine.google.com/ con un proyecto habilitado.
 *
 * Fuente: NASA/GPM_L3/IMERG_V07. La banda precipitation está en mm/h y cada
 * imagen representa 30 minutos; el acumulado diario se calcula como
 * sum(mm/h) * 0.5 h. No se confunde tasa con acumulado.
 *
 * El script no crea tareas si la colección no tiene 48 intervalos por día,
 * si falta un día o si la geometría regional no es única. La exportación es
 * un mapa 2D con relieve sombreado de SRTM como contexto, no una medición de
 * lluvia a escala de barrio ni un modelo hidrológico.
 */
var source = 'NASA/GPM_L3/IMERG_V07';
var dem = 'USGS/SRTMGL1_003';
var boundaryAsset = 'WM/geoLab/geoBoundaries/600/ADM0';
var boundaryFilter = {shapeGroup: 'ECU'};
var year = 2024;
var start = ee.Date.fromYMD(year, 1, 1);
var end = start.advance(1, 'year');
var framesPerSecond = 12;
var videoDimensions = 1080;
var exportCrs = 'EPSG:4326';
var maxPixels = 100000000;
var region = ee.Geometry.Rectangle([-81.5, -5.2, -75.0, 1.8], 'EPSG:4326', false);

var sourceCollection = ee.ImageCollection(source).filterDate(start, end)
  .filter(ee.Filter.eq('status', 'permanent')).select('precipitation');
var boundary = ee.FeatureCollection(boundaryAsset)
  .filter(ee.Filter.eq('shapeGroup', boundaryFilter.shapeGroup));

function dateKey(day) { return ee.Date(day).format('YYYY-MM-dd'); }

function dailyImage(day) {
  day = ee.Date(day);
  var halfHourly = sourceCollection.filterDate(day, day.advance(1, 'day'));
  // precipitation is a rate in mm/h; each source image represents 0.5 h.
  var accumulated = halfHourly.sum().multiply(0.5).rename('rain_mm_day')
    .setDefaultProjection(ee.Image(sourceCollection.first()).projection());
  return accumulated.set({
    'system:time_start': day.millis(),
    'date': dateKey(day),
    'interval_count': halfHourly.size(),
    'unit': 'mm/day',
    'derivation': 'sum(IMERG precipitation mm/h) * 0.5 h'
  });
}

var dayCount = end.difference(start, 'day');
var days = ee.List.sequence(0, dayCount.subtract(1));
var daily = ee.ImageCollection(days.map(function (offset) {
  return dailyImage(start.advance(offset, 'day'));
}));

// Use hillshade only as visual context. It is never encoded as rainfall.
var hillshade = ee.Terrain.hillshade(ee.Image(dem).select('elevation'))
  .visualize({min: 60, max: 255, palette: ['173431', '2d5d54', 'b9c8b0']});
// Bilinear resampling is used only for rendered pixels. It does not add
// information to IMERG's native ~11 km cells; that limit remains in the receipt.
var palette = ['102b5c', '155fa0', '36a9c9', '7bd38f', 'e8e76a', 'f5b44e', 'd95b45'];
var rainMin = 0;
var rainMax = 120;
var frames = daily.map(function (image) {
  var rain = image.select('rain_mm_day').resample('bilinear')
    .visualize({min: rainMin, max: rainMax, palette: palette, opacity: 0.9});
  var composed = hillshade.blend(rain)
    .blend(boundary.style({color: 'f7f0dc', fillColor: '00000000', width: 2}))
    .clip(region);
  return composed.set({
    'system:time_start': image.get('system:time_start'),
    'date': image.get('date'),
    'interval_count': image.get('interval_count')
  });
});

// Evaluate all structural gates before creating any task.
ee.Dictionary({
  boundary_count: boundary.size(),
  daily_count: daily.size(),
  interval_counts: daily.aggregate_array('interval_count'),
  first_date: daily.first().get('date'),
  last_date: daily.sort('system:time_start', false).first().get('date')
}).evaluate(function (metadata, failure) {
  var expectedDays = (year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0)) ? 366 : 365;
  var intervals = metadata && metadata.interval_counts;
  var all48 = Array.isArray(intervals) && intervals.length === expectedDays &&
    intervals.every(function (value) { return value === 48; });
  if (failure || !metadata || metadata.boundary_count !== 1 || metadata.daily_count !== expectedDays ||
      !all48 || metadata.first_date !== year + '-01-01' || metadata.last_date !== year + '-12-31') {
    print('No se crearon tareas: control de integridad IMERG falló.', failure || metadata);
    return;
  }
  var receipt = {
    schema_version: 1,
    source: source,
    source_url: 'https://developers.google.com/earth-engine/datasets/catalog/NASA_GPM_L3_IMERG_V07',
    doi: 'https://doi.org/10.5067/GPM/IMERG/3B-HH/07',
    dem: dem,
    year: year,
    source_band: 'precipitation',
    source_units: 'mm/h',
    interval_minutes: 30,
    derivation: 'daily accumulation = sum(rate_mm_per_hour) * 0.5 hour',
    output_units: 'mm/day',
    grid_native_m: 11132,
    daily_images: expectedDays,
    interval_count_per_day: 48,
    region_bbox: [-81.5, -5.2, -75.0, 1.8],
    visual_min_mm_day: rainMin,
    visual_max_mm_day: rainMax,
    export_crs: exportCrs,
    display_note: 'Bilinear resampling is display-only; it does not increase the native 0.1 degree information.',
    note: 'Satellite estimate; 0.1 degree cells. Hillshade and border are context, not precipitation.',
    license_note: 'NASA-produced GPM data are freely available for public use; retain citation.',
    export_requested_at: new Date().toISOString()
  };
  print('Recibo metodológico (conservar junto al video)', receipt);
  Export.video.toDrive({
    collection: frames,
    description: 'ecuador_lluvia_diaria_2024',
    fileNamePrefix: 'ecuador_lluvia_diaria_2024',
    folder: 'EcuadorVivo',
    region: region,
    dimensions: videoDimensions,
    framesPerSecond: framesPerSecond,
    crs: exportCrs,
    maxPixels: maxPixels
  });
  Export.table.toDrive({
    collection: ee.FeatureCollection([ee.Feature(null, {receipt: JSON.stringify(receipt)})]),
    description: 'ecuador_lluvia_diaria_2024_receipt',
    fileNamePrefix: 'ecuador_lluvia_diaria_2024_receipt',
    folder: 'EcuadorVivo',
    fileFormat: 'GeoJSON'
  });
  Map.centerObject(boundary, 7);
  Map.addLayer(ee.Image(dem), {min: 0, max: 5000, palette: ['0b2830', '567a63', 'e9d9ae', 'ffffff']}, 'Relieve SRTM', true);
  Map.addLayer(daily.first(), {min: rainMin, max: rainMax, palette: palette}, 'Primer día · lluvia acumulada mm/día', true);
  print('Tareas creadas:', 'ecuador_lluvia_diaria_2024 y su recibo');
});
