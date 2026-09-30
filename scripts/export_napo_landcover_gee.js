/* Paste in https://code.earthengine.google.com/ after enabling your own project.
 * Two export tasks: the native categorical raster and its provenance receipt.
 * This is Publisher Catalog V1, NOT a renamed Collection 3 or 4.
 * Mirror data/landcover/napo-config.json; tests enforce the shared parameters.
 */
var asset = 'projects/mapbiomas-public/assets/ecuador/lulc/v1';
var years = [2000, 2024];
var bbox = [-78.04, -1.12, -77.55, -0.72];
var region = ee.Geometry.Rectangle(bbox, 'EPSG:4326', false);
var collection = ee.ImageCollection(asset);
var subsets = years.map(function (year) {
  return collection.filter(ee.Filter.eq('year', year));
});
// Asynchronous requests avoid blocking the browser (and synchronous-XHR failures).
// No task is created until the year counts and both native grids are validated.
ee.List(subsets.map(function (subset) { return subset.size(); })).evaluate(function (counts, failure) {
  if (failure) { print('Source lookup failed; no exports created.', failure); return; }
  if (!counts || counts.length !== years.length || counts.some(function (count) { return count !== 1; })) {
    print('Expected exactly one source image per year; no exports created.', counts); return;
  }
  var images = subsets.map(function (subset, index) {
    return ee.Image(subset.first()).select('classification').rename('classification_' + years[index]);
  });
  ee.Dictionary({
    projection: images[0].projection(), secondProjection: images[1].projection(),
    nominalScale: images[0].projection().nominalScale()
  }).evaluate(function (metadata, metadataFailure) {
    if (metadataFailure) { print('Native grid lookup failed; no exports created.', metadataFailure); return; }
    var projection = metadata.projection;
    var nominalScale = metadata.nominalScale;
    if (!isFinite(nominalScale) || nominalScale < 25 || nominalScale > 35) {
      print('Unexpected native sampling; no exports created.', nominalScale); return;
    }
    if (!projection || !projection.crs || !projection.transform ||
        JSON.stringify(projection) !== JSON.stringify(metadata.secondProjection)) {
      print('Native year grids differ or are missing; no exports created.', metadata); return;
    }
    createExports(images, projection, nominalScale);
  });
});

function createExports(images, projection, nominalScale) {
var receipt = {
  schema_version: 1, asset: asset, version: 'V1.0', years: years, bbox: bbox,
  band_order: years.map(function (year) { return 'classification_' + year; }),
  crs: projection.crs, crs_transform: projection.transform,
  nominal_resolution_m: 30, native_scale_m: nominalScale, license: 'CC-BY-4.0',
  source_url: 'https://developers.google.com/earth-engine/datasets/catalog/projects_mapbiomas-public_assets_ecuador_lulc_v1',
  export_requested_at: new Date().toISOString()
};
print('Source and export parameters (not proof of independent local accuracy)', receipt);
Export.image.toDrive({
  image: ee.Image.cat(images).clip(region).unmask(0).toUint8(),
  description: 'napo_mapbiomas_v1_2000_2024',
  fileNamePrefix: 'napo_mapbiomas_v1_2000_2024', folder: 'EcuadorVivo',
  region: region, crs: projection.crs, crsTransform: projection.transform,
  maxPixels: 25000000, fileFormat: 'GeoTIFF',
  formatOptions: {cloudOptimized: true, noData: 0}
});
Export.table.toDrive({
  collection: ee.FeatureCollection([ee.Feature(null, {receipt: JSON.stringify(receipt)})]),
  description: 'napo_mapbiomas_v1_receipt', fileNamePrefix: 'napo_mapbiomas_v1_receipt',
  folder: 'EcuadorVivo', fileFormat: 'GeoJSON'
});
Map.centerObject(region, 10);
Map.addLayer(region, {color: 'ffffff'}, 'Editorial window, not canton boundaries');
}
