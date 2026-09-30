/* Ecuador Vivo: Napo province, NOT just Jatunyacu and NOT the entire Napo basin.
 * Real 10 m optical bands. Annual RGB is not a scene from one date.
 * Screening cells are candidates, never mining/pollution/river-migration claims.
 * Public reproducible settings: data/rivers/napo-config.json.
 */
var boundaryAsset = 'WM/geoLab/geoBoundaries/600/ADM1';
var boundaryFilter = {shapeGroup: 'ECU', shapeName: 'Napo'};
var asset = 'COPERNICUS/S2_SR_HARMONIZED';
var qualityAsset = 'GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED';
var years = [2019, 2024];
var periods = [['2019-01-01', '2020-01-01'], ['2024-01-01', '2025-01-01']];
var bands = ['B4', 'B3', 'B2', 'B8'];
var threshold = 0.65, minObservations = 10, rgbMinObservations = 3;
// Only one block per run. Change to 0..8 sequentially after reviewing outputs.
// Do not launch all nine blindly: first confirm quota and image quality.
var blockId = 7;
// Default: export small exact counts; connectivity is processed locally.
// 'rgb' reproduces the existing display product without re-running screening.
var exportMode = 'water-counts';
var countBands = ['y2019_water_count', 'y2019_valid_count', 'y2024_water_count', 'y2024_valid_count'];
var processingGrid = {bbox: [-78.42535, -1.24118, -77.04568, 0.03164], columns: 3, rows: 3};
var sceneSelection = {mode: 'quarter-cloud-ranked-per-block', max_per_quarter: 8};
var excludedScl = [0, 1, 3, 8, 9, 10, 11];
var waterThreshold = 0.2, changeThreshold = 0.5, waterFrequencyMin = 0.5;
var minConnectedPixels = 100, cellSize = 1000, minCellChangeHa = 1;
var crs = 'EPSG:3857', crsTransform = [10, 0, 0, 0, -10, 0];
var display = {min: 0, max: 0.3, gamma: 1.2};
var exportBands = ['y2019_R', 'y2019_G', 'y2019_B', 'y2019_A', 'y2024_R', 'y2024_G', 'y2024_B', 'y2024_A'];
var fileDimensions = 4096, maxPixels = 50000000;
var boundary = ee.FeatureCollection(boundaryAsset)
  .filter(ee.Filter.eq('shapeGroup', boundaryFilter.shapeGroup))
  .filter(ee.Filter.eq('shapeName', boundaryFilter.shapeName));
function integer(value) { return typeof value === 'number' && isFinite(value) && Math.floor(value) === value; }
boundary.size().evaluate(function (size, failure) {
  if (failure || size !== 1) { print('No unique Napo boundary; no exports.', failure || size); return; }
  if (!integer(blockId) || blockId < 0 || blockId > 8) { print('Select one block 0..8; no tasks.'); return; }
  if (exportMode !== 'water-counts' && exportMode !== 'rgb') { print('Invalid export mode; no tasks.'); return; }
  var province = boundary.geometry(), projection = ee.Projection(crs, crsTransform);
  var dx = (processingGrid.bbox[2] - processingGrid.bbox[0]) / 3, dy = (processingGrid.bbox[3] - processingGrid.bbox[1]) / 3;
  var column = blockId % 3, row = Math.floor(blockId / 3);
  var west = processingGrid.bbox[0] + column * dx, north = processingGrid.bbox[3] - row * dy;
  var blockBbox = [west, north - dy, west + dx, north];
  var block = ee.Geometry.Rectangle(blockBbox, 'EPSG:4326', false);
  var region = province.intersection(block, 10);
  var processingBlock = {id: blockId, bbox: blockBbox};
  var collections = years.map(function (year, i) {
    // merge() prefixes system:index. Preserve the provider's original ID BEFORE
    // merging quarters so Cloud Score+ still joins the exact acquisition.
    var source = ee.ImageCollection(asset).filterBounds(region).filterDate(periods[i][0], periods[i][1])
      .map(function (image) { return image.set('source_scene_index', image.get('system:index')); });
    var optical = ee.ImageCollection([]);
    [1, 4, 7, 10].forEach(function (month) {
      var start = ee.Date.fromYMD(year, month, 1);
      optical = optical.merge(source.filterDate(start, start.advance(3, 'month')).sort('CLOUDY_PIXEL_PERCENTAGE').limit(sceneSelection.max_per_quarter));
    });
    var quality = ee.ImageCollection(qualityAsset).filterBounds(region).filterDate(periods[i][0], periods[i][1]);
    return ee.ImageCollection(ee.Join.inner().apply(optical, quality,
      ee.Filter.equals({leftField: 'source_scene_index', rightField: 'system:index'})).map(function (pair) {
        pair = ee.Feature(pair);
        return ee.Image(pair.get('primary')).addBands(ee.Image(pair.get('secondary')).select('cs_cdf'));
      })).sort('source_scene_index');
  });
  var sceneRows = collections.map(function (collection, i) {
    return ee.Dictionary({year: years[i], period: periods[i], joined_count: collection.size(),
      scene_ids: collection.aggregate_array('source_scene_index'), acquired_ms: collection.aggregate_array('system:time_start')});
  });
  ee.Dictionary({scenes: sceneRows, boundary: boundary.first(), area_m2: province.area(10), bounds: block}).evaluate(function (provenance, error) {
    if (error || !provenance || !Array.isArray(provenance.scenes) || provenance.scenes.length !== 2 || provenance.scenes.some(function (row, i) {
      var seen = Object.create(null), start = Date.parse(periods[i][0]), end = Date.parse(periods[i][1]);
      return row.year !== years[i] || JSON.stringify(row.period) !== JSON.stringify(periods[i]) || !integer(row.joined_count) ||
        row.joined_count < minObservations || row.joined_count > 32 || !Array.isArray(row.scene_ids) ||
        !Array.isArray(row.acquired_ms) || row.scene_ids.length !== row.joined_count || row.acquired_ms.length !== row.joined_count ||
        row.scene_ids.some(function (id) { if (typeof id !== 'string' || !id || seen[id]) return true; seen[id] = true; return false; }) ||
        row.acquired_ms.some(function (ms) { return !isFinite(ms) || ms < start || ms >= end; });
    })) { print('Invalid acquisition provenance; no exports.', error || provenance); return; }
    var observations = collections.map(function (collection) {
      return collection.map(function (image) {
        var optical = image.select(bands).multiply(0.0001);
        var valid = image.select('cs_cdf').gte(threshold).and(optical.mask().reduce(ee.Reducer.min()));
        excludedScl.forEach(function (code) { valid = valid.and(image.select('SCL').neq(code)); });
        var denominator = optical.select('B3').add(optical.select('B8'));
        // Use identical valid support for RGB/count/frequency, zero is real non-water.
        valid = valid.and(denominator.gt(0));
        var ndwi = optical.select('B3').subtract(optical.select('B8')).divide(denominator);
        return optical.addBands(ndwi.gt(waterThreshold).rename('water')).updateMask(valid);
      });
    });
    var counts = observations.map(function (collection) { return collection.select('B4').count().setDefaultProjection(projection); });
    var rgbCommon = counts[0].gte(rgbMinObservations).and(counts[1].gte(rgbMinObservations)).clip(region);
    var rendered = observations.map(function (collection, i) {
      var rgba = collection.select(['B4', 'B3', 'B2']).median().setDefaultProjection(projection).updateMask(rgbCommon)
        .visualize({bands: ['B4', 'B3', 'B2'], min: display.min, max: display.max, gamma: display.gamma})
        .rename(['R', 'G', 'B']);
      var alpha = rgbCommon.unmask(0).multiply(255).toByte().rename('A');
      return rgba.unmask(0).addBands(alpha).rename(['R', 'G', 'B', 'A'].map(function (band) { return 'y' + years[i] + '_' + band; }));
    });
    // Counts retain exact fractions (water / valid), including real zero water.
    // No global connected components or vectorization in Earth Engine.
    var waterCounts = observations.map(function (collection, i) {
      return collection.select('water').sum().setDefaultProjection(projection).rename(countBands[i * 2])
        .addBands(counts[i].rename(countBands[i * 2 + 1]));
    });
    var receipt = {schema_version: 1, asset: asset, quality_asset: qualityAsset,
      boundary_asset: boundaryAsset, boundary_filter: boundaryFilter, boundary: provenance.boundary,
      area_m2: provenance.area_m2, bounds: provenance.bounds, scenes: provenance.scenes,
      years: years, periods: periods, bands: bands, clear_threshold: threshold, min_observations: minObservations,
      rgb_min_observations: rgbMinObservations, scene_selection: sceneSelection, processing_grid: processingGrid, processing_block: processingBlock,
      excluded_scl: excludedScl, water_formula: '(B3-B8)/(B3+B8)', water_threshold: waterThreshold,
      change_threshold: changeThreshold, water_frequency_min: waterFrequencyMin, min_connected_pixels: minConnectedPixels,
      screening_cell_m: cellSize, min_cell_change_ha: minCellChangeHa,
      export_crs: crs, export_transform: crsTransform, export_bands: exportBands, display: display,
      method: 'joint-four-band-qa-annual-median-rgb-scene-level-ndwi-frequency',
      scope: 'province-napo-incremental-blocks-not-entire-river-basin', export_requested_at: new Date().toISOString()};
    print('Actual provincial acquisition receipt', receipt);
    var prefix = 'napo_block' + blockId + (exportMode === 'rgb' ? '_rgb10_2019_2024' : '_water_counts_2019_2024');
    if (exportMode === 'water-counts') {
      receipt.product = 'water-observation-counts';
      receipt.count_bands = countBands;
      receipt.count_dtype = 'uint8';
      receipt.count_encoding = 'exact-water-and-valid-observation-counts-zero-valid-is-nodata';
    }
    var product = exportMode === 'rgb' ? ee.Image.cat(rendered).select(exportBands) : ee.Image.cat(waterCounts).select(countBands);
    Export.image.toDrive({image: product.clip(region).unmask(0).toByte(),
      description: prefix, fileNamePrefix: prefix,
      folder: 'EcuadorVivo', region: block, crs: crs, crsTransform: crsTransform,
      fileDimensions: fileDimensions, skipEmptyTiles: true, maxPixels: maxPixels, fileFormat: 'GeoTIFF',
      formatOptions: {cloudOptimized: true}});
    Export.table.toDrive({collection: ee.FeatureCollection([ee.Feature(null, {receipt: JSON.stringify(receipt)})]),
      description: prefix + '_receipt', fileNamePrefix: prefix + '_receipt',
      folder: 'EcuadorVivo', fileFormat: 'GeoJSON'});
    Map.centerObject(region, 9);
    if (exportMode === 'rgb') Map.addLayer(rendered[1].select(['y2024_R', 'y2024_G', 'y2024_B']), {min: 0, max: 255}, 'Napo RGB 2024 — native bands 10 m');
    Map.addLayer(boundary.style({color: 'dcefe1', fillColor: '00000000', width: 1}), {}, 'Napo province');
  });
});
