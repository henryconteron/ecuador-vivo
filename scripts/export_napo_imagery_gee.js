/* Ecuador Vivo: observational context, not independent classification validation.
 * 2024 per-band median; 10m optical inputs sampled at 30m for the web comparison.
 * Config: data/imagery/napo-config.json. No synchronous getInfo or paid storage.
 */
var asset = 'COPERNICUS/S2_SR_HARMONIZED';
var qualityAsset = 'GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED';
var period = ['2024-01-01', '2025-01-01'];
var bbox = [-78.04, -1.12, -77.55, -0.72];
var threshold = 0.65;
var minObservations = 3;
var excludedScl = [0, 1, 3, 8, 9, 10, 11];
var crs = 'EPSG:32718';
var scale = 30;
var region = ee.Geometry.Rectangle(bbox, 'EPSG:4326', false);
function integer(value) { return typeof value === 'number' && isFinite(value) && Math.floor(value) === value; }
var source = ee.ImageCollection(asset).filterBounds(region).filterDate(period[0], period[1]).sort('system:index');
var quality = ee.ImageCollection(qualityAsset).filterBounds(region).filterDate(period[0], period[1]);
// Explicit inner join excludes scenes without a QA counterpart and records the IDs.
var joined = ee.Join.inner().apply(source, quality, ee.Filter.equals({leftField: 'system:index', rightField: 'system:index'}));
var linked = ee.ImageCollection(joined.map(function (pair) {
  pair = ee.Feature(pair);
  var image = ee.Image(pair.get('primary'));
  return image.addBands(ee.Image(pair.get('secondary')).select('cs_cdf'));
})).sort('system:index');
ee.Dictionary({source_count: source.size(), joined_count: linked.size(),
  scene_ids: linked.aggregate_array('system:index'),
  acquired_ms: linked.aggregate_array('system:time_start')
}).evaluate(function (metadata, failure) {
  if (failure) { print('Source lookup failed; no tasks created.', failure); return; }
  if (!metadata || !Array.isArray(metadata.scene_ids) || !Array.isArray(metadata.acquired_ms) ||
      !integer(metadata.joined_count) || !integer(metadata.source_count) ||
      metadata.source_count < metadata.joined_count || metadata.joined_count < minObservations || metadata.joined_count > 800 ||
      metadata.joined_count !== metadata.scene_ids.length || metadata.joined_count !== metadata.acquired_ms.length) {
    print('Unexpected source count; no tasks created.', metadata); return;
  }
  var masked = linked.map(function (image) {
    var usable = image.select('cs_cdf').gte(threshold);
    excludedScl.forEach(function (code) { usable = usable.and(image.select('SCL').neq(code)); });
    return image.select(['B4', 'B3', 'B2']).updateMask(usable);
  });
  var count = masked.select('B4').count().rename('clear_count');
  var rgb = masked.median().updateMask(count.gte(minObservations));
  // Keep count even where RGB is missing. NoData is 65535, NOT dark reflectance=0.
  var output = rgb.addBands(count).clip(region).unmask(65535).toUint16();
  var receipt = {
    schema_version: 1, asset: asset, quality_asset: qualityAsset,
    period: period, bbox: bbox, bands: ['B4', 'B3', 'B2', 'clear_count'],
    quality_band: 'cs_cdf', clear_threshold: threshold, min_observations: minObservations,
    excluded_scl: excludedScl, composite: 'per-band-median',
    source_count: metadata.source_count, joined_count: metadata.joined_count,
    scene_ids: metadata.scene_ids, acquired_ms: metadata.acquired_ms,
    export_crs: crs, export_scale_m: scale, export_resampling: 'nearest',
    nominal_resolution_m: 10, reflectance_scale: 0.0001,
    export_requested_at: new Date().toISOString()
  };
  print('Source IDs, QA and composition parameters', receipt);
  Export.image.toDrive({image: output, description: 'napo_sentinel2_2024',
    fileNamePrefix: 'napo_sentinel2_2024', folder: 'EcuadorVivo', region: region,
    crs: crs, scale: scale, maxPixels: 5000000, fileFormat: 'GeoTIFF',
    formatOptions: {cloudOptimized: true, noData: 65535}});
  Export.table.toDrive({collection: ee.FeatureCollection([ee.Feature(null, {receipt: JSON.stringify(receipt)})]),
    description: 'napo_sentinel2_2024_receipt', fileNamePrefix: 'napo_sentinel2_2024_receipt',
    folder: 'EcuadorVivo', fileFormat: 'GeoJSON'});
  Map.centerObject(region, 10);
  Map.addLayer(rgb, {bands: ['B4', 'B3', 'B2'], min: 0, max: 3000, gamma: 1.2}, '2024 median, not a single-date photo');
});
