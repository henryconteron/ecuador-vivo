/* Ecuador Vivo — real spectral observations, not an automatic mining detector.
 * Index of annual per-band median, NOT median of scene-level indices.
 * B2/B3/B4/B8: 10 m; B11: 20 m; common export grid: 30 m, UTM 18S.
 * Reproducible configuration: data/spectral/napo-config.json.
 */
var asset = 'COPERNICUS/S2_SR_HARMONIZED';
var qualityAsset = 'GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED';
var years = [2019, 2024];
var periods = [['2019-01-01', '2020-01-01'], ['2024-01-01', '2025-01-01']];
var bbox = [-78.04, -1.12, -77.55, -0.72];
var opticalBands = ['B4', 'B3', 'B2', 'B8', 'B11'];
var yearBands = ['B4', 'B3', 'B2', 'B8', 'B11', 'NDVI', 'MNDWI', 'clear_count'];
var threshold = 0.65;
var minObservations = 3;
var excludedScl = [0, 1, 3, 8, 9, 10, 11];
var crs = 'EPSG:32718';
var crsTransform = [30, 0, 0, 0, -30, 0];
var region = ee.Geometry.Rectangle(bbox, 'EPSG:4326', false);
// The Code Editor executes ES5: Number.isInteger is not always available there.
function integer(value) { return typeof value === 'number' && isFinite(value) && Math.floor(value) === value; }
function sceneProvenanceInvalid(row, index) {
  var seen = Object.create(null), period = periods[index];
  if (JSON.stringify(row.period) !== JSON.stringify(period)) return true;
  var start = Date.parse(period[0]), end = Date.parse(period[1]);
  return row.scene_ids.some(function (id) {
    if (typeof id !== 'string' || !id || seen[id]) return true;
    seen[id] = true; return false;
  }) || row.acquired_ms.some(function (ms) { return typeof ms !== 'number' || !isFinite(ms) || ms < start || ms >= end; });
}
var linkedCollections = [];
var lookups = years.map(function (year, index) {
  var period = periods[index];
  var source = ee.ImageCollection(asset).filterBounds(region).filterDate(period[0], period[1]).sort('system:index');
  var quality = ee.ImageCollection(qualityAsset).filterBounds(region).filterDate(period[0], period[1]);
  var joined = ee.Join.inner().apply(source, quality,
    ee.Filter.equals({leftField: 'system:index', rightField: 'system:index'}));
  var linked = ee.ImageCollection(joined.map(function (pair) {
    pair = ee.Feature(pair);
    return ee.Image(pair.get('primary')).addBands(ee.Image(pair.get('secondary')).select('cs_cdf'));
  })).sort('system:index');
  linkedCollections.push(linked);
  return ee.Dictionary({year: year, period: period, source_count: source.size(), joined_count: linked.size(),
    scene_ids: linked.aggregate_array('system:index'), acquired_ms: linked.aggregate_array('system:time_start')});
});
// Async lookup prevents hidden synchronous-browser failures; gate before creating tasks.
ee.Dictionary({scenes: lookups}).evaluate(function (metadata, failure) {
  if (failure) { print('Source lookup failed; no tasks created.', failure); return; }
  if (!metadata || !Array.isArray(metadata.scenes) || metadata.scenes.length !== 2 ||
      metadata.scenes.some(function (row, index) {
        return row.year !== years[index] || !integer(row.source_count) || !integer(row.joined_count) ||
          row.source_count < row.joined_count || row.source_count > 800 || row.joined_count < minObservations || row.joined_count > 800 ||
          !Array.isArray(row.scene_ids) || !Array.isArray(row.acquired_ms) ||
          row.scene_ids.length !== row.joined_count || row.acquired_ms.length !== row.joined_count || sceneProvenanceInvalid(row, index);
      })) { print('Unexpected source provenance; no tasks created.', metadata); return; }
  var composites = years.map(function (year, index) {
    var masked = linkedCollections[index].map(function (image) {
      var optical = image.select(opticalBands).multiply(0.0001);
      var usable = image.select('cs_cdf').gte(threshold)
        .and(optical.mask().reduce(ee.Reducer.min()));
      excludedScl.forEach(function (code) { usable = usable.and(image.select('SCL').neq(code)); });
      return optical.updateMask(usable);
    });
    var count = masked.select('B4').count().rename('clear_count');
    var median = masked.median().updateMask(count.gte(minObservations));
    // Explicit formula and denominator mask, no implicit normalizedDifference masks.
    function ratio(first, second, name) {
      var a = median.select(first), b = median.select(second), sum = a.add(b);
      return a.subtract(b).divide(sum).updateMask(sum.gt(0)).rename(name);
    }
    var ndvi = ratio('B8', 'B4', 'NDVI');
    var mndwi = ratio('B3', 'B11', 'MNDWI');
    return median.addBands(ndvi).addBands(mndwi).addBands(count).select(yearBands);
  });
  var packed = composites.map(function (image, index) {
    return image.rename(yearBands.map(function (band) { return 'y' + years[index] + '_' + band; }));
  });
  // One multiyear raster forces identical native pixel alignment. Missing != zero.
  var output = ee.Image.cat(packed).clip(region).unmask(-9999).toFloat();
  var receipt = {
    schema_version: 1, asset: asset, quality_asset: qualityAsset,
    years: years, periods: periods, bbox: bbox, optical_bands: opticalBands, year_bands: yearBands,
    quality_band: 'cs_cdf', clear_threshold: threshold, min_observations: minObservations,
    excluded_scl: excludedScl, composite: 'index-of-per-band-median', observation_mask: 'joint-five-optical-bands',
    index_formulas: {ndvi: '(B8-B4)/(B8+B4)', mndwi: '(B3-B11)/(B3+B11)'},
    export_crs: crs, export_transform: crsTransform, nodata: -9999,
    reflectance_scale: 0.0001, export_resampling: 'nearest',
    scenes: metadata.scenes, export_requested_at: new Date().toISOString()
  };
  print('Source provenance and method', receipt);
  Export.image.toDrive({image: output, description: 'napo_spectral_2019_2024',
    fileNamePrefix: 'napo_spectral_2019_2024', folder: 'EcuadorVivo', region: region,
    crs: crs, crsTransform: crsTransform, maxPixels: 5000000, fileFormat: 'GeoTIFF',
    formatOptions: {cloudOptimized: true, noData: -9999}});
  Export.table.toDrive({collection: ee.FeatureCollection([ee.Feature(null, {receipt: JSON.stringify(receipt)})]),
    description: 'napo_spectral_2019_2024_receipt', fileNamePrefix: 'napo_spectral_2019_2024_receipt',
    folder: 'EcuadorVivo', fileFormat: 'GeoJSON'});
  Map.centerObject(region, 10);
  Map.addLayer(composites[1], {bands: ['B4', 'B3', 'B2'], min: 0, max: 0.3, gamma: 1.2}, '2024 annual median RGB');
  Map.addLayer(composites[1].select('NDVI'), {min: -1, max: 1, palette: ['72513d', 'f0ead2', '146b42']}, '2024 NDVI', false);
  Map.addLayer(composites[1].select('MNDWI'), {min: -1, max: 1, palette: ['94664b', 'f0ead2', '166eae']}, '2024 MNDWI', false);
});
