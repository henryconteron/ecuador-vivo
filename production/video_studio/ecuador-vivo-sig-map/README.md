# Ecuador Vivo SIG map adapter

Internal CCv2 package generated from Streamlit's official v2 template. It consumes the existing canonical catalog and presentation commands; no scientific document, persistence engine or clock of its own. Use through `studio_sig_map_ui`. SVG remains an explicit compatible alternative.

From the repository root, install this local package into the existing environment:

```powershell
& '_local/video-studio/.venv/Scripts/python.exe' -m pip install --no-deps -e 'production/video_studio/ecuador-vivo-sig-map'
```

Compiled assets ship with the package. Node is only required to rebuild. In `ecuador_vivo_sig_map/frontend`, use `npm ci --ignore-scripts`, `npm run typecheck` and `npm run build`. Exact versions and the transitive tree are locked. Builds preserve existing assets (`emptyOutDir=false`); do not run the template's optional clean command on resources you need to preserve.

OpenLayers 10.11.0 WebGLVector is encapsulated because its API is unstable. Initialization failure/context loss explicitly switches to Canvas; equivalent performance is not claimed. Originals remain OGC:CRS84, display EPSG:4326 with x=longitude/y=latitude. Other projections and raster imports are future increments.

Camera and picking are local. Envelopes include all unconfirmed sequenced intents. Python validates before one durable WorkspaceSession commit, then acknowledges the accepted sequence/version. Rejected intents remain visible for explicit retry/discard. Old responses cannot reset a newer camera. Map input is not disabled while waiting for persistence. Resize/layout never publishes a camera. Sources rebuild only when their verified representation revision changes; visibility/order/style/selection update existing resources.

The software retains the repository's reserved license. Dependency notices are separate in `THIRD-PARTY-NOTICES.md`. The actual build inventory in `frontend/build/dependencies.json` lists bundled modules. The optional GeoTIFF decoder in the npm tree is not in the presentation build. No private datasets or credentials are included. This internal package is not a public release.
