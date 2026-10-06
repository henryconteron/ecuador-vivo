/* Ecuador Vivo · archivo climático mensual para contar El Niño y La Niña.
 *
 * Exporta dos animaciones de anomalías (lluvia y temperatura) y una tabla
 * mensual con los valores regionales. La climatología de referencia es
 * 1981–2010; el periodo observado llega hasta agosto de 2026, sin rellenar
 * meses futuros. CHIRPS aporta precipitación diaria a 0.05° y ERA5-Land
 * aporta temperatura del aire a 2 m a ~11 km.
 */
var rainSource = 'UCSB-CHG/CHIRPS/DAILY';
var tempSource = 'ECMWF/ERA5_LAND/DAILY_AGGR';
var dem = 'USGS/SRTMGL1_003';
var boundaryAsset = 'WM/geoLab/geoBoundaries/600/ADM0';
var start = ee.Date('1981-01-01');
var end = ee.Date('2026-09-01');
var baselineStart = ee.Date('1981-01-01');
var baselineEnd = ee.Date('2011-01-01');
var expectedMonths = 548;
var framesPerSecond = 12;
var videoDimensions = 1080;
var exportCrs = 'EPSG:4326';
var maxPixels = 100000000;
var region = ee.Geometry.Rectangle([-81.5, -5.2, -75.0, 1.8], 'EPSG:4326', false);

var boundary = ee.FeatureCollection(boundaryAsset)
  .filter(ee.Filter.eq('shapeGroup', 'ECU'));
var rainDaily = ee.ImageCollection(rainSource).filterDate(start, end).select('precipitation');
var tempDaily = ee.ImageCollection(tempSource).filterDate(start, end).select('temperature_2m');
var monthOffsets = ee.List.sequence(0, expectedMonths - 1);

function buildMonthlyRain(offset) {
  var date = start.advance(offset, 'month');
  return rainDaily.filterDate(date, date.advance(1, 'month')).sum()
    .rename('rain_mm_month').setDefaultProjection(ee.Image(rainDaily.first()).projection()).set({'system:time_start': date.millis(), 'month': date.get('month'), 'date': date.format('YYYY-MM')});
}

function buildMonthlyTemp(offset) {
  var date = start.advance(offset, 'month');
  return tempDaily.filterDate(date, date.advance(1, 'month')).mean()
    .subtract(273.15).rename('temperature_2m_c').setDefaultProjection(ee.Image(tempDaily.first()).projection())
    .set({'system:time_start': date.millis(), 'month': date.get('month'), 'date': date.format('YYYY-MM')});
}

var monthlyRain = ee.ImageCollection(monthOffsets.map(buildMonthlyRain));
var monthlyTemp = ee.ImageCollection(monthOffsets.map(buildMonthlyTemp));

function anomaly(collection, band, offset) {
  var image = ee.Image(collection.toList(expectedMonths).get(offset));
  var month = ee.Number(image.get('month'));
  var baseline = collection.filterDate(baselineStart, baselineEnd)
    .filter(ee.Filter.calendarRange(month, month, 'month')).mean().select(band);
  return image.select(band).subtract(baseline).rename(band + '_anomaly')
    .set({'system:time_start': image.get('system:time_start'), 'date': image.get('date'), 'month': month});
}

var rainAnomalies = ee.ImageCollection(monthOffsets.map(function (offset) {
  return anomaly(monthlyRain, 'rain_mm_month', offset);
}));
var tempAnomalies = ee.ImageCollection(monthOffsets.map(function (offset) {
  return anomaly(monthlyTemp, 'temperature_2m_c', offset);
}));

var hillshade = ee.Terrain.hillshade(ee.Image(dem).select('elevation'))
  .visualize({min: 60, max: 255, palette: ['111525', '26344b', 'a5b5bd']});
var rainPalette = ['7f0000', 'd7301f', 'fc8d59', 'fdd49e', 'fff7ec', 'e0f3f8', '91bfdb', '4575b4', '313695'];
var tempPalette = ['313695', '4575b4', '74add1', 'abd9e9', 'ffffbf', 'fdae61', 'f46d43', 'd73027', 'a50026'];
var rainFrames = rainAnomalies.map(function (image) {
  var visual = image.resample('bilinear').visualize({min: -250, max: 250, palette: rainPalette, opacity: 0.9});
  return hillshade.blend(visual).clip(region).set({'system:time_start': image.get('system:time_start'), 'date': image.get('date')});
});
var tempFrames = tempAnomalies.map(function (image) {
  var visual = image.resample('bilinear').visualize({min: -3, max: 3, palette: tempPalette, opacity: 0.9});
  return hillshade.blend(visual).clip(region).set({'system:time_start': image.get('system:time_start'), 'date': image.get('date')});
});

var monthlyTable = ee.FeatureCollection(monthOffsets.map(function (offset) {
  var rain = ee.Image(monthlyRain.toList(expectedMonths).get(offset));
  var temp = ee.Image(monthlyTemp.toList(expectedMonths).get(offset));
  var rainAnomalyImage = ee.Image(rainAnomalies.toList(expectedMonths).get(offset));
  var tempAnomalyImage = ee.Image(tempAnomalies.toList(expectedMonths).get(offset));
  var rainValues = rain.addBands(rainAnomalyImage).reduceRegion({reducer: ee.Reducer.mean(), geometry: region, scale: 5566, bestEffort: true, maxPixels: maxPixels});
  var tempValues = temp.addBands(tempAnomalyImage).reduceRegion({reducer: ee.Reducer.mean(), geometry: region, scale: 11132, bestEffort: true, maxPixels: maxPixels});
  return ee.Feature(null, rainValues.combine(tempValues).set({'date': rain.get('date'), 'month': rain.get('month')}));
}));

ee.Dictionary({
  boundary_count: boundary.size(),
  rain_months: monthlyRain.size(),
  temp_months: monthlyTemp.size(),
  rain_first: monthlyRain.first().get('date'),
  rain_last: monthlyRain.sort('system:time_start', false).first().get('date'),
  temp_first: monthlyTemp.first().get('date'),
  temp_last: monthlyTemp.sort('system:time_start', false).first().get('date')
}).evaluate(function (metadata, failure) {
  if (failure || !metadata || metadata.boundary_count !== 1 || metadata.rain_months !== expectedMonths ||
      metadata.temp_months !== expectedMonths || metadata.rain_first !== '1981-01' ||
      metadata.rain_last !== '2026-08' || metadata.temp_first !== '1981-01' || metadata.temp_last !== '2026-08') {
    print('No se crearon tareas: archivo climático incompleto.', failure || metadata);
    return;
  }
  var receipt = {
    schema_version: 1,
    case_id: 'ecuador-clima-mensual-1981-2026',
    rainfall_source: rainSource,
    temperature_source: tempSource,
    rainfall_source_url: 'https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY',
    temperature_source_url: 'https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_DAILY_AGGR',
    period: ['1981-01', '2026-08'],
    baseline: ['1981-01', '2010-12'],
    months: expectedMonths,
    rainfall_band: 'precipitation',
    rainfall_units: 'mm/day summed by month',
    temperature_band: 'temperature_2m',
    temperature_units: 'K converted to degC before monthly mean',
    anomalies: 'monthly value minus same-calendar-month 1981-2010 mean',
    rainfall_resolution_m: 5566,
    temperature_resolution_m: 11132,
    terrain_context: dem,
    enso_note: 'Join the exported monthly table to NOAA ONI seasons before attributing an anomaly to El Niño or La Niña.',
    limits: ['Regional mean is not a station observation.', 'Anomaly is a climatological signal, not proof of causation.', '2026 contains January–August only.']
  };
  print('Recibo histórico (conservar junto a los videos)', receipt);
  Export.video.toDrive({collection: rainFrames, description: 'ecuador_lluvia_anomalia_1981_2026', fileNamePrefix: 'ecuador_lluvia_anomalia_1981_2026', folder: 'EcuadorVivo', region: region, dimensions: videoDimensions, framesPerSecond: framesPerSecond, crs: exportCrs, maxPixels: maxPixels, maxFrames: expectedMonths});
  Export.video.toDrive({collection: tempFrames, description: 'ecuador_temperatura_anomalia_1981_2026', fileNamePrefix: 'ecuador_temperatura_anomalia_1981_2026', folder: 'EcuadorVivo', region: region, dimensions: videoDimensions, framesPerSecond: framesPerSecond, crs: exportCrs, maxPixels: maxPixels, maxFrames: expectedMonths});
  Export.table.toDrive({collection: monthlyTable, description: 'ecuador_clima_mensual_1981_2026_table', fileNamePrefix: 'ecuador_clima_mensual_1981_2026_table', folder: 'EcuadorVivo', fileFormat: 'CSV'});
  Export.table.toDrive({collection: ee.FeatureCollection([ee.Feature(null, {receipt: JSON.stringify(receipt)})]), description: 'ecuador_clima_mensual_1981_2026_receipt', fileNamePrefix: 'ecuador_clima_mensual_1981_2026_receipt', folder: 'EcuadorVivo', fileFormat: 'GeoJSON'});
  Map.centerObject(boundary, 7);
  Map.addLayer(ee.Image(rainAnomalies.first()), {min: -250, max: 250, palette: rainPalette}, 'Anomalía lluvia primer mes · mm/mes', true);
  Map.addLayer(ee.Image(tempAnomalies.first()), {min: -3, max: 3, palette: tempPalette}, 'Anomalía temperatura primer mes · °C', false);
  print('Tareas creadas:', 'lluvia, temperatura, tabla mensual y recibo histórico');
});
