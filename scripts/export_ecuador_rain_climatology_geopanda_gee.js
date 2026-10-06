/* Ecuador Vivo · “Ecuador bajo la lluvia” · formato GeoPanda.
 *
 * Una imagen por mes representa la precipitación mensual media de 1991–2020.
 * Es una climatología, no un pronóstico ni una fotografía de un año concreto.
 * La escala de colores es fija para los 12 meses. El suavizado bilineal solo
 * mejora la lectura visual; la resolución nativa de CHIRPS (~5 km) permanece
 * en el recibo metodológico.
 */
var source = 'UCSB-CHG/CHIRPS/DAILY';
var dem = 'USGS/SRTMGL1_003';
var boundaryAsset = 'WM/geoLab/geoBoundaries/600/ADM0';
var baselineStartYear = 1991;
var baselineEndYear = 2020;
var framesPerSecond = 2;
var videoDimensions = 1440;
var exportCrs = 'EPSG:4326';
var maxPixels = 100000000;
var region = ee.Geometry.Rectangle([-81.5, -5.2, -75.0, 1.8], 'EPSG:4326', false);
var rainMin = 0;
var rainMax = 700;
var palette = ['08243f', '0b5f73', '27a6a1', '73c79f', 'dce76a', 'f8be59', 'df5d46'];

var daily = ee.ImageCollection(source)
  .filterDate(ee.Date.fromYMD(baselineStartYear, 1, 1), ee.Date.fromYMD(baselineEndYear + 1, 1, 1))
  .select('precipitation');
var boundary = ee.FeatureCollection(boundaryAsset)
  .filter(ee.Filter.eq('shapeGroup', 'ECU'));
var monthNumbers = ee.List.sequence(1, 12);
var years = ee.List.sequence(baselineStartYear, baselineEndYear);

function monthlyClimatology(month) {
  month = ee.Number(month);
  var yearImages = years.map(function (year) {
    year = ee.Number(year);
    var start = ee.Date.fromYMD(year, month, 1);
    return daily.filterDate(start, start.advance(1, 'month')).sum()
      .rename('rain_mm_month').set('year', year);
  });
  var image = ee.ImageCollection.fromImages(yearImages).mean().rename('rain_mm_month')
    .setDefaultProjection(ee.Image(daily.first()).projection());
  return image.set({
    'system:time_start': ee.Date.fromYMD(2000, month, 1).millis(),
    'month': month,
    'label': ee.Date.fromYMD(2000, month, 1).format('MMMM'),
    'period': baselineStartYear + '-' + baselineEndYear,
    'unit': 'mm/month mean'
  });
}

var monthly = ee.ImageCollection.fromImages(monthNumbers.map(monthlyClimatology));
var hillshade = ee.Terrain.hillshade(ee.Image(dem).select('elevation'))
  .visualize({min: 60, max: 255, palette: ['163039', '315d55', 'b9c8b0']});
var ecuadorOutline = boundary.style({color: 'f7f0dc', fillColor: '00000000', width: 2});
var frames = monthly.map(function (image) {
  var rain = image.select('rain_mm_month').resample('bilinear')
    .visualize({min: rainMin, max: rainMax, palette: palette, opacity: 0.91});
  return hillshade.blend(rain).blend(ecuadorOutline).clip(region).set({
    'system:time_start': image.get('system:time_start'),
    'month': image.get('month'),
    'label': image.get('label')
  });
});

ee.Dictionary({
  boundary_count: boundary.size(),
  month_count: monthly.size(),
  first_month: monthly.first().get('month'),
  last_month: monthly.sort('system:time_start', false).first().get('month')
}).evaluate(function (metadata, failure) {
  if (failure || !metadata || metadata.boundary_count !== 1 || metadata.month_count !== 12 ||
      metadata.first_month !== 1 || metadata.last_month !== 12) {
    print('No se crearon tareas: control de climatología mensual falló.', failure || metadata);
    return;
  }
  var receipt = {
    schema_version: 1,
    case_id: 'ecuador-lluvia-climatologia-1991-2020',
    source: source,
    source_url: 'https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY',
    period: [baselineStartYear + '-01-01', baselineEndYear + '-12-31'],
    aggregation: 'monthly sum for each year, then mean across 1991–2020',
    source_band: 'precipitation',
    source_units: 'mm/day',
    output_units: 'mean mm/month',
    months: 12,
    native_resolution_m: 5566,
    visual_min_mm_month: rainMin,
    visual_max_mm_month: rainMax,
    display_note: 'Bilinear resampling is display-only; it does not increase the native CHIRPS information.',
    terrain_context: dem,
    export_crs: exportCrs,
    limits: [
      'Climatology describes the 1991–2020 baseline, not the rainfall of a particular year.',
      'Satellite-derived precipitation is not a station measurement at every pixel.',
      'A zoomed frame does not resolve local showers below the native grid.'
    ]
  };
  print('Recibo climatológico (conservar junto al video)', receipt);
  Export.video.toDrive({
    collection: frames,
    description: 'ecuador_lluvia_climatologia_1991_2020_geopanda',
    fileNamePrefix: 'ecuador_lluvia_climatologia_1991_2020_geopanda',
    folder: 'EcuadorVivo',
    region: region,
    dimensions: videoDimensions,
    framesPerSecond: framesPerSecond,
    crs: exportCrs,
    maxPixels: maxPixels
  });
  Export.table.toDrive({
    collection: ee.FeatureCollection([ee.Feature(null, receipt)]),
    description: 'ecuador_lluvia_climatologia_1991_2020_receipt',
    fileNamePrefix: 'ecuador_lluvia_climatologia_1991_2020_receipt',
    folder: 'EcuadorVivo',
    fileFormat: 'GeoJSON'
  });
  Map.centerObject(boundary, 7);
  Map.addLayer(monthly.first(), {min: rainMin, max: rainMax, palette: palette}, 'Enero · media 1991–2020 · mm/mes', true);
  print('Tareas creadas:', 'video GeoPanda mensual y recibo metodológico');
});
